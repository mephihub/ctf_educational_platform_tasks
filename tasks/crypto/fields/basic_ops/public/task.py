# secret value that you don't know
from flag import FLAG
from random import randint
from Crypto.Util.number import getPrime

def bytes_to_long(b: bytes) -> int:
    return int.from_bytes(b, 'big')


p = getPrime(1024)
secret = bytes_to_long(FLAG)

class LCG:
    def __init__(self, p: int):
        self.p = p
        self.a = randint(1, p - 1)
        self.b = randint(1, p - 1)
        self.x = randint(1, p - 1)

    def next(self) -> int:
        self.x = (self.a * self.x + self.b) % self.p
        return self.x
    

def main():
    lcg = LCG(p)
    for _ in range(10):
        print(lcg.next())
    print(f"{p = }")

if __name__ == "__main__":
    main()