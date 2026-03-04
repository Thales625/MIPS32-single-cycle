from enum import Enum
from dataclasses import dataclass

def to_bin(value:int, size:int, signed:bool=False) -> str:
    if signed:
        min_val = -(1 << (size - 1))
        max_val =  (1 << (size - 1)) - 1
    else:
        min_val = 0
        max_val = (1 << size) - 1

    if not (min_val <= value <= max_val):
        raise ValueError(f"Value {value} out of range for {size} bits ({min_val} to {max_val}).")

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

class InstrFormat(Enum):
    R = "R-TYPE"
    I = "I-TYPE"
    J = "J-TYPE"

    M = "MEM-TYPE"

@dataclass
class InstructionDef:
    opcode: str
    format: InstrFormat
    funct: str = ""

ISA = {
    "add":  InstructionDef(opcode="000000", format=InstrFormat.R, funct="000010"),
    "sub":  InstructionDef(opcode="000000", format=InstrFormat.R, funct="000011"),
    "sll":  InstructionDef(opcode="000000", format=InstrFormat.R, funct="001010"),
    "srl":  InstructionDef(opcode="000000", format=InstrFormat.R, funct="001011"),
    "mul":  InstructionDef(opcode="000000", format=InstrFormat.R, funct="001100"),
    "addi": InstructionDef(opcode="000100", format=InstrFormat.I),
    "subi": InstructionDef(opcode="000101", format=InstrFormat.I),
    "ldi":  InstructionDef(opcode="000110", format=InstrFormat.I),
    "beq":  InstructionDef(opcode="000111", format=InstrFormat.I),
    "lw":   InstructionDef(opcode="010000", format=InstrFormat.M),
    "sw":   InstructionDef(opcode="010001", format=InstrFormat.M),
    "j":    InstructionDef(opcode="010010", format=InstrFormat.J),
}

class AssemblerState(Enum):
    D = "DATA-SECTION"
    T = "TEXT-SECTION"

class Assembler:
    sym_table = {}
    state = None

    @classmethod
    def assemble(cls, lines:list[str]) -> list[str]:
        print(TermFormat.BOLD + TermFormat.BLUE + "MIPS Assembler" + TermFormat.END, end="\n\n")

        # FIRST PASS
        print(TermFormat.BOLD + TermFormat.UNDERLINE + "First pass" + TermFormat.END)
        code_address = 0
        data_bin = []
        data_address = 0
        first_pass_out = []
        for i, line in enumerate(lines):
            i+=1
            line = line.replace("\n", '') # solve break line
            line = line.split('#')[0].strip() # solve comments
            line = line.replace(',', ' ')

            # ignore empty lines
            if not line: continue

            # .DATA
            if line.lower().startswith(".data"):
                cls.state = AssemblerState.D
                continue

            # .TEXT
            if line.lower().startswith(".text"):
                cls.state = AssemblerState.T
                continue

            # EQV
            if line.lower().startswith(".eqv"):
                line_split = line.split()
                if len(line_split) == 3:
                    if not line_split[1] in Assembler.sym_table:
                        Assembler.sym_table[line_split[1]] = line_split[2]
                    else:
                        print(TermFormat.YELLOW + f"Label '{label_split[1]}' already defined in Symbol table." + TermFormat.END)
                else:
                    raise ValueError(f"Define with invalid format in line {i}.")
                continue

            # DATA SECTION
            if cls.state == AssemblerState.D:
                label_split = line.split(':')
                if len(label_split) > 1:
                    if not label_split[0] in Assembler.sym_table:
                        Assembler.sym_table[label_split[0]] = data_address
                    else:
                        print(TermFormat.YELLOW + f"Label '{label_split[0]}' already defined in line {Assembler.sym_table[label_split[0]]}." + TermFormat.END)

                data_info = label_split[-1].split()
                if len(data_info) > 1:
                    if data_info[0].startswith(".space"):
                        for _ in range(int(data_info[1], 0)):
                            data_bin.append(to_bin(0, 32))
                            data_address += 4
                        continue

                    if data_info[0].startswith(".word"):
                        for v in data_info[1:]:
                            data_bin.append(to_bin(int(v, 0), 32))
                            data_address += 4
                        continue
                else:
                    raise ValueError(f"Invalid format in data section line {i}")
                continue

            # TEXT/CODE SECTION
            if cls.state == AssemblerState.T:
                # LABEL
                label_split = line.split(':')
                if len(label_split) > 1:
                    if not label_split[0] in Assembler.sym_table:
                        Assembler.sym_table[label_split[0]] = code_address
                    else:
                        print(TermFormat.YELLOW + f"Symbol '{label_split[0]}' already defined with value: {Assembler.sym_table[label_split[0]]}." + TermFormat.END)
                    line = label_split[1].strip()

                first_pass_out.append((i, line))
                code_address += 1
                continue

        print()
        print(TermFormat.UNDERLINE + TermFormat.BLUE + "\tData Section:" + TermFormat.END)
        for address, value in enumerate(data_bin):
            print(f"\t\t{f'[{address}]':<4} =  b{value}")

        print()
        print(TermFormat.UNDERLINE + TermFormat.CYAN + "\tSymbol Table:" + TermFormat.END)
        for symbol, value in cls.sym_table.items():
            print(f"\t\t{symbol:<10} = {value}")
        print()

        # SECOND PASS
        print(TermFormat.BOLD + TermFormat.UNDERLINE + "Second pass" + TermFormat.END)
        code_bin = []
        for line_index, (i, line) in enumerate(first_pass_out):
            try:
                bin_line = cls.assemble_line(line, line_index)
                code_bin.append(bin_line + "\n")

                print(f"\t{line:<20} -> b{bin_line}")
            except Exception as e:
                print(TermFormat.RED + f"Error line {i}:\n\t{line}\n\t{e}" + TermFormat.END)

        return code_bin, data_bin

    @classmethod
    def assemble_line(cls, line:str, line_index:int) -> str:
        line = line.replace(',', ' ').replace('(', ' ').replace(')', ' ')
        parts = line.split()
        if not parts: return ""

        mnemonic = parts[0].lower()
        args = []
        for arg in parts[1:]:
            if arg in Assembler.sym_table:
                arg = Assembler.sym_table[arg]
                
            if type(arg) == str: arg = arg.replace('$', '')

            args.append(int(str(arg), 0))

        if mnemonic not in ISA: raise ValueError(f"Instruction '{mnemonic}' not found.")

        instr = ISA[mnemonic]

        if instr.format == InstrFormat.R:
            return cls._encode_r_type(instr, args)
        elif instr.format == InstrFormat.I:
            return cls._encode_i_type(instr, args, line_index)
        elif instr.format == InstrFormat.M:
            return cls._encode_m_type(instr, args)
        elif instr.format == InstrFormat.J:
            return cls._encode_j_type(instr, args)

    @classmethod
    def _encode_r_type(cls, instr:InstructionDef, args:list) -> str:
        if len(args) == 3: # ex: add $c, $a, $b
            c, a, b = args
        elif len(args) == 2: # ex: sll $c, $b
            c, b = args
            a = 0
        else:
            raise ValueError("Invalid number of args for R-Type.")

        return (instr.opcode + 
                to_bin(a, 5) + 
                to_bin(b, 5) + 
                to_bin(c, 5) + 
                "00000" + 
                instr.funct)

    @classmethod
    def _encode_i_type(cls, instr:InstructionDef, args:list, line_index:int) -> str:
        if len(args) == 3:
            a, b, imm = args

            if instr == ISA["beq"]: # BEQ | relative jump
                imm = imm - line_index - 1
        elif len(args) == 2: # ldi
            b, imm = args
            a = 0
        else:
            raise ValueError("Invalid number of args for I-Type.")

        return (instr.opcode + 
                to_bin(a, 5) + 
                to_bin(b, 5) + 
                to_bin(imm, 16, signed=True))

    @classmethod
    def _encode_m_type(cls, instr:InstructionDef, args:list) -> str:
        if len(args) != 3: raise ValueError("Invalid format for memory-type instruction.")
        
        b, imm, a = args
        
        return (instr.opcode + 
                to_bin(a, 5) + 
                to_bin(b, 5) + 
                to_bin(imm, 16, signed=True))

    @classmethod
    def _encode_j_type(cls, instr:InstructionDef, args:list) -> str:
        if len(args) != 1: raise ValueError("J-Type requires 1 argument (address).")

        address = args[0]
        return instr.opcode + to_bin(address, 26)


if __name__ == "__main__":
    with open("code.asm", 'r') as f:
        lines = f.readlines()
    
    bin_code, bin_data = Assembler.assemble(lines)
    
    with open("code.bin", 'w') as f:
        f.writelines(bin_code)

    with open("data.bin", 'w') as f:
        f.writelines([d+"\n" for d in bin_data])
