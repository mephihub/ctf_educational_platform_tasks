# secret value that you don't know
from flag import FLAG
from random import randint
from Crypto.Util.number import getStrongPrime

p = getStrongPrime(1024)
q = getStrongPrime(1024)
n = p * q
def main():
    print(f"{n = }")
    print(f"{p = }")
    print(f"{q = }")
    while True:
        random_number = randint(1, n - 1)
        print(f"{random_number = }")

        root = int(input())
        if  pow(root, 2, n) == random_number:
            print(FLAG)
            exit()
        else:
            print("Try again")

if __name__ == "__main__":
    main()