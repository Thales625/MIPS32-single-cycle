def to_bin(value:int, size:int, signed:bool=False) -> str:
    max_val = (1 << size) - 1

    if value > max_val:
        raise ValueError(f"Value {value} out of range for {size} bits ({max_val}).")

    # negative numbers
    if value < 0: value = (1 << size) + value
        
    return f"{value:0{size}b}"

class TermFormat:
    PURPLE = '\033[95m'
    BLUE   = '\033[94m'
    CYAN   = '\033[96m'
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    RED    = '\033[91m'
    BOLD   = '\033[1m'
    UNDERLINE = '\033[4m'
    END    = '\033[0m'
