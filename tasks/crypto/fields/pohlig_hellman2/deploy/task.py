# secret value that you don't know
from flag import FLAG
from random import randint
from Crypto.Util.number import getPrime, bytes_to_long

SECRET = bytes_to_long(FLAG)
p = getPrime(1024)

def main():
    print(f"{p = }")
    print(pow(2, SECRET, p))

main()