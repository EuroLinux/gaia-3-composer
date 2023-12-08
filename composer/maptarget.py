import argparse
import logging
import re
import os


def map_target(target: str, args: argparse.Namespace) -> dict[str, dict[str, str]]:
    """
    Map a directory and create a dictionary that lists relevant files and its properties.
    Properties are indexed using unique keys (a set of concatenated file properties).
    Some directory patterns may be skipped using skip_dirs argument.
    Dictionary is returned.

    Args:
        target: target directory to use as the base for repo-dictionary
        args: argparse object (requires: mask, skip_dirs, archs, repo_priority, include_beta, include_extra)

    Returns:
        dictionary consisting of indexed file paths/properties.

    Note:
        A hardcoded 'Packages' directory needs to exist somewhere in the tree
    """

    logging.info(f'Mapping target {target}')
    current_root: dict[str, dict[str, str]] = {}
    if not os.path.exists(target):
        logging.warning(f'Target {target} does not exist! Return empty!')
        return current_root
    abs_path = os.path.abspath(target)
    pattern = re.compile(args.mask)
    for rootdir, dirs, files in os.walk(abs_path):
        if any([sd in rootdir for sd in args.skip_dirs]):
            continue
        for elem_name in files:
            if not pattern.match(elem_name):
                continue
            elem_arch = _set_elem_arch(rootdir, args.archs)
            elem_repo = _set_elem_repo(rootdir, args)
            if elem_arch is None or elem_repo is None:
                continue
            elem_path = os.path.join(rootdir, elem_name)
            m = re.search(f'{target}(.*/(Packages/.*)$)', elem_path)
            if not m:
                continue
            elem_rel = os.path.dirname(m.group(1))
            elem_pkg = os.path.dirname(m.group(2))
            elem_key = f'{elem_repo}:{elem_arch}:{elem_pkg}:{elem_name}'
            current_root[elem_key] = {'elem_name': elem_name, 'elem_abs': abs_path,
                                      'elem_path': elem_path, 'elem_arch': elem_arch,
                                      'elem_repo': elem_repo, 'elem_base': target,
                                      'elem_rel': elem_rel, 'elem_pkg': elem_pkg}
    return current_root


# Internal


def _set_elem_arch(root: str, archs: list[str]) -> 'str|None':
    """
    Output appropriate arch found in root.

    Args:
        root: string containing architecture
        archs: list of archs to seek for (in root)

    Returns:
        Found architecture string (or None)
    """

    for a in archs:
        if a in root:
            return a
    return None


def _set_elem_repo(root: str, args: argparse.Namespace) -> 'str|None':
    """
    Output appropriate repository found in root.

    Args:
        root: string containing architecture
        args: argparse object (requires: repo_priority, include_beta, include_extra)

    Returns:
        Found repository string (or None).

    Note:
        We return 'canonic' repository i.e. for 'AppStream-beta', returned value is still 'AppStream'
    """
    if (not hasattr(args, 'repo_priority') or  # make mypy happy
       not hasattr(args, 'include_beta') or
       not hasattr(args, 'include_extra')):
        return None
    for repo in args.repo_priority:
        search_string = f'/{repo}' if args.include_beta else f'/{repo}/'  # no need for regex here :)
        if search_string in root:
            return repo
        if args.include_extra and repo.lower() in root:
            return repo
    return None
