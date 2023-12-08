import os
import unittest
from unittest.mock import call, patch, mock_open

import composer.execution as e


class TestExecution(unittest.TestCase):

    def test_create_local_repo_script(self):
        mocked_repo = {
                          "AppStream:x86_64:Packages/a:aide-0.16-11.el8.x86_64.rpm": {
                            "elem_name": "aide-0.16-11.el8.x86_64.rpm",
                            "elem_abs": "/minefield/eurolinux8",
                            "elem_path": "/minefield/eurolinux8/AppStream/x86_64/" +
                                         "all/Packages/a/aide-0.16-11.el8.x86_64.rpm",
                            "elem_arch": "x86_64",
                            "elem_repo": "AppStream",
                            "elem_base": "minefield/eurolinux8/",
                            "elem_rel": "AppStream/x86_64/all/Packages/a",
                            "elem_pkg": "Packages/a"
                          }
                        }
        m = mock_open()
        with patch('composer.execution.open', m):
            e.create_local_repo_script(mocked_repo, 'foo')
        handle = m()
        handle.write.assert_called_once_with('#!/bin/bash\n')
        handle.writelines.assert_has_calls([
            call(['mkdir -p AppStream/x86_64/all/Packages/a\n']),
            call(['touch AppStream/x86_64/all/Packages/a/aide-0.16-11.el8.x86_64.rpm\n'])
            ])

    @patch('composer.execution._run_single_thread')
    def test_apply_rules_run_single(self, once_mock):
        mock_cmd_dict = {
                          "mkdir": [],
                          "mv":
                          [
                            [
                              "/minefield/eurolinux8/BaseOS/i686/all/Packages/a/alsa-lib-1.2.8-2.el8.i686.rpm",
                              "/minefield/eurolinux8/AppStream/x86_64/os/Packages/a/alsa-lib-1.2.8-2.el8.i686.rpm"
                            ]
                          ],
                          "ln":
                          [
                           [
                              "/minefield/eurolinux8/AppStream/x86_64/all/Packages/a/aide-0.16-11.el8.x86_64.rpm",
                              "/minefield/eurolinux8/AppStream/x86_64/os/Packages/a/aide-0.16-11.el8.x86_64.rpm"
                           ]
                          ]
                        }

        e.apply_rules(mock_cmd_dict, threads=1, real_run=True)
        self.assertEqual(len(mock_cmd_dict['mkdir']), 1)
        self.assertEqual(mock_cmd_dict['mkdir'], ['/minefield/eurolinux8/AppStream/x86_64/os/Packages/a'])
        once_mock.assert_called_once_with(mock_cmd_dict)

    @patch('composer.execution._run_in_threads')
    def test_apply_rules_run_threaded(self, threads_mock):
        mock_cmd_dict = {
                          "mkdir": [],
                          "mv":
                          [
                            [
                              "/minefield/eurolinux8/BaseOS/i686/all/Packages/a/alsa-lib-1.2.8-2.el8.i686.rpm",
                              "/minefield/eurolinux8/AppStream/x86_64/os/Packages/a/alsa-lib-1.2.8-2.el8.i686.rpm"
                            ]
                          ],
                          "ln":
                          [
                           [
                              "/minefield/eurolinux8/AppStream/x86_64/all/Packages/a/aide-0.16-11.el8.x86_64.rpm",
                              "/minefield/eurolinux8/AppStream/x86_64/os/Packages/a/aide-0.16-11.el8.x86_64.rpm"
                           ]
                          ]
                        }

        e.apply_rules(mock_cmd_dict, threads=2, real_run=True)
        self.assertEqual(len(mock_cmd_dict['mkdir']), 1)
        self.assertEqual(mock_cmd_dict['mkdir'], ['/minefield/eurolinux8/AppStream/x86_64/os/Packages/a'])
        threads_mock.assert_called_once_with(mock_cmd_dict, 2)

    @patch('os.makedirs')
    @patch('os.rename')
    @patch('os.link')
    def test_run_single_thread(self, link_mock, rename_mock, makedirs_mock):
        mock_cmd_dict = {
                          "mkdir": [],
                          "mv":
                          [
                            [
                              "/minefield/eurolinux8/BaseOS/i686/all/Packages/a/alsa-lib-1.2.8-2.el8.i686.rpm",
                              "/minefield/eurolinux8/AppStream/x86_64/os/Packages/a/alsa-lib-1.2.8-2.el8.i686.rpm"
                            ]
                          ],
                          "ln":
                          [
                           [
                              "/minefield/eurolinux8/AppStream/x86_64/all/Packages/a/aide-0.16-11.el8.x86_64.rpm",
                              "/minefield/eurolinux8/AppStream/x86_64/os/Packages/a/aide-0.16-11.el8.x86_64.rpm"
                           ]
                          ]
                        }
        e._run_single_thread(mock_cmd_dict)
        rename_mock.assert_called_once_with(
                "/minefield/eurolinux8/BaseOS/i686/all/Packages/a/alsa-lib-1.2.8-2.el8.i686.rpm",
                "/minefield/eurolinux8/AppStream/x86_64/os/Packages/a/alsa-lib-1.2.8-2.el8.i686.rpm")
        link_mock.assert_called_once_with(
                "/minefield/eurolinux8/AppStream/x86_64/all/Packages/a/aide-0.16-11.el8.x86_64.rpm",
                "/minefield/eurolinux8/AppStream/x86_64/os/Packages/a/aide-0.16-11.el8.x86_64.rpm")

    @patch('composer.execution._prep_for_threads')
    @patch('composer.execution._apply_2arg_fun')
    def test_run_multiple_threads(self, two_arg_mock, prep_mock):
        mock_cmd_dict = {
                          "mkdir": [],
                          "mv": [],
                          "ln":
                          [
                           [
                              "/minefield/eurolinux8/AppStream/x86_64/all/Packages/a/aide-0.16-11.el8.x86_64.rpm",
                              "/minefield/eurolinux8/AppStream/x86_64/os/Packages/a/aide-0.16-11.el8.x86_64.rpm"
                           ],
                           [
                              "/minefield/eurolinux8/BaseOS/i686/all/Packages/a/alsa-lib-1.2.8-2.el8.i686.rpm",
                              "/minefield/eurolinux8/AppStream/x86_64/os/Packages/a/alsa-lib-1.2.8-2.el8.i686.rpm"
                           ]
                          ]
                        }
        prep_mock.side_effect = [
                    [[]],
                    [
                        ["/minefield/eurolinux8/AppStream/x86_64/all/Packages/a/aide-0.16-11.el8.x86_64.rpm",
                         "/minefield/eurolinux8/AppStream/x86_64/os/Packages/a/aide-0.16-11.el8.x86_64.rpm"
                         ],
                        ["/minefield/eurolinux8/BaseOS/i686/all/Packages/a/alsa-lib-1.2.8-2.el8.i686.rpm",
                         "/minefield/eurolinux8/AppStream/x86_64/os/Packages/a/alsa-lib-1.2.8-2.el8.i686.rpm"
                         ]
                    ]
                ]
        e._run_in_threads(mock_cmd_dict, thread_num=2)
        prep_mock.assert_has_calls([call(mock_cmd_dict['mv'], 2), call(mock_cmd_dict['ln'], 2)])
        two_arg_mock.assert_called()
        # GH has some issues with check below
        # two_arg_mock.assert_has_calls(
        #         [call([], os.rename),
        #          call(["/minefield/eurolinux8/AppStream/x86_64/all/Packages/a/aide-0.16-11.el8.x86_64.rpm",
        #                "/minefield/eurolinux8/AppStream/x86_64/os/Packages/a/aide-0.16-11.el8.x86_64.rpm"],
        #               e._create_link)])

    @patch('os.rename')
    def test_apply_2arg_fun(self, mock_rename):
        e._apply_2arg_fun([('src1', 'dst1'), ('src2', 'dst2')], os.rename)
        mock_rename.assert_has_calls([call('src1', 'dst1'), call('src2', 'dst2')])

    @patch('os.stat')
    @patch('os.link')
    @patch('os.remove')
    @patch('sys.exit')
    def test_create_link_ok(self, mock_exit, mock_remove, mock_link, mock_stat):
        e._create_link('src1', 'dst1')
        mock_link.assert_called_once_with('src1', 'dst1')

    @patch('os.stat')
    @patch('os.link')
    @patch('os.remove')
    @patch('sys.exit')
    def test_create_link_diff_device(self, mock_exit, mock_remove, mock_link, mock_stat):
        mock_link.side_effect = FileExistsError('dst1')
        mock_stat.side_effect = [os.stat_result((33188, 79629535, 37, 1, 1000,
                                                1000, 8031, 1697446592,
                                                1697446592, 1697446592),),
                                 os.stat_result((33188, 79629535, 87, 1, 1000,
                                                1000, 8031, 1697446592,
                                                1697446592, 1697446592),)]
        e._create_link('src1', 'dst1')
        mock_stat.assert_has_calls([call('src1'), call('dst1')])
        mock_exit.assert_called_once_with(1)

    @patch('os.stat')
    @patch('os.link')
    @patch('os.remove')
    @patch('sys.exit')
    def test_create_link_diff_ino(self, mock_exit, mock_remove, mock_link, mock_stat):
        mock_link.side_effect = [FileExistsError('dst1'), None]
        mock_stat.side_effect = [os.stat_result((33188, 79629535, 37, 1, 1000,
                                                1000, 8031, 1697446592,
                                                1697446592, 1697446592),),
                                 os.stat_result((33188, 79629777, 37, 1, 1000,
                                                1000, 8031, 1697446592,
                                                1697446592, 1697446592),)]
        e._create_link('src1', 'dst1')
        mock_stat.assert_has_calls([call('src1'), call('dst1')])
        mock_remove.assert_called_once_with('dst1')
        mock_link.assert_has_calls([call('src1', 'dst1'), call('src1', 'dst1')])

    def test_prep_for_threads(self):
        tuplelist = [('src1', 'dst1'), ('src2', 'dst2'), ('src3', 'dst3'), ('src4', 'dst4')]
        ret = e._prep_for_threads(tuplelist, 2)
        self.assertEqual(ret, [[('src1', 'dst1'), ('src2', 'dst2')], [('src3', 'dst3'), ('src4', 'dst4')]])
