![](https://github.com/hasii2011/code-ally-basic/blob/master/developer/agpl-license-web-badge-version-2-256x48.png "AGPL")

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/hasii2011/buildlackey/tree/master.svg?style=shield)](https://dl.circleci.com/status-badge/redirect/gh/hasii2011/buildlackey/tree/master)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![PyPI version](https://badge.fury.io/py/buildlackey.svg)](https://badge.fury.io/py/buildlackey)

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

## Rationale

These utilities are meant to help me with my python packages and their maintenance.

## Dependencies

These utilities work best using the following opinionated dependencies

* Python [virtual environments](https://realpython.com/python-virtual-environments-a-primer/) on a per project/repository basis
*  [direnv](https://direnv.net) to set up the project virtual environment and any necessary environment variables
* Building using setup.py and the [build](https://pypi.org/project/build/) module to create source and binary distributions.  The documentation is [here](https://pypa-build.readthedocs.io/en/stable/)
* Using [pypi](https://pypi.org/) for source and binary distributions
* A correctly setup [$(HOME)/.pypirc](https://packaging.python.org/en/latest/specifications/pypirc/) for easy interaction with [twine](https://pypi.org/project/twine/) and [pypi](https://pypi.org/)

## Required Environment Variables

The above commands depend on the following environment variables.

```bash
PROJECTS_BASE -  The local directory where the python projects are based
PROJECT       -  The name of the project;  It should be a directory name
```

 An example, of a PROJECTS_BASE is:

```bash
export PROJECTS_BASE="${HOME}/PycharmProjects" 
```

This should be set in your shell startup script.  For example `.bash_profile`.

The PROJECT environment variable should be set on a project by project basis.  I recommend you use [direnv](https://direnv.net) to manage these.  An example of a .envrc follows:

```bash
export PROJECT=buildlackey
source pyenv-3.10.6/bin/activate
```


## Python Console Scripts

The Python command line scripts in buildlackey automate the maintenance process by providing the following capabilities

* unittests -- Runs the project's unit tests
* runmypy   -- Run the [mypy](https://www.mypy-lang.org) static type checker 
* package   --  Creates a pypi package using [build](https://pypi.org/project/build/) and setup.py 
* cleanup   -- Deletes the artifacts created by `package`
* prodpush  -- Pushes the built package to [pypi](https://pypi.org)

## Usage

* unittests
```text
Usage: unittests [OPTIONS]

  Runs the unit tests for the project specified by the environment variables listed below.
  This command differs from the 'runtests' command in that it uses the unit test TestLoader
  discovery mechanism

  Environment Variables

      PROJECTS_BASE -  The local directory where the python projects are based
      PROJECT       -  The name of the project;  It should be a directory name

  However, if one or the other is not defined the command assumes it is executing in a CI
  environment and thus the current working directory is the project base directory.
  
  Legal values for -w/--warning are:

      default
      error
      always
      module
      once
      ignore      This is the default
  
  The default pattern is 'Test*.py'
  
  Legal values for -v/--verbosity are:
      quiet
      default     This is the default 🧐
      verbose
      loud

  The -h/--html flag runs the HTMLTestRunner and places the reports in the
  'html_unit_test_reports' directory

  The -r/--report-name options names the HTML Test report

  The -s/--source option specifies the project subdirectory where the Python
  source code resides. The source default value is 'src' 

Options:
  --version               Show the version and exit.
  -w, --warning TEXT      Use this option to control Python warnings
  -v, --verbosity TEXT    How verbose to be
  -p, --pattern TEXT      Test files that match pattern will be loaded
  -h, --html              Run the HTML rest runner
  -r, --report-name TEXT  The HTML test report name
  -s, --source TEXT       The project subdirectory where the source code
                          resides
  --help                  Show this message and exit.

```

* runmypy
```text
Usage: runmypy [OPTIONS]

  Runs the mypy checks for the project specified by the following environment variables
  
      PROJECTS_BASE -  The local directory where the python projects are based
      PROJECT       -  The name of the project;  It should be a directory name

  PROJECT is overridden if the developer specifies a package name

  The -p/--package-name option to change the package name when it does not
  much the project name

  The -d/--delete-cache option allows the developer to delete the default mypy
  cache prior to running the command

  The -s/--source option specifies the project subdirectory where the Python
  source code resides. The source default value is 'src'

Options:
  --version                Show the version and exit.
  -p, --package-name TEXT  Use this option when the package name does not
                           match the project name
  -d, --delete-cache       Delete .mypy_cache prior to running
  -s, --source TEXT        The project subdirectory where the source code
                           resides
  --help                   Show this message and exit.

  Written by Humberto A. Sanchez II (humberto.a.sanchez.ii@gmail.com)

```
* cleanup

```text
Usage: cleanup [OPTIONS]

  Clean the build artifacts for the project specified by the following environment variables
  
      PROJECTS_BASE -  The local directory where the python projects are based
      PROJECT       -  The name of the project;  It should be a directory name

  PROJECT is overridden if the developer specifies a package name

Options:
  --version                    Show the version and exit.
  -p, --package-name TEXT      Use this option when the package name does not
                               match the project name
  -a, --application-name TEXT  Use this option when the generated application
                               name does not match the project name
  --help                       Show this message and exit.

```

* package
```text
Usage: package [OPTIONS]

  Creates the deployable for the project specified by the environment variables listed below
  
  Use the -i/--input-file option to specify a set of custom commands to execute to build
  your deployable

  Environment Variables       PROJECTS_BASE -  The local directory where the
  python projects are based   PROJECT       -  The name of the project;  It
  should be a directory name

Options:
  --version              Show the version and exit.
  -i, --input-file TEXT  Use input file to specify a set of commands to
                         execute
  --help                 Show this message and exit.

```
* prodpush
```text
Usage: prodpush [OPTIONS]

  Pushes the deployable to pypi.  The project is specified by the following environment variables
  
      PROJECTS_BASE -  The local directory where the python projects are based
      PROJECT       -  The name of the project;  It should be a directory name

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

```

___

Written by <a href="mailto:email@humberto.a.sanchez.ii@gmail.com?subject=Hello Humberto">Humberto A. Sanchez II</a>  (C) 2025

---

## Note
For all kind of problems, requests, enhancements, bug reports, etc.,
please drop me an e-mail.


![Humberto's Modified Logo](https://raw.githubusercontent.com/wiki/hasii2011/gittodoistclone/images/SillyGitHub.png)

I am concerned about GitHub's Copilot project



I urge you to read about the
[Give up GitHub](https://GiveUpGitHub.org) campaign from[the Software Freedom Conservancy](https://sfconservancy.org).

While I do not advocate for all the issues listed there I do not like that a company like Microsoft may profit from open source projects.

I continue to use GitHub because it offers the services I need for free.  But, I continue to monitor their terms of service.

Any use of this project's code by GitHub Copilot, past or present, is done without my permission.  I do not consent to GitHub's use of this project's code in Copilot.
