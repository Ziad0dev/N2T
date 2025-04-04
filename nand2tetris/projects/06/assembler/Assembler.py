#!/usr/local/bin/python3
# To run use Assembler.py <file.asm>
from Parser import Parser
from Code import BCode
from SymTable import SymTable
import sys
#import pdb; pdb.set_trace()
class Assembler(object):
    def __init__(self):
        self.symb = SymTable.SymTable()
        self.symb.addr = 16
    def initialpass(self, file):
        parser = Parser.Parser(file)
        cur_address = 0
        while parser.has_more_commnads():
            Parser.advance()
            cmd = parser.command_type()
            if cmd == parser.A_instr or cmd == parser.C_instr:
                cur_address += 1
            elif cmd == parser.S_instr:
                self.symb.add_entry(parser.symb(), cur_address)

    def Pass_1(self, infile, outfile):
        parser = Parser.Parser(infile)
        outfile = open(outfile, 'w')
        code = BCode.BitCode()
        while parser.has_more_commnads():
            parser.advance()
            cmd = parser.command_type()
            if cmd == parser.A_instr:
                outfile.write(code.gen_a(self._get_adress(parser.symb)) + '\n')
            elif cmd == parser.C_instr:
                outfile.write(code.gen_c(parser.dest(), parser.comp(), parser.jmp()) + '\n')
            elif cmd == parser.S_instr:
                    pass
        outfile.close()

        # search for symb or num address

        def _get_adress(self, symb):
            if symb.isdigit():
                return symb
            else:
                if not self.symb.contains(symb):
                    self.symb.add_entry(symb, self.symb_addr)
                    self.symb_addr += 1
                return self.symb._get_adress(symb)


        # run assembly 
    def assemble(self, file):
        self.initialpass(file)
        self.Pass_1(file, self._outfile(file))

    def _outfile(self, infile):
        if infile.endswith('.asm'):
            return infile.replace('.asm', '.hack')
        else:
            return infile + '.hack'
def main():
    if len(sys.argv) != 2:
        print("Use: Assembler.py file.asm")
    else:
        infile = sys.argv[1]
        asm = Assembler()
        asm.assemble(infile)

if __name__ == "__main__":
    main()
