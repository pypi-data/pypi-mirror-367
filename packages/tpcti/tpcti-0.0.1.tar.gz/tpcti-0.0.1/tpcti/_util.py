import time
import random

def gen_threading_id():
    return str(
        int(format(int(time.time() * 1000), "b") +
            ("0000000000000000000000" +
             format(int(random.random() * 4294967295), "b"))[-22:], 2)
    )

def AnkLaDontCry(cookie_str):
    cookies = {}
    cookie_items = cookie_str.split(';')
    for item in cookie_items:
        parts = item.strip().split('=', 1)
        if len(parts) == 2:
            cookies[parts[0].strip()] = parts[1].strip()
    return cookies
    
   
