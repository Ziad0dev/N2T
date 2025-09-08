import sys
import os
import glob

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
            return "C_LABEL"
        elif op == "goto":
            return "C_GOTO"
        elif op == "if-goto":
            return "C_IF"
        elif op == "function":
            return "C_FUNCTION"
        elif op == "call":
            return "C_CALL"
        elif op == "return":
            return "C_RETURN"
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
        self.filename = None
        self.label_counter = 0
        self.current_function = None
        self.call_counter = 0

    def set_filename(self, filename):
        self.filename = filename

    def write_bootstrap(self):
        self.file.write("@256\nD=A\n@SP\nM=D\n")
        self.write_call("Sys.init", 0)

    def write_arithmetic(self, command):
        self.file.write(f"// {command}\n")
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
        self.file.write(f"// {command_type.lower()} {segment} {index}\n")
        if command_type == "C_PUSH":
            if segment == "constant":
                self.file.write(f"@{index}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment in ("local", "argument", "this", "that"):
                base = self._segment_pointer(segment)
                self.file.write(f"@{index}\nD=A\n{base}A=M+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "pointer":
                addr = "THIS" if int(index) == 0 else "THAT"
                self.file.write(f"@{addr}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "temp":
                self.file.write(f"@{5+int(index)}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "static":
                self.file.write(f"@{self.filename}.{index}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif command_type == "C_POP":
            if segment in ("local", "argument", "this", "that"):
                base = self._segment_pointer(segment)
                self.file.write(f"@{index}\nD=A\n{base}D=M+D\n@R13\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@R13\nA=M\nM=D\n")
            elif segment == "pointer":
                addr = "THIS" if int(index) == 0 else "THAT"
                self.file.write(f"@SP\nM=M-1\nA=M\nD=M\n@{addr}\nM=D\n")
            elif segment == "temp":
                self.file.write(f"@SP\nM=M-1\nA=M\nD=M\n@{5+int(index)}\nM=D\n")
            elif segment == "static":
                self.file.write(f"@SP\nM=M-1\nA=M\nD=M\n@{self.filename}.{index}\nM=D\n")

    def write_label(self, label):
        if self.current_function:
            full_label = f"{self.current_function}${label}"
        else:
            full_label = label
        self.file.write(f"// label {label}\n")
        self.file.write(f"({full_label})\n")

    def write_goto(self, label):
        if self.current_function:
            full_label = f"{self.current_function}${label}"
        else:
            full_label = label
        self.file.write(f"// goto {label}\n")
        self.file.write(f"@{full_label}\n0;JMP\n")

    def write_if(self, label):
        if self.current_function:
            full_label = f"{self.current_function}${label}"
        else:
            full_label = label
        self.file.write(f"// if-goto {label}\n")
        self.file.write("@SP\nM=M-1\nA=M\nD=M\n" + f"@{full_label}\nD;JNE\n")

    def write_function(self, function_name, num_locals):
        self.current_function = function_name
        self.file.write(f"// function {function_name} {num_locals}\n")
        self.file.write(f"({function_name})\n")
        for i in range(int(num_locals)):
            self.file.write("@SP\nA=M\nM=0\n@SP\nM=M+1\n")

    def write_call(self, function_name, num_args):
        return_label = f"RETURN_{self.call_counter}"
        self.call_counter += 1
        self.file.write(f"// call {function_name} {num_args}\n")
        self.file.write(f"@{return_label}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        self.file.write("@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        self.file.write("@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        self.file.write("@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        self.file.write("@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        self.file.write(f"@SP\nD=M\n@{5 + int(num_args)}\nD=D-A\n@ARG\nM=D\n")
        self.file.write("@SP\nD=M\n@LCL\nM=D\n")
        self.file.write(f"@{function_name}\n0;JMP\n")
        self.file.write(f"({return_label})\n")

    def write_return(self):
        self.file.write("// return\n")
        self.file.write("@LCL\nD=M\n@R13\nM=D\n")
        self.file.write("@5\nA=D-A\nD=M\n@R14\nM=D\n")
        self.file.write("@SP\nM=M-1\nA=M\nD=M\n@ARG\nA=M\nM=D\n")
        self.file.write("@ARG\nD=M+1\n@SP\nM=D\n")
        self.file.write("@R13\nM=M-1\nA=M\nD=M\n@THAT\nM=D\n")
        self.file.write("@R13\nM=M-1\nA=M\nD=M\n@THIS\nM=D\n")
        self.file.write("@R13\nM=M-1\nA=M\nD=M\n@ARG\nM=D\n")
        self.file.write("@R13\nM=M-1\nA=M\nD=M\n@LCL\nM=D\n")
        self.file.write("@R14\nA=M\n0;JMP\n")

    def _segment_pointer(self, segment):
        if segment == "local":
            return "@LCL\n"
        elif segment == "argument":
            return "@ARG\n"
        elif segment == "this":
            return "@THIS\n"
        elif segment == "that":
            return "@THAT\n"

    def _write_binary(self, op):
        self.file.write("@SP\nM=M-1\nA=M\nD=M\n@SP\nM=M-1\nA=M\n" + op + "\n@SP\nM=M+1\n")

    def _write_unary(self, op):
        self.file.write("@SP\nM=M-1\nA=M\n" + op + "\n@SP\nM=M+1\n")

    def _write_compare(self, jump):
        label_true = f"TRUE_{self.label_counter}"
        label_end = f"END_{self.label_counter}"
        self.label_counter += 1
        self.file.write("@SP\nM=M-1\nA=M\nD=M\n@SP\nM=M-1\nA=M\nD=M-D\n")
        self.file.write(f"@{label_true}\nD;{jump}\n")
        self.file.write("@SP\nA=M\nM=0\n")
        self.file.write(f"@{label_end}\n0;JMP\n")
        self.file.write(f"({label_true})\n@SP\nA=M\nM=-1\n")
        self.file.write(f"({label_end})\n@SP\nM=M+1\n")

    def close(self):
        self.file.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 vmtranslator.py <input.vm or directory>")
        return

    input_path = sys.argv[1]

    if os.path.isdir(input_path):
        vm_files = glob.glob(os.path.join(input_path, "*.vm"))
        vm_files.sort()
        output_file = os.path.join(input_path, os.path.basename(os.path.normpath(input_path)) + ".asm")
        needs_bootstrap = True
    else:
        vm_files = [input_path]
        output_file = input_path.replace(".vm", ".asm")
        needs_bootstrap = False

    codewriter = CodeWriter(output_file)
    if needs_bootstrap:
        codewriter.write_bootstrap()

    for vm_file in vm_files:
        filename = os.path.basename(vm_file).replace(".vm", "")
        codewriter.set_filename(filename)
        parser = Parser(vm_file)
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
            elif ctype == "C_IF":
                codewriter.write_if(parser.arg1())
            elif ctype == "C_FUNCTION":
                codewriter.write_function(parser.arg1(), parser.arg2())
            elif ctype == "C_CALL":
                codewriter.write_call(parser.arg1(), parser.arg2())
            elif ctype == "C_RETURN":
                codewriter.write_return()
        parser.close()
    codewriter.close()

if __name__ == "__main__":
    main()
