import re
import sys
import argparse

def convert_assembly_to_binary_file(asm_file, binary_file):
    with open(asm_file, "r") as f:
        result = translate_lines(f.readlines())
        output = "\n".join([l for l in result if l]) 
        with open(binary_file, "w") as f:
            f.write(output)

def translate_lines(lines):
    lines = strip_whitespace_and_comments(lines)
    symbol_table = build_symbol_table(lines)
    translate_instruction = build_instruction_translator(symbol_table)
    return [translate_instruction(x) for x in lines]

def strip_whitespace_and_comments(lines):
    instructions = []
    for line in lines:
        stripped_line = line.strip() 
        if stripped_line:
            if not stripped_line.startswith("//"):
                if "//" in stripped_line:
                    instructions.append(stripped_line.split("//")[0].strip())
                else:
                    instructions.append(stripped_line)
    return instructions

def build_symbol_table(lines):
    symbols = {
        "R0": "0000000000000000",
        "R1": "0000000000000001",
        "R2": "0000000000000010",
        "R3": "0000000000000011",
        "R4": "0000000000000100",
        "R5": "0000000000000101",
        "R6": "0000000000000110",
        "R7": "0000000000000111",
        "R8": "0000000000001000",
        "R9": "0000000000001001",
        "R10": "0000000000001010",
        "R11": "0000000000001011",
        "R12": "0000000000001100",
        "R13": "0000000000001101",
        "R14": "0000000000001110",
        "R15": "0000000000001111",
        "SP": "0000000000000000",
        "ARG": "0000000000000010",
        "LCL": "0000000000000001",
        "THIS": "0000000000000011",
        "THAT": "0000000000000100",
        "KBD": "0110000000000000",
        "SCREEN": "0100000000000000"
    }
    is_address_instruction = lambda x: x.startswith("@")
    is_compute_instruction = lambda x: "=" in x or ";" in x
    label_value = lambda x: x.replace("(", "").replace(")", "").strip()
    current_line_num = 0
    for line in lines: 
        if is_address_instruction(line) or is_compute_instruction(line):
            current_line_num +=1 
        elif is_label(line):
            symbols[label_value(line)] = decimal_to_binary(current_line_num)
    base_address = 16
    for line in lines:
        if line.startswith("@"):
            value = line[1:]
            if value not in symbols and not value.isnumeric():
                symbols[value] = decimal_to_binary(base_address)
                base_address += 1
    return symbols

def build_instruction_translator(symbol_table):
    COMPUTATIONS = {
        "0": "0101010",
        "1": "0111111",
        "-1": "0111010",
        "D": "0001100",
        "A": "0110000",
        "!D": "0001101",
        "!A": "0110001",
        "-D": "0001111",
        "-A": "0110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "D+A": "0000010",
        "D-A": "0010011",
        "A-D": "0000111",
        "D&A": "0000000",
        "D|A": "0010101",
        "M": "1110000",
        "!M": "1110001",
        "-M": "1110011",
        "M+1": "1110111",
        "M-1": "1110010",
        "D+M": "1000010",
        "D-M": "1010011",
        "M-D": "1000111",
        "D&M": "1000000",
        "D|M": "1010101"
    }
    DESTINATIONS = {
        "": "000",
        "M": "001",
        "D": "010",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "AD": "110",
        "AMD": "111"
    }
    JUMPS = {
        "": "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111"
    }
    def fn(line):
        if is_label(line):
            return
        if line.startswith("@"):
            value = line[1:]
            if value in symbol_table:
                return symbol_table[value]
            return decimal_to_binary(int(value))
        dest, jump = "", ""
        comp = line.split("=").pop().split(";")[0]
        if "=" in line: 
            dest = line.split("=")[0]
        if ";" in line: 
            jump = line.split(";").pop()
        return f"111{COMPUTATIONS.get(comp, '0000000')}{DESTINATIONS.get(dest, '000')}{JUMPS.get(jump, '000')}"
    return fn

def is_label(line):
    return line.startswith("(") and line.endswith(")")

def decimal_to_binary(decimal_value):  
    return f"{decimal_value:0>16b}"

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description="Generates a hack binary file from assembly")
    parser.add_argument("asm_file", help="name of a HACK assembly file, i.e input.asm")
    parser.add_argument("binary_file", help="name of the HACK file, i.e output.hack")
    args = parser.parse_args()
    convert_assembly_to_binary_file(args.asm_file, args.binary_file)