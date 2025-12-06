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
        # Try to resolve symbol or use direct integer
        if op in symbols:
            addr = symbols[op]
        elif op.isdigit():
            addr = int(op)
        else:
            # If symbol not found, mark as error
            return None
    if indexed:
        # SIC indexed addressing: set the highest bit (0x8000)
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
