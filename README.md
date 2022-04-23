# tappr

`tappr` is CLI for Tanzu Application Platform related stuff. This is super unofficial and I write and maintain features that are helpful to me and my team at VMware.

## Features

- Install TAP on any K8s cluster using a single `tappr tap install` command.
- Setup Developer namespace for workloads creation on any TAP cluster using `tappr tap setup` command.
- Create/Delete k8s clusters suitable for TAP deployment using `tappr create/tappr delete` commands. (`gke` and `kind` supported. Other `cloud` providers will be added later)
- Store your Tanzu Network, Registry and other useful credentials once, which are then seamlessly used throughout `tappr` commands.
- Mini test-framework that can be used to write `bash` based integration tests.

### Upcoming

- Edit TAP installations on the fly using `tappr tap edit`.
- Supply chain and Workloads visualizer across multiple TAP clusters using `tappr tap visualize`.

### Utils

- Auto generate `changelog` on a project using conventional commits standard using `tappr utils changelog`.
- Auto generate `release` notes on any Git project using `tappr utils release`
- Check/Set up your local environment for useful tools in life of a k8s developer/operator using `tappr utils local` commands.

## Documentation
[CLI Usage documentation](docs/USAGE.md) is auto generated and is located in the `docs` folder.

## Install tappr
### Prerequisites
- Install the latest Python 3.x.x from [python.org](https://www.python.org/downloads/)

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
Generate the usage docs automatically using the `generate_paparwork` script in the hack folder.
```
$ ./hack/generate_paperwork.sh
```