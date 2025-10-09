# secret value that you don't know
from flag import FLAG
from random import randint
from Crypto.Util.number import getPrime

p = getPrime(1024)

# group generator (hopefully)
g = 2 

server_secret = randint(1, p - 1)
server_public = pow(g, server_secret, p)

def main():
    print(f"{p = }")
    print(f"{g = }")
    print(f"Prove your knowledge of the server's secret")
    print(f"Provide such a, b that server_public^a = g ^ b mod p")
    print(f"You only can do this with the knowledge of the server's secret!!!")

    a = int(input())
    if a <= 0 or a >= p:
        print("HACKER GO AWAY!!!!")
        exit()
    b = int(input())
    if b <= 0 or b >= p:
        print("HACKER GO AWAY!!!!")
        exit()
    if pow(server_public, a, p) == pow(g, b, p):
        print(FLAG)
    else:
        print("Try again")


main()
