from binaryninja import (Architecture, InstructionInfo, InstructionTextToken,
                         InstructionTextTokenType, BranchType, RegisterInfo,
                         BinaryView, SegmentFlag, SectionSemantics)

from collections import defaultdict
import struct

opcodes = defaultdict(
    lambda: 'ret', {
        1: 'store',
        2: 'load',
        3: 'xor'
    }
)


class VMMalwaretech(Architecture):
    name = "VMMalwaretech"

    # 1 byte address size
    address_size = 1

    default_int_size = 1
    # the machine always consumes 3 bytes
    max_instr_length = 3

    # Stack pointer
    stack_pointer = 'sp'

    regs = {
        'sp': RegisterInfo('sp', 1),
        'ax': RegisterInfo('ax', 1)
    }

    # Helper method
    def parse_instruction(self, data, addr):
        # fuuuuuu, might be time to start using python3
        opcode, offset, value = struct.unpack("BBB", data[:3])

        return opcode, offset, value, 3

    def get_instruction_info(self, data, addr):
        opcode, offset, value, length = self.parse_instruction(data, addr)

        optext = opcodes[opcode]
        info = InstructionInfo()
        info.length = length
        if optext == 'ret':
            info.add_branch(BranchType.FunctionReturn)

        return info

    def get_instruction_text(self, data, addr):
        opcode, offset, value, length = self.parse_instruction(data, addr)
        tokens = []
        optext = opcodes[opcode]
        tokens.append(
            InstructionTextToken(
                InstructionTextTokenType.InstructionToken,
                "{:<8}".format(optext),
                value=opcode
            )
        )

        tokens.append(
            InstructionTextToken(
                InstructionTextTokenType.OperandSeparatorToken,
                ' '
            )
        )

        if optext == 'store':
            tokens.append(
                InstructionTextToken(
                    InstructionTextTokenType.PossibleAddressToken,
                    '{}'.format(offset),
                    value=offset,
                    size=1
                )
            )
            tokens.append(
                InstructionTextToken(
                    InstructionTextTokenType.OperandSeparatorToken,
                    ', '
                )
            )
            tokens.append(
                InstructionTextToken(
                    InstructionTextTokenType.IntegerToken,
                    '{}'.format(value),
                    value=value,
                    size=1
                )
            )
        if optext == 'load':
            tokens.append(
                InstructionTextToken(
                    InstructionTextTokenType.RegisterToken,
                    'ax'
                )
            )
            tokens.append(
                InstructionTextToken(
                    InstructionTextTokenType.OperandSeparatorToken,
                    ', '
                )
            )
            tokens.append(
                InstructionTextToken(
                    InstructionTextTokenType.PossibleAddressToken,
                    '{}'.format(offset),
                    value=offset,
                    size=1
                )
            )
        if optext == 'xor':
            tokens.append(
                InstructionTextToken(
                    InstructionTextTokenType.PossibleAddressToken,
                    '{}'.format(offset),
                    value=offset,
                    size=1
                )
            )
            tokens.append(
                InstructionTextToken(
                    InstructionTextTokenType.OperandSeparatorToken,
                    ', '
                )
            )
            tokens.append(
                InstructionTextToken(
                    InstructionTextTokenType.RegisterToken,
                    'ax'
                )
            )
        return tokens, length

    def get_instruction_low_level_il(self, data, addr, il):
        opcode, offset, value, length = self.parse_instruction(data, addr)
        optext = opcodes[opcode]

        if optext == 'ret':
            il.append(il.no_ret())

        # stack[offset] = value
        if optext == 'store':
            il.append(
                il.store(
                    1,
                    il.const_pointer(1, offset),
                    il.const(1, value)
                )
            )
        # ax = stack[offset]
        if optext == 'load':
            il.append(
                il.set_reg(
                    1, 'ax',
                    il.load(1, il.const_pointer(1, offset))
                )
            )

        # stack[offset] = stack[offset] ^ ax
        if optext == 'xor':
            il.append(
                il.store(
                    1,
                    il.const_pointer(1, offset),
                    il.xor_expr(
                        1,
                        il.load(1, il.const_pointer(1, offset)),
                        il.reg(1, 'ax')
                    )
                )
            )

        return length


VMMalwaretech.register()


class VMMalwaretechView(BinaryView):
    name = 'VMMalwaretech'
    long_name = 'VMMalwaretech simple view'

    def __init__(self, data):
        BinaryView.__init__(self, parent_view=data, file_metadata=data.file)
        self.platform = Architecture['VMMalwaretech'].standalone_platform
        self.add_auto_segment(0x0, 0xff,
                              0x0, 0xff,
                              SegmentFlag.SegmentWritable | SegmentFlag.SegmentReadable)
        self.add_auto_segment(0xff, 0xff,
                              0xff, 0xff,
                              SegmentFlag.SegmentReadable | SegmentFlag.SegmentExecutable)
        self.add_auto_section('data',
                              0x0, 0xff,
                              SectionSemantics.ReadWriteDataSectionSemantics)
        self.add_auto_section('text',
                              0xff, 0xff,
                              SectionSemantics.ReadOnlyCodeSectionSemantics)

        self.add_entry_point(0xff)

    @classmethod
    def is_valid_for_data(self, data):
        return True


VMMalwaretechView.register()
