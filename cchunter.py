# (M4UD's CoveCave Hunter)

import pykd
import sys
import re

print("\r\nM4UD's CodeCave hunter!\r\n")
module_name = ""
if len(sys.argv) > 1:
    module_name = sys.argv[1]

# step 2: run dd (module name) + 3C L1
output = pykd.dbgCommand(f"dd {module_name} + 3C L1")
parts = output.split()
var = hex(int(parts[1], 16))

# step 4: run dd (module name) + var  + 2c L1
output = pykd.dbgCommand(f"dd {module_name} + {var} + 2c L1")
parts = output.split()
var2 = hex(int(parts[1], 16))

# step 6: run ? (module name) + 1000
output = pykd.dbgCommand(f"? {module_name} + 1000")
parts = output.split()
var3 = parts[4]

# step 8: run !address var3
output = pykd.dbgCommand(f"!address {var3}")

# step 9: parse the output of !address command
for line in output.split("\n"):
    if "End Address:" in line:
        var4 = int(line.split()[-1], 16)
    if "Protect:" in line:
        var5 = line.split()[-1]

# step 10: print var4 and var5
print(f"End Address: 0x{var4:x}")
print(f"Protect: {var5}")

# step 11: run dd var4 - x
start_address = None
end_address = None
for i in range(0, var4, 4):
    address = hex(var4-i)
    output = pykd.dbgCommand(f"dd {address} L1")
    parts = output.split()
    if parts[1] == "00000000":
        if start_address is None:
            start_address = var4-i
        end_address = var4-i
    else:
        if start_address is not None:
            break

# step 12: print the last dword address filled with 0 and the first dword address filled with 0
print(f"Code Cave start at: 0x{end_address:x}")
print(f"Code Cave finishes at: 0x{start_address:x}")
size = pykd.dbgCommand(f"? 0x{end_address:x} - 0x{start_address:x}")
match = re.search(r': (.*) =', size)
value = match.group(1)
print(f"Size of codecave: {value}")
