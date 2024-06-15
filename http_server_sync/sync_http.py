import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup as bs
from rich import print


class Tree:
    pass
    # TODO: should produce nodes


class Node:
    def __init__(self, url):
        self.url = url
        # self.name = ''
        if self.url.endswith('/'):
            self.is_dir = True
            self.is_file = False
        else:
            self.is_dir = False
            self.is_file = True

    def iter(self):
        pass

    def __repr__(self):
        return f'Node(url={self.url})'


class RemoteFile:
    def __init__(self, url):
        self.url = url
        self.path = Path(url.split('/', maxsplit=3)[-1])

    def save(self, context='.', exists_ok=True):
        final_path = context / self.path
        if final_path.exists():
            print(f'  [!] path exists: {final_path}')
            return
        content = requests.get(self.url).content
        final_path.parent.mkdir(exist_ok=True, parents=True)
        final_path.write_bytes(content)
        print(f'  [+] {url} -> {final_path}')

    def __repr__(self):
        return f'RemoteFile(url={self.url})'


def walk(url):
    """walk http files server"""
    response = requests.get(url)
    soup = bs(response.text, "lxml")
    ul = soup.ul
    if ul is None:
        return []
    items = [(url + item.text) for item in ul.find_all('li')]
    remote_files = []
    for item in items:
        # TODO: item as remote here?
        if item.endswith('/'):
            children = walk(item)
            remote_files.extend(children)
        else:
            remote = RemoteFile(item)
            # print(remote)
            remote_files.append(remote)
    return remote_files


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print('usage:\n    python sync_http.py <http-server-url>')
        sys.exit()
    url = args[0]
    remote_files = walk(url)
    for index, remote in enumerate(remote_files, start=1):
        print(f'{index}) {remote}')
        remote.save()
