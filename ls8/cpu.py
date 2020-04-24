
# https://github.com/Nov05/Lambda-School-Data-Science/blob/master/daily%20notes/2020-03-23%20CS%20Week%207%20Computer%20Architecture.md
# https://github.com/Nov05/Lambda-Computer-Architecture

"""CPU functionality."""
import sys


LDI = 0b10000010
LD = 0b10000011 # 00000aaa 00000bbb
PRN = 0b01000111
HLT = 0b00000001
PUSH = 0b01000101
POP = 0b01000110
JMP = 0b01010100
CALL = 0b01010000
RET = 0b00010001
ST = 0b10000100
PRA = 0b01001000
IRET = 0b00010011
JEQ = 0b01010101
JNE = 0b01010110
# ALU
ADD = 0b10100000 # 00000aaa 00000bbb
SUB = 0b10100011 # 00000aaa 00000bbb
MUL = 0b10100010 # 00000aaa 00000bbb
MOD = 0b10100100 # 00000aaa 00000bbb
AND = 0b10101000 # 00000aaa 00000bbb
NOT = 0b01101001 # 00000rrr
OR = 0b10101010 # 00000aaa 00000bbb
XOR = 0b10101011 # 00000aaa 00000bbb
SHL = 0b10101100 # 00000aaa 00000bbb
SHR = 0b10101101 # 00000aaa 00000bbb
CMP = 0b10100111 # 00000aaa 00000bbb
INC = 0b01100101 # 00000rrr
DEC = 0b01100110 # 00000rrr


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = False
        self.pc = 0 # Program Counter
        self.fl = 0 # flags: 0b00000LGE
        self.reg = [0] * 8 # registers
        self.ram = [0] * 256 # RAM
        self.IM = 5 # register for Interrupt Mask
        self.IS = 6 # register for Interrupt Status
        self.SP = 7 # register for Stack Pointer
        self.reg[self.SP] = 0xF4 # Stack Pointer initial position

        # brach tables
        self.ops = {
            LDI: self.op_ldi,
            LD: self.op_ld,
            PRN: self.op_prn,
            HLT: self.op_hlt,
            PUSH: self.op_push,
            POP: self.op_pop,
            JMP: self.op_jmp,
            JEQ: self.op_jeq,
            JNE: self.op_jne,
            CALL: self.op_call,
            RET: self.op_ret,
            ST: self.op_st,
            PRA: self.op_pra,
            IRET: self.op_iret,
            ADD: self.op_alu,
            SUB: self.op_alu,
            MUL: self.op_alu,
            MOD: self.op_alu,
            CMP: self.op_alu,
            NOT: self.op_alu_,
            INC: self.op_alu_,
            DEC: self.op_alu_,
        }

    def load(self):
        """Load a program into memory."""
        # For now, we've just hardcoded a program:
        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]
        # address = 0
        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        if len(sys.argv) != 2:
            print('Please specify program file name.')
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                address = 0
                for line in f:
                    instruction = line.split('#')[0].strip()
                    if instruction: 
                        self.ram[address] = int(instruction, 2)
                        address += 1
        except FileNotFoundError:
            print('File is not found.')
            sys.exit(2)


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')
        for i in range(8):
            print(" %02X" % self.reg[i], end='')
        print()


    def ram_read(self, addr):
        return self.ram[addr]
    def ram_write(self, addr, value):
        self.ram[addr] = value


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        # if op == ADD:
        #     self.reg[reg_a] += self.reg[reg_b]
        # elif op == SUB:
        #     self.reg[reg_a] -= self.reg[reg_b]
        # else:
        #     raise Exception("Unsupported ALU operation")
        
        def alu_add(): self.reg[reg_a] += self.reg[reg_b]
        def alu_sub(): self.reg[reg_a] -= self.reg[reg_b]
        def alu_mul(): 
            self.reg[reg_a] *= self.reg[reg_b]
        def alu_cmp(): 
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            else: # equal
                self.fl = 0b00000001
        alus = {
            ADD: alu_add,
            SUB: alu_sub,
            MUL: alu_mul,
            CMP: alu_cmp,
        }
        if op not in alus:
            raise Exception(f'Unsupported ALU operation {bin(op)}')
        alus[op]()

        
    def alu_(self, op, reg_num):
        '''ALU operations'''
        def alu_not(): self.reg[reg_num] = ~self.reg[reg_num]
        def alu_inc(): self.reg[reg_num] += 1
        def alu_dec(): self.reg[reg_num] -= 1
        alus = {
            NOT: alu_not,
            INC: alu_inc,
            DEC: alu_dec,
        }
        if op not in alus:
            raise Exception(f'Unsupported ALU operation {bin(op)}')
        alus[op]()


    def op_ldi(self, op): # e.g. LDI R0, 8
        reg_num = self.ram_read(self.pc+1)
        value = self.ram_read(self.pc+2)
        self.reg[reg_num] = value
        self.pc += 3
    def op_ld(self, op):
        '''Loads registerA with the value at the 
           memory address stored in registerB.'''
        reg_a = self.ram_read(self.pc+1)
        reg_b = self.ram_read(self.pc+2) # RAM address
        self.reg[reg_a] = self.ram_read(self.reg[reg_b])
        self.pc += 3
    def op_prn(self, op): # e.g. PRN R0
        reg_num = self.ram_read(self.pc+1)
        print(self.reg[reg_num])
        self.pc += 2
    def op_hlt(self, op): # Halt the CPU (and exit the emulator).
        self.running = False
        sys.exit()
    def op_alu(self, op):  # e.g. add, sub, div, mul
        reg_a = self.ram_read(self.pc+1)
        reg_b = self.ram_read(self.pc+2)
        self.alu(op, reg_a, reg_b)
        self.pc += 3
    def op_alu_(self, op):
        reg_num = self.ram_read(self.pc+1)
        self.alu_(op, reg_num)
        self.pc += 2
    def op_push(self, op): # Push from register to stack
        self.reg[self.SP] -= 1
        reg_num = self.ram_read(self.pc+1)
        self.ram[self.reg[self.SP]] = self.reg[reg_num]
        self.pc += 2
    def op_pop(self, op): # Pop stack to register
        reg_num = self.ram_read(self.pc+1)
        self.reg[reg_num] = self.ram[self.reg[self.SP]]
        self.reg[self.SP] += 1
        self.pc += 2
    def op_jmp(self, op): # Jump
        reg_num = self.ram_read(self.pc+1)
        self.pc = self.reg[reg_num]
    def op_jeq(self, op):
        '''If Equal flag is set (true), jump to the 
           address stored in the given register.'''
        if (self.fl & 1):
            reg_num = self.ram_read(self.pc+1)
            self.pc = self.reg[reg_num]
        else:
            self.pc += 2
    def op_jne(self, op):
        '''If Equal flag is clear (false, 0), jump to the 
           address stored in the given register.'''
        if not (self.fl & 1):
            reg_num = self.ram_read(self.pc+1)
            self.pc = self.reg[reg_num]
        else:
            self.pc += 2
    def op_call(self, op): # Call
        '''Calls a subroutine (function) at the 
           address stored in the register.'''
        self.reg[self.SP] -= 1
        self.ram[self.reg[self.SP]] = self.pc + 2 # Push return address to stack
        reg_num = self.ram_read(self.pc+1)
        self.pc = self.reg[reg_num] # Jump to subroutine address
    def op_ret(self, op): # Return
        self.pc = self.ram[self.reg[self.SP]] # Pop return address and jump there
        self.reg[self.SP] += 1
    def op_st(self, op): # store value to RAM
        reg_a = self.ram_read(self.pc+1)  # RAM address
        reg_b = self.ram_read(self.pc+2)  # value
        self.ram[self.reg[reg_a]] = self.reg[reg_b]
        self.pc += 2
    def op_pra(self, op): # pseudo-instruction
        '''Print to the console the ASCII character 
           corresponding to the value in the register.'''
        reg_num = self.ram_read(self.pc+1)
        print(chr(self.reg[reg_num]))
        self.pc += 2
    def op_iret(self, op):
        '''Return from an interrupt handler.
           The following steps are executed:
            1. Registers R6-R0 are popped off the stack in that order.
            2. The FL register is popped off the stack.
            3. The return address is popped off the stack and stored in PC.
            4. Interrupts are re-enabled.'''
        for i in range(6):



    def run(self):
        """Run the CPU."""
        self.running = True
        # self.trace()

        while self.running:
            op = self.ram_read(self.pc)
            if op not in self.ops:
                raise Exception(f'Unsupported operation {bin(op)}')
            self.ops[op](op) 
            # self.trace()       