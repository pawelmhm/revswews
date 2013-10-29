# -*- coding: utf-8 -*-
from hmac import HMAC
from hashlib import sha256
import random
import logging
logging.basicConfig(level=logging.DEBUG) 
logger = logging.getLogger(__name__)

def pbkd(password,salt):
    """ 
    password must be a string in ascii, for some reasons 
    string of type unicode provokes the following error:

    "TypeError: character mapping must return integer, None or unicode"

    TODO: should we check type of string before it gets here?

    """
    return HMAC(str(password),salt,sha256).digest()

def randomSalt(num_bytes):
    return "".join(chr(random.randrange(256)) for i in xrange(num_bytes))

def hash_password(plain_text):
    salt = randomSalt(8)
    for i in xrange(1000):
        hashed_password = pbkd(plain_text,salt)
    return salt.encode("base64").strip() + "," + hashed_password.encode("base64").strip()

def check_password(saved_pass, plain_pass):
    salt,hashed_p = saved_pass.split(",")
    salt=salt.decode("base64")
    hashed_p = hashed_p.decode("base64")
    return hashed_p == pbkd(plain_pass, salt)