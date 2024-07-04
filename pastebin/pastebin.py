import sys
import os
from pathlib import Path
import requests
import lxml
from urllib.parse import urljoin
from bs4 import BeautifulSoup as bs
from rich import print

"""
useful:
    https://stackoverflow.com/questions/47384652/python-write-replaces-n-with-r-n-in-windows
    https://pastebin.com/doc_api
"""


def write_file(filename, text, mode='w'):
    """write to file"""
    try:
        with open(filename, mode, newline='\n', encoding='utf-8') as f:
            f.write(text)
    except Exception as err:
        print('[x] Failed to write to file: {}, err: {}'.format(filename, err))
    return None
    
    
def collect_pastebin_archives(keyword):
    """collect pastebin archives urls"""
    pastebin_archive = 'https://pastebin.com/archive/{}'.format(keyword)
    pastebin_base = 'https://pastebin.com'
    response = requests.get(pastebin_archive)
    soup = bs(response.text, "lxml")
    maintable = soup.find('table', {'class': 'maintable'})
    rows = maintable.tbody.find_all('tr')
    rows = rows[1:]
    href_last_parts = [(row.td.a.text, row.td.a['href']) for row in rows]
    full_urls = [(title, urljoin(pastebin_base, part)) for (title, part) in href_last_parts]
    raw_urls = [(title, '{}{}{}'.format(pastebin_base, '/raw', part)) for (title, part) in href_last_parts]
    return raw_urls
    
    
if __name__ == "__main__":
    os.chdir(str(Path(__file__).parent))
    
    # ********** specify keyword **********
    # keyword, extension = 'python', 'py
    # keyword, extension = 'email', 'txt'
    keyword, extension = 'arduino', 'ino'
    
    # ********** collect python archives **********
    raw_urls = collect_pastebin_archives(keyword)
    directory = Path(keyword)
    directory.mkdir(exist_ok=True)
    already_collected = os.listdir(directory)
    for title, url in raw_urls:
        try:
            print('{} -> {}'.format(url, title))
            part = url.rsplit('/', 1)[-1]
            filename = '{}.{}'.format(part, extension)
            if filename in already_collected:
                print('    [cyan][*] already collected')
                continue
            path = directory.joinpath(filename)
            response = requests.get(url)
            write_file(path, response.text)
            print('    [green][+] collected')
        except KeyboardInterrupt:
            print('    [yellow]\[x] broken by user')
            break
            