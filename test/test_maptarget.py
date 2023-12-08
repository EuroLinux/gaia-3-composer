import argparse
import unittest
from unittest.mock import patch

import composer.maptarget as mt


# Namespace(action='direct',
#           repo_priority=['BaseOS', 'AppStream', 'PowerTools', 'HighAvailability', 'ResilientStorage', 'CodeReady'],
#           archs=['x86_64', 'i686', 'aarch64', 'noarch'],
#           skip_dirs=['/debug/', '/os/'],
#           mask='.*\\.rpm$',
#           include_beta=False, include_extra=False, src_repo='minefield/redhat8/',
#           dst_repo='minefield/eurolinux8/', move_debug=True, os_dir='/os/', debug_dir='/debug/', all_dir='/all/',
#           custom_rules_file=None, replacements={'CodeReady': 'PowerTools'}, real_run=True, threads=1)

class TestMapTarget(unittest.TestCase):

    def test_set_elem_arch_none(self):
        arch = mt._set_elem_arch("/minefield/eurolinux8/PowerTools/all/Packages/n",
                                 ["x86_64", "aarch"])
        self.assertIsNone(arch)

    def test_set_elem_arch_ok(self):
        arch = mt._set_elem_arch("/minefield/eurolinux8/PowerTools/x86_64/all/Packages/n",
                                 ["x86_64", "aarch"])
        self.assertEqual(arch, "x86_64")

    def test_set_elem_repo_arg_repo_missing(self):
        repo = mt._set_elem_repo("/minefield/eurolinux8/PowerTools/x86_64/all/Packages/n",
                                 argparse.Namespace(include_beta=False, include_extra=False))
        self.assertIsNone(repo)

    def test_set_elem_repo_arg_extra_missing(self):
        repo = mt._set_elem_repo("/minefield/eurolinux8/PowerTools/x86_64/all/Packages/n",
                                 argparse.Namespace(repo_priority=['AppStream', 'PowerTools'], include_beta=False))
        self.assertIsNone(repo)

    def test_set_elem_repo_arg_bonus_missing(self):
        repo = mt._set_elem_repo("/minefield/eurolinux8/PowerTools/x86_64/all/Packages/n",
                                 argparse.Namespace(repo_priority=['AppStream', 'PowerTools'], include_extra=False))
        self.assertIsNone(repo)

    def test_set_elem_repo_arg_namespace_empty(self):
        repo = mt._set_elem_repo("/minefield/eurolinux8/PowerTools/x86_64/all/Packages/n",
                                 argparse.Namespace())
        self.assertIsNone(repo)

    def test_set_elem_repo_ok(self):
        repo = mt._set_elem_repo("/minefield/eurolinux8/PowerTools/x86_64/all/Packages/n",
                                 argparse.Namespace(repo_priority=['AppStream', 'PowerTools'],
                                                    include_beta=False, include_extra=False))
        self.assertEqual(repo, 'PowerTools')

    def test_map_target_not_exists(self):
        with patch('os.path.exists'):
            mapped = mt.map_target('eurolinux8/', argparse.Namespace(mask=".*\\.rpm$",
                                                                     skip_dirs=['/debug/', '/os/'],
                                                                     archs=["x86_64", "aarch64"]))
            self.assertEqual(mapped, {})

    def _abspath_side_effect_func(self, value):
        """ adjust for abspath-like behavior """
        if value[0] != '/':
            value = '/' + value
        if value[-1] == '/':
            value = value[:-1]
        return value

    @patch('os.path.exists')
    @patch('os.path.abspath')
    def test_map_target_ok(self, abspath, exists):

        abspath.side_effect = self._abspath_side_effect_func
        expected = \
            {
             'AppStream:x86_64:Packages/a:autoconf-2.69-27.el8.noarch.rpm':
             {'elem_name': 'autoconf-2.69-27.el8.noarch.rpm',
              'elem_abs': '/minefield/eurolinux8',
              'elem_path': '/minefield/eurolinux8/' +
                           'AppStream/x86_64/all/Packages/a/autoconf-2.69-27.el8.noarch.rpm',
              'elem_arch': 'x86_64',
              'elem_repo': 'AppStream',
              'elem_base': 'minefield/eurolinux8/',
              'elem_rel': 'AppStream/x86_64/all/Packages/a',
              'elem_pkg': 'Packages/a'},
             'AppStream:x86_64:Packages/a:autoconf-2.69-29.el8.noarch.rpm':
             {'elem_name': 'autoconf-2.69-29.el8.noarch.rpm',
              'elem_abs': '/minefield/eurolinux8',
              'elem_path': '/minefield/eurolinux8/' +
                           'AppStream/x86_64/all/Packages/a/autoconf-2.69-29.el8.noarch.rpm',
              'elem_arch': 'x86_64',
              'elem_repo': 'AppStream',
              'elem_base': 'minefield/eurolinux8/',
              'elem_rel': 'AppStream/x86_64/all/Packages/a',
              'elem_pkg': 'Packages/a'},
            }
        with patch('os.walk') as mockwalk:
            mockwalk.return_value = [
                    ('/minefield/eurolinux8', ['AppStream', 'PowerTools'], []),
                    ('/minefield/eurolinux8/AppStream', ['aarch64', 'i686', 'x86_64'], []),
                    ('/minefield/eurolinux8/AppStream/x86_64', ['all', 'os'], []),
                    ('/minefield/eurolinux8/AppStream/x86_64/all', ['Packages'], []),
                    ('/minefield/eurolinux8/AppStream/x86_64/all/Packages', ['a'], []),
                    ('/minefield/eurolinux8/AppStream/x86_64/all/Packages/a', [],
                     ['autoconf-2.69-27.el8.noarch.rpm', 'autoconf-2.69-29.el8.noarch.rpm']),
                    ('/minefield/eurolinux8/AppStream/x86_64', ['all', 'os'], []),
                    ('/minefield/eurolinux8/AppStream/x86_64/os', ['Packages'], []),
                    ('/minefield/eurolinux8/AppStream/x86_64/os/Packages', ['a'], []),
                    ('/minefield/eurolinux8/AppStream/x86_64/os/Packages/a', [],
                     ['autoconf-2.69-27.el8.noarch.rpm', 'autoconf-2.69-29.el8.noarch.rpm'])
                    ]
            mapped = mt.map_target('minefield/eurolinux8/',
                                   argparse.Namespace(action='maptarget',
                                                      repo_priority=['BaseOS', 'AppStream',
                                                                     'PowerTools', 'HighAvailability',
                                                                     'ResilientStorage', 'CodeReady'],
                                                      archs=['x86_64', 'i686', 'aarch64', 'noarch'],
                                                      skip_dirs=['/debug/', '/os/'], mask='.*\\.rpm$',
                                                      include_beta=False, include_extra=False))
            self.assertEqual(mapped, expected)
