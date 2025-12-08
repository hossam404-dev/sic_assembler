import sys
import os
from pass1 import pass1
from pass2 import pass2
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
    print_symbol_table(symbols)
    print_listing(listing)
    print(f"\nProgram Length: {program_length:06X}")
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
        print("Usage: python main.py program.txt [--export-optable]")
        sys.exit(1)
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
