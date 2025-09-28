# secret value that you don't know
from flag import FLAG
from random import randint
from Crypto.Util.number import getPrime, isPrime

def generate_secure_prime(bits: int) -> int:
    while True:
        p = getPrime(bits)
        if isPrime(p * 2 + 1):
            return 2*p + 1

p = generate_secure_prime(64)
def main():
    print(f"{p = }")
    secret = randint(1, p - 1)
    g = 2 
    public = pow(g, secret, p)
    print(f"{g = }")
    print(f"{public = }")
    a = int(input())
    if pow(g, a, p) == public:
        print(FLAG)
    else:
        print("Try again")

main()