from hmac import HMAC
from hashlib import sha256
import random

def pbkd(password,salt):
    return HMAC(password,salt,sha256).digest()

def randomSalt(num_bytes):
    return "".join(chr(random.randrange(256)) for i in xrange(num_bytes))

def hash_password(plain_text):
    salt = randomSalt(8)
    for i in xrange(1000):
        hashed_password = pbkd(plain_text,salt)
    return salt.encode("base64").strip() + "," + hashed_password.encode("base64").strip()

def check_password(saved_pass,plain_pass):
    salt,hashed_p = saved_pass.split(",")
    salt=salt.decode("base64")
    hashed_p = hashed_p.decode("base64")
    return hashed_p == pbkd(plain_pass,salt)


#print hash_password("sssss")
