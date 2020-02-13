#!/usr/bin/env python3
import sys
from collections import defaultdict


stack = []
text = []

opcodes = defaultdict(
    lambda: 'ret', {
        1: 'store',
        2: 'load',
        3: 'xor'
    }
)

regs = {
    'ac': 1
}


def print_stack():
    global stack
    for i in range(17):
        for j in range(0xf):
            print(stack[0xf * i + j], end=' ')
        print()


def exec_bin(text):
    to_end = False
    while True:
        opcode, offset, value = text[:3]
        text = text[3:]
        disas(opcode, offset, value)
        r = exec_opcode(opcode, offset, value)
        while not to_end:
            op = input('> ').strip()
            if op == 'p':
                print_stack()
            if op == 'r':
                print("{:x}".format(regs['ac']))
            if op == 'd':
                disas(opcode, offset, value)
            if op == 'q':
                sys.exit(0)
            if op == 'e':
                to_end = True
            if op == '' or op == 'c':
                break
        if r:
            return


def disas(opcode, offset, value):
    optext = opcodes[opcode]
    if optext == 'ret':
        print('ret')

    if optext == 'store':
        print(f"store stack[{offset}], {value}")

    if optext == 'load':
        print(f"load ac, stack[{offset}]")

    if optext == 'xor':
        print(f"stack[{offset}] = stack[{offset}] ^ ac")


def exec_opcode(opcode, offset, value):
    global stack
    global regs
    optext = opcodes[opcode]
    if optext == 'ret':
        return True

    #
    if optext == 'store':
        stack[offset] = value

    # ac = stack[offset]
    if optext == 'load':
        regs['ac'] = stack[offset]

    # stack[offset] = stack[offset] ^ ac
    if optext == 'xor':
        stack[offset] = stack[offset] ^ regs['ac']
    return False


if __name__ == '__main__':
    with open(sys.argv[1], 'rb') as f:
        data = f.read()
    stack = bytearray(data[0x0:0xff])
    text = bytearray(data[0xff:])
    exec_bin(text)
    print_stack()
    for i in range(25):
        print(chr(stack[i]), end='')
    print()
