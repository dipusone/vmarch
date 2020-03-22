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
    'ax': 1,
    'ip': 1
}

dbg_conf = {
    'to_end': False,
    'always_print_data': False,
    'always_print_regs': False,
    'clear_screen': False,
    'breakpoints': [],
    'sep': '=' * 30,
    'sleep': 0,
    'state': []
}


def catch_everyting(func):
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("Error: ", str(e))
    return wrap


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
        print("{:<3}: 0x{:x}".format(reg, regs[reg]))
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


@catch_everyting
def exec_commands(op):
    def text_to_int(value):
        if value.startswith('0x'):
            int_val = int(value, 16)
        else:
            int_val = int(value)
        return int_val

    global dbg_conf
    global text
    global data
    global regs

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
    if op.startswith('d'):
        to_disas = dbg_conf['state']
        if ' ' in op:
            disass_ip = text_to_int(op.split()[1])
            to_disas = text[(disass_ip - 1) * 3:disass_ip * 3]
        disas(*to_disas)
    if op == 'q':
        sys.exit(0)
    if op.startswith('b '):
        b_ip = text_to_int(op.split()[1])
        if b_ip not in dbg_conf['breakpoints']:
            dbg_conf['breakpoints'].append(b_ip)
    if op == 'ib':
        print("Breakpoints:")
        for i, breakpoint in enumerate(dbg_conf['breakpoints']):
            print("{:<2}: {:d}".format(i, breakpoint))
    if op.startswith('db '):
        bp_idx = text_to_int(op.split()[1])
        if bp_idx < len(dbg_conf['breakpoints']):
            del dbg_conf['breakpoints'][bp_idx]
    if op == 'c':
        dbg_conf['to_end'] = True
        return True
    if op.startswith('s '):
        t, src, val = op.split(' ')[1:]
        if t == 'r' and src in regs:
            regs[src] = ext_to_int(val)
        if t == 'd':
            addr = ext_to_int(src)
            if addr < len(data):
                data[addr] = ext_to_int(val)
    if op.startswith('w '):
        dbg_conf['sleep'] = float(op.split()[1])
    if op == '' or op == 'n':
        dbg_conf['to_end'] = False
        return True
    return False


def exec_bin(text):
    global dbg_conf
    global regs
    while True:
        curr_ip = regs['ip']
        opcode, offset, value = text[(curr_ip - 1) * 3:curr_ip * 3]
        dbg_conf['state'] = [opcode, offset, value]
        r = exec_opcode(opcode, offset, value)
        if dbg_conf['clear_screen']:
            print('\033c', end='')
        if dbg_conf['always_print_regs']:
            print_regs()
        if dbg_conf['always_print_data']:
            print_data()
        disas(opcode, offset, value)

        while not dbg_conf['to_end'] or curr_ip in dbg_conf['breakpoints']:
            op = input('> ').strip()
            if exec_commands(op):
                break
        if r:
            return
        regs['ip'] += 1
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
