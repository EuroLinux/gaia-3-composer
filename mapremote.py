import logging
import urllib.request
from bs4 import BeautifulSoup


class TreeElement:

    def __init__(self, elem_name, elem_type, elem_base, elem_rel=''):
        self.elem_name = elem_name
        self.elem_type = elem_type
        self.elem_base = elem_base
        self.elem_rel = elem_rel
        self.parent_to = {}


def write_repo_tree_shell(baseurl: str, output_file: str) -> None:
    """
    Models baseurl repository and writes a bash script that is able to
    locally recreate a mock of that repository (using mkdirs and touches).
    Args:
        baseurl: url of a remote repository
        output_file: outputfile to write the script to (will overwrite)
    """

    results = []
    repo = _create_mapped_repo(baseurl)
    (mkdirs, touches) = _debug_recreate_repo_tree(repo, [], [])
    results += mkdirs
    results += touches
    with open(output_file, 'w') as savefile:
        savefile.write('#!/bin/bash\n')
        for line in results:
            savefile.write(line+'\n')

# Internal


def _create_mapped_repo(baseurl: str) -> 'TreeElement|None':
    root = TreeElement('/', 'dir', baseurl)
    if root:
        return _recursive_map_target(root, baseurl)
    else:
        return None


def _recursive_map_target(current_root: 'TreeElement|None', base: str, rel: str = '') -> 'TreeElement|None':
    current_root = _map_target(current_root, base, rel)
    if not current_root:
        return None
    for sub in current_root.parent_to.values():
        if sub.elem_type == 'dir':
            sub_url = rel + '/' + sub.elem_name if rel and rel[-1] != '/' else rel + sub.elem_name
            current_root.parent_to[sub.elem_name] = _recursive_map_target(sub, base, sub_url)
    return current_root


def _debug_recreate_repo_tree(repo_root: 'TreeElement|None', mkdirs: list[str],
                              touches: list[str]) -> tuple[list[str], list[str]]:
    if repo_root is None:
        return ([], [])
    for r in repo_root.parent_to.values():
        if r and r.parent_to:
            _debug_recreate_repo_tree(r, mkdirs, touches)
        if r and r.elem_type == 'dir':
            mkdirs.append('mkdir -p ' + r.elem_rel + r.elem_name)
        if r and r.elem_type == 'file':
            touches.append('touch ' + r.elem_rel + r.elem_name)
    return (mkdirs, touches)


def _map_target(current_root: 'TreeElement|None', base: str, rel: str = '') -> 'TreeElement|None':
    if current_root is None:
        return None
    target = base + '/' + rel if base[-1] != '/' else base + rel
    logging.info(f'Mapping remote target {target}')
    try:
        with urllib.request.urlopen(target) as response:
            html = response.read()
    except (urllib.error.HTTPError, ValueError):
        return None
    soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
    for packages in soup.find_all('a'):
        href = packages.get('href')
        if href == '../':
            continue
        if href[-1] == '/':
            element = TreeElement(href, 'dir', base, rel)
            current_root.parent_to[element.elem_name] = element
        else:
            element = TreeElement(href, 'file', base, rel)
            current_root.parent_to[element.elem_name] = element
    return current_root
