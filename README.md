# VMArch
This is what I ended up writing to solve the VM Challenge from MarwareTech [here](https://www.malwaretech.com/vm1).

I got a little carried away and ended up writing a BinaryNinja custom architecture and an emulator with a debugger.

## Files
* `vmarch.py` is the BinaryNinja architecture for the ram dump
* `emulate.py` is the emulator and simple debugger for the code

## Binja architecture

The BinaryNinja architecture is quite simple and is comprised of the architecture itself and the binary view.

The view will check the bytes from offset 0x20 on to verify if the file is the dump, in order not to trigger on other files. Nevertheless is this possible that the view will trigger on unexpected files.

## Emulator commands
The set of emulator commands is quite limited but enough to have fun.

### Settings
* `rr` : print registers at each step
* `pp` : print data at each step
* `cc` : clear screen at each step

### Breakpoints
* `b <ip>` : set a breakpoint ad a given ip value
* `db <bp_number>` : delete a given breakpoint
* `ib` : print the list of breakpoints

### Inspections
* `p` : print data
* `r` : print registers
* `d <ip>` : disassemble the instruction ad address

### Stepping
* `<return>|n`: step an instruction
* `c`: continue to end

### Modifying values
* `s r <reg> <val>`: set the register <reg> to <val>. It is equivalent to `reg=val`
* `s d <addr> <val>`: set the data at <addr> to <val>. It is equivalent to `*addr = val`

### Misc
* `w <wait_time>` : when in `run to end` mode, wait `<waith_time>` seconds before, stepping. Just because :)
* `q` : exit from the emulator




