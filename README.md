# Composer

## TODO

- [ ] Development && test docs (in README.md) keep it short

## Brief introduction

Composer is used to compose an rpm repository into shape of a model repository.
At the most general level, composer looks through packages in the model (source) repository, tries to find these packages in modeled repository (destination).
When it does, it creates a hardlink inside targeted repository (from `/all/` into `/os/` dir).
The process of this composition is best shown on a small-scale example.

## Development

**We are using Python version 3.6 as this is default for the EuroLinux 8. You
can also use Python3.9 (default for EuroLinux 9).**

## Example

Given this (modeled/target) repository:
```
.
├── AppStream
│   ├── aarch64
│   │   └── all
│   │       └── Packages
│   │           └── a
│   │               └── abrt-2.10.9-20.el8.aarch64.rpm
│   ├── i686
│   │   └── all
│   │       └── Packages
│   │           └── a
│   │               ├── aide-0.16-11.el8.i686.rpm
│   │               └── aide-0.16-14.el8.i686.rpm
│   └── x86_64
│       └── all
│           └── Packages
│               └── a
│                   ├── aide-0.16-11.el8.x86_64.rpm
│                   ├── aide-0.16-14.el8.x86_64.rpm
│                   └── amanda-3.5.1-13.el8.x86_64.rpm
└── BaseOS
    ├── aarch64
    │   └── all
    │       └── Packages
    │           └── a
    │               └── at-3.1.20-12.el8.aarch64.rpm
    ├── i686
    │   └── all
    │       └── Packages
    │           └── a
    │               ├── aide-0.16-14.el8_5.1.i686.rpm
    │               ├── aide-debuginfo-0.16-14.el8_5.1.i686.rpm
    │               ├── aide-debugsource-0.16-14.el8_5.1.i686.rpm
    │               ├── alsa-lib-1.2.8-2.el8.i686.rpm
    │               └── alsa-ucm-1.2.8-2.el8.noarch.rpm
    └── x86_64
        └── all
            └── Packages
                └── a
                    ├── aide-0.16-14.el8_5.1.x86_64.rpm
                    ├── aide-debuginfo-0.16-14.el8_5.1.x86_64.rpm
                    ├── aide-debugsource-0.16-14.el8_5.1.x86_64.rpm
                    ├── alsa-lib-1.2.8-2.el8.x86_64.rpm
                    ├── alsa-ucm-1.2.8-2.el8.noarch.rpm
                    ├── amanda-3.5.1-13.el8.x86_64.rpm
                    └── amanda-3.5.1-14.el8_7.x86_64.rpm
```

And this (model/source) repository:
```
.
├── aarch64
│   └── AppStream
│       └── Packages
│           └── a
│               └── abrt-2.10.9-20.el8.aarch64.rpm
└── x86_64
    └── AppStream
        └── Packages
            └── a
                ├── aide-0.16-11.el8.x86_64.rpm
                ├── aide-0.16-14.el8_5.1.x86_64.rpm
                ├── aide-0.16-14.el8.x86_64.rpm
                ├── aide-0.16-8.el8.x86_64.rpm
                ├── alsa-lib-1.2.8-2.el8.i686.rpm
                ├── alsa-lib-1.2.8-2.el8.x86_64.rpm
                ├── alsa-ucm-1.2.8-2.el8.noarch.rpm
                └── amanda-3.5.1-13.el8.x86_64.rpm
```

We will compose the following repository:
```
.
├── AppStream
│   ├── aarch64
│   │   ├── all
│   │   │   └── Packages
│   │   │       └── a
│   │   │           └── abrt-2.10.9-20.el8.aarch64.rpm
│   │   └── os
│   │       └── Packages
│   │           └── a
│   │               └── abrt-2.10.9-20.el8.aarch64.rpm
│   ├── i686
│   │   └── all
│   │       └── Packages
│   │           └── a
│   │               ├── aide-0.16-11.el8.i686.rpm
│   │               └── aide-0.16-14.el8.i686.rpm
│   └── x86_64
│       ├── all
│       │   └── Packages
│       │       └── a
│       │           ├── aide-0.16-11.el8.x86_64.rpm
│       │           ├── aide-0.16-14.el8.x86_64.rpm
│       │           └── amanda-3.5.1-13.el8.x86_64.rpm
│       └── os
│           └── Packages
│               └── a
│                   ├── aide-0.16-11.el8.x86_64.rpm
│                   ├── aide-0.16-14.el8_5.1.x86_64.rpm
│                   ├── aide-0.16-14.el8.x86_64.rpm
│                   ├── alsa-lib-1.2.8-2.el8.i686.rpm
│                   ├── alsa-lib-1.2.8-2.el8.x86_64.rpm
│                   ├── alsa-ucm-1.2.8-2.el8.noarch.rpm
│                   └── amanda-3.5.1-13.el8.x86_64.rpm
└── BaseOS
    ├── aarch64
    │   └── all
    │       └── Packages
    │           └── a
    │               └── at-3.1.20-12.el8.aarch64.rpm
    ├── i686
    │   ├── all
    │   │   └── Packages
    │   │       └── a
    │   │           ├── aide-0.16-14.el8_5.1.i686.rpm
    │   │           ├── alsa-lib-1.2.8-2.el8.i686.rpm
    │   │           └── alsa-ucm-1.2.8-2.el8.noarch.rpm
    │   └── debug
    │       └── Packages
    │           └── a
    │               ├── aide-debuginfo-0.16-14.el8_5.1.i686.rpm
    │               └── aide-debugsource-0.16-14.el8_5.1.i686.rpm
    └── x86_64
        ├── all
        │   └── Packages
        │       └── a
        │           ├── aide-0.16-14.el8_5.1.x86_64.rpm
        │           ├── alsa-lib-1.2.8-2.el8.x86_64.rpm
        │           ├── alsa-ucm-1.2.8-2.el8.noarch.rpm
        │           ├── amanda-3.5.1-13.el8.x86_64.rpm
        │           └── amanda-3.5.1-14.el8_7.x86_64.rpm
        └── debug
            └── Packages
                └── a
                    ├── aide-debuginfo-0.16-14.el8_5.1.x86_64.rpm
                    └── aide-debugsource-0.16-14.el8_5.1.x86_64.rpm
```

Inode composition being:
```
Inode    File
79623402 minefield/eurolinux8/AppStream/i686/all/Packages/a/aide-0.16-11.el8.i686.rpm
79623403 minefield/eurolinux8/AppStream/i686/all/Packages/a/aide-0.16-14.el8.i686.rpm
79623410 minefield/eurolinux8/AppStream/x86_64/all/Packages/a/amanda-3.5.1-13.el8.x86_64.rpm
79623421 minefield/eurolinux8/BaseOS/i686/all/Packages/a/aide-0.16-14.el8_5.1.i686.rpm
79623423 minefield/eurolinux8/BaseOS/i686/all/Packages/a/alsa-ucm-1.2.8-2.el8.noarch.rpm
79623431 minefield/eurolinux8/BaseOS/x86_64/all/Packages/a/amanda-3.5.1-14.el8_7.x86_64.rpm
79623436 minefield/eurolinux8/BaseOS/aarch64/all/Packages/a/at-3.1.20-12.el8.aarch64.rpm
79623408 \ -> minefield/eurolinux8/AppStream/x86_64/all/Packages/a/aide-0.16-11.el8.x86_64.rpm
79623408 / --> minefield/eurolinux8/AppStream/x86_64/os/Packages/a/aide-0.16-11.el8.x86_64.rpm
79623409 \ -> minefield/eurolinux8/AppStream/x86_64/all/Packages/a/aide-0.16-14.el8.x86_64.rpm
79623409 / --> minefield/eurolinux8/AppStream/x86_64/os/Packages/a/aide-0.16-14.el8.x86_64.rpm
79623415 \ -> minefield/eurolinux8/AppStream/aarch64/all/Packages/a/abrt-2.10.9-20.el8.aarch64.rpm
79623415 / --> minefield/eurolinux8/AppStream/aarch64/os/Packages/a/abrt-2.10.9-20.el8.aarch64.rpm
79623422 \ -> minefield/eurolinux8/BaseOS/i686/all/Packages/a/alsa-lib-1.2.8-2.el8.i686.rpm
79623422 / --> minefield/eurolinux8/AppStream/x86_64/os/Packages/a/alsa-lib-1.2.8-2.el8.i686.rpm
79623428 \ -> minefield/eurolinux8/BaseOS/x86_64/all/Packages/a/aide-0.16-14.el8_5.1.x86_64.rpm
79623428 / --> minefield/eurolinux8/AppStream/x86_64/os/Packages/a/aide-0.16-14.el8_5.1.x86_64.rpm
79623429 \ -> minefield/eurolinux8/BaseOS/x86_64/all/Packages/a/alsa-lib-1.2.8-2.el8.x86_64.rpm
79623429 / --> minefield/eurolinux8/AppStream/x86_64/os/Packages/a/alsa-lib-1.2.8-2.el8.x86_64.rpm
79623430 \ -> minefield/eurolinux8/BaseOS/x86_64/all/Packages/a/alsa-ucm-1.2.8-2.el8.noarch.rpm
79623430 / --> minefield/eurolinux8/AppStream/x86_64/os/Packages/a/alsa-ucm-1.2.8-2.el8.noarch.rpm
79625750 \ -> minefield/eurolinux8/BaseOS/x86_64/all/Packages/a/amanda-3.5.1-13.el8.x86_64.rpm
79625750 / --> minefield/eurolinux8/AppStream/x86_64/os/Packages/a/amanda-3.5.1-13.el8.x86_64.rpm
79625761 minefield/eurolinux8/BaseOS/i686/debug/Packages/a/aide-debuginfo-0.16-14.el8_5.1.i686.rpm
79625762 minefield/eurolinux8/BaseOS/x86_64/debug/Packages/a/aide-debuginfo-0.16-14.el8_5.1.x86_64.rpm
79625763 minefield/eurolinux8/BaseOS/i686/debug/Packages/a/aide-debugsource-0.16-14.el8_5.1.i686.rpm
79625764 minefield/eurolinux8/BaseOS/x86_64/debug/Packages/a/aide-debugsource-0.16-14.el8_5.1.x86_64.rpm
```

Rules at play here are:
1. Move `debuginfo` and `debugsource` files into debug directory
2. Look through all package files of the model (source) repository
3. For each file in the source/model repository (as an example let us take `alsa-lib-1.2.8-2.el8.x86_64.rpm`):
    - Look for the package in the destination/modeled repository the pre-defined order of priority (e.g. first look in `BaseOS`, then in `AppStream`).
      (i.e. If `alsa-lib` package existed in both directories - the one in `BaseOS` would be picked.)
    - Look where is this package in source/model ( (\*) `x86_64/AppStream/Packages/a/alsa-lib-1.2.8-2.el8.x86_64.rpm`)
    - Hardlink picked file from original place in the destination(!) (`BaseOS/x86_64/all/Packages/a/alsa-lib-1.2.8-2.el8.x86_64.rpm`)
      to the linked path (relating to placement in source(\*): `x86_64/AppStream`) into the `/os/` dir in destination(!) (`AppStream/x86_64/os/Packages/a/alsa-lib-1.2.8-2.el8.x86_64.rpm`)
4. Files not in source/model are left untouched (e.g. `at-3.1.20-12.el8.aarch64.rpm`).

Things worth pointing out:
- `amanda-3.5.1-13.el8.x86_64.rpm` in this example is in both `BaseOS` and `AppStream`. For the `os.hardlink`, `BaseOS` is picked (inode `79625750`), because its priority is higher.
- Some packages (e.g. `at-3.1.20-12.el8.aarch64.rpm`) are not landing in `/os/` directory, because they never appear in the "source" repo (thus they are ignored).

## Usage

> Note: in case of issues with finding modules (ModuleNotFoundError), please export `PYTHONPATH` variable to appropriate path.<br/>
> e.g. `export PYTHONPATH=~/git/gaia-3/` (supposing that composer is in `~/git/gaia-3/composer`)

Composer's main feature is to:
- Directly create and apply rules on the modeled repo

This will be usually done by executing the following:
```
time python app.py direct -s minefield/redhat8/ -d minefield/eurolinux8/ -T 4 -r True -p BaseOS,AppStream,PowerTools,HighAvailability,ResilientStorage,CodeReady -R CodeReady/PowerTools -C example.json.conf
```
Let's break it down:<br/>
direct - chooses the option to perform compositions in one go (read repos, create rules and apply them).<br/>
-s is the source repo (this is the repo that acts as a model that will tell us where to put each rpm).<br/>
-d is the destination repo (this is the repo that we will actively change).<br/>
-T is the number of threads to use (if omitted, a single thread will run).<br/>
-r tells us if operations should actually be executed (files actually moved/linked, directoris created, etc.).<br/>
-p sets the priorities i.e. the order in which to check directoriesfor packages.<br/>
-R is the replacement, here meaning that CodeReady will be (in the destination) replaced by PowerTools.<br/>
-C is the additional configuration (to create extra hardlinks that would not be created based just on modeling source repo).<br/>

Apart from that, composer also can:
- Create a bash script that recreates a tree-structure of a repository (both remote and local repository) (for test purposes)<br/>
    Example of this is:
    ```
    python app.py fakeremote -i https://repo.eurolinux.local/repo/eurolinux/8/prod/ -b create_eurolinux8.sh
    ```

    and:
    ```
    $ time python app.py maprepo -s minefield/eurolinux8/ -o mapped.euro8.json
    $ python app.py fakerepo -i mapped.euro8.json -b euro8.repo.sh
    ```
    These will create an output bash script with commands creating a repository-tree (with 0-length files).
    This is great for testing purposes.

- Map a (local) repository into a file:<br/>
    Main usage is demonstated above (maprepo option during local repo script creation).

- Save move/link rules for future execution (please note: rules are saved with absolute paths)<br/>
    Example:
    ```
    time python app.py saverules -s minefield/redhat8/ -d minefield/eurolinux8/ -o out.json
    ```

- Apply rules saved previously (note: rules have absolute paths; if base paths change, please edit them directly in the -i json)<br/>
    Example:
    ```
    time python app.py fromrules -i out.json -T 4 -r True
    ```

## Additional configuration
For additional hardlinks, one has to use configuration file.
Configuration may be handled with two formats - the "short" format and the "json" format.
Although "short format takes significantly less space, "json" format is recommended.
Let us take a look at an examples of both:
Short:
```
...
el-backgrounds-84.4-3.* -> BaseOS:x86_64/AppStream:x86_64
...
```
Json:
```
[
    {
        "file_pattern": "el-backgrounds-84.4-3.*",
        "src_repo": "BaseOS",
        "src_arch": "x86_64",
        "dst_repo": "AppStream",
        "dst_arch": "x86_64"
    },
    {
        ...
    },
    ...
]
```
These files do the same - they look for file patterns and create a link from source (BaseOS, x86_64) into a destination (AppStream, x86_64).
Each field is actually a regular expression pattern and may be written as such.
All matching files will be taken under account when executing the rule.

For a more advanced use please consider this rule:
```
...
el-backgrounds-84.4-[12].* -> BaseOS:[^i].*
...
```
or as a json:
```
[
    {
        "file_pattern": "el-backgrounds-84.4-[12].*",
        "src_repo": "BaseOS",
        "src_arch": "[^i].*"
    },
    {
        ...
    },
    ...
]
```
Destination places are optional. If they are not specified, a copy of the original match is assumed.
Meaning - in the above example, each file matching a pattern will be moved from BaseOS into BaseOS (and arch the package is found under - matching as long as the arch does not contain "i" [as the first character - see note]; which practically means i686)
> Note:
> The full pattern created from these rules is:
> ```
> pattern = re.compile(f"{rule['src_repo']}:{rule['src_arch']}:.*?:{rule['file_pattern']}")
> ```
> With matched keys being of form:
> ```
> BaseOS:x86_64:Packages/e:el-indexhtml-8-8.el8.noarch.rpm
> [Repo]:[Arch]:[Placement]:[Filename]
> ```
> Therefore please be very aware, when using beginning of line (^) and end of line ($) matching - they may mess up the match at times.

Please see `example.json.conf` and `example.short.conf` for a complete rule-file demonstration.

## Use case
Scenario: Testing out composer.

1. Creating fake repos:
    ```
    # Note: creating "remote" fake repositories (fakerepo) will take time (most likely up to 20 minutes, depending on the connection)
    [~/composer]$ python app.py fakeremote -i https://repo.eurolinux.local/repo/redhat/8 -b create_redhat8.sh
    [~/composer]$ python app.py fakeremote -i https://repo.eurolinux.local/repo/eurolinux/8/prod/ -b create_eurolinux8.sh
    [~/composer]$ mkdir -p repo/redhat8
    [~/composer]$ mkdir -p repo/eurolinux8
    [~/composer]$ cd repo/redhat8/
    [~/composer/repo/redhat8]$ bash ../../create_redhat8.sh # important - fakerepo scripts create trees in-place - be sure to position yourself in the right directory(!)
    [~/composer/repo/redhat8]$ cd ../eurolinux8/
    [~/composer/repo/eurolinux8]$ bash ../../create_eurolinux8.sh
    [~/composer/repo/eurolinux8]$ cd ../..
    ```

2. Recreating state from before partitioning
    ```
    [~/composer]$ rm -rf minefield/ && cp -r repo/ minefield/ && find repo/ -iname "*debug*" | awk '/-debug(info|source)-/{ t=$1; sub(/repo/, "minefield", t); sub(/debug\//, "all/", t); print t}' | xargs -i touch {} && rm -rf minefield/eurolinux8/*/*/{os,debug}
    ```

3. Applying composer:
    ```
    [~/composer]$ time python app.py direct -s minefield/redhat8/ -d minefield/eurolinux8/ -r True -T 4 -p BaseOS,AppStream,PowerTools,HighAvailability,ResilientStorage,CodeReady -R CodeReady/PowerTools -C example.json.conf
    ```

4. Comparing results
    ```
    [~/composer]$ vimdiff <(find minefield/eurolinux8/ -iname *.rpm|sed "s/^minefield//g"|sort) <(find repo/eurolinux8/ -iname *.rpm|sed "s/^repo//g"|sort)
    ```
