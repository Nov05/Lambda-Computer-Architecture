"""CPU functionality."""

import sys


LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = False
        self.pc = 0 # Program Counter
        self.fl = 0 # flags: 00000LGE
        self.reg = [0] * 8 # registers
        self.ram = [0] * 256 # RAM

        self.reg[7] = 0xF4

    def load(self, mode='test'):
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


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == 'SUB':
            self.reg[reg_a] -= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")


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


    def run(self):
        """Run the CPU."""
        self.running = True
        self.trace()

        while self.running:
            op = self.ram_read(self.pc)
            if op == LDI: # e.g. LDI R0, 8
                reg_num = self.ram_read(self.pc+1)
                value = self.ram_read(self.pc+2)
                self.reg[reg_num] = value
                self.pc += 3
            elif op == PRN: # e.g. PRN R0
                reg_num = self.ram_read(self.pc+1)
                print(self.reg[reg_num])
                self.pc += 2
            # Halt the CPU (and exit the emulator).
            elif op == HLT:
                self.running = False
                sys.exit()


    def ram_read(self, pc):
        return self.ram[pc]


    def ram_write(self, pc, value):
        self.ram[pc] = value