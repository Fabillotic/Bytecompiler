# Bytecompiler

A tool to generate Java bytecode in Python.

More information on bytecode can be found here: [Oracle docs](https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-4.html), [Wikipedia class file](https://en.wikipedia.org/wiki/Java_class_file), [Wikipedia instruction listings](https://en.wikipedia.org/wiki/Java_bytecode_instruction_listings) (Very useful)

## Usage

```python
from bytecompiler import ClassFile

cf = ClassFile("Main") #Make a ClassFile with name "Main". Try to match the file name. (i.e. Main.class)
cf.addpool("long", 50000) #Add a long entry to the constant pool and return the index

cf.qpool("class", "java/lang/System") #this quick shorthand is equivalent to
cf.addpool("class", cf.addpool("utf8", "java/lang/System"))

x = cf.qpool("class", "java/lang/System")

f = cf.qpool("field", x, "out", "Ljava/io/PrintStream;") #Get System.out, again shorthand to
f = cf.addpool("field", x, cf.addpool("name_type", cf.addpool("utf8", "out"), cf.addpool("utf8", "Ljava/io/PrintStream;")))

cf.field("myfield", "Ljava/lang/Object;", ["private"]) #Create a private field called "myfield" of type java/lang/Object

from bytecompiler import CodeAttribute
code = CodeAttribute(b"Insert bytecode in bytes format")
cf.method("main", "([Ljava/lang/String;)V", ["public", "static"], [code]) #Typical main method

f = open("Main.class", "wb")
f.write(cf.serialize()) #Serialize the classfile
f.close()
```

### ClassFile constructor
name - The name of the classfile. Match this to the output file

access - Access flags. Default: ```["public"]```

sname - The name of the super class. Default: ```"java/lang/Object"```

version - The version. Default: ```(49, 0)```
