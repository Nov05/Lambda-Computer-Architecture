
# https://github.com/Nov05/Lambda-School-Data-Science/blob/master/daily%20notes/2020-03-23%20CS%20Week%207%20Computer%20Architecture.md
# https://github.com/Nov05/Lambda-Computer-Architecture

"""CPU functionality."""
import sys


LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
PUSH = 0b01000101
POP = 0b01000110
JMP = 0b01010100
CALL = 0b01010000
RET = 0b00010001
# ALU
ADD = 0b10100000
SUB = 0b10100011
MUL = 0b10100010


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = False
        self.pc = 0 # Program Counter
        self.fl = 0 # flags: 0b00000LGE
        self.reg = [0] * 8 # registers
        self.ram = [0] * 256 # RAM
        self.SP = 7 # register number that stores Stack Pointer value
        self.reg[self.SP] = 0xF4 # Stack Pointer initial position

        # brach tables
        self.ops = {
            LDI: self.op_ldi,
            PRN: self.op_prn,
            HLT: self.op_hlt,
            PUSH: self.op_push,
            POP: self.op_pop,
            JMP: self.op_jmp,
            CALL: self.op_call,
            RET: self.op_ret,
            ADD: self.op_alu,
            SUB: self.op_alu,
            MUL: self.op_alu,
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


    def ram_read(self, pc):
        return self.ram[pc]
    def ram_write(self, pc, value):
        self.ram[pc] = value


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == SUB:
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

        
    def op_ldi(self, op): # e.g. LDI R0, 8
        reg_num = self.ram_read(self.pc+1)
        value = self.ram_read(self.pc+2)
        self.reg[reg_num] = value
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
    def op_call(self, op): # Call
        '''Calls a subroutine (function) at the address stored in the register.'''
        self.reg[self.SP] -= 1
        self.ram[self.reg[self.SP]] = self.pc + 2 # Push return address to stack
        reg_num = self.ram_read(self.pc+1)
        self.pc = self.reg[reg_num] # Jump to subroutine address
    def op_ret(self, op): # Return
        self.pc = self.ram[self.reg[self.SP]] # Pop return address and jump there
        self.reg[self.SP] += 1


    def run(self):
        """Run the CPU."""
        self.running = True
        self.trace()

        while self.running:
            op = self.ram_read(self.pc)
            self.ops[op](op) 
            self.trace()       