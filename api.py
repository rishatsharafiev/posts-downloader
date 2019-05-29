import multiprocessing
import threading
import sqlite3
import random
import json

from urllib.request import urlopen

api_addr = ['http://188.127.251.4:8240', 'http://188.127.251.49:8240']

process_lock = multiprocessing.Lock()
threading_lock = threading.Lock()

connection = sqlite3.connect("db.sqlite3", check_same_thread=False)
cursor = connection.cursor()
# cursor.execute("""DROP TABLE IF EXISTS hits""")
cursor.execute("""CREATE TABLE IF NOT EXISTS hits(ip varchar(255), request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

def retrive_post(post_id):
    global multiprocessing_lock, threading_lock, connection, cursor

    current_ip = None

    try:
        process_lock.acquire()
        threading_lock.acquire()

        cursor.execute("""SELECT ip FROM hits WHERE request_time > datetime('now', '-60 seconds') GROUP BY ip HAVING COUNT(request_time) >= 30;""")
        hot_ips = set([row[0] for row in cursor.fetchall()])
        cold_ips = list(set(api_addr).difference(hot_ips))
        
        if len(cold_ips):
            current_ip = random.choice(cold_ips)
            prepared_statements = (current_ip,)
            cursor.execute("""INSERT INTO hits(ip) VALUES (?)""", prepared_statements)
            connection.commit()
        else:
            exp = Exception('All proxies are hot')
            exp.status_code = 1
            raise exp
    finally:
        threading_lock.release()
        process_lock.release()

    if current_ip:
        with urlopen(f'{current_ip}/posts/{post_id}') as response:
            return json.loads(response.read())
