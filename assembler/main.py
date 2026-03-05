from enum import Enum
from dataclasses import dataclass

from utils import to_bin, TermFormat

REGISTERS = {
    "$zero": 0,
    "$r1": 1, "$r2": 2, "$r3": 3, "$r4": 4, "$r5": 5, "$r6": 6, "$r7": 7, "$r8": 8, "$r9": 9,
    "$s0": 16, "$s1": 17, "$s2": 18, "$s3": 19, "$s4": 20, "$s5": 21, "$s6": 22, "$s7": 23,
    "$sp": 29,
    "$ra": 31
}

class InstrFormat(Enum):
    R = "R-TYPE"
    I = "I-TYPE"
    J = "J-TYPE"
    M = "MEM-TYPE"

class Operand(Enum):
    A = "A"
    B = "B"
    C = "C"
    I = "Immediate"
    J = "Address"

@dataclass
class InstructionDef:
    opcode: str
    format: InstrFormat
    operand_order: tuple = ()
    funct: str = ""

ISA = {
    # R-Type
    "add":  InstructionDef(opcode="000000", format=InstrFormat.R, operand_order=(Operand.C, Operand.A, Operand.B), funct="000010"),
    "sub":  InstructionDef(opcode="000000", format=InstrFormat.R, operand_order=(Operand.C, Operand.A, Operand.B), funct="000011"),
    "inc":  InstructionDef(opcode="000000", format=InstrFormat.R, operand_order=(Operand.C, Operand.A),            funct="000011"),
    "dec":  InstructionDef(opcode="000000", format=InstrFormat.R, operand_order=(Operand.C, Operand.A),            funct="000011"),
    "not":  InstructionDef(opcode="000000", format=InstrFormat.R, operand_order=(Operand.C, Operand.A),            funct="000011"),
    "and":  InstructionDef(opcode="000000", format=InstrFormat.R, operand_order=(Operand.C, Operand.A, Operand.B), funct="000111"),
    "or":   InstructionDef(opcode="000000", format=InstrFormat.R, operand_order=(Operand.C, Operand.A, Operand.B), funct="001000"),
    "xor":  InstructionDef(opcode="000000", format=InstrFormat.R, operand_order=(Operand.C, Operand.A, Operand.B), funct="001000"),
    "sll":  InstructionDef(opcode="000000", format=InstrFormat.R, operand_order=(Operand.C, Operand.B),            funct="001010"),
    "srl":  InstructionDef(opcode="000000", format=InstrFormat.R, operand_order=(Operand.C, Operand.B),            funct="001011"),
    "mult": InstructionDef(opcode="000000", format=InstrFormat.R, operand_order=(Operand.C, Operand.A, Operand.B), funct="001100"),

    # I-Type
    "addi": InstructionDef(opcode="000100", format=InstrFormat.I, operand_order=(Operand.B, Operand.A, Operand.I)),
    "andi": InstructionDef(opcode="000101", format=InstrFormat.I, operand_order=(Operand.B, Operand.A, Operand.I)),
    "ori":  InstructionDef(opcode="000110", format=InstrFormat.I, operand_order=(Operand.B, Operand.A, Operand.I)),
    "ldi":  InstructionDef(opcode="000111", format=InstrFormat.I, operand_order=(Operand.B, Operand.I)),
    "beq":  InstructionDef(opcode="001000", format=InstrFormat.I, operand_order=(Operand.B, Operand.A, Operand.I)),
    "bne":  InstructionDef(opcode="001001", format=InstrFormat.I, operand_order=(Operand.B, Operand.A, Operand.I)),

    # M-Type
    "lw":   InstructionDef(opcode="010000", format=InstrFormat.M, operand_order=(Operand.B, Operand.I, Operand.A)),
    "sw":   InstructionDef(opcode="010001", format=InstrFormat.M, operand_order=(Operand.B, Operand.I, Operand.A)),

    # J-Type
    "j":    InstructionDef(opcode="010010", format=InstrFormat.J, operand_order=(Operand.J,)),
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

                if not line.strip(): continue

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

            if type(arg) == str and arg.lower() in REGISTERS:
                arg = REGISTERS[arg.lower()]
                
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
        if len(args) != len(instr.operand_order):
            raise ValueError("Invalid number of args for R-Type.")

        # default fields
        fields = {
            Operand.A: 0,
            Operand.B: 0,
            Operand.C: 0
        }

        for field, value in zip(instr.operand_order, args):
            fields[field] = value

        return (instr.opcode + 
                to_bin(fields[Operand.A], 5) + 
                to_bin(fields[Operand.B], 5) + 
                to_bin(fields[Operand.C], 5) + 
                "00000" + 
                instr.funct)

    @classmethod
    def _encode_i_type(cls, instr:InstructionDef, args:list, line_index:int) -> str:
        if len(args) != len(instr.operand_order):
            raise ValueError("Invalid number of args for I-Type.")

        # default fields
        fields = {
            Operand.A: 0,
            Operand.B: 0,
            Operand.I: 0
        }

        for field, value in zip(instr.operand_order, args):
            fields[field] = value

        if instr == ISA["beq"] or instr == ISA["bne"]: # relative jump
            fields[Operand.I] = fields[Operand.I] - line_index - 1

        return (instr.opcode + 
                to_bin(fields[Operand.A], 5) + 
                to_bin(fields[Operand.B], 5) + 
                to_bin(fields[Operand.I], 16, signed=True))

    @classmethod
    def _encode_m_type(cls, instr:InstructionDef, args:list) -> str:
        if len(args) != len(instr.operand_order):
            raise ValueError("Invalid number of args for M-Type.")

        # default fields
        fields = {
            Operand.A: 0,
            Operand.B: 0,
            Operand.I: 0
        }

        for field, value in zip(instr.operand_order, args):
            fields[field] = value
        
        return (instr.opcode + 
                to_bin(fields[Operand.A], 5) + 
                to_bin(fields[Operand.B], 5) + 
                to_bin(fields[Operand.I], 16, signed=True))

    @classmethod
    def _encode_j_type(cls, instr:InstructionDef, args:list) -> str:
        if len(args) != len(instr.operand_order):
            raise ValueError("Invalid number of args for J-Type.")

        # default fields
        fields = {
            Operand.J: 0
        }

        for field, value in zip(instr.operand_order, args):
            fields[field] = value

        return (instr.opcode +
                to_bin(fields[Operand.J], 26))

if __name__ == "__main__":
    with open("code.asm", 'r') as f:
        lines = f.readlines()
    
    bin_code, bin_data = Assembler.assemble(lines)
    
    with open("code.bin", 'w') as f:
        f.writelines(bin_code)

    with open("data.bin", 'w') as f:
        f.writelines([d+"\n" for d in bin_data])
