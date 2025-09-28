# secret value that you don't know
from flag import FLAG
from random import randint
from Crypto.Util.number import getPrime

def bytes_to_long(b: bytes) -> int:
    return int.from_bytes(b, 'big')

def generate_prime(bits: int) -> int:
    while True:
        p = getPrime(bits)
        if (p - 1) % 3 != 0:
            return p

p = generate_prime(1024)
secret = bytes_to_long(FLAG)



class LCG:
    def __init__(self, p: int, secret: int):
        self.p = p
        self.a = randint(1, p - 1)
        self.b = randint(1, p - 1)
        self.x = secret

    def next(self) -> int:
        self.x = self.a ** 17 * self.x ** 6 + self.a * self.b + self.b ** 2
        self.x %= self.p
        return self.x
    

def main():
    lcg = LCG(p, secret)
    for _ in range(10):
        print(lcg.next())
    print(f"{p = }")

if __name__ == "__main__":
    main()