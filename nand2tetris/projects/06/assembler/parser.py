#!/usr/local/bin/python3
import Lex

class Parser(object):
    A_instr = 0
    C_instr = 1
    S_instr = 2

    def __init__(self, file):
        self.lex = Lex.Lex(file)
        self.__init_cmd_info()

    def __init_cmd_info(self):
        self._cmd_type = -1
        self._symbol = ''
        self._dest = ''
        self._comp = ''
        self._jmp = ''

    def __str__(self):
        pass

    def has_more_commands(self):
        return self.lex.has_more_commands()
# fetch netch command line by line

    def advance(self):
        self.__init_cmd_info()
        self.lex.next_command()
        tok, val = self.lex.cur_token
        
        if tok == Lex.OP and val == '@':
            self._a_instr()
        
        elif tok == Lex.OP and val == '(':
            self._s_instr()
        else:
            self._c_instr(tok, val)

# extracted parts
    def command_type(self):
        return self._cmd_type
    def symbol(self):
        return self._symbol
    def dest(self):
        return self._dest
    def comp(self):
        return self._comp
    def jmp(self):
        return self._jmp
    # symb/num
    def _a_command(self):
        self._cmd_type = Parser.A_instr
        tok_type, self._symbol = self.lex.next_token()
        # symb 
    def _s_instr(self):
        self._cmd_type = Parser.S_instr
        tok_type, self._symbol = self.lex.next_token()

    def _c_instr(self, tok1, val1):
        self._cmd_type = Parser.C_instr 
        comp_tok, comp_val = self._get_dest(tok1, val1)
        self._get_comp(comp_tok, comp_val)
        self._get_jump()

    # dest part, return first tokem from comp

    def _get_dest(self, tok1, val1):
         tok2, val2 = self.lex.peek_token()
         if tok2 == Lex.OP and val2 == '=':
            self.lex.next_token()
            self._dest = val1
            comp_tok, comp_val = self.lex.next_token()
         else:
            comp_tok, comp_val = tok1, val1
            return (comp_tok, comp_val)
    
    # Get the 'comp' part - must be present.
    def _get_comp(self, tok, val):
        if tok == Lex.OP and (val == '-' or val == '!'):
            tok2, val2 = self.lex.next_token()
            self._comp = val+val2
        elif tok == Lex.NUM or tok == Lex.ID:
            self._comp = val
            tok2, val2 = self.lex.peek_token()
            if tok2 == Lex.OP and val2 != ';':
                self.lex.next_token()
                tok3, val3 = self.lex.next_token()
                self._comp += val2+val3
        
    # Get the 'jump' part if any
    def _get_jump(self):
        tok, val = self.lex.next_token()
        if tok == Lex.OP and val == ';':
            jump_tok, jump_val = self.lex.next_token()
            self._jmp = jump_val

