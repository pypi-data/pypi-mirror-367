# Infrastructure Launcher

The launcher of the Dead-Hosts infrastructure and project.

## Installation

```shell
pip3 install --user dead-hosts-launcher
```

## Configuration

To work, the launcher will look for a file named :code:`info.json` in
your current directory.

The file should look like follow:

```json
{
    "currently_under_test": false, # Don't touch this.
    "custom_pyfunceble_config": {}, # Put your PyFunceble custom configuration here.
    "days_until_next_test": 0.0,  # Ask an admin. Otherwise, this is the number of days between each authorizations.
    "name": "[repository-name]",  # The name of the current repository. WARNING: Partially autocompleted under CI.
    "own_management": false,  # You are the one managing the PyFunceble configuration.
    "ping": [],  # Put your GitHub username here to get a mention at the end of the test of your file.
    "ping_enabled": false,  # Enable the ping through GitHub.
    "raw_link": "[URL]" # Put the link to your file. Or leave empty and fill the origin.list file.
}
```

### Persistent configuration

The launcher has some hard-coded configuration that can't be changed. Even
if you try to overwrite them, the configuration will just overwrite them.

### PyFunceble configuration

Please consider the following as a flatten representation of the PyFunceble
configuration. Meaning that each :code:`.` is a nested dictionary.

```json
{
    "cli_testing.cooldown_time": 1.25,
    "cli_testing.display_mode.execution_time": True,
    "cli_testing.ci.max_exec_minutes": 20,
    "cli_testing.max_workers": 1,
}
```

## Usage

```shell
usage: dead-hosts-launcher [-h] [-d] [-s] [-e] [--authorize] [--update] [-v]

The launcher of the Dead-Hosts infrastructure.

options:
  -h, --help     show this help message and exit
  -d, --debug    Activate the logging in verbose mode..
  -s, --save     Declare a test as 'to be continued'.
  -e, --end      Declare a test as completely finished and generate `clean.list`.
  --authorize    Try to authorize the next job.
  --update       Update the local infrastructure.
  -v, --version  Show the version of and exit.

Crafted with ♥ by Nissar Chababy (@funilrys)
```

# License

```text
MIT License

Copyright (c) 2019, 2020, 2021, 2022, 2023, 2024, 2025 Dead Hosts Contributors
Copyright (c) 2019, 2020. 2021, 2022, 2023, 2024 Nissar Chababy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```