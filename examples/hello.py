import os.path; import sys; sys.path.append(os.path.abspath(".")) #You can run 'python examples/(something).py' easily

from bytecompiler import ClassFile, CodeAttribute

def test():
    c = ClassFile("Main")

    constWorld = c.qpool("string", "Hello, world!")
    constSystem = c.qpool("class", "java/lang/System")
    constOut = c.qpool("field", constSystem, "out", "Ljava/io/PrintStream;")
    constPrintStream = c.qpool("class", "java/io/PrintStream")
    constPrintln = c.qpool("method", constPrintStream, "println", "(Ljava/lang/String;)V")

    code = b"\xb2" + constOut.to_bytes(2, "big") + b"\x12" + constWorld.to_bytes(1, "big") + b"\xb6" + constPrintln.to_bytes(2, "big") + b"\xb1"
    c.method("main", "([Ljava/lang/String;)V", ["public", "static"], [CodeAttribute(code)])

    f = open("Main.class", "wb")
    f.write(c.serialize())
    f.close()

if __name__ == "__main__":
    test()
