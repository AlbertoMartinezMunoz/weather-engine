# python-project-template

Template for developing new python projects

## Run

## Setup

### Python

Install Python3

```shell
sudo apt update
sudo apt install python3
```

Install pip3

```shell
sudo apt-get install python3-pip
python3 -m pip install --user --upgrade pip
```

#### Python Virtual Environment

Install venv

```shell
sudo apt-get install python3-venv
```

The scripts in this folder are designed to be set up using a Python virtual environment (`venv`). The first time you want to set up the application on Linux, execute the steps below on a shell:

```sh
# Set up a virtual environment
python3 -m venv .venv

# Activate it
. .venv/bin/activate

# Install necessary packages and upgrade
pip install -r requirements.txt --upgrade
```

Please do _not_ use `sudo` within a virtual environment; it will not work as intended. Instead, set up your system correctly so that you do not need root access to run the script.

On Windows Command Prompt, the commands are slightly different:

```bat
REM Set up a virtual environment
python3 -m venv .venv

REM Activate it
CALL .venv\Scripts\activate.bat

REM Install necessary packages and upgrade
pip install -r requirements.txt --upgrade
```

For more information, e.g., using `venv` with Windows PowerShell, see the [official Python venv documentation](https://docs.python.org/3/library/venv.html).

To use the application again at a later time, you only need to perform the activation step.

#### Create/Update Requirements File
You can use the following code to generate a requirements.txt file:

```sh
pip freeze > requirements.txt
```

However, instead of adding all the dependencies to the `requirements.txt` file, we can append only the packages we need to install without deppendencies and let pip t solve the dependencies:

```sh
pip freeze | grep "PACKAGE_NAME==" >> requirements.txt
```

To start intalling libraries again for fresh, you can update the dependencies list and then uninstall all the dependencies:

```sh
pip freeze > requirements_old.txt
pip uninstall -y -r requirements_old.txt
```

### Python Unitary Testing

#### Pytest for Unit Testing

To use Pytest for unit testing, we first need to install it. We can install Pytest by writing the following command in the command prompt:

```sh
pip install pytest
```

The test files in Pytest should either start with `test_` or end with `_test`. Also, the test functions/methods' name should start with `test_` or `test`. In case we are making a test class, we need to start its name with `Test` or `Test_`.

Pytest unit test file simple template:

```py
import pytest


class TestClassPytest:
    @pytest.fixture
    def set_up(self):
        c = data
        yield c

    def test_given_class_when_method_expected_str_then_return_expected_str(self, set_up):
        c = set_up
        assert expected_data == c
```

To run the tests:

```sh
pytest -v -s ./src
```

#### Unittest

Test file simple template:

```py
import unittest


class TestSum(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")


if __name__ == "__main__":
    unittest.main()
```

To skip a test `@unittest.skip("<message>")` should be added in the source code before the test we want to skip:

```py
@unittest.skip("Should be refactored to work")
def test_to_skip(self):
```

To run the unit tests in the test root directory:

```shell
python3 -m unittest
```

You can select which is the root directory:

```shell
python3 -m unittest discover <test_directory>
```

To run the test in this project structure:

```shell
python -m unittest discover -s ./src -p "test_*.py" -v
```

To select the test of one test suite:

```shell
python3 -m unittest discover -k <test_suite_name> <project_source_dir>
```

To call one test case we use the test case name. To only run the test `dataset.utest.dataset_test.TestSuiteNNN.test_xxx` we use `test_xxx`:

```console
$ python -m unittest discover -s ./src/ -p "test_*.py" -v -k "test_xxx"
test_xxx (dataset.utest.dataset_test.TestSuiteNNN.test_xxx) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.230s

OK

```

To run the whole test suite NNN, we use the the test suite name `TestSuiteNNN`:

```console
$ python -m unittest discover -s ./src/ -p "test_*.py"  -v -k "TestSuiteNNN"
test_yyy (dataset.utest.dataset_test.TestSuiteNNN.test_yyy) ... ok
test_xxx (dataset.utest.dataset_test.TestSuiteNNN.test_xxx) ... ok
test_zzz (dataset.utest.dataset_test.TestSuiteNNN.test_zzz) ... ok

----------------------------------------------------------------------
Ran 3 tests in 3.036s

OK
```

### Pre-Commit Hooks

Before you can run hooks, you need to have the pre-commit package manager installed.

```sh
pip install pre-commit
pre-commit --version
```

In a python project, add the `pre-commit` package to your requirements.txt

After installing, create a file named `.pre-commit-config.yaml`. A very basic configuration file can be created using `pre-commit sample-config`

```console
$ pre-commit sample-config
# See https://pre-commit.com for more information
# See https://pre-commit.com/hooks.html for more hooks
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v3.2.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
```

After defining the configuration file, we have to install the git hook scripts

```console
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

It's usually a good idea to run the hooks against all of the files when adding new hooks (usually pre-commit will only run on the changed files during git hooks)

```console
$ pre-commit run --all-files
[INFO] Initializing environment for https://github.com/pre-commit/pre-commit-hooks.
[INFO] Initializing environment for https://github.com/psf/black.
[INFO] Installing environment for https://github.com/pre-commit/pre-commit-hooks.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
[INFO] Installing environment for https://github.com/psf/black.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
Check Yaml...............................................................Passed
Fix End of Files.........................................................Passed
Trim Trailing Whitespace.................................................Failed
- hook id: trailing-whitespace
- exit code: 1

Files were modified by this hook. Additional output:

Fixing sample.py

```

### Build UML Diagrams

The C4 diagrams are made using [PlantUML](https://plantuml.com/). First, you have to install the `plantuml` package:

```console
sudo apt-get update
sudo apt-get install plantuml
```

Then, to build the diagrams, you only have to run the `plantuml` command:

```console
plantuml -tpng <path-to-the-files>
```
