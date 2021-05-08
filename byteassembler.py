"""
The Byteassembler takes a human-readable form of Bytecode and assembles it into actual bytecode.
opcodes.txt contains the list of opcodes and their arguments.
"""

import sys
import os.path
from bytecompiler import MathHelper

def test():
    if not len(sys.argv) > 1:
        print("Please enter a file!")
        return

    if not (os.path.exists(sys.argv[1]) and os.path.isfile(sys.argv[1])):
        print("Not a file!")
        return
    
    f = open(sys.argv[1], "r")
    d = f.read()
    f.close()

    print(assemble(d).hex())

def assemble(code):
    a = Assembler()
    a.add_data(code)
    return a.assemble()

class Assembler:
    def __init__(self):
        f = open("opcodes.txt", "r")
        o = f.read()
        f.close()

        o = o.split("\n")[10:-1]

        self.data = ""
        
        self.labels = {}

        self.opcodes = {}
        for l in o:
            l = l.split(" ")
            self.opcodes[l[1]] = ((int(l[0], 16), l[2:]))

    def add_data(self, data):
        self.data += data

    def assemble(self):
        code = b""

        self.data = self.data.split("\n")
        
        lb = dict()

        for ln, l in enumerate(self.data):
            l = self._remove_ws(l)
            
            if l == "":
                continue

            if l.endswith(":"):
                if l.count(" ") == 0:
                    l = l[:-1]
                    
                    if l in self.labels:
                        print("The label '" + l + "' has already been defined.")
                        return

                    self.labels[l] = len(code)
                    
                    if l in lb:
                        for e in lb[l]:
                            n = e[1]
                            x = e[0]
                            
                            code = code[:x] + MathHelper.ifsign((len(code) - (x - 1)), n).to_bytes(n, "big") + code[x+n:]
                        del lb[l]
                    continue
                else:
                    print("Labels can't have spaces!")
                    return
            
            l = l.split(" ")
            
            op = self.opcodes[l[0]]
            code += op[0].to_bytes(1, "big")

            a = 1
            for x in op[1]:
                if x == "local":
                    code += int(l[a]).to_bytes(1, "big")
                elif x == "const2" or x == "const":
                    code += int(l[a]).to_bytes((1 if x == "const" else 2), "big")
                elif x == "byte":
                    n = 1
                    code += MathHelper.ifsign(int(l[a]), n).to_bytes(n, "big")
                elif x == "short":
                    n = 2
                    code += MathHelper.ifsign(int(l[a]), n).to_bytes(n, "big")
                elif x == "tbranch" or x == "fbranch":
                    n = (2 if x == "tbranch" else 4)
                    if not l[a] in self.labels:
                        code += bytes(n)
                        
                        if l[a] in lb:
                            lb[l[a]] = [*lb[l[a]], (len(code) - n, n)]
                        else:
                            lb[l[a]] = [(len(code) - n, n)]
                        continue
                    
                    f = self.labels[l[a]]
                    code += MathHelper.ifsign(-((len(code) - 1) - f), n).to_bytes(n, "big")
                elif x == "atype":
                    if l[a] == "boolean":
                        code += b"\x04"
                    elif l[a] == "char":
                        code += b"\x05"
                    elif l[a] == "float":
                        code += b"\x06"
                    elif l[a] == "double":
                        code += b"\x07"
                    elif l[a] == "byte":
                        code += b"\x08"
                    elif l[a] == "short":
                        code += b"\x09"
                    elif l[a] == "int":
                        code += b"\x0a"
                    elif l[a] == "long":
                        code += b"\x0b"
                    else:
                        print("Invalid array type!")
                        return
                elif x == "special":
                    print("Special cases aren't allowed yet.")
                    return
                a += 1

        return code
    
    def _remove_ws(self, l): #Remove whitespace
        i = 0
        for c in l:
            if c != " " and c != "\t":
                break
            else:
                i += 1
        return l[i:]

if __name__ == "__main__":
    test()
