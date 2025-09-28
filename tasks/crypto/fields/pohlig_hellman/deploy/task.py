# secret value that you don't know
from flag import FLAG
from random import randint
from sympy import nextprime
from Crypto.Util.number import isPrime
from random import choice

sieve = [2]
while len(sieve) < 10000:
    sieve.append(nextprime(sieve[-1]))

def generate_smooth_prime(bits: int) -> int:
    accumulator = 1
    while accumulator.bit_length() < bits: 
        accumulator *= choice(sieve)
    if isPrime(2 * accumulator + 1):
        return 2 * accumulator + 1
    return generate_smooth_prime(bits)

p = generate_smooth_prime(1024)

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