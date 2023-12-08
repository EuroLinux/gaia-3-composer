import unittest
from unittest.mock import call, mock_open, patch

import composer.mapremote as mr


# Namespace(action='direct',
#           repo_priority=['BaseOS', 'AppStream', 'PowerTools', 'HighAvailability', 'ResilientStorage', 'CodeReady'],
#           archs=['x86_64', 'i686', 'aarch64', 'noarch'],
#           skip_dirs=['/debug/', '/os/'],
#           mask='.*\\.rpm$',
#           include_beta=False, include_extra=False, src_repo='minefield/redhat8/',
#           dst_repo='minefield/eurolinux8/', move_debug=True, os_dir='/os/', debug_dir='/debug/', all_dir='/all/',
#           custom_rules_file=None, replacements={'CodeReady': 'PowerTools'}, real_run=True, threads=1)

class TestMapRemote(unittest.TestCase):

    root_tree_elem = mr.TreeElement(**{"elem_name": "/",
                                       "elem_type": "dir",
                                       "elem_base": "https://repo.eurolinux.local/repo/redhat/8/",
                                       "elem_rel": ""})
    aarch64_tree_elem = mr.TreeElement(**{"elem_name": "aarch64/",
                                          "elem_type": "dir",
                                          "elem_base": "https://repo.eurolinux.local/repo/redhat/8/",
                                          "elem_rel": ""})
    appstream_tree_elem = mr.TreeElement(**{"elem_name": "AppStream/",
                                            "elem_type": "dir",
                                            "elem_base": "https://repo.eurolinux.local/repo/redhat/8/",
                                            "elem_rel": "aarch64/"})
    packages_tree_elem = mr.TreeElement(**{"elem_name": "Packages/",
                                           "elem_type": "dir",
                                           "elem_base": "https://repo.eurolinux.local/repo/redhat/8/",
                                           "elem_rel": "aarch64/AppStream/"})
    a_tree_elem = mr.TreeElement(**{"elem_name": "a/",
                                    "elem_type": "dir",
                                    "elem_base": "https://repo.eurolinux.local/repo/redhat/8/",
                                    "elem_rel": "aarch64/AppStream/Packages/"})
    abrt_tree_elem = mr.TreeElement(**{"elem_name": "abrt-2.10.9-21.el8.aarch64.rpm",
                                       "elem_type": "file",
                                       "elem_base": "https://repo.eurolinux.local/repo/redhat/8/",
                                       "elem_rel": "aarch64/AppStream/Packages/a/"})

    a_tree_elem.parent_to['abrt-2.10.9-21.el8.aarch64.rpm'] = abrt_tree_elem
    packages_tree_elem.parent_to['a/'] = a_tree_elem
    appstream_tree_elem.parent_to['Packages/'] = packages_tree_elem
    aarch64_tree_elem.parent_to['AppStream/'] = appstream_tree_elem
    root_tree_elem.parent_to['aarch64/'] = aarch64_tree_elem

    @patch('composer.mapremote._create_mapped_repo')
    def test_write_repo_tree_shell(self, mapped_mock):
        mapped_mock.return_value = self.root_tree_elem
        m = mock_open()
        with patch('composer.mapremote.open', m):
            mr.write_repo_tree_shell('https://something.local', 'foo')
        handle = m()
        handle.write.assert_has_calls([
            call('#!/bin/bash\n'),
            call('mkdir -p aarch64/AppStream/Packages/a/\n'),
            call('mkdir -p aarch64/AppStream/Packages/\n'),
            call('mkdir -p aarch64/AppStream/\n'),
            call('mkdir -p aarch64/\n'),
            call('touch aarch64/AppStream/Packages/a/abrt-2.10.9-21.el8.aarch64.rpm\n')
            ])
