import pykd
import sys
import re

print("\r\nM4UD's Code Cave and .data section hunter!\r\n")
module_name = ""
if len(sys.argv) > 1:
    module_name = sys.argv[1]

output = pykd.dbgCommand(f"dd {module_name} + 3C L1")
parts = output.split()
var = hex(int(parts[1], 16))

output = pykd.dbgCommand(f"dd {module_name} + {var} + 2c L1")
parts = output.split()
var2 = hex(int(parts[1], 16))

output = pykd.dbgCommand(f"? {module_name} + 1000")
parts = output.split()
var3 = parts[4]

output = pykd.dbgCommand(f"!address {var3}")

for line in output.split("\n"):
    if "End Address:" in line:
        var4 = int(line.split()[-1], 16)
    if "Protect:" in line:
        var5 = line.split()[-1]

print(f"End Address: 0x{var4:x}")
print(f"Protect: {var5}")

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

print(f"Code Cave start at: 0x{end_address:x}")
print(f"Code Cave finishes at: 0x{start_address:x}")
size = pykd.dbgCommand(f"? 0x{end_address:x} - 0x{start_address:x}")
match = re.search(r': (.*) =', size)
value = match.group(1)
print(f"Size of codecave: {value} bytes")

print("\r\n=====================")
print("Finding .data section...")
print("=====================\r\n")
output = pykd.dbgCommand(f"!dh -a {module_name}")

lines = output.split("\n")
for i in range(len(lines)):
    if ".data" in lines[i]:
        var = lines[i+1]
        var2 = lines[i+2]
        break

var3 = re.search(r'([\w]+)\s+virtual size',var).group(1)
var4 = re.search(r'([\w]+)\s+virtual address',var2).group(1)
print("virtual size = "+var3)
print("virtual address = "+var4)

output = pykd.dbgCommand(f"? {module_name} + {var3} + {var4}")

var5 = re.search(r'=\s+([\w]+)',output).group(1)
print("SECTION HEADER .data located at = "+var5)

output = pykd.dbgCommand(f"!vprot {var5}")

protect = re.search(r'(?m)^Protect:\s+(\w+)*',output).group(1)
if protect == "00000004":
	print("Protect: "+protect +"  PAGE_READWRITE")
else:
	print("NOT PAGE_READWRITE, something is off!")
    quit()

output = pykd.dbgCommand(f"?{var5} - {module_name}")
match = re.search(r': (.*) =', output)
value = match.group(1)
print("Offset to writable .data section is: "+ hex(int(value)))
