import sys

class Parser:
    ARITHMETIC = {
        "add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"
    }

    SEGMENTS = {
        "argument", "local", "static", "constant", "this", "that", "pointer", "temp"
    }

    def __init__(self, input_file):
        self.file = open(input_file, "r")
        self.current_command = None
        self.next_command = None
        self._advance_to_next_command()

    def has_more_commands(self):
        return self.next_command is not None

    def advance(self):
        self.current_command = self.next_command
        self._advance_to_next_command()

    def command_type(self):
        op = self.current_command[0]
        if op in self.ARITHMETIC:
            return "C_ARITHMETIC"
        elif op == "push":
            return "C_PUSH"
        elif op == "pop":
            return "C_POP"
        elif op == "label":
            return "C_LABEl"
        elif op == "goto":
            return "C_goto"
        elif op == "if-goto":
            return "C_IF"
        else:
            raise ValueError(f"Unknown command {op}")

    def arg1(self):
        if self.command_type() == "C_ARITHMETIC":
            return self.current_command[0]
        return self.current_command[1]

    def arg2(self):
        return int(self.current_command[2])

    def _advance_to_next_command(self):
        while True:
            line = self.file.readline()
            if not line:
                self.next_command = None
                return
            line = line.split("//")[0].strip()
            if line == "":
                continue
            tokens = line.split()
            self.next_command = tokens
            return

    def close(self):
        self.file.close()

class CodeWriter:
    def __init__(self, output_file):
        self.file = open(output_file, "w")
        self.filename = output_file.split(".")[0]
        self.label_counter = 0

    def write_arithmetic(self, command):
        if command == "add":
            self._write_binary("M=M+D")
        elif command == "sub":
            self._write_binary("M=M-D")
        elif command == "neg":
            self._write_unary("M=-M")
        elif command == "eq":
            self._write_compare("JEQ")
        elif command == "gt":
            self._write_compare("JGT")
        elif command == "lt":
            self._write_compare("JLT")
        elif command == "and":
            self._write_binary("M=M&D")
        elif command == "or":
            self._write_binary("M=M|D")
        elif command == "not":
            self._write_unary("M=!M")

    def write_push_pop(self, command_type, segment, index):
        if command_type == "C_PUSH":
            if segment == "constant":
                self.file.write(f"@{index}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            else:
                base = self._segment_base(segment, index)
                self.file.write(f"{base}D=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif command_type == "C_POP":
            base = self._segment_base(segment, index)
            self.file.write(f"@SP\nM=M-1\nA=M\nD=M\n{base}M=D\n")

    def _segment_base(self, segment, index):
        # Returns assembly code to set A to the target address
        if segment == "local":
            return f"@LCL\nD=M\n@{index}\nA=D+A\n"
        elif segment == "argument":
            return f"@ARG\nD=M\n@{index}\nA=D+A\n"
        elif segment == "this":
            return f"@THIS\nD=M\n@{index}\nA=D+A\n"
        elif segment == "that":
            return f"@THAT\nD=M\n@{index}\nA=D+A\n"
        elif segment == "pointer":
            return f"@{'THIS' if int(index) == 0 else 'THAT'}\n"
        elif segment == "temp":
            return f"@{5+int(index)}\n"
        elif segment == "static":
            return f"@{self.filename}.{index}\n"
        else:
            raise ValueError(f"Unknown segment: {segment}")

    def _write_binary(self, op):
        self.file.write("@SP\nM=M-1\nA=M\nD=M\n@SP\nM=M-1\nA=M\n" + op + "\n@SP\nM=M+1\n")

    def _write_unary(self, op):
        self.file.write("@SP\nM=M-1\nA=M\n" + op + "\n@SP\nM=M+1\n")

    def _write_compare(self, jump):
        label_true = f"TRUE_{self.label_counter}"
        label_end = f"END_{self.label_counter}"
        self.label_counter += 1
        self.file.write(
            "@SP\nM=M-1\nA=M\nD=M\n@SP\nM=M-1\nA=M\nD=M-D\n"
            f"@{label_true}\nD;{jump}\n"
            "@SP\nA=M\nM=0\n"
            f"@{label_end}\n0;JMP\n"
            f"({label_true})\n@SP\nA=M\nM=-1\n"
            f"({label_end})\n@SP\nM=M+1\n"
        )
    def write_label(self, label):
        self.file.write(f"// label {label}\n")
        self.file.write(f"({label})\n")

    def write_goto(self, label):
        self.file.write(f"// goto {label}\n")
        self.file.write(f"@{label})\n0;JMP\n")

    def write_if(self, label):
        self.file.write(f"// if-goto {label}\n")
        self.file.write(
            "@SP\n"
            "M=M-1\n"
            "A=M\n"
            "D=M\n"
            f"@{label}\n"
            "D;JNE\n"
        )

    def close(self):
        self.file.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 vmtranslator.py MyProgram.vm")
        return
    input_file = sys.argv[1]
    output_file = input_file.replace(".vm", ".asm")

    parser = Parser(input_file)
    codewriter = CodeWriter(output_file)

    while parser.has_more_commands():
        parser.advance()
        ctype = parser.command_type()
        if ctype == "C_ARITHMETIC":
            codewriter.write_arithmetic(parser.arg1())
        elif ctype in ("C_PUSH", "C_POP"):
            codewriter.write_push_pop(ctype, parser.arg1(), parser.arg2())
        elif ctype == "C_LABEL":
            codewriter.write_label(parser.arg1())
        elif ctype == "C_GOTO":
            codewriter.write_goto(parser.arg1())
        elif ctype == "C_if":
            codewriter.write_if(parser.arg1())
    parser.close()
    codewriter.close()

if __name__ == "__main__":
    main()
