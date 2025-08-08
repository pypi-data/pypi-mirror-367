import json
import urllib.request as request
import unicodedata
from hashlib import sha256
import re

def make_request(url, **kwargs):
    body = kwargs.get('body', {})
    method = kwargs.get('method', 'GET')
    headers = kwargs.get('headers', {})

    data = json.dumps(body).encode()
        
    req = request.Request(url, data=data, headers=headers, method=method)
    return request.urlopen(req)

# This hashes a data structure and returns its sha256sum.
def identify(data):
    data_string = json.dumps(data, separators=(',',':'), ensure_ascii=False)
    return sha256(data_string.encode()).hexdigest()

# This provides a filesafe name from any string passed to it.
def slugify(string):
    slug = unicodedata.normalize('NFKD', string)
    slug = slug.encode('ascii', 'ignore').lower().decode()
    slug = re.sub(r'[^a-z0-9._]+', '-', slug).strip('-')
    slug = re.sub(r'[-]+', '-', slug)
    return slug

def print_banner():

    YELLOW = '[38;5;11m'
    RESET  = '[0m'

    print('')
    print(f'  ▄▀▀▀▄ {YELLOW} ▄▀▀▀▄  {RESET}█    ▄▀▀▀▄ █▀▀▀▄')
    print(f'  ▀▄▄▄  {YELLOW}█  ▄  █ {RESET}█    █▄▄▄█ █▄▄▄▀')
    print(f'  ▄   █ {YELLOW}▀▄   ▄▀ {RESET}█    █   █ █   █')
    print(f'   ▀▀▀  {YELLOW}  ▀▀▀   {RESET}▀▀▀▀ ▀   ▀ ▀   ▀')
    print('')


