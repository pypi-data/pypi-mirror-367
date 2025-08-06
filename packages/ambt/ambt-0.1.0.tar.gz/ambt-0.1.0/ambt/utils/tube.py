from abc import ABC, abstractmethod
from ambt.utils.packing import unpack
from ambt.utils.typing import anyToStrBytesType, anyType, any_to_bytes, any_to_str, any_to_int

class GenericTube(ABC):

    @abstractmethod
    def send(self, data: str|bytes):
        pass

    @abstractmethod
    def recv(self, numb: int|None, timeout: int|None) -> str|bytes:
        pass

    @abstractmethod
    def interactive(self):
        pass

class AmbtTube():

    TIMEOUT: int = 1048576 

    def __init__(self, tube: GenericTube, input_type: type = bytes, output_type: type = str, export: bool = True):
        global _currentTube
        self._buffer: str|bytes
        self._newline: str|bytes 
        self._transform_input: anyToStrBytesType
        self._transform_output: anyToStrBytesType

        self.tube: GenericTube = tube
    
        if input_type == bytes:
            self._newline = b"\n"
            self._transform_input = any_to_bytes
        elif input_type == str:
            self._newline = "\n"
            self._transform_input = any_to_str
        else:
            raise Exception(f"[AmbtTube] Unknown output type {output_type}")
        
        if output_type == bytes:
            self._buffer = b""
            self._transform_output = any_to_bytes 
        elif output_type == str:
            self._buffer = ""
            self._transform_output = any_to_str
        else:
            raise Exception(f"[AmbtTube] Unknown output type {output_type}")

        if export:
            _currentTube = self


    def send(self, data: anyType): 
        return self.tube.send(self._transform_input(data))

    def sendline(self, data: anyType):
        return self.tube.send(self._transform_input(data) + self._newline)

    def recv(self, numb: int = 4096, timeout: int = TIMEOUT) -> str|bytes:
        return self._transform_output(self.tube.recv(numb, timeout))

    def recvuntil(self, delim: anyType, drop: bool = False, timeout: int = TIMEOUT) -> str|bytes:
        delims = self._transform_output(delim) 
        
        if not delim:
            raise Exception("[AmbtTube] Empty delim provided to recvuntil()")

        self._buffer = self._buffer[:0] 
        while len(delim) > len(self._buffer) or self._buffer[-(len(delim)):] != delims:
            self._buffer += self._transform_output(self.tube.recv(1, timeout)) 

        if drop:
            self._buffer = self._buffer[:-(len(delims))]

        return self._buffer

    def recvline(self, drop: bool = False, timeout: int = TIMEOUT) -> str|bytes:
        return self.recvuntil("\n", drop, timeout)

    def sendafter(self, delim: anyType, data: anyType, timeout: int = TIMEOUT) -> str|bytes:
        recvd = self.recvuntil(delim, timeout=timeout)
        self.send(data)
        return recvd 

    def sendlineafter(self, delim: anyType, data: anyType, timeout: int = TIMEOUT) -> str|bytes:
        recvd = self.recvuntil(delim, timeout=timeout)
        self.sendline(data)
        return recvd

    def shell(self):
        self.tube.interactive()


_currentTube: AmbtTube|None = None

def _tubeDoesNotExist():
    raise Exception("[AmbtTube] Tube not initialized!")

s = lambda d: _currentTube.send(d) if _currentTube else _tubeDoesNotExist()
sl = lambda d: _currentTube.sendline(d) if _currentTube else _tubeDoesNotExist() 
r = re = lambda n: _currentTube.recv(n) if _currentTube else _tubeDoesNotExist()
ru = reu = lambda d: _currentTube.recvuntil(d) if _currentTube else _tubeDoesNotExist()
rl = lambda: _currentTube.recvline() if _currentTube else _tubeDoesNotExist()
sa = lambda k,d: _currentTube.sendafter(k,d) if _currentTube else _tubeDoesNotExist()
sla = lambda k,d: _currentTube.sendlineafter(k,d) if _currentTube else _tubeDoesNotExist()
sh = lambda: _currentTube.shell() if _currentTube else _tubeDoesNotExist()

byteleak = lambda w: unpack(_currentTube.recv(w//8), w) if _currentTube else _tubeDoesNotExist()
intleak = lambda n: any_to_int(_currentTube.recv(n)) if _currentTube else _tubeDoesNotExist()
