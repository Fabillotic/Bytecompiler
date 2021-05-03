from compiler import ClassFile, CodeAttribute

def test():
    c = ClassFile("Main")

    constWorld = hex(c.addpool("string", c.addpool("utf8", "Hello, world!")))[2:].zfill(2)
    constOut = hex(c.addpool("field", (c.addpool("class", c.addpool("utf8", "java/lang/System")), c.addpool("name_type", (c.addpool("utf8", "out"), c.addpool("utf8", "Ljava/io/PrintStream;"))))))[2:].zfill(4)
    constPrintln = hex(c.addpool("method", (c.addpool("class", c.addpool("utf8", "java/io/PrintStream")), c.addpool("name_type", (c.addpool("utf8", "println"), c.addpool("utf8", "(Ljava/lang/String;)V"))))))[2:].zfill(4)

    code = "b2" + constOut + "12" + constWorld + "b6" + constPrintln + "b1"
    c.method(c.addpool("utf8", "main"), c.addpool("utf8", "([Ljava/lang/String;)V"), ["public", "static"], [CodeAttribute(bytes.fromhex(code.replace(" ", "")))])

    f = open("Main.class", "wb")
    f.write(c.serialize())
    f.close()

if __name__ == "__main__":
    test()
