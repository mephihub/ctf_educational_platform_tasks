# secret value that you don't know
from flag import FLAG
from random import randint

p = 257

def rand_scalar(length: int) -> list[int]:
    return [randint(0, p - 1) for _ in range(length)]

def scalar_mul(a, b, p) -> int:
    return sum(a_i * b_i for a_i, b_i in zip(a, b)) % p

def main():
    while True:
        a = rand_scalar(len(FLAG))
        print(scalar_mul(a, list(FLAG), p))
        print(a)

        b = int(input("Option [1] exit, [ANY OTHER] continue: "))
        if b == 1:
            exit()

main()