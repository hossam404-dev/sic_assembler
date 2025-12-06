from optable import OPTABLE
from utils import parse_line, byte_length_operand

def pass1(lines):
    LOCCTR = 0
    start_addr = 0
    symbols = {}
    intermediate = []
    started = False

    for raw in lines:
        label, opcode, operand = parse_line(raw)
        if opcode is None:
            intermediate.append((None, label, opcode, operand, raw))
            continue

        if opcode == "START":
            if operand:
                try:
                    start_addr = int(operand, 16)
                except Exception:
                    start_addr = int(operand)
            LOCCTR = start_addr
            started = True
            intermediate.append((LOCCTR, label, opcode, operand, raw))
            continue

        if not started:
            start_addr = 0
            LOCCTR = 0
            started = True

        addr_before = LOCCTR

        if label:
            if label in symbols:
                raise ValueError(label)
            symbols[label] = addr_before

        if opcode == "END":
            intermediate.append((addr_before, label, opcode, operand, raw))
            break

        if opcode == "WORD":
            LOCCTR += 3
        elif opcode == "RESW":
            if operand is None:
                raise ValueError("Missing operand for RESW")
            try:
                count = int(operand)
            except ValueError:
                try:
                    count = int(operand, 16)
                except ValueError:
                    raise ValueError(f"Invalid operand for RESW: {operand!r}")
            LOCCTR += 3 * count
        elif opcode == "RESB":
            if operand is None:
                raise ValueError("Missing operand for RESB")
            try:
                count = int(operand)
            except ValueError:
                try:
                    count = int(operand, 16)
                except ValueError:
                    raise ValueError(f"Invalid operand for RESB: {operand!r}")
            LOCCTR += count
        elif opcode == "BYTE":
            LOCCTR += byte_length_operand(operand)
        else:
            LOCCTR += 3

        intermediate.append((addr_before, label, opcode, operand, raw))

    program_length = LOCCTR - start_addr
    return intermediate, symbols, start_addr, program_length
