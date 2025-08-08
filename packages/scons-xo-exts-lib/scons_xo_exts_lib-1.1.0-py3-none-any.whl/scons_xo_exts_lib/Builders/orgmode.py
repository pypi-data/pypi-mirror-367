#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import subprocess

from SCons.Script import Builder

from scons_xo_exts_lib.BuildSupport import NodeMangling


def orgmode_action(target, source, env):
    emacs_exe = env.get("EMACS_EXE", "emacs")
    emacs_exec_flags = env.get("EMACS_EXEC_FLAGS", "-batch -q --no-site-file")

    cwd = NodeMangling.get_first_directory(source)

    inp = NodeMangling.get_first_node(source).abspath
    out = NodeMangling.get_first_node(target).abspath

    ext = os.path.splitext(out)[1][1:]
    fun = f'(org-export-to-file \'{ext} \\"{out}\\")'

    load_flags = "-l org -l ox-latex"
    flags = f'{emacs_exec_flags} {load_flags} {inp} --eval "{fun}"'

    cmd = f"{emacs_exe} {flags}"
    print(cmd)

    result = subprocess.run(
        args=cmd,
        capture_output=False,
        check=False,
        shell=True,
        cwd=cwd,
    )

    return result.returncode


def generate(env):
    orgmode_file_builder = Builder(action=orgmode_action)

    env.Append(BUILDERS={"OrgmodeFile": orgmode_file_builder})


def exists(env):
    return env.Detect("orgmode")
