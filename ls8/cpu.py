"""CPU functionality."""
# An 8 bit CPU is one that only has 8 wires available for addresses (specifying where something is in memory), computations, and instructions. With 8 bits, our CPU has a total of 256 bytes of memory and can only compute values up to 255
# execute code that stores the value 8 in a register, then prints it out

import sys
filename = sys.argv
print(filename)
# LDI Set the value of a register to an integer
# PRN Set the value of a register to an integer
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # hold 256 bytes of memory and 8 general-purpose registers
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0 # internal register
        # Set up the branch table
        self.branchtable = {}
        self.branchtable[LDI] = self.handleLDI
        self.branchtable[PRN] = self.handlePRN
        self.branchtable[HLT] = self.handleHLT
        self.branchtable[MUL] = self.handleMUL
        self.branchtable[PUSH] = self.handlePUSH
        self.branchtable[POP] = self.handlePOP

        #All CPUs manage a stack that can be used to store information temporarily. This stack resides in main memory and typically starts at the top of memory (at a high address) and grows downward as things are pushed on

        self.stack_pointer = 0xf4
        # When booted, * `R7` is set to `0xF4`.
        # R7 is reserved as the stack pointer (SP)

        #The stack pointer points at the value at the top of the stack (most recently pushed), or at address `F4` if the stack is empty.

        self.reg[7] = self.stack_pointer

    def load(self):
        """Load a program into memory."""

        # address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    # accept the address to read and return the value stored there
    # Memory Address Register, holds the memory address we're reading or writing

        
        # sys.argv[0] is the name of the running program itself
        # sys.argv[1] the name of the file to load
        address = 0
        filename = sys.argv[1]

        if filename:
            with open(filename) as f:
                for entry in f:
                    entry = entry.split('#')
                    # ignore blank lines, and everything after a #, since that’s a comment
                    if entry[0] == '' or entry[0] == '\n':
                        continue

                    # convert the binary strings to integer values to store in RAM
                    self.ram[address] = int(entry[0], 2)
                    address += 1

        else:
            print('missing command line argument')
            sys.exit(0)

    def ram_read(self, MAR):
        return self.ram[MAR]

    # accept a value to write, and the address to write it to
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    # handle calls into the branch table
    def handleHLT(self, a=None, b=None):
        exit()

    def handleLDI(self, a, b):
        self.reg[a] = b
        self.pc += 3

    def handlePRN(self, a, b=None):
        print(self.reg[a])
        self.pc += 2

    def handleMUL(self, a, b):
        #Multiply the values in two registers together and store the result in register
        self.reg[a] = self.reg[a] * self.reg[b]
        self.pc += 3

    def handlePUSH(self, a, b=None):
        # Push the value in the given register on the stack. Store the value in the register into RAM at the address stored in SP.
        # Decrement stack pointer
        self.stack_pointer -= 1
        self.stack_pointer = self.stack_pointer + 0xff  # keep in range of 00-FF
        # These registers only hold values between 0-255. After performing math on registers in the emulator, bitwise-AND the result with 0xFF (255) to keep the register values in that range.

        # Retreive register index and value stored
        reg_num = self.ram[self.pc + 1]
        val = self.reg[reg_num]

        # Store value of register in RAM
        self.ram[self.stack_pointer] = val
        self.pc += 2

    def handlePOP(self, a, b=None):
        # Get value from RAM
        # Pop the value at the top of the stack into the given register. Retrieve the value from RAM at the address stored in SP, and store that value in the register.
        address = self.stack_pointer
        val = self.ram[address]

        # Store at register index
        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = val

        # Increase the stack pointer and program counter
        self.stack_pointer += 1
        self.stack_pointer &= 0xff  # Maintian range of 00-FF bits

        self.pc += 2

    def run(self):
        """Run the CPU."""
        # Read the memory address that's stored in register PC, and store that result in IR, the Instruction Register
        running = True
        while running:
            # instruction register, read memory address stored in register
            IR = self.ram_read(self.pc)
            # # bytes at PC+1 and PC+2 from RAM into variables operand_a and operand_b
            # operand_a = self.ram_read(self.pc + 1)
            # operand_b = self.ram_read(self.pc + 2)
            # # instructions require up to the next two bytes of data after the PC in memory to perform operations on
            # # read the bytes at PC+1 and PC+2 from RAM into variables operand_a and operand_b in case the instruction require them

            #if IR == HLT:
                # exit the loop if a HLT instruction is encountered
            #    running = False
            # elif IR == LDI:
            #     # set register to value
            #     self.reg[operand_a] = [operand_b]
            #     self.pc += 3
            # elif IR == PRN:
            #     # print value from register
            #     print(self.reg[operand_a])
            #     self.pc += 2
            # else:
            #     print(f'unknown instruction {IR} at address {self.pc}')
            #     self.running = False
            # IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            if IR not in self.branchtable:
                print(f'unknown instruction {IR} at address {self.pc}')
            else:
                f = self.branchtable[IR]
                f(operand_a, operand_b)