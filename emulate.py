#!/usr/bin/env python3
import sys
import time

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
    'ax': 1
}


def print_stack():
    global stack
    for i in range(17):
        print("0x{:<3x}: ".format(i), end='')
        for j in range(0xf):
            print("{:<3x}".format(stack[0xf * i + j]), end=' ')
        print(" | ", end='')
        for j in range(0xf):
            try:
                print(chr(stack[0xf * i + j]), end=' ')
            except:
                print(repr(stack[0xf * i + j]), end=' ')
        print()


def exec_bin(text):
    to_end = False
    always_print_stack = False
    sleep = 0
    while True:
        opcode, offset, value = text[:3]
        text = text[3:]
        disas(opcode, offset, value)
        r = exec_opcode(opcode, offset, value)
        if always_print_stack:
            print_stack()
        while not to_end:
            op = input('> ').strip()
            if op == 'p':
                print_stack()
            if op == 'pp':
                always_print_stack = not always_print_stack
            if op == 'r':
                print("{:x}".format(regs['ax']))
            if op == 'd':
                disas(opcode, offset, value)
            if op == 'q':
                sys.exit(0)
            if op == 'e':
                to_end = True
            if op.startswith('s '):
                sleep = float(op.split()[1])
            if op == '' or op == 'c':
                break
        if r:
            return
        time.sleep(sleep)


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
        regs['ax'] = stack[offset]

    # stack[offset] = stack[offset] ^ ac
    if optext == 'xor':
        stack[offset] = stack[offset] ^ regs['ax']
    return False


if __name__ == '__main__':
    with open(sys.argv[1], 'rb') as f:
        data = f.read()
    stack = bytearray(data[0x0:0xff])
    text = bytearray(data[0xff:])
    exec_bin(text)
    print('=' * 30)
    print_stack()
    print()
    for i in range(25):
        print(chr(stack[i]), end='')
    print()
