#
# MIT License
#
# (C) Copyright [2024] Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
"""Wrapped dulwich functions for processing git repo configs

"""
from os.path import join as join_path
from vtds_base import read_config
from .git_repo import (
    GitRepo,
    GitRepos
)


class GitConfigs(GitRepos):
    """Container for the list and state of git configuration repos.

    """
    def __init__(self, build_dir):
        """Constructor: prepare a place for repos to live and
        initialize the list and state of the repos.

        """
        GitRepos.__init__(self, build_dir, "configs")

    def add_config(self, url):
        """Create or learn a directory to contain the repo found at
        the specified URL under the specified build directory tree.

        """
        return self._add_repo(url)


class GitConfig(GitRepo):
    """Configuration from a git repo

    """
    # Class variable to keep track of the container we are putting all
    # GitConfig instances into.
    configs = None

    def __init__(self, url, version, build_dir):
        """Constructor...

        """
        GitConfig.configs = (
            GitConfigs(build_dir) if GitConfig.configs is None else
            GitConfig.configs
        )
        repo_name, git_dir = GitConfig.configs.add_config(url)
        GitRepo.__init__(self, url, version, repo_name, git_dir)

    def retrieve(self, config_path):
        """Retrieve the repo at the specified URL if necessary and
        return the configuration in the file at the relative path in
        the repo specified by 'config_path'. The value of 'config_path'
        is a relative pathname separated by forward slashes ('/').

        """
        self._clone()
        self._get_version()
        file_path = join_path(self.git_dir, config_path)
        return read_config(file_path)
