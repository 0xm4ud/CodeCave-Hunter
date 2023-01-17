# ( M4UD's Code Cave Hunter! )

import pykd
import sys
import re

print("\r\n===========================\r\n[*] M4UD's CodeCave hunter!")

module_name = ""
Win32_API = "WriteProcessMemory"

if len(sys.argv) == 2:
    module_name = sys.argv[1]

if len(sys.argv) == 3:
    module_name = sys.argv[1]
    Win32_API = sys.argv[2]

print("\r\n=============================================")
print(f"Hunting for Code Cave on module {module_name}...")
print("=============================================\r\n")

output = pykd.dbgCommand(f"dd {module_name} + 3C L1")
parts = output.split()

if len(sys.argv) == 3:
	var = hex(int(parts[1], 16))

if len(sys.argv) == 2:
	var = hex(int(str(parts[0]), 16))
	print(var)

output = pykd.dbgCommand(f"dd {module_name} + {var} + 2c L1")
parts = output.split()

if len(sys.argv) == 3:
	var2 = hex(int(parts[1], 16))
else:
	var2 = hex(int(str(parts[0]), 16))

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
size = pykd.dbgCommand(f"?  0x{start_address:x} - 0x{end_address:x}")
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

output = pykd.dbgCommand(f"?{var5} - {module_name}")
match = re.search(r': (.*) =', output)
value = match.group(1)
print("Offset to writable .data section is: "+ hex(int(value)))

if len(sys.argv) == 3:
    print("\r\n========================================================")
    print(f"Retriving {Win32_API} addr from {module_name} IAT...")
    print("========================================================\r\n")
    output2 = pykd.dbgCommand(f"$$>a<c:\\tools\osed-scripts\Find-IAT.txt {module_name}")
    api = re.findall(r"[^\n]*{}[^\n]*".format(Win32_API), str(output2), re.MULTILINE)
    print(api[-1]+"\r\n")
    api = re.search(r'(?m)^\d+',api[-1], re.IGNORECASE).group()

    if sys.argv[2] == "WriteProcessMemory":
        print(f"Win32 {Win32_API} API call Skelleton\r\n")
        print(f"wpm = pack(\"<L\", (0x{api})) # {Win32_API} addr")
        print(f"wpm += pack(\"<L\", (0x{end_address:x})) # CODE CAVE- Shellcode Return Address")
        print(f"wpm += pack(\"<L\", (0xffffffff)) # dummy hProcess - 0xfffffffff")
        print(f"wpm += pack(\"<L\", (0x{end_address:x})) # dummy lpBaseAddress - CODE CAVE")
        print(f"wpm += pack(\"<L\", (0x45454545)) # dummy lpBuffer")
        print(f"wpm += pack(\"<L\", (0x46464646)) # dummy nSize")
	print(f"wpm += pack(\"<L\", (0x{var5})) # dummy *lpNumberOfBytesWritten - .data")
