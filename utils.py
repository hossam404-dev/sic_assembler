import re

def parse_line(line):
    if line is None:
        return None, None, None
    s = line.strip()
    if s == "" or s.startswith('.'):
        return None, None, None
    parts = re.split(r'\s+', s, maxsplit=2)
    if len(parts) == 1:
        return None, parts[0].upper(), None
    if len(parts) == 2:
        return None, parts[0].upper(), parts[1].upper()
    return parts[0].upper(), parts[1].upper(), parts[2].upper()

def byte_length_operand(operand):
    if operand is None:
        return 0
    op = operand.strip()
    if op.startswith("C'") and op.endswith("'"):
        return len(op[2:-1])
    if op.startswith("X'") and op.endswith("'"):
        hx = op[2:-1]
        return (len(hx) + 1) // 2
    return 0
