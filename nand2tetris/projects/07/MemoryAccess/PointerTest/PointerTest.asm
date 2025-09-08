// c_push constant 3030
@3030
D=A
@SP
A=M
M=D
@SP
M=M+1
// c_pop pointer 0
@SP
M=M-1
A=M
D=M
@THIS
M=D
// c_push constant 3040
@3040
D=A
@SP
A=M
M=D
@SP
M=M+1
// c_pop pointer 1
@SP
M=M-1
A=M
D=M
@THAT
M=D
// c_push constant 32
@32
D=A
@SP
A=M
M=D
@SP
M=M+1
// c_pop this 2
@2
D=A
@THIS
D=M+D
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
// c_push constant 46
@46
D=A
@SP
A=M
M=D
@SP
M=M+1
// c_pop that 6
@6
D=A
@THAT
D=M+D
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
// c_push pointer 0
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
// c_push pointer 1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M+D
@SP
M=M+1
// c_push this 2
@2
D=A
@THIS
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M-D
@SP
M=M+1
// c_push that 6
@6
D=A
@THAT
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M+D
@SP
M=M+1
