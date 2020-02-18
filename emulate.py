#!/usr/bin/env python3
import sys
import time

from collections import defaultdict


data = []
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

dbg_conf = {
    'to_end': False,
    'always_print_data': False,
    'always_print_regs': False,
    'clear_screen': False,
    'sep': '=' * 30,
    'sleep': 0,
    'state': []
}


def print_data():
    global data, dbg_conf
    for i in range(17):
        print("0x{:<3x}: ".format(i), end='')
        for j in range(0xf):
            print("{:<3x}".format(data[0xf * i + j]), end=' ')
        print(" | ", end='')
        for j in range(0xf):
            try:
                print(chr(data[0xf * i + j]), end=' ')
            except:
                print(repr(data[0xf * i + j]), end=' ')
        print()
    print(dbg_conf['sep'])


def print_regs():
    global regs, dbg_conf
    for reg in sorted(regs.keys()):
        print("{:<3}: {:x}".format(reg, regs[reg]))
    print(dbg_conf['sep'])


def disas(opcode, offset, value):
    optext = opcodes[opcode]
    if optext == 'ret':
        print('ret')

    if optext == 'store':
        print(f"store data[{offset}], {value}")

    if optext == 'load':
        print(f"load ac, data[{offset}]")

    if optext == 'xor':
        print(f"data[{offset}] = data[{offset}] ^ ac")


def exec_commands(op):
    global dbg_conf
    opcode, offset, value = dbg_conf['state']
    if op == 'p':
        print_data()
    if op == 'pp':
        dbg_conf['always_print_data'] = not dbg_conf['always_print_data']
    if op == 'r':
        print_regs()
    if op == 'rr':
        dbg_conf['always_print_regs'] = not dbg_conf['always_print_regs']
    if op == 'cc':
        dbg_conf['clear_screen'] = not dbg_conf['clear_screen']
    if op == 'd':
        disas(opcode, offset, value)
    if op == 'q':
        sys.exit(0)
    if op == 'c':
        dbg_conf['to_end'] = True
        return True
    if op.startswith('s '):
        dbg_conf['sleep'] = float(op.split()[1])
    if op == '' or op == 'n':
        return True
    return False


def exec_bin(text):
    global dbg_conf
    while True:
        opcode, offset, value = text[:3]
        dbg_conf['state'] = [opcode, offset, value]
        text = text[3:]
        r = exec_opcode(opcode, offset, value)
        if dbg_conf['clear_screen']:
            print('\033c', end='')
        if dbg_conf['always_print_regs']:
            print_regs()
        if dbg_conf['always_print_data']:
            print_data()
        disas(opcode, offset, value)

        while not dbg_conf['to_end']:
            op = input('> ').strip()
            if exec_commands(op):
                break
        if r:
            return
        time.sleep(dbg_conf['sleep'])


def exec_opcode(opcode, offset, value):
    global data
    global regs
    optext = opcodes[opcode]
    if optext == 'ret':
        return True

    #
    if optext == 'store':
        data[offset] = value

    # ac = data[offset]
    if optext == 'load':
        regs['ax'] = data[offset]

    # data[offset] = data[offset] ^ ac
    if optext == 'xor':
        data[offset] = data[offset] ^ regs['ax']
    return False


if __name__ == '__main__':
    with open(sys.argv[1], 'rb') as f:
        dump = f.read()
    data = bytearray(dump[0x0:0xff])
    text = bytearray(dump[0xff:])
    exec_bin(text)
    print('\nFLAG: ', end='')
    for i in range(25):
        print(chr(data[i]), end='')
    print()
