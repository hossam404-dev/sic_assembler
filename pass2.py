from optable import OPTABLE

def encode_instruction(opcode, operand, symbols):
    if opcode not in OPTABLE:
        return None
    ophex = OPTABLE[opcode]
    addr = 0
    indexed = False
    if operand:
        op = operand.strip()
        if op.endswith(",X"):
            indexed = True
            op = op[:-2].strip()
        if op in symbols:
            addr = symbols[op]
        elif op.isdigit():
            addr = int(op)
        else:
            return None
    if indexed:
        addr = addr + 0x8000
    return f"{ophex}{addr:04X}"

def pass2(intermediate, symbols):
    listing = []
    for addr, label, opcode, operand, raw in intermediate:
        if opcode is None:
            listing.append((None, None, raw))
            continue
        if opcode == "START":
            listing.append((addr, None, raw))
            continue
        if opcode == "END":
            listing.append((addr, None, raw))
            break
        if opcode == "WORD":
            try:
                listing.append((addr, f"{int(operand):06X}", raw))
            except Exception:
                listing.append((addr, None, raw))
            continue
        if opcode == "BYTE":
            op = operand
            if op.startswith("C'") and op.endswith("'"):
                listing.append((addr, ''.join(f"{ord(c):02X}" for c in op[2:-1]), raw))
                continue
            if op.startswith("X'") and op.endswith("'"):
                hx = op[2:-1].upper()
                if len(hx) % 2 == 1:
                    hx = "0" + hx
                listing.append((addr, hx, raw))
                continue
            listing.append((addr, None, raw))
            continue
        if opcode in ("RESW", "RESB"):
            listing.append((addr, None, raw))
            continue
        obj = encode_instruction(opcode, operand, symbols)
        listing.append((addr, obj, raw))
    return listing

def generate_object_program(intermediate, symbols, start_addr, program_length, program_name="PROGRAM"):
    """Generate SIC object program (H, T, E, M records)"""
    records = []
    modification_records = []
    
    records.append(f"H{program_name}{start_addr:06X}{program_length:06X}")
    
    text_records = []
    current_record_addr = None
    current_record_bytes = []
    
    for addr, label, opcode, operand, raw in intermediate:
        if opcode is None or opcode in ("START", "END"):
            continue
        
        if opcode == "WORD":
            try:
                obj_hex = f"{int(operand):06X}"
            except:
                continue
        elif opcode == "BYTE":
            op = operand
            if op.startswith("C'") and op.endswith("'"):
                obj_hex = ''.join(f"{ord(c):02X}" for c in op[2:-1])
            elif op.startswith("X'") and op.endswith("'"):
                hx = op[2:-1].upper()
                if len(hx) % 2 == 1:
                    hx = "0" + hx
                obj_hex = hx
            else:
                continue
        elif opcode in ("RESW", "RESB"):
            continue
        else:
            obj_hex = encode_instruction(opcode, operand, symbols)
            if obj_hex is None:
                continue
            if operand:
                op = operand.strip()
                if op.endswith(",X"):
                    op = op[:-2].strip()
                if op in symbols:
                    modification_records.append(f"M{addr+1:06X}05")
        
        if current_record_addr is None:
            current_record_addr = addr
            current_record_bytes = []
        
        current_record_bytes.append(obj_hex)
        
        total_bytes = sum(len(b) // 2 for b in current_record_bytes)
        if total_bytes >= 30:
            byte_count = sum(len(b) // 2 for b in current_record_bytes)
            obj_code = '^'.join(current_record_bytes)
            records.append(f"T{current_record_addr:06X}{byte_count:02X}{obj_code}")
            current_record_addr = None
            current_record_bytes = []
    
    if current_record_bytes:
        byte_count = sum(len(b) // 2 for b in current_record_bytes)
        obj_code = '^'.join(current_record_bytes)
        records.append(f"T{current_record_addr:06X}{byte_count:02X}{obj_code}")
    
    # Add modification records
    records.extend(modification_records)
    
    entry_addr = start_addr  
    records.append(f"E{entry_addr:06X}")
    
    return records
