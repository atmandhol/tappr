## tappr

`tappr` is CLI for Tanzu Application Platform related stuff. This is super unofficial and I write and maintain features that are helpful to me and my team at VMware.

### Prerequisites
- Install the latest Python 3.x.x from [python.org](https://www.python.org/downloads/)

### Install tappr
Recommended way to install tappr is by using [pipx](https://pypa.github.io/pipx/#install-pipx).
You can `brew` install `pipx` as follows:

```bash
brew install pipx
pipx ensurepath
```

To Install latest:
```
pipx install git+https://github.com/atmandhol/tappr.git
```

To Install a specific version
```
pipx install git+https://github.com/atmandhol/tappr.git@version
```

- Run `tappr` on your command line to confirm if its installed

## Setup for Local build

* Install `poetry` on the system level using 
```
pip3 install poetry
```
* Create a virtualenv `tappr` using virtualenvwrapper and run install
```
mkvirtualenv tappr -p python3
poetry install
```

### Build
Run the following poetry command
```bash
$ poetry build
```
This will generate a dist folder with a whl file and a tar.gz file.

### Auto Generate Docs
Generate the docs automatically using typer-cli
```
$ ./hack/generate_readme.sh
```
