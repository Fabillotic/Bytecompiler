"""
Copyright 2021 Fabillo
All rights reserved.

This is the implementation of "Hello, world" in Bytecompiler.
"""

import os.path; import sys; sys.path.append(os.path.abspath(".")) #You can run 'python examples/(something).py' easily

from bytecompiler import ClassFile, CodeAttribute
from byteassembler import assemble

def test():
    c = ClassFile("Main")

    constWorld = c.qpool("string", "Hello, world!")
    constSystem = c.qpool("class", "java/lang/System")
    constOut = c.qpool("field", constSystem, "out", "Ljava/io/PrintStream;")
    constPrintStream = c.qpool("class", "java/io/PrintStream")
    constPrintln = c.qpool("method", constPrintStream, "println", "(Ljava/lang/String;)V")
    
    code = f"""
    iconst_5
    istore_2
    start:
    getstatic {constOut}
    ldc {constWorld}
    invokevirtual {constPrintln}
    iload_2
    iconst_m1
    iadd
    istore_2
    iload_2
    ifle done
    goto start
    done:
    return
    """
    code = assemble(code)
    
    c.method("main", "([Ljava/lang/String;)V", ["public", "static"], [CodeAttribute(code)])

    f = open("Main.class", "wb")
    f.write(c.serialize())
    f.close()

if __name__ == "__main__":
    test()
