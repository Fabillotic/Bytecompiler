def test():
    a = Assembler()
    a.assemble("")

class Assembler:
    def __init__(self):
        f = open("opcodes.txt", "r")
        o = f.read()
        f.close()

        o = o.split("\n")[10:-1]
        
        self.labels = []

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
                    self.labels.append(l[1:])
                    continue
                else:
                    print("Labels can't have spaces!")
                    return
            l = l.split(" ")

            op = self.opcodes[l[0]]
            code += op[0].to_bytes(1, "big")
            
            for x in op[1]:
                print(x)
    
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
