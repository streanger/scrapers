import os
from itertools import count
from typing import NamedTuple
from pathlib import Path
import requests
import pandas as pd
from rich import print
from bs4 import BeautifulSoup as bs


class Row(NamedTuple):
    uploaded: str
    duration: str
    title: str
    
    
def script_path():
    """set current path, to script path"""
    current_path = str(Path(__file__).parent)
    os.chdir(current_path)
    return current_path
    
    
def parse_bitchute(text):
    """parse single response website"""
    soup = bs(text, 'lxml')
    table = soup.find('div', {'class': 'channel-videos-list'})
    rows = table.find_all('div', {'class': 'channel-videos-container'})
    parsed_rows = []
    for index, row in enumerate(rows, start=1):
        title = row.find('div', {'class': 'channel-videos-title'}).text.strip()
        duration = row.find('span', {'class', 'video-duration'}).text
        uploaded = row.find('div', {'class', 'channel-videos-details'}).text.strip()
        parsed = Row(uploaded=uploaded, duration=duration, title=title)
        parsed_rows.append(parsed)
    return parsed_rows
    
    
def parse_bitchute_extend(text):
    """parse extended response"""
    soup = bs(text, 'lxml')
    rows = soup.find_all('div', {'class': 'channel-videos-container'})
    parsed_rows = []
    for index, row in enumerate(rows, start=1):
        title = row.find('div', {'class': 'channel-videos-title'}).text.strip()
        duration = row.find('span', {'class', 'video-duration'}).text
        uploaded = row.find('div', {'class', 'channel-videos-details'}).text.strip()
        parsed = Row(uploaded=uploaded, duration=duration, title=title)
        parsed_rows.append(parsed)
    return parsed_rows
    
    
def prepare_data_and_headers(session, offset=25):
    """prepare data and headers for extended post request
    jump every 25 items
    """
    csrftoken = session.cookies['csrftoken']
    data = {
        'csrfmiddlewaretoken': csrftoken,
        'name': None,
        'offset': offset,
    }
    headers = {
        "Authority": "www.bitchute.com",
        "Method": "POST",
        "Path": f"/channel/{CHANNEL}/extend/",
        "Scheme": "https",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Length": "101",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": f"csrftoken={csrftoken}",
        "Origin": "https://www.bitchute.com",
        "Referer": f"https://www.bitchute.com/channel/{CHANNEL}/",
        "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    return data, headers


script_path()
CHANNEL = 'bluewater'

# ***** init page *****
input('go ')
rows_container = []
with requests.Session() as session:
    url = f'https://www.bitchute.com/channel/{CHANNEL}/'
    response = session.get(url)
    parsed_rows = parse_bitchute(response.text)
    rows_container.extend(parsed_rows)
    print()
    for index, row in enumerate(parsed_rows, start=1):
        print(f'{index:>2}) {row.uploaded} -> {row.duration:>7} -> {row.title}')
        
    # ***** next pages *****
    for offset in count(25, 25):
        extend_url = f'https://www.bitchute.com/channel/{CHANNEL}/extend/'
        data, headers = prepare_data_and_headers(session, offset=offset)
        response = session.post(extend_url, headers=headers, data=data)
        text = response.json()['html']
        parsed_rows = parse_bitchute_extend(text)
        rows_container.extend(parsed_rows)
        if not parsed_rows:
            print('end reached...')
            break
        print()
        for index, row in enumerate(parsed_rows, start=1):
            print(f'{index:>2}) {row.uploaded} -> {row.duration:>7} -> {row.title}')
            
# ***** save collected data *****
df = pd.DataFrame(rows_container)
df.index += 1
out = f'bitchute-{CHANNEL}.csv'
df.to_csv(out)
