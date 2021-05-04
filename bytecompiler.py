import struct

class ClassFile:
    def __init__(self, name, access=["public"], sname="java/lang/Object", version=(49, 0)):
        self.pool = ConstantPool()
        self.interfaces = []
        self.fields = []
        self.methods = []
        self.attributes = []
        self.version = version
        self.access = access

        self.__tix = self.addpool("class", self.pool.add("utf8", name)) #Add this class to the constant pool and get the index
        self.__six = self.addpool("class", self.pool.add("utf8", sname)) #And the super class
        self.addpool("utf8", "Code")

    def serialize(self):
        d = bytes.fromhex("cafebabe")
        d += self.version[1].to_bytes(2, "big")
        d += self.version[0].to_bytes(2, "big")

        d += len(self.pool).to_bytes(2, "big")
        d += self.pool.serialize()

        d += AccessHelper.bitmask(self.access).to_bytes(2, "big")
        
        d += self.__tix.to_bytes(2, "big")
        d += self.__six.to_bytes(2, "big")

        d += len(self.interfaces).to_bytes(2, "big")
        for i in self.interfaces:
            d += i.to_bytes(2, "big")

        d += len(self.fields).to_bytes(2, "big")
        for f in self.fields:
            d += f.serialize()

        d += len(self.methods).to_bytes(2, "big")
        for m in self.methods:
            d += m.serialize()

        d += len(self.attributes).to_bytes(2, "big")
        for a in self.attributes:
            d += a.serialize()
        
        return d
    
    def addpool(self, etype, *entry):
        return self.pool.add(etype, *entry)

    def qpool(self, etype, *entry): #Quick method allowing easy and uncomplicated constant generation
        return self.pool.qadd(etype, *entry)

    def interface(self, name):
        self.interfaces.append(name)

    def field(self, name, descriptor, access=["public"], attributes=[]):
        self.fields.append(Field(name, descriptor, access, attributes))

    def method(self, name, descriptor, access=["public"], attributes=[]):
        self.methods.append(Method(name, descriptor, access, attributes))

class Field:
    def __init__(self, name, descriptor, access=["public"], attributes=[]):
        self.name = name
        self.descriptor = descriptor
        self.access = access
        self.attributes = attributes

    def serialize(self):
        atts = b""
        for a in self.attributes:
            atts += a.serialize()
        return (AccessHelper.bitmask(self.access).to_bytes(2, "big") + self.name.to_bytes(2, "big") + self.descriptor.to_bytes(2, "big") + len(self.attributes).to_bytes(2, "big") + atts)

class Method:
    def __init__(self, name, descriptor, access=["public"], attributes=[]):
        self.name = name
        self.descriptor = descriptor
        self.access = access
        self.attributes = attributes

    def serialize(self):
        atts = b""
        for a in self.attributes:
            atts += a.serialize()
        return (AccessHelper.bitmask(self.access).to_bytes(2, "big") + self.name.to_bytes(2, "big") + self.descriptor.to_bytes(2, "big") + len(self.attributes).to_bytes(2, "big") + atts)

class Attribute:
    def serialize(self):
        return (self.name.to_bytes(2, "big") + len(self.data).to_bytes(4, "big") + self.data)

class CodeAttribute(Attribute):
    def __init__(self, code, max_stack=10, max_locals=5, exceptions=[], attributes=[]): #Exceptions are tuples of start_pc, end_pc, handler_pc and catch_type
        self.name = 5 #TODO: Remove hardcoded constpool index
        self.code = code
        self.max_stack = max_stack
        self.max_locals = max_locals
        self.exceptions = exceptions
        self.attributes = attributes

        self.data = self._data()

    def _data(self):
        d = b""
        d += self.max_stack.to_bytes(2, "big")
        d += self.max_stack.to_bytes(2, "big")
        d += len(self.code).to_bytes(4, "big")
        d += self.code
        d += len(self.exceptions).to_bytes(2, "big")
        for e in self.exceptions:
            for i in range(4):
                d += e[i].to_bytes(2, "big")
        d += len(self.attributes).to_bytes(2, "big")
        for a in self.attributes:
            d += a.serialize()
        return d

class ConstantPool:
    def __init__(self):
        self.entries = []
        self.__index = 0 #Starts at cpool equivalent of -1
    
    def __len__(self):
        return self.__index + 1

    def serialize(self):
        d = b""
        for entry in self.entries:
            d += entry
        return d

    def add(self, etype, *entry):
        etype = etype.lower()
        self.__index += 1
        
        if len(entry) == 1:
            entry = entry[0] #Quick hack with *args

        if etype == "utf8":
            self.entries.append(self._utf8Const(entry))
        elif etype == "int":
            self.entries.append(self._intConst(entry))
        elif etype == "float":
            self.entries.append(self._floatConst(entry))
        elif etype == "long":
            self.entries.append(self._intConst(entry))
            self.__index += 1
            return self.__index - 1
        elif etype == "double":
            self.entries.append(self._floatConst(entry))
            self.__index += 1
            return self.__index - 1
        elif etype == "class":
            self.entries.append(self._classRefConst(entry))
        elif etype == "string":
            self.entries.append(self._stringRefConst(entry))
        elif etype == "field":
            self.entries.append(self._fieldRefConst(entry[0], entry[1]))
        elif etype == "method":
            self.entries.append(self._methodRefConst(entry[0], entry[1]))
        elif etype == "interface_method":
            self.entries.append(self._interfaceMethodRefConst(entry[0], entry[1]))
        elif etype == "name_type":
            self.entries.append(self._nameTypeConst(entry[0], entry[1]))
        elif etype == "method_handle":
            self.entries.append(self._methodHandleConst(entry[0], entry[1]))
        elif etype == "method_type":
            self.entries.append(self._methodTypeConst(entry))
        elif etype == "invoke_dynamic":
            self.entries.append(self._invokeDynamicConst(entry[0], entry[1]))
        else:
            print("Invalid constant pool type!")
            return 0
        
        return self.__index

    def qadd(self, etype, *entry):
        etype = etype.lower()

        if len(entry) == 1:
            entry = entry[0]
        
        if etype == "class":
            return self.add("class", self.add("utf8", entry))
        elif etype == "string":
            return self.add("string", self.add("utf8", entry))
        elif etype == "field": #entry -> (class index, name, type)
            return self.add("field", entry[0], self.add("name_type", self.add("utf8", entry[1]), self.add("utf8", entry[2])))
        elif etype == "method": #entry -> (class index, name, type)
            return self.add("method", entry[0], self.add("name_type", self.add("utf8", entry[1]), self.add("utf8", entry[2])))
        elif etype == "interface_method": #entry -> (class index, name, type)
            return self.add("interface_method", entry[0], self.add("name_type", self.add("utf8", entry[1]), self.add("utf8", entry[2])))
        else:
            print("Invalid constant pool quicktype!")
            return 0

    def _utf8Const(self, text):
        return (b"\x01" + len(text).to_bytes(2, "big") + text.encode("utf-8"))

    def _stringRefConst(self, index):
        return (b"\x08" + index.to_bytes(2, "big"))

    def _classRefConst(self, nameIndex):
        return (b"\x07" + nameIndex.to_bytes(2, "big"))

    def _methodTypeConst(self, descriptorIndex):
        return (b"\x10" + descriptorIndex.to_bytes(2, "big"))

    def _methodRefConst(self, classIndex, nameTypeIndex):
        return (b"\x0a" + classIndex.to_bytes(2, "big") + nameTypeIndex.to_bytes(2, "big"))

    def _interfaceMethodRefConst(self, classIndex, nameTypeIndex):
        return (b"\x0b" + classIndex.to_bytes(2, "big") + nameTypeIndex.to_bytes(2, "big"))

    def _fieldRefConst(self, classIndex, nameTypeIndex):
        return (b"\x09" + classIndex.to_bytes(2, "big") + nameTypeIndex.to_bytes(2, "big"))

    def _nameTypeConst(self, nameIndex, typeIndex):
        return (b"\x0c" + nameIndex.to_bytes(2, "big") + typeIndex.to_bytes(2, "big"))

    def _intConst(self, x):
        return (b"\x03" + MathHelper.ifsign(x, 4).to_bytes(4, "big"))

    def _longConst(self, x):
        return (b"\x05" + MathHelper.ifsign(x, 8).to_bytes(8, "big"))

    def _floatConst(self, x):
        return (b"\x04" + struct.pack("!f", x)) #Got tired of reading about IEEE754 and just used struct

    def _doubleConst(self, x):
        return (b"\x06" + struct.pack("!d", x))

    def _methodHandleConst(self, kind, index):
        return (b"\x0f" + kind.to_bytes(1, "big") + index.to_bytes(2, "big"))

    def _invokeDynamicConst(self, bootstrap, nametype):
        return (b"\x12" + bootstrap.to_bytes(2, "big") + nametype.to_bytes(2, "big"))

class MathHelper:
    @staticmethod
    def sign(x, n): #Two's complement sign, n is the byte-length of x.
        n = 2 ** (8 * n) - 1
        return (x ^ n) + 1

    @staticmethod
    def ifsign(x, n): #sign if x < 0
        if x < 0:
            return sign(x, n)
        return x

class AccessHelper:
    flags = {"public": 0x0001, "private": 0x0002, "protected": 0x0004, "static": 0x0008, "final": 0x0010, "synthetic": 0x1000, "volatile": 0x0040, "transient": 0x0080, "enum": 0x4000, "synchronized": 0x0020, "bridge": 0x0040, "varargs": 0x0080, "native": 0x0100, "abstract": 0x0400, "strict": 0x0800, "super": 0x0020, "interface": 0x0200, "annotation": 0x2000}

    @staticmethod
    def bitmask(access):
        a = 0
        for x in access:
            a |= AccessHelper.flags[x]
        return a

