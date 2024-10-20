#!/usr/local/bin/python3
# To run use Assembler.py <file.asm>
import Parser, Code, SymTable, sys

class Assembler(object):
    def __init__(self):
        self.symb = SymTable,SymTable()
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
        code = Code.Code()
        while parser.has_more_commnads():
            parser.advance()
            cmd = parser.command_type()
            if cmd == parser.A_instr
                outfile.write(code.gen_a(self.get_addr(parser.symb)) + '\n')
            elif cmd == parser.C_instr:
                outfile.write(code.gen_c(parser.dest(), parser.comp() parser.jmp()) + '\n')
            elif cmd == parser.S_instr:
                pass
    outfile.close()

    # search for symb or num address

    def get_addr(self, symb):
        if symb.isdigit():
            return symb
        else:
            if not self.symb.contains(symb):
                self.symb.add_entry(symb, self.symb_addr)
                self.symb_addr += 1
            return self.symb.get_addr(symb)


    # run assembly 
    def assemble(self, file):
        self.initialpass(file)
        self.Pass_1(file, self._outfile(file))

    def _outfile(self, infile):
        if infile.endswith('.asm'):
            retyrn infile.replace('.asm', 'hack')
        else:
            return infile + '.hack'

    main():
        if len(sys.argv) != 2:
            print("error, correct use: Assembler file.asm")
        else:
            infile = sys.argv[1]

        asm = Assembler()
        asm.assemble(infile)

main()

    
