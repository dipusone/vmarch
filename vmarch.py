from binaryninja import (Architecture, InstructionInfo, InstructionTextToken,
                         InstructionTextTokenType)

from collections import defaultdict
import struct

opcodes = defaultdict(
    lambda: 'ret', {
        1: 'store',
        2: 'load',
        3: 'xor'
    }
)


class VMTest(Architecture):
    name = "VMTest"

    # 1 byte address size
    address_size = 1

    default_int_size = 1
    # the machine always consumes 3 bytes
    max_instr_length = 3

    # Helper method
    def parse_instruction(self, data, addr):
        # fuuuuuu, might be the case to start using python3
        opcode, offset, value = struct.unpack("BBB", data[:3])

        return opcode, offset, value, 3

    def get_instruction_info(self, data, addr):
        opcode, offset, value, length = self.parse_instruction(data, addr)

        info = InstructionInfo()
        info.length = length

        return info

    def get_instruction_text(self, data, addr):
        opcode, offset, value, length = self.parse_instruction(data, addr)
        tokens = []
        optext = opcodes[opcode]
        tokens.append(
            InstructionTextToken(
                InstructionTextTokenType.InstructionToken,
                "{:<8}".format(optext), value=opcode
            )
        )

        tokens.append(
            InstructionTextToken(
                InstructionTextTokenType.OperandSeparatorToken,
                ' '
            )
        )
        if optext != 'ret':
            tokens.append(
                InstructionTextToken(
                    InstructionTextTokenType.PossibleAddressToken,
                    '{}'.format(offset), value=offset, size=1
                )
            )

        if optext == 'store':
            tokens.append(
                InstructionTextToken(
                    InstructionTextTokenType.OperandSeparatorToken,
                    ', '
                )
            )
            tokens.append(
                InstructionTextToken(
                    InstructionTextTokenType.IntegerToken,
                    '{}'.format(value), value=value, size=1
                )
            )

        # if optext == 'store'
        # elif optext == 'load':
        # elif optext == 'xor':
        # elif optext == 'ret':
        # else:

        return tokens, length

    def get_instruction_low_level_il(self, data, addr, il):
        pass


VMTest.register()
