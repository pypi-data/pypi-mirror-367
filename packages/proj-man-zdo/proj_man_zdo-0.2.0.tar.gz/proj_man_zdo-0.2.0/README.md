* website: <https://arrizza.com/python-proj-man-zdo.html>
* installation: see <https://arrizza.com/setup-common.html>

## Summary

This project is used to manage many projects from the command line.

If you have common commands that you need to run across many projects, you would
normally need to cd into each directory and manually invoke that command.
This module lets you automate those activities.

For example, you can visit all or a subset of all the projects and invoke a command in each one.
Or you can write a more complex command in python and invoke it in any directories you need to.

## run

Note: the examples here use ```sample-zdo```.
You should probably rename it to ```zdo``` to simplify typing it on the command line.
(I used sample-zdo since I already have a zdo to manage the 60+ repos I have.)

```bash
./sample-zdo            <== shows list of commands
./sample-zdo one-off    <== runs the one-off command
```

## set up repos.py

* fill in repos.py with the directories/repos/projects you want to work with.

```text
$ sample-zdo run all2 pwd
     group: "all2"
---> running cmd: pwd in project: /home/arrizza/projects/web/xplat-utils
 --  /home/arrizza/projects/web/xplat-utils] 1
OK   cmd rc=0
<snip>
---> total run :  11      <= should be total #repos/projects you've added to repos.py
OK   total fail:   0
```

The directories printed out by ```pwd``` should be the correct for each project in repos.py

Now try the groups you've named:

```text
$ sample-zdo run rb pwd
     group: "rb"
<snip>
---> total run :   3
OK   total fail:   0
```

## nesting calls

Note: you can nest calls to sample-zdo:

```text
$ sample-zdo run all sample-zdo search
     group: "rb"
<snip>
---> total run :   3
OK   total fail:   0
```

## adding commands

See sample/app.py for an example.

* create the function. The signature is no parameters, returns an error code (0 for no errors)/

```text
def one_off(self):
    errs = 0
    <snip>
    return errs
```

* add the command

```
self.add_cmd('one-off', self.one_off)
```

## Commands

#### run

Runs the given command on all repos in the given group.

* The group must be one of those listed in proj_top_groups or proj_groups in repos.py
  Note that the sample also accepts: all, all1, and all2

```text
    proj_top_groups = {
        'rb': ['rb-apps', 'rb-gems', 'rb-wip'],
        'py': ['py-mods', 'py-apps', 'py-wip'],
        'cpp': ['cpp-libs', 'cpp-apps', 'cpp-wip'],
        'ard': ['ard-libs', 'ard-apps', 'ard-wip'],
    }

    proj_groups = [
        'base',  # for projects that are common to all other projects
        'common',  # basic projects
        'py-mods',
        <snip>
        'wip',
        'non-project',
    ]
```

* The command can be any terminal command.
    * single and double quotes are stripped before the python script gets the full text of the command.
      Some commands are not possible to do.
      e.g. ```sample-zdo run all git commit -m "hi there"``` will fail because the double quotes are removed and
      git sees two arguments instead of one.
    * piping, tees etc. are stripped out as well

```text
$ sample-zdo run rb pwd
# will run the "pwd" command in each directory for ruby repos
```

#### first

Creates a new terminal in the first directory of the repos list.

Currently, the terminal is only a gnome-terminal for Ubuntu.

If the repo does not exist, a git clone is attempted.

* define ```self.set_cmn_attr('get_git_url', self._get_git_url)```
* define a ```self._get_git_url``` to return a git clone URL

#### next

Creates a new terminal in the next directory of the repos list based on the current directory.
Check if the repo exists, creates it if necessary.

If at the end of the list:

```text
$ sample-zdo next
OK   git urls match
     curr directory: /home/arrizza/projects/web/ruby/rb-falcon-logger
OK   no next project, all done!
```

#### prev

Creates a new terminal in the next directory of the repos list based on the current directory.
Check if the repo exists, creates it if necessary.

If at the start of the list:

```text
$ sample-zdo prev
OK   git urls match
     curr directory: /home/arrizza/projects/web/xplat-utils
OK   no prev project, all done!
```

#### cd

Creates a new terminal for the best match of the given directory name.
The fuzzy-wuzzy module is used to select the best matching name in the repos.py list.

```text
$ sample-zdo cd logger
found matches for logger:
    rank 100: ~/projects/web/ruby/rb-falcon-logger
    rank  32: ~/projects/web/ruby/rb-cfg-parser
cd directory: ~/projects/web/ruby/rb-falcon-logger
```

Must have a ranking of 30 or greater to be considered a match

```text
$ sample-zdo cd xyz
ERR  no matches found for "xyz"
sample-zdo rc=1 cd xyz
```

#### check-repo

Report any uncommitted changes, unpushed changes and/or untracked files in the repo:

```text
sample-zdo check-repo
OK   check-repo: all changes are committed
```

The default branch is ```master```. Change that using:

```text
self.set_cmn_attr('default_branch', 'my_branch')
```

or use a command line args:

```text
sample-zdo check-repo cool-branch
WARN check-repo: not on cool-branch
WARN check-repo: actual Your branch is up to date with 'origin/master'.
```

#### check-subm

Report any uncommitted changes, unpushed changes and/or untracked files in submodules (if any):

Set ```subm_info``` with a list of tuples, one for each submodule directory and expected branch:

```text
self.set_cmn_attr('subm_info', [
    # subm directory,     subm branch
    ('tools/xplat_utils', 'v1.0.3'),
])
```

Set subm_excludes to exclude any repos that should be excluded from the check:

```text
self.set_cmn_attr('subm_excludes', ['xplat-utils'])
```

Typical output:

``` text
$ sample-zdo check-subm
WARN check-subm: untracked files found (tools/xplat_utils)
 --    1] Untracked files:
 --    2]   (use "git add <file>..." to include in what will be committed)
 --    3] 	xx
 --    4] 
 --    5] nothing added to commit but untracked files present (use "git add" to track)
```

#### check-branch

Report if the main git repo is on a given branch and if any submodules also the current branch.

Set ```subm_info``` (see check-subm above)

Typical output:

```text
$ sample-zdo check-branch
OK   check_branch: repo: branch matches: master
OK   check_branch: subm: branch matches: v1.0.3 (tools/xplat_utils)
```

Set subm_excludes as needed (see check-subm):

```text
# typical output:
sample-zdo check-branch
OK   check_branch: repo: branch matches: master
OK   check_branch: repo : does not have submodules: xplat-utils
```

#### check-size

Reports the current disk sizes for the repo and the .git subdirectory.
These are stored in proj_sizes.json file.

```text
---> running cmd: sample-zdo check-size in project: /home/arrizza/projects/web/ruby/rb-falcon-logger
 --    1] OK   cmd rc=0
 --    2]      {'.git': '2.9M', '.': '49M'}
 --    3] sample-zdo rc=0
OK   cmd rc=0
```

#### check-reqmts

Checks all Python module requirements and ruby gem requirements.

For ruby, it will run ```'bundle outdated``` which will list any outdated gems.

For python, if you have base-level files holding common modules for all your repos,
use  ```reqmts_base_paths``` to provide a list of them.

```text
root_dir = os.path.join('tools', 'xplat_utils', 'install')
self.set_cmn_attr('reqmts_base_paths', [
    os.path.join(root_dir, 'reqmts_arduino_app.txt'),
    os.path.join(root_dir, 'reqmts_arduino_common.txt'),
    <snip>
  ])
```

If you have a requirements file that contains the modules needed for the current repo,
use ```reqmts_top_path``` to provide a path to it.

```text
self.set_cmn_attr('reqmts_top_path', os.path.join('tools', 'requirements.txt'))
```

If you have some repos that don't have requirements.txt, add them to ```reqmts_skip```.

```text
self.set_cmn_attr('reqmts_skip', ['xplat-utils', 'fpga-led-blink'])
```

Typical output:

```text
---> running cmd: sample-zdo check-reqmts in project: /home/arrizza/projects/web/ai/ai-linear-regression
 --    1] WARN check-reqmts: setuptools        in use:  80.8.0  latest:  80.9.0, see tools/xplat_utils/install/reqmts_arduino_common.txt
 --    2] WARN check-reqmts: scipy             in use:  1.15.2  latest:  1.15.3, see tools/requirements.txt
 --    3] ERR  check-reqmts: number errs found: 2
 --    4] sample-zdo rc=2
ERR  cmd rc=2
```
