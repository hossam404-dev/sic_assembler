import sys
import os
from pass1 import pass1
from pass2 import pass2, generate_object_program
from optable import OPTABLE
from utils import parse_line


def export_optable(input_path: str, output_path: str) -> int:

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")


    DIRECTIVES = {"START", "END", "BYTE", "WORD", "RESB", "RESW", "BASE", "NOBASE", "ORG", "EQU"}
    seen = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            label, opcode, operand = parse_line(line)
            if opcode:
                m = opcode.upper()

                if m in DIRECTIVES:
                    continue
                if m not in seen:
                    seen.append(m)

    with open(output_path, "w", encoding="utf-8") as f:
        for m in seen:
            code = OPTABLE.get(m, "")
            f.write(f"{m} {code}\n")

    return len(seen)

def format_object_record(record):
    """Format object program record with ^ separators"""
    if record.startswith("H"):
        program_name = record[1:-12]
        start_addr = record[-12:-6]
        length = record[-6:]
        return f"{record[0]}^{program_name}^{start_addr}^{length}"
    elif record.startswith("T"):
        start_addr = record[1:7]
        byte_count = record[7:9]
        obj_code = record[9:]
        return f"{record[0]}^{start_addr}^{byte_count}^{obj_code}"
    elif record.startswith("M"):
        addr = record[1:7]
        length = record[7:9]
        return f"{record[0]}^{addr}^{length}"
    elif record.startswith("E"):
        return f"{record[0]}^{record[1:]}"
    return record

def print_symbol_table(symbols):
    print("Symbol Table:")
    print("{:<10} {:>6}".format("Label", "Address"))
    for label in sorted(symbols):
        print("{:<10} {:06X}".format(label, symbols[label]))

def print_listing(listing):
    print("\nListing:")
    for addr, obj, raw in listing:
        if addr is None:
            print("      " + "   " + " " * 10 + "   " + raw)
        else:
            print(f"{addr:06X}   {obj or '':<10}   {raw}")

def assemble(path):
    with open(path, "r") as f:
        lines = [x.rstrip("\n") for x in f]
    intermediate, symbols, start_addr, program_length = pass1(lines)
    listing = pass2(intermediate, symbols)
    object_records = generate_object_program(intermediate, symbols, start_addr, program_length, 
                                             os.path.splitext(os.path.basename(path))[0])
    print_symbol_table(symbols)
    print_listing(listing)
    print(f"\nProgram Length: {program_length:06X}")
    print("\nObject Program:")
    for record in object_records:
        print(format_object_record(record))
    
    base = os.path.splitext(os.path.basename(path))[0]
    out_path = base + ".lst"
    sym_path = base + ".sym"
    int_path = base + ".int"

    with open(sym_path, "w") as sym:
        sym.write("Symbol Table:\n")
        sym.write("{:<10} {:>6}\n".format("Label", "Address"))
        for label in sorted(symbols):
            sym.write("{:<10} {:06X}\n".format(label, symbols[label]))

    with open(out_path, "w") as o:
        o.write("Listing:\n")
        for addr, obj, raw in listing:
            if addr is None:
                o.write("      \t\t" + raw + "\n")
            else:
                obj_str = obj if obj and all(c in '0123456789ABCDEF' for c in obj.upper()) else 'NULL'
                o.write(f"{addr:06X}\t{raw}\t{obj_str}\n")
        o.write(f"\nProgram Length: {program_length:06X}\n")
        o.write("\nObject Program:\n")
        for record in object_records:
            o.write(format_object_record(record) + "\n")
    
    with open(int_path, "w") as f:
        f.write("Intermediate File:\n")
        f.write("{:<8} {:<10} {:<8} {:<10} {}\n".format("Address", "Label", "Opcode", "Operand", "Source"))
        for addr, label, opcode, operand, raw in intermediate:
            addr_str = f"{addr:06X}" if addr is not None else "      "
            label_str = label or ""
            opcode_str = opcode or ""
            operand_str = operand or ""
            f.write(f"{addr_str:<8} {label_str:<10} {opcode_str:<8} {operand_str:<10} {raw}\n")
    print("Listing file written:", out_path)
    print("Symbol table file written:", sym_path)
    print("Intermediate file written:", int_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.argv.append("--all-examples")
    
    if sys.argv[1] == "--all-examples":
        example_dir = "example"
        if not os.path.isdir(example_dir):
            print(f"Error: {example_dir} directory not found")
            sys.exit(1)
        
        txt_files = [f for f in os.listdir(example_dir) if f.endswith(".txt")]
        if not txt_files:
            print(f"No .txt files found in {example_dir}")
            sys.exit(1)
        
        print(f"Processing {len(txt_files)} program files from {example_dir}:\n")
        for txt_file in sorted(txt_files):
            input_path = os.path.join(example_dir, txt_file)
            print(f"{'='*60}")
            print(f"Assembling: {input_path}")
            print(f"{'='*60}")
            try:
                assemble(input_path)
                base = os.path.splitext(txt_file)[0]
                out = base + ".optable"
                n = export_optable(input_path, out)
                print(f"Wrote {out} with {n} mnemonics")
            except Exception as e:
                print(f"Error assembling {input_path}: {e}")
            print()
        print("All programs assembled successfully!")
    else:
        path = sys.argv[1]
        assemble(path)

        if "--export-optable" in sys.argv or "-e" in sys.argv:
            base = os.path.splitext(os.path.basename(path))[0]
            out = base + ".optable"
            try:
                n = export_optable(path, out)
                print(f"Wrote {out} with {n} mnemonics")
                try:
                    print("\nOptable:")
                    with open(out, "r", encoding="utf-8") as fo:
                        for line in fo:
                            print(line.rstrip())
                except Exception as e:
                    print(f"Could not read {out}: {e}")
            except FileNotFoundError as e:
                print(e)
