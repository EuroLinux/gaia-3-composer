import json
import unittest
import argparse
from unittest.mock import patch, mock_open

import composer.rules as r


class TestRules(unittest.TestCase):

    mocked_source = {
                      "AppStream:x86_64:Packages/a:aide-0.16-11.el8.x86_64.rpm": {
                          "elem_name": "aide-0.16-11.el8.x86_64.rpm",
                          "elem_abs": "/model/redhat8",
                          "elem_path": "/model/redhat8/x86_64/AppStream/Packages/a/aide-0.16-11.el8.x86_64.rpm",
                          "elem_arch": "x86_64",
                          "elem_repo": "AppStream",
                          "elem_base": "model/redhat8/",
                          "elem_rel": "x86_64/AppStream/Packages/a",
                          "elem_pkg": "Packages/a"
                      }
                    }

    mocked_dest = {
                      "AppStream:x86_64:Packages/a:aide-0.16-11.el8.x86_64.rpm": {
                        "elem_name": "aide-0.16-11.el8.x86_64.rpm",
                        "elem_abs": "/model/eurolinux8",
                        "elem_path": "/model/eurolinux8/AppStream/x86_64/" +
                                     "all/Packages/a/aide-0.16-11.el8.x86_64.rpm",
                        "elem_arch": "x86_64",
                        "elem_repo": "AppStream",
                        "elem_base": "model/eurolinux8/",
                        "elem_rel": "AppStream/x86_64/all/Packages/a",
                        "elem_pkg": "Packages/a"
                      },
                      "BaseOS:x86_64:Packages/a:aide-debuginfo-0.16-14.el8_5.1.x86_64.rpm": {
                          "elem_name": "aide-debuginfo-0.16-14.el8_5.1.x86_64.rpm",
                          "elem_abs": "/model/eurolinux8",
                          "elem_path": "/model/eurolinux8/BaseOS/x86_64/" +
                                       "all/Packages/a/aide-debuginfo-0.16-14.el8_5.1.x86_64.rpm",
                          "elem_arch": "x86_64",
                          "elem_repo": "BaseOS",
                          "elem_base": "/model/eurolinux8/",
                          "elem_rel": "BaseOS/x86_64/all/Packages/a",
                          "elem_pkg": "Packages/a"
                          },
                      "BaseOS:x86_64:Packages/a:aide-debugsource-0.16-14.el8_5.1.x86_64.rpm": {
                          "elem_name": "aide-debugsource-0.16-14.el8_5.1.x86_64.rpm",
                          "elem_abs": "/model/eurolinux8",
                          "elem_path": "/model/eurolinux8/BaseOS/x86_64/" +
                                       "all/Packages/a/aide-debugsource-0.16-14.el8_5.1.x86_64.rpm",
                          "elem_arch": "x86_64",
                          "elem_repo": "BaseOS",
                          "elem_base": "/model/eurolinux8/",
                          "elem_rel": "BaseOS/x86_64/all/Packages/a",
                          "elem_pkg": "Packages/a"
                          }
                    }

    def test_create_move_commands_for_debug_packages(self):
        result = r.create_move_commands_for_debug_packages(self.mocked_dest, '/all/', '/debug/')
        print(result)
        self.assertEqual(result, [('/model/eurolinux8/BaseOS/x86_64/all/Packages/' +
                                   'a/aide-debuginfo-0.16-14.el8_5.1.x86_64.rpm',
                                   '/model/eurolinux8/BaseOS/x86_64/debug/Packages/' +
                                   'a/aide-debuginfo-0.16-14.el8_5.1.x86_64.rpm'),
                                  ('/model/eurolinux8/BaseOS/x86_64/all/Packages/' +
                                   'a/aide-debugsource-0.16-14.el8_5.1.x86_64.rpm',
                                   '/model/eurolinux8/BaseOS/x86_64/debug/Packages/' +
                                   'a/aide-debugsource-0.16-14.el8_5.1.x86_64.rpm')])

    @patch('composer.maptarget.map_target')
    @patch('composer.rules._append_rule')
    def test_create_ruleset(self, append_rule_mock, maptarget_mock):
        args = argparse.Namespace(src_repo='/model/redhat8',
                                  dst_repo='/model/eurolinux8',
                                  move_debug=True,
                                  all_dir='/all/',
                                  debug_dir='/debug/',
                                  archs=['x86_64'],
                                  repo_priority=['AppStream', 'PowerTools'],
                                  os_dir='/os/',
                                  replacements={'CodeReady': 'PowerTools'},
                                  custom_rules_file=None,
                                  mask=".*\\.rpm$",
                                  skip_dirs=['/debug/', '/os/'])
        append_rule_mock.return_value = ('/model/eurolinux8/AppStream/x86_64/all/Packages/' +
                                         'a/aide-0.16-11.el8.x86_64.rpm',
                                         '/model/eurolinux8/AppStream/x86_64/os/Packages/' +
                                         'a/aide-0.16-11.el8.x86_64.rpm')
        maptarget_mock.side_effect = [self.mocked_source, self.mocked_dest]
        ret = r.create_ruleset(args)
        print(ret)
        self.assertDictEqual(ret, {'mkdir': [],
                                   'mv': [('/model/eurolinux8/BaseOS/x86_64/all/Packages/' +
                                           'a/aide-debuginfo-0.16-14.el8_5.1.x86_64.rpm',
                                           '/model/eurolinux8/BaseOS/x86_64/debug/Packages/' +
                                           'a/aide-debuginfo-0.16-14.el8_5.1.x86_64.rpm'),
                                          ('/model/eurolinux8/BaseOS/x86_64/all/Packages/' +
                                           'a/aide-debugsource-0.16-14.el8_5.1.x86_64.rpm',
                                           '/model/eurolinux8/BaseOS/x86_64/debug/Packages/' +
                                           'a/aide-debugsource-0.16-14.el8_5.1.x86_64.rpm')],
                                   'ln': [('/model/eurolinux8/AppStream/x86_64/all/Packages/' +
                                           'a/aide-0.16-11.el8.x86_64.rpm',
                                           '/model/eurolinux8/AppStream/x86_64/os/Packages/' +
                                           'a/aide-0.16-11.el8.x86_64.rpm')]
                                   })

    @patch('composer.rules._append_custom_rules_json')
    @patch('composer.rules._append_custom_rules_short')
    def test_append_custom_rules_json_route(self, short_mock, json_mock):
        args = argparse.Namespace(custom_rules_file='custom.rules.conf', all_dir='/all/', os_dir='/os/')
        r.append_custom_rules(self.mocked_dest, args)
        json_mock.assert_called_once_with(self.mocked_dest, args.custom_rules_file, args.all_dir, args.os_dir)

    @patch('composer.rules._append_custom_rules_json')
    @patch('composer.rules._append_custom_rules_short')
    def test_append_custom_rules_short_route(self, short_mock, json_mock):
        args = argparse.Namespace(custom_rules_file='custom.rules.conf', all_dir='/all/', os_dir='/os/')
        json_mock.side_effect = json.decoder.JSONDecodeError('error', 'custom.rules.conf', 1)
        r.append_custom_rules(self.mocked_dest, args)
        json_mock.assert_called_once()
        short_mock.assert_called_once_with(self.mocked_dest, args.custom_rules_file, args.all_dir, args.os_dir)

    def test_append_custom_rules_short_ok(self):
        args = argparse.Namespace(custom_rules_file='custom.rules.conf', all_dir='/all/', os_dir='/os/')
        with patch('composer.rules.open', mock_open(read_data='aide-0.* -> AppStream:x86_64\n')):
            ret = r._append_custom_rules_short(self.mocked_dest, args.custom_rules_file, args.all_dir, args.os_dir)
        print(f'{ret=}')
        self.assertEqual(ret, [('/model/eurolinux8/AppStream/x86_64/all/Packages/' +
                                'a/aide-0.16-11.el8.x86_64.rpm',
                                '/model/eurolinux8/AppStream/x86_64/os/Packages/' +
                                'a/aide-0.16-11.el8.x86_64.rpm')])

    @patch('composer.util.load_from_json')
    def test_append_custom_rules_json_ok(self, load_mock):
        args = argparse.Namespace(custom_rules_file='custom.rules.conf', all_dir='/all/', os_dir='/os/')
        load_mock.return_value = [{"file_pattern": "aide-0.*",
                                   "src_repo": "AppStream",
                                   "src_arch": "x86_64",
                                   "dst_repo": "AppStream",
                                   "dst_arch": "x86_64"}]
        ret = r._append_custom_rules_json(self.mocked_dest, args.custom_rules_file, args.all_dir, args.os_dir)
        self.assertEqual(ret, [('/model/eurolinux8/AppStream/x86_64/all/Packages/' +
                                'a/aide-0.16-11.el8.x86_64.rpm',
                                '/model/eurolinux8/AppStream/x86_64/os/Packages/' +
                                'a/aide-0.16-11.el8.x86_64.rpm')])

    @patch('composer.util.load_from_json')
    def test_append_rule_key_found(self, load_mock):
        cmd = r._append_rule(self.mocked_source, self.mocked_dest,
                             'AppStream:x86_64:Packages/a:aide-0.16-11.el8.x86_64.rpm',
                             'Packages/a:aide-0.16-11.el8.x86_64.rpm',
                             'AppStream', 'x86_64', '/all/', '/os/', {'CodeReady': 'PowerTools'})
        self.assertEqual(cmd, ('/model/eurolinux8/AppStream/x86_64/all/Packages/a/aide-0.16-11.el8.x86_64.rpm',
                               '/model/eurolinux8/AppStream/x86_64/os/Packages/a/aide-0.16-11.el8.x86_64.rpm'))

    @patch('composer.util.load_from_json')
    def test_append_rule_key_not_found(self, load_mock):
        cmd = r._append_rule(self.mocked_source, self.mocked_dest,
                             'AppStream:x86_64:Packages/a:aide-0.16-11.el8.x86_64.rpm',
                             'Packages/a:aide-0.16-11.el8.x86_64.rpm',
                             'AppStream', 'aarch', '/all/', '/os/', {'CodeReady': 'PowerTools'})
        self.assertIsNone(cmd)
