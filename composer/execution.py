import os
import sys
import logging
import threading
import typing as t

from composer.composer_types import CommandsDataType


def create_local_repo_script(repo: dict[str, dict[str, str]], output_file: str) -> None:
    """
    Outputs a bash script file that creates a mock repository locally.

    Args:
        repo: A dictionary representing a repository (to mock)
        output_file: destination filename to write the script to (will overwrite)
    """

    mkdirs = []
    touches = []
    for repo_elem in repo.values():
        directory = repo_elem['elem_rel']
        path = os.path.join(directory, repo_elem['elem_name'])
        mkdirs.append(f'mkdir -p {directory}\n')
        touches.append(f'touch {path}\n')
    mkdirs = sorted(list(set(mkdirs)))
    touches = sorted(list(set(touches)))
    with open(output_file, 'w') as savefile:
        savefile.write('#!/bin/bash\n')
        savefile.writelines(mkdirs)
        savefile.writelines(touches)


def apply_rules(cmds: CommandsDataType, threads: int, real_run: bool = False) -> None:
    """
    Apply collected command rules.

    Args:
        cmds: rule dictionary to apply
        threads: number of threads to execute in (applied only if real_run is True)
        real_run: if True, an actual execution will be carried out (otherwise we just log commands)
    """

    cmds['mkdir'] = []
    for _, dst in [*cmds['ln'], *cmds['mv']]:
        outdir = os.path.dirname(dst)
        if not os.path.exists(outdir):
            cmds['mkdir'].append(outdir)
    cmds['mkdir'] = list(set(cmds['mkdir']))
    if real_run:
        if threads > 1:
            _run_in_threads(cmds, threads)
        else:
            _run_single_thread(cmds)
    else:
        for v in cmds['mkdir']:
            logging.info(f'os.makedirs("{v}", exist_ok=True)')
        for src, dst in cmds['mv']:
            logging.info(f'os.rename("{src}", "{dst}")')
        for src, dst in cmds['ln']:
            logging.info(f'os.link("{src}", "{dst}")')
            if os.path.exists(dst):
                src_stat = os.stat(src)
                dst_stat = os.stat(dst)
                if dst_stat.st_dev != src_stat.st_dev:
                    logging.error(f'Sorry, we require {src} and {dst} to be on the same device')
                    sys.exit(1)
                if dst_stat.st_ino != src_stat.st_ino:
                    logging.info(f'os.remove("{dst}")')
                    logging.info(f'os.link("{src}", "{dst}")')


def _run_single_thread(cmds: CommandsDataType) -> None:
    """
    Executes system commands in a single thread.

    Args:
        cmds: commands to execute
    """
    for v in cmds['mkdir']:
        os.makedirs(v, exist_ok=True)
    for src, dst in cmds['mv']:
        os.rename(src, dst)
    for src, dst in cmds['ln']:
        _create_link(src, dst)


def _run_in_threads(cmds: CommandsDataType, thread_num: int) -> None:
    """
    Executes system commands in multiple threads.

    Args:
        cmds: commands to execute
        thread_num: number of threads to start (i.e. evenly split cmds list into)
    """
    for v in cmds['mkdir']:
        os.makedirs(v, exist_ok=True)
    thread_list = []
    splitlist = _prep_for_threads(cmds['mv'], thread_num)
    for chunk in splitlist:
        t = threading.Thread(target=_apply_2arg_fun, args=(chunk, os.rename))
        thread_list.append(t)
        t.start()
    splitlist = _prep_for_threads(cmds['ln'], thread_num)
    for chunk in splitlist:
        t = threading.Thread(target=_apply_2arg_fun, args=(chunk, _create_link))
        thread_list.append(t)
        t.start()
    for t in thread_list:
        t.join()


def _prep_for_threads(lst: list[tuple[str, str]], thread_num: int) -> list[list[tuple[str, str]]]:
    """
    Split list evenly into thread_num parts. For threaded execution.
    What happens here is best demonstrated on an example:
    Let:
    list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    We want to split it into 4 [roughly] equal parts (4 threads):
    len(list) = 11, thread_num = 4
    divmod(11, 4) = (2, 3) i.e. dividing by 4 gives 2[-element lists] and 3 elements remaining.
    So to get 4 such lists (one for each thread) out of our main list we would have to
    split elements into lists of 2 (d) (division) and add 3 (r) elements somewhere (remainder).
    Now the comprehension:
    We take parts indexed with range (i) - for four threads i = 0, 1, 2, 3.
    So: i = [0, 1, 2, 3], d = 2, r = 3
    ------------------ [i*d+min(i, r):(i+1)*d+min(i+1, r)]
    First list  (i=0): [0*2+min(0, 3):(0+1)*2+min(0+1, 3)] = lst[0:3]  = [1,  2,  3]
    Second list (i=1): [1*2+min(1, 3):(1+1)*2+min(1+1, 3)] = lst[3:6]  = [4,  5,  6]
    Third list  (i=2): [2*2+min(2, 3):(2+1)*2+min(2+1, 3)] = lst[6:9]  = [7,  8,  9]
    Fourth list (i=3): [3*2+min(3, 3):(3+1)*2+min(3+1, 3)] = lst[9:11] = [10, 11]
    The result then becomes: [ [1,2,3], [4,5,6], [7,8,9], [10,11] ]
    In essence:
    - We set starting point to the "complete list" (d) point (with lists of two this is 0, 2, 4)
    - We set the ending point at the next end (next d) (with lists of two this is 2, 4, 6)
    - Then we offset these values by 1 for as many times as there are remainders (r) (the min() part)
      (enlarging first (r) lists by 1 and moving next starting index forward by 1)

    Args:
        lst: list to split
        thread_num: number of parts.

    Returns:
        A list of `thread_num` lists that each contain roughly the same number of elements.
    """

    d, r = divmod(len(lst), thread_num)
    return [lst[i*d+min(i, r):(i+1)*d+min(i+1, r)] for i in range(thread_num)]


def _apply_2arg_fun(lst: list[tuple[str, str]], fun: t.Callable[[str, str], None]) -> None:
    """
    Execute function on list. function has to take in 2 arguments.
    Args:
        lst: list of tuples (arguments to function)
        fun: function to executeon each list element
    """
    for src, dst in lst:
        fun(src, dst)


def _create_link(src: str, dst: str) -> None:
    """
    Create a hardlink.
    If link already exists -> replace it only if different than original

    Args:
        src: source file
        dst: destination file
    """

    try:
        os.link(src, dst)
    except FileExistsError:
        src_stat = os.stat(src)
        dst_stat = os.stat(dst)
        if dst_stat.st_dev != src_stat.st_dev:
            logging.error(f'Sorry, we require {src} and {dst} to be on the same device')
            sys.exit(1)
        if dst_stat.st_ino != src_stat.st_ino:
            os.remove(dst)
            os.link(src, dst)
