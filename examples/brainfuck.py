"""
Copyright 2021 Fabillotic
All rights reserved.

This is a simple Brainfuck to Bytecode compiler.
It takes a Brainfuck file as input and uses Bytecompiler to compile it to Java bytecode.
"""

import os.path; import sys; sys.path.append(os.path.abspath(".")) #You can run 'python examples/(something).py' easily

import sys
import os.path

from bytecompiler import ClassFile, CodeAttribute

def main():
    if not len(sys.argv) > 1:
        print("Please enter a file!")
        return

    if not (os.path.exists(sys.argv[1]) and os.path.isfile(sys.argv[1])):
        print("Not a file!")
        return

    bf = b""
    
    f = open(sys.argv[1], "rb")
    d = f.read()
    f.close()

    for c in d:
        if b"<>+-.,[]".count(c) > 0:
            bf += bytes([c])

    c = ClassFile("Main")
    
    constSystem = c.qpool("class", "java/lang/System")
    constOut = c.qpool("field", constSystem, "out", "Ljava/io/PrintStream;")
    constIn = c.qpool("field", constSystem, "in", "Ljava/io/InputStream;")
    constPrintStream = c.qpool("class", "java/io/PrintStream")
    constInputStream = c.qpool("class", "java/io/InputStream")
    constWrite = c.qpool("method", constPrintStream, "write", "(I)V")
    constRead = c.qpool("method", constInputStream, "read", "()I")
    constFlush = c.qpool("method", constPrintStream, "flush", "()V")
    constPrintln = c.qpool("method", constPrintStream, "println", "(I)V")

    t3 = c.addpool("int", 30000).to_bytes(1, "big")
    ldct3 = b"\x12" + t3 #ldc #t3

    def clean(x):
        return bytes.fromhex(x.replace(" ", ""))

    code = b""
    code += ldct3 + clean("bc0a4d 033e 1d") + ldct3 + clean("a2000d") + clean("2c1d034f840301a7fff3") + clean("033e") #1230bc0a4d 033e 1d1230a2000d 2c1d034f840301a7fff3 033e #brainfuck init
    
    def putcode(c): #Outputs a character with ascii code c
        return clean("b2") + constOut.to_bytes(2, "big") + clean("10" + hex(c)[2:].zfill(2) + "b6") + constWrite.to_bytes(2, "big")
    def flushcode(): #Calls System.out.flush()
        return clean("b2") + constOut.to_bytes(2, "big") + clean("b6") + constFlush.to_bytes(2, "big")
    def _ocode(): #. but print number instead of character
        return clean("b2") + constOut.to_bytes(2, "big") + clean("2c1d2eb6") + constPrintln.to_bytes(2, "big")
    def ocode(): #.
        return clean("b2") + constOut.to_bytes(2, "big") + clean("2c1d2eb6") + constWrite.to_bytes(2, "big") + flushcode()
    def icode(): #,
        sysin = b"\xb2" + constIn.to_bytes(2, "big")
        r = b"\xb6" + constRead.to_bytes(2, "big")
        return (putcode(62) + putcode(32) + flushcode() + clean("2c1d") + sysin + r + clean("4f") + sysin + r + clean("57"))
    def addcode(num=1): #+ / -
        if num < 0:
            num = (-num ^ 0xff) + 1
        return clean("2c1d5c2e 10" + hex(num)[2:].zfill(2) + "60 4f")
    def shiftcode(num=1): #< / >
        if num < 0:
            num = (-num ^ 0xffff) + 1
        return clean("1d11" + hex(num)[2:].zfill(4) + "603e")
    def obcode(offset=0): #[
        if offset < 0:
            offset = (-offset ^ 0xffff) + 1
        return clean("2c1d2e 99" + hex(offset)[2:].zfill(4))
    def cbcode(offset): #]
        if offset < 0:
            offset = (-offset ^ 0xffff) + 1
        return clean("2c1d2e 9a" + hex(offset)[2:].zfill(4))

    #I will now be using bf (The brainfuck code I read earlier)
    
    bstack = []
    
    p = 0

    for n, ch in enumerate(bf):
        if (ch == 43 or ch == 45): #+/-
            p += (1 if ch == 43 else -1)
            continue
        elif p != 0:
            code += addcode(p)
            p = 0
        if ch == 62: #>
            code += shiftcode()
            continue
        if ch == 60: #<
            code += shiftcode(-1)
            continue
        if ch == 46: #.
            code += ocode()
            continue
        if ch == 44: #,
            code += icode()
            continue
        if ch == 91: #[
            code += obcode(0) #default value, replaced later
            bstack.append(len(code))
            continue
        if ch == 93: #]
            o = bstack[-1]
            bstack = bstack[:-1]
            code += cbcode(-(len(code) - o) - 3)

            fill = bytes.fromhex(hex(len(code) - o + 3)[2:].zfill(4))
            code = code[:o-2] + fill + code[o:]
            continue

    code += b"\xb1"
    
    c.method("main", "([Ljava/lang/String;)V", ["public", "static"], [CodeAttribute(code)])

    f = open("Main.class", "wb")
    f.write(c.serialize())
    f.close()

if __name__ == "__main__":
    main()
