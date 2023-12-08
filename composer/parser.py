import argparse
from distutils.util import strtobool


def parse_args(argv: list[str]) -> argparse.Namespace:
    """
    Parse arguments

    Args:
        argv: argument list

    Returns:
        argparse Namespace object
    """
    parser = _create_parser()
    args = parser.parse_args(argv)
    if hasattr(args, 'archs') and args.archs is not None:
        args.archs = args.archs.split(',')
    if hasattr(args, 'repo_priority') and args.repo_priority is not None:
        args.repo_priority = args.repo_priority.split(',')
    if hasattr(args, 'skip_dirs') and args.skip_dirs is not None:
        args.skip_dirs = args.skip_dirs.split(',')
        for i in range(len(args.skip_dirs)):
            args.skip_dirs[i] = _add_end_slashes(args.skip_dirs[i])
    if hasattr(args, 'all_dir') and args.all_dir is not None:
        args.all_dir = _add_end_slashes(args.all_dir)
    if hasattr(args, 'os_dir') and args.os_dir is not None:
        args.os_dir = _add_end_slashes(args.os_dir)
    if hasattr(args, 'debug_dir') and args.debug_dir is not None:
        args.debug_dir = _add_end_slashes(args.debug_dir)
    if hasattr(args, 'replacements') and args.replacements is not None:
        args.replacements = _process_replacements(args.replacements)
    return args


def _create_parser() -> argparse.ArgumentParser:
    """
    Manages help menu/argument parser
    """
    parser = argparse.ArgumentParser(description='Help for composer',
                                     formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='action', required=True, help='Available commands')
    parser_direct = subparsers.add_parser('direct', help='create commands based on repos and execute (or dryrun)')
    parser_fromrules = subparsers.add_parser('fromrules', help='load commands from file and execute (or dryrun)')
    parser_saverules = subparsers.add_parser('saverules', help='create commands and save output (no execution)')
    parser_maprepo = subparsers.add_parser('maprepo', help='map repo and store to json file')
    parser_fakerepo = subparsers.add_parser('fakerepo', help='create fake-repo creation script (for testing)')
    parser_fakeremote = subparsers.add_parser('fakeremote',
                                              help='create fake remote repo creation script (for testing)')
    for sub in parser_direct, parser_saverules, parser_maprepo:
        sub.add_argument('-p', '--repo_priority', help='Priority for repos (which is to be taken first)' +
                                                       'e.g. AppStream,BaseOS,HighAvailability (no spaces!)\n' +
                                                       '(default: %(default)s)',
                         type=str, required=False,
                         default='BaseOS,AppStream,PowerTools,HighAvailability,ResilientStorage')
        sub.add_argument('-a', '--archs', help='Recognized architectures to choose from ' +
                                               'e.g. x86_64,noarch,i686  (no spaces!)\n' +
                                               '(default: %(default)s)',
                         type=str, required=False, default='x86_64,i686,aarch64,noarch')
        sub.add_argument('-S', '--skip_dirs', help='Do not include (skip) patterns' +
                                                   'e.g. debug,os (no spaces!)\n' +
                                                   '(default: %(default)s)',
                         type=str, required=False, default='debug,os')
        sub.add_argument('-M', '--mask', help='A mask for files of relevance (default: %(default)s)',
                         type=str, required=False, default='.*\.rpm$')
        sub.add_argument('-b', '--include_beta',
                         help='include beta dirs (e.g. AppStream-beta/)\n' +
                              '(default: %(default)s)',
                         type=lambda x: bool(strtobool(x)), required=False, default=False)
        sub.add_argument('-e', '--include_extra',
                         help='include additional dirs (e.g. rhel-9-for-x86_64-baseos-rpms/)\n' +
                              '(default: %(default)s)',
                         type=lambda x: bool(strtobool(x)), required=False, default=False)
    for sub in parser_direct, parser_saverules:
        sub.add_argument('-s', '--src_repo', help='src repo (what we want to model)',
                         type=str, required=True)
        sub.add_argument('-d', '--dst_repo', help='dst repo (what we want to modify)',
                         type=str, required=True)
        sub.add_argument('-m', '--move_debug', help='move debug packages out of destination repo\n' +
                                                    '(default: %(default)s)',
                         type=lambda x: bool(strtobool(x)), required=False, default=True)
        sub.add_argument('-O', '--os_dir', help='name of the /os/ directory (default: %(default)s)',
                         type=str, required=False, default='os')
        sub.add_argument('-D', '--debug_dir', help='name of the /debug/ directory (default: %(default)s)',
                         type=str, required=False, default='debug')
        sub.add_argument('-A', '--all_dir', help='name of the /all/ directory (default: %(default)s)',
                         type=str, required=False, default='all')
        sub.add_argument('-C', '--custom_rules_file', help='Custom rules file with additional hardlinks. ' +
                                                           '(default: %(default)s)',
                         type=str, required=False, default=None)
        sub.add_argument('-R', '--replacements', help='Replacement list for repository names.\n' +
                                                      'It is of format from_repo/to_repo' +
                                                      'e.g. CodeReady/PowerTools,Devel/BaseOS (no spaces!)',
                         type=str, required=False)
    for sub in parser_direct, parser_fromrules:
        sub.add_argument('-r', '--real_run', help='real_run (default: %(default)s)',
                         type=lambda x: bool(strtobool(x)), required=False, default=False)
        sub.add_argument('-T', '--threads', help='run in T threads (default: %(default)s)',
                         type=int, required=False, default=1)
    parser_fromrules.add_argument('-i', '--input_file', help='Infile to load repository commands from',
                                  type=str, required=True)
    parser_saverules.add_argument('-o', '--output_file', help='Outfile to save repository commands to',
                                  type=str, required=True)
    parser_maprepo.add_argument('-s', '--src_repo', help='src repo (what we want to model)',
                                type=str, required=True)
    parser_maprepo.add_argument('-o', '--output_file', help='Map out file (as json)',
                                type=str, required=True)
    for sub in parser_fakerepo, parser_fakeremote:
        sub.add_argument('-b', '--bash_output', help='Bash output script (fake repo creation script)',
                         type=str, required=True)
    parser_fakerepo.add_argument('-i', '--input_file', help='File with repository map',
                                 type=str, required=True)
    parser_fakeremote.add_argument('-i', '--input_url', help='Repository url',
                                   type=str, required=True)
    return parser


def _add_end_slashes(tested: str) -> str:
    """
    Add slashes in front and at the end of the string.
    Used to make directory strings used in composer uniform (e.g. os, os/, /os, /os/ will all translate to: /os/)

    Args:
        tested: tested string

    Returns:
        uniformed directory string
    """
    if tested[0] != '/':
        tested = '/' + tested
    if tested[-1] != '/':
        tested = tested + '/'
    return tested


def _process_replacements(replacements: str) -> dict[str, str]:
    """
    Model replacement strings into dictionary.

    Args:
        replacements: string indicating what [repository] replacements are to be used.

    Returns:
        Dictionary where key is the 'replaced' repository and value is the repository to use instead.
    """

    reps = replacements.split(',')
    res = {}
    for r in reps:
        rl = r.split('/')
        res[rl[0]] = rl[1]
    return res
