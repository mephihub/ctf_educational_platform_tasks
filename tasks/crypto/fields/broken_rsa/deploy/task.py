# secret value that you don't know
from flag import FLAG
from random import randint
from Crypto.Util.number import getStrongPrime

def bytes_to_long(b: bytes) -> int:
    return int.from_bytes(b, 'big')

def get_prime(nbits: int) -> int:
    while True:
        p = getStrongPrime(nbits)
        if p % 4 == 3:
            return p

p = get_prime(1024)
q = get_prime(1024)
e = 0x10001 # default RSA public exponent
e *= 2 # hehehehehe
n = p * q

try:
    d = pow(e, -1, (p - 1) * (q - 1))
    exit()
except:
    print("How are you going to solve this?")


def main():
    print(f"{n = }")
    print(f"{p = }")
    print(f"{q = }")
    print(f"{e = }")
    print(pow(bytes_to_long(FLAG), e, n))

if __name__ == "__main__":
    main()