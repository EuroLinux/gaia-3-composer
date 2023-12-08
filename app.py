import argparse
import logging
import sys

import composer.execution as execution
import composer.mapremote as mapremote
import composer.maptarget as maptarget
import composer.parser as parser
import composer.rules as rules
import composer.util as util


def func_mapper(args: argparse.Namespace) -> None:
    """
    Map action into the execution flow

    Args:
        args: argparse object
    """

    if args.action == 'direct':
        cmds = rules.create_ruleset(args)
        execution.apply_rules(cmds, args.threads, args.real_run)
    elif args.action == 'fromrules':
        cmds = util.load_from_json(args.input_file)
        execution.apply_rules(cmds, args.threads, args.real_run)
    elif args.action == 'saverules':
        cmds = rules.create_ruleset(args)
        util.save_to_json(cmds, args.output_file)
    elif args.action == 'maprepo':
        src_repo = maptarget.map_target(args.src_repo, args)
        util.save_to_json(src_repo, args.output_file)
    elif args.action == 'fakerepo':
        repo = util.load_from_json(args.input_file)
        execution.create_local_repo_script(repo, args.bash_output)
    elif args.action == 'fakeremote':
        mapremote.write_repo_tree_shell(args.input_url, args.bash_output)


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    args = parser.parse_args(sys.argv[1:])
    logging.debug(args)
    func_mapper(args)
