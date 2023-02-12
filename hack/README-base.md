# tappr

`tappr` makes it easy to create Kubernetes clusters on your local machine and some cloud providers as well as install/manage Tanzu Application Platform installs on it. The CLI can be used by developers to do local development as well as in the CI to run end-2-end tests on a Kubernetes cluster with TAP installed.

## Features

- Create/Delete k8s clusters suitable for TAP deployment using `tappr cluster create/tappr cluster delete` commands.
  - `kind`, `minikube`, and `GKE` are supported as of now. Other providers will be added in the future.
  - GKE cluster creation requires `gcloud` CLI installed and configured using `gcloud auth` or `service-accounts`.
- Install TAP on any K8s cluster using a single `tappr tap install` command.
- Upgrade TAP using `tappr tap upgrade` command. 
- Setup Developer namespace for workloads creation on any TAP cluster using `tappr tap setup` command. This command will help setup your registry credentials, tekton test pipelines and scan policies for testing scanning supply chain.
- Edit TAP installations on the fly using `tappr tap edit`
- Easily connect your TAP GUI with other clusters in a multi-cluster environment using `tappr gui track/untrack` commands.
- Check your local for useful utilities that are used by `tappr`. You can install missing ones using `tappr utils local setup`.
- Store your credentials once, which are then seamlessly used throughout `tappr` commands.

## Getting Started
### Install tappr
#### Prerequisites
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

If you already have `tappr` installed from latest, and want to pull in the new changes:
```
pipx reinstall tappr
```


To Install a specific version of tappr:
```
pipx install git+https://github.com/atmandhol/tappr.git@version
```

- Run `tappr` on your command line to confirm if its installed

### Setup Environment to run tappr
- Start by running `tappr utils local check` command to see if all the required tools to use `tappr` are installed or not.

![tappr utils local check](assets/local-check.png)

- Run `tappr utils local setup` command and install the missing tools. 
All prompts defaults to `No` you can keep hitting enter till you get to the tool that is missing.
- Run `tappr init` to set up credentials once.

![tappr init](assets/init.png)

## Usage
Check the [Full CLI Usage documentation](docs/USAGE.md) for everything that is possible.
- Run `tappr cluster create/delete` commands to create K8s clusters on different providers.
- Run `tappr tap install {profile} {version}` command to install TAP on it along with Cluster Essentials. You can skip the Cluster essential install using the `--skip-cluster-essentials` flag.
You can also install only Cluster Essentials using `tappr tap install-cluster-essentials` command.
- Run `tappr tap edit --show` to update your TAP install with your custom settings.
- Run `tappr tap upgrade {version}` command to install TAP on it.

Use the `--help` global flag to see the options and possible values you can provide.

## Use with minikube

```bash
# Create a minikube cluster. You can use --help on this command to see more flags to customize the minikube cluster
tappr cluster create minikube tap-local

# Start a tunnel in a separate terminal using (requires sudo)
minikube tunnel --profile tap-local

# Install TAP. Only install full profile if your machine can handle it :D.
tappr tap install full 1.4.0

# After the install is complete, you can access TAP GUI on 
# http://tap-gui.127.0.0.1.nip.io

# You can also set a different ingress-domain if you like 
# using the --ingress-domain flag as long as it routes to a 
# proper IP in your /etc/hosts file
```

## Utils

- Mini test-framework that can be used to write `bash` based integration tests.
- Auto generate `changelog` on a project using conventional commits standard using `tappr utils changelog`.
- Auto generate `release` notes on any Git project using `tappr utils release`
- Check/Set up your local environment for useful tools in life of a k8s developer/operator using `tappr utils local` commands.

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

### Upgrade dependencies
Run the following poetry command
```bash
$ poetry update
```

### Auto Generate Docs
Generate the usage docs automatically using the `generate_paparwork` script in the hack folder.
```
$ ./hack/generate_paperwork.sh
```
