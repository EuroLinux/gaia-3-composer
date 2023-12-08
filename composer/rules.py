import os
import re
import json
import logging
import argparse
import composer.util as util
import composer.maptarget as maptarget

from composer.types import CommandsDataType


def create_move_commands_for_debug_packages(repo: dict[str, dict[str, str]], all_dir: str,
                                            debug_dir: str) -> list[tuple[str, str]]:
    """
    This function creates move rules for 'debuginfo' and debugsource packages.

    Args:
        repo: repository dict to apply to.
        all_dir: string indicating from which directory to move files (e.g. '/all/')
        debug_dir: string indicating to which directory to move (e.g. '/debug/')

    Returns:
        A list of src-dst tuples to later append to some section of commands to execute (possibly 'mv')
    """

    move_commands = []
    for repo_elem in repo.values():
        if (all_dir in repo_elem['elem_rel'] and
            ('-debuginfo-' in repo_elem['elem_name'] or
             '-debugsource-' in repo_elem['elem_name'])):
            out_repo = repo_elem['elem_rel'].replace(all_dir, debug_dir)
            out_path = os.path.join(repo_elem['elem_abs'], out_repo, repo_elem['elem_name'])
            move_commands.append((repo_elem['elem_path'], out_path))
    return move_commands


def create_ruleset(args: argparse.Namespace) -> CommandsDataType:
    """
    Create rules dictionary. This dictionary is a set of src-dst tuples where src is applied a command to create dst.
    For example tuple (file1.txt, file2.txt) may be placed under the 'mv' key.
    Meaning that, upon execution, file1.txt will be moved as file2.txt

    Args:
        args: argparse object (requires: src_repo, dst_repo, move_debug, all_dir, debug_dir, archs, repo_priority,
                                         os_dir, replacements, custom_rules_file + <map_target requirements>)

    Returns:
        commands dictionary containing src-dst tuples placed under desired [command] key.
    """

    cmds: CommandsDataType = {'mkdir': [], 'mv': [], 'ln': []}
    mapped_src = maptarget.map_target(args.src_repo, args)
    mapped_dst = maptarget.map_target(args.dst_repo, args)
    if not mapped_src or not mapped_dst:
        logging.warning('One or both maps are empty. Return empty.')
        return cmds
    if args.move_debug:
        cmds['mv'] = create_move_commands_for_debug_packages(mapped_dst, args.all_dir, args.debug_dir)
    for mapped_src_key in mapped_src.keys():
        src_arch, src_variable_key = mapped_src_key.split(':', 2)[1:3]
        for current_arch in [src_arch] + args.archs:  # place "our" arch first
            for current_repo in args.repo_priority:  # try out repositories in order of importance
                cmd = _append_rule(mapped_src, mapped_dst, mapped_src_key, src_variable_key, current_repo,
                                   current_arch, args.all_dir, args.os_dir, args.replacements)
                if cmd:
                    cmds['ln'].append(cmd)
                    break
            if cmd:  # noarchs will hit a couple of times, therefore as soon as we get a hit - we break
                break
    if args.custom_rules_file:
        cmds['ln'] += append_custom_rules(mapped_dst, args)
    return cmds


def append_custom_rules(repo: dict[str, dict[str, str]], args: argparse.Namespace) -> list[tuple[str, str]]:
    """
    Create additional rules for repository based on created configuration file

    Args:
        repo: repository to create additional rules for
        args: argparse object (requires: custom_rules_file, all_dir, os_dir)

    Returns:
        src-dst tuples to later append to relevant command section
    """

    try:
        return _append_custom_rules_json(repo, args.custom_rules_file, args.all_dir, args.os_dir)
    except json.decoder.JSONDecodeError:
        return _append_custom_rules_short(repo, args.custom_rules_file, args.all_dir, args.os_dir)


def _append_custom_rules_json(repo: dict[str, dict[str, str]], rulefile:
                              str, all_dir: str, os_dir: str) -> list[tuple[str, str]]:
    """
    Helper additional rules creator to parse json-style config files.

    Args:
        repo: repository to create additional rules for
        rulefile: file with additional rules
        all_dir: /all/ directory name
        os_dir: /os/ directory name

    Returns:
        A list of src-dst tuples to later append to some section of commands to execute (possibly 'ln')
    """
    appended_cmds = []
    rulelist = util.load_from_json(rulefile)
    for rule in rulelist:
        pattern = re.compile(f"{rule['src_repo']}:{rule['src_arch']}:.*?:{rule['file_pattern']}")
        for elem_key, repo_elem in repo.items():
            if all_dir not in repo_elem['elem_path']:
                continue
            if not pattern.match(elem_key):
                continue
            output_path = repo_elem['elem_path'].replace(all_dir, os_dir)
            if rule.get('dst_repo'):
                output_path = output_path.replace(repo_elem['elem_repo'], rule['dst_repo'].strip())
            if rule.get('dst_arch'):
                output_path = output_path.replace(repo_elem['elem_arch'], rule['dst_arch'].strip())
            appended_cmds.append((repo_elem['elem_path'], output_path))
    return appended_cmds


def _append_custom_rules_short(repo: dict[str, dict[str, str]], rulefile: str,
                               all_dir: str, os_dir: str) -> list[tuple[str, str]]:
    """
    Helper additional rules creator to parse condensed config files.

    Args:
        repo: repository to create additional rules for
        rulefile: file with additional rules
        all_dir: /all/ directory name
        os_dir: /os/ directory name

    Returns:
        A list of src-dst tuples to later append to some section of commands to execute (possibly 'ln')
    """
    appended_cmds = []
    rules = []
    with open(rulefile) as fh:
        content = fh.readlines()
    for line in content:
        rule = line.split('->')
        rules.append((rule[0].strip(), rule[1].strip()))
    for file_pattern, repo_archs in rules:
        repo_arch_list = repo_archs.split('/')
        pattern = re.compile(f"{repo_arch_list[0]}:.*:{file_pattern}")
        for elem_key, repo_elem in repo.items():
            m = pattern.match(elem_key)
            if m:
                if all_dir not in repo_elem['elem_path']:
                    continue
                output_path = repo_elem['elem_path'].replace(all_dir, os_dir)
                if len(repo_arch_list) > 1:
                    output_repo = repo_arch_list[1].split(':')[0].strip()
                    output_path = output_path.replace(repo_elem['elem_repo'], output_repo)
                    output_arch = repo_arch_list[1].split(':')[1].strip()
                    output_path = output_path.replace(repo_elem['elem_arch'], output_arch)
                appended_cmds.append((repo_elem['elem_path'], output_path))
    return appended_cmds


def _append_rule(src_repo: dict[str, dict[str, str]], dst_repo: dict[str, dict[str, str]], mapped_src_key: str,
                 variable_key: str, current_repo: str, current_arch: str,
                 all_dir: str, os_dir: str, replacements: dict[str, str]) -> 'tuple[str, str]|None':
    """
    Create a link rule between src-repo file and dst-repo file.
    Source repository is a repository we want to model.
    Destinaion repository is the repository we want to have modeled based on source.
    "Modeling" here means linking appropriate files from (dst's) /all/ directory to dst's /os/ directory.
    These links' placement is determined by looking at the placement of the file in the source directory.

    Args:
        src_repo: repository dict to model after
        dst_repo: repository dict that is modeled
        mapped_src_key: key identifying file in source repository
        variable_key: partial key from which to create complete keys (for search)
        current_repo: repository to look into (add to variable_key)
        current_arch: arch to look into (add to variable key)
        all_dir: /all/ directory name
        os_dir: /os/ directory name
        replacements: replacement dict for repository names

    Returns:
        src-dst tuple (to later add to command list)
    """

    ret_cmd = None
    try:
        search_key = f'{current_repo}:{current_arch}:{variable_key}'  # create search key
        if dst_repo[search_key]:  # test if such key exists - i.e. the first most important repo hits
            # in the file path relative to base replace destination repository with repository found in source
            target_repo = src_repo[mapped_src_key]["elem_repo"]
            if replacements and replacements.get(target_repo):
                target_repo = replacements[target_repo]
            output_repo = dst_repo[search_key]['elem_rel'].replace(f'{current_repo}/', f'{target_repo}/')
            # replace destination architecture with architecture found in source
            output_repo = output_repo.replace(f'{current_arch}/', f'{src_repo[mapped_src_key]["elem_arch"]}/')
            output_repo = output_repo.replace(all_dir, os_dir)
            output_path = os.path.join(dst_repo[search_key]['elem_abs'], output_repo, dst_repo[search_key]['elem_name'])
            # linking dest elem_path (full path to file) to (os) path created from source's repository
            ret_cmd = (dst_repo[search_key]['elem_path'], output_path)
    except KeyError:
        pass
    return ret_cmd
