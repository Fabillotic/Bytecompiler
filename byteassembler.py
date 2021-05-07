def test():
    return

def assemble(code):
    return Assembler().assemble(code)

class Assembler:
    def __init__(self):
        f = open("opcodes.txt", "r")
        o = f.read()
        f.close()

        o = o.split("\n")[10:-1]
        
        self.labels = {}

        self.opcodes = {}
        for l in o:
            l = l.split(" ")
            self.opcodes[l[1]] = ((int(l[0], 16), l[2:]))

    def assemble(self, data):
        code = b""

        data = data.split("\n")
        
        for l in data:
            l = self._remove_ws(l)
            if l.endswith(":"):
                if l.count(" ") == 0:
                    self.labels[l[:-1]] = len(code)
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
                    code += int(l[a]).to_bytes(1, "big")
                elif x == "short":
                    code += int(l[a]).to_bytes(2, "big")
                elif x == "tbranch" or x == "fbranch":
                    if not l[a] in self.labels:
                        print("Invalid branch location!")
                        return
                    code += ((len(code) - 1) - self.labels[l[a]]).to_bytes((2 if x == "tbranch" else 4), "big")
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
