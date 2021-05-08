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
from byteassembler import assemble

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

    t3 = c.addpool("int", 30000)
    ldct3 = assemble(f"ldc {t3}")

    def clean(x):
        return bytes.fromhex(x.replace(" ", ""))

    code = b""

    code += assemble( #brainfuck init
    f"""
    ldc {t3}
    newarray int
    astore_2
    
    iconst_0
    istore_3
    
    loop:
    iload_3
    ldc {t3}
    if_icmpge done
    
    aload_2
    iload_3
    iconst_0
    iastore
    iinc 3 1
    goto loop
    
    done:
    iconst_0
    istore_3
    """)
    
    def putcode(c): #Outputs a character with ascii code c
        #return clean("b2") + constOut.to_bytes(2, "big") + clean("10" + hex(c)[2:].zfill(2) + "b6") + constWrite.to_bytes(2, "big")
        return assemble(
        f"""
        getstatic {constOut}
        bipush {c}
        invokevirtual {constWrite}
        """)
    def flushcode(): #Calls System.out.flush()
        #return clean("b2") + constOut.to_bytes(2, "big") + clean("b6") + constFlush.to_bytes(2, "big")
        return assemble(
        f"""
        getstatic {constOut}
        invokevirtual {constFlush}
        """)
    def _ocode(): #. but print number instead of character
        #return clean("b2") + constOut.to_bytes(2, "big") + clean("2c1d2eb6") + constPrintln.to_bytes(2, "big")
        return assemble(
        f"""
        getstatic {constOut}
        aload_2
        iload_3
        iaload
        invokevirtual {constPrintln}
        """)
    def ocode(): #.
        #return clean("b2") + constOut.to_bytes(2, "big") + clean("2c1d2eb6") + constWrite.to_bytes(2, "big") + flushcode()
        return assemble(
        f"""
        getstatic {constOut}
        aload_2
        iload_3
        iaload
        invokevirtual {constWrite}
        """) + flushcode()
    def icode(): #,
        #sysin = b"\xb2" + constIn.to_bytes(2, "big")
        sysin = assemble(f"getstatic {constIn}")
        #r = b"\xb6" + constRead.to_bytes(2, "big")
        r = assemble(f"invokevirtual {constRead}")
        #return (putcode(62) + putcode(32) + flushcode() + clean("2c1d") + sysin + r + clean("4f") + sysin + r + clean("57"))
        return (putcode(62) + putcode(32) + flushcode() + assemble(f"aload_2\niload_3") + sysin + r + assemble(f"iastore") + sysin + r + assemble(f"pop"))
    def addcode(num=1): #+ / -
        if num < 0:
            num = (-num ^ 0xff) + 1
        #return clean("2c1d5c2e 10" + hex(num)[2:].zfill(2) + "60 4f")
        return assemble(
        f"""
        aload_2
        iload_3
        dup2
        iaload
        bipush {num}
        iadd
        iastore
        """)
    def shiftcode(num=1): #< / >
        if num < 0:
            num = (-num ^ 0xffff) + 1
        #return clean("1d11" + hex(num)[2:].zfill(4) + "603e")
        return assemble(
        f"""
        iload_3
        sipush {num}
        iadd
        istore_3
        """)
    def obcode(offset=0): #[
        if offset < 0:
            offset = (-offset ^ 0xffff) + 1
        #return clean("2c1d2e 99" + hex(offset)[2:].zfill(4))
        return assemble(
        f"""
        aload_2
        iload_3
        iaload

        ifeq {offset}
        """)
    def cbcode(offset): #]
        if offset < 0:
            offset = (-offset ^ 0xffff) + 1
        #return clean("2c1d2e 9a" + hex(offset)[2:].zfill(4))
        return assemble(
        f"""
        aload_2
        iload_3
        iaload

        ifne {offset}
        """)

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

    #code += b"\xb1"
    code += assemble(f"return")
    
    c.method("main", "([Ljava/lang/String;)V", ["public", "static"], [CodeAttribute(code)])

    f = open("Main.class", "wb")
    f.write(c.serialize())
    f.close()

if __name__ == "__main__":
    main()
