# `tappr`

CLI for Tanzu Application Platform

**Usage**:

```console
$ tappr [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--verbose / --no-verbose`: Logger verbose flag, Set env_var TAPPR_VERBOSE=true to change default to true.  [default: False]
* `--context TEXT`: Kubernetes context to target from the KUBECONFIG, set env_var TAPPR_K8S_CONTEXT to set default
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `cluster`: Kubernetes cluster CRUD commands
* `gui`: Tanzu Application Platform GUI management.
* `init`: Initialize the tappr cli with required...
* `tap`: Tanzu Application Platform management.
* `utils`: Random utils for making life easier.

## `tappr cluster`

Kubernetes cluster CRUD commands

**Usage**:

```console
$ tappr cluster [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create Kubernetes clusters.
* `delete`: Delete Kubernetes clusters.

### `tappr cluster create`

Create Kubernetes clusters.

**Usage**:

```console
$ tappr cluster create [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `gke`: Create a GKE cluster.
* `kind`: Create a multi-node kind cluster.
* `minikube`: Create a minikube cluster.

#### `tappr cluster create gke`

Create a GKE cluster. Assumes gcloud is set to create clusters.

**Usage**:

```console
$ tappr cluster create gke [OPTIONS]
```

**Options**:

* `--cluster-name TEXT`: Name of the GKE cluster
* `--channel [RAPID|REGULAR|STABLE|None]`: GKE Release Channel  [default: None]
* `--cluster-version TEXT`: auto takes the latest in the channel. You can specify a fixed version as well.  [default: auto]
* `--project TEXT`: Name of the GCP project. If gcloud is pointing to a specific project, it will be automatically picked up
* `--customize / --no-customize`: Customize the default values  [default: False]
* `--region TEXT`: GKE cluster region
* `--num-nodes-per-zone INTEGER`: Number of worker nodes in NodePool per zone
* `--help`: Show this message and exit.

#### `tappr cluster create kind`

Create a multi-node kind cluster.

**Usage**:

```console
$ tappr cluster create kind [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--customize / --no-customize`: Customize the default config file  [default: False]
* `--help`: Show this message and exit.

#### `tappr cluster create minikube`

Create a minikube cluster.

**Usage**:

```console
$ tappr cluster create minikube [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--cpus TEXT`: Number of CPUs to allot for cluster  [default: max]
* `--memory TEXT`: Amount of memory to allot for cluster  [default: max]
* `--driver TEXT`: minikube driver to use to create clusters. Other options are virtualbox, parallels, vmwarefusion, hyperkit, vmware, docker  [default: docker]
* `--embed-certs / --no-embed-certs`: if true, will embed the certs present at $HOME/.minikube/certs/ in kubeconfig  [default: False]
* `--k8s-version TEXT`: Kubernetes version  [default: stable]
* `--dns-domain TEXT`: The cluster dns domain name used in the Kubernetes cluster  [default: cluster.local]
* `--help`: Show this message and exit.

### `tappr cluster delete`

Delete Kubernetes clusters.

**Usage**:

```console
$ tappr cluster delete [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `gke`: Delete a GKE cluster.
* `kind`: Delete a kind cluster.
* `minikube`: Delete a minikube cluster.

#### `tappr cluster delete gke`

Delete a GKE cluster.

**Usage**:

```console
$ tappr cluster delete gke [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--region TEXT`: [default: us-east4]
* `--help`: Show this message and exit.

#### `tappr cluster delete kind`

Delete a kind cluster.

**Usage**:

```console
$ tappr cluster delete kind [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

#### `tappr cluster delete minikube`

Delete a minikube cluster.

**Usage**:

```console
$ tappr cluster delete minikube [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `tappr gui`

Tanzu Application Platform GUI management.

**Usage**:

```console
$ tappr gui [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: Get a list of Clusters tracked by TAP GUI.
* `server-ip`: Get the TAP GUI server external IP.
* `track`: Add cluster credential to TAP GUI for...
* `untrack`: Remove cluster credential from TAP GUI.

### `tappr gui list`

Get a list of Clusters tracked by TAP GUI.

**Usage**:

```console
$ tappr gui list [OPTIONS]
```

**Options**:

* `--namespace TEXT`: TAP installation namespace on the cluster where TAP GUI is located  [default: tap-install]
* `--help`: Show this message and exit.

### `tappr gui server-ip`

Get the TAP GUI server external IP.

**Usage**:

```console
$ tappr gui server-ip [OPTIONS]
```

**Options**:

* `--service TEXT`: [default: server]
* `--namespace TEXT`: [default: tap-gui]
* `--help`: Show this message and exit.

### `tappr gui track`

Add cluster credential to TAP GUI for tracking resources on GUI.

**Usage**:

```console
$ tappr gui track [OPTIONS]
```

**Options**:

* `--namespace TEXT`: TAP installation namespace on the cluster where TAP GUI is located  [default: tap-install]
* `--tap-viewer-sa TEXT`: TAP Viewer service account in the cluster and namespace to be tracked  [default: tap-gui-viewer]
* `--help`: Show this message and exit.

### `tappr gui untrack`

Remove cluster credential from TAP GUI.

**Usage**:

```console
$ tappr gui untrack [OPTIONS]
```

**Options**:

* `--namespace TEXT`: TAP installation namespace on the cluster where TAP GUI is located  [default: tap-install]
* `--help`: Show this message and exit.

## `tappr init`

Initialize the tappr cli with required configuration.

**Usage**:

```console
$ tappr init [OPTIONS]
```

**Options**:

* `--tanzunet-username TEXT`: Tanzu Network Username.
* `--tanzunet-password TEXT`: Tanzu Network Password.
* `--pivnet-uaa-token TEXT`: Pivnet UAA Login Token used to download artifacts.
* `--install-registry-server TEXT`: Registry where the TAP packages are
* `--registry-server TEXT`: Default registry server to use while installing tap. e.g. gcr.io, index.docker.io etc.
* `--registry-tap-package-repo TEXT`: Default registry repo on the registry server to use for relocating TAP packages to.
* `--registry-tbs-repo TEXT`: Default registry repo on the registry server to use for build service. Don't include the registry server or starting /.
* `--registry-username TEXT`: Registry username to use while installing tap
* `--registry-password TEXT`: Registry password to use while installing tap. If using GCR set this as path to jsonkey file.
* `--help`: Show this message and exit.

## `tappr tap`

Tanzu Application Platform management.

**Usage**:

```console
$ tappr tap [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--verbose / --no-verbose`: Logger verbose flag, Set env_var TAPPR_VERBOSE=true to change default to true.  [default: False]
* `--context TEXT`: Kubernetes context to target from the KUBECONFIG, set env_var TAPPR_K8S_CONTEXT to set default
* `--help`: Show this message and exit.

**Commands**:

* `edit`: Modify TAP Installation.
* `ingress-ip`: Get the Tanzu System Ingress External IP of...
* `install`: Install TAP.
* `install-cluster-essentials`: Install only Cluster Essentials.
* `setup`: Setup Developer Namespace.
* `status`: Get TAP installation status.
* `uninstall`: Uninstall TAP.
* `upgrade`: Upgrade TAP to a higher version.

### `tappr tap edit`

Modify TAP Installation.

**Usage**:

```console
$ tappr tap edit [OPTIONS]
```

**Options**:

* `--namespace TEXT`: TAP installation namespace  [default: tap-install]
* `--from-file TEXT`: Yaml file path containing tap values to shallow merge (first level only) with the existing tap values on the cluster. Inline editor is not invoked if this option is used.
* `--force / --no-force`: Force save the changes to the yaml file without any user prompt  [default: False]
* `--show / --no-show`: Show the current content of the tap values file on the cluster in the inline editor. Defaults to false for security purposes.  [default: False]
* `--help`: Show this message and exit.

### `tappr tap ingress-ip`

Get the Tanzu System Ingress External IP of the TAP cluster.

**Usage**:

```console
$ tappr tap ingress-ip [OPTIONS]
```

**Options**:

* `--service TEXT`: [default: envoy]
* `--namespace TEXT`: Tanzu System Ingress installation namespace  [default: tanzu-system-ingress]
* `--help`: Show this message and exit.

### `tappr tap install`

Install TAP. Make sure to run tappr init before installing TAP.

**Usage**:

```console
$ tappr tap install [OPTIONS] PROFILE:[full|full-scan|iterate-local|iterate-slim|iterate-scan|iterate-essentials|iterate-local-essentials|iterate|build|build-slim|build-essential|run|run-local|view] VERSION
```

**Arguments**:

* `PROFILE:[full|full-scan|iterate-local|iterate-slim|iterate-scan|iterate-essentials|iterate-local-essentials|iterate|build|build-slim|build-essential|run|run-local|view]`: [required]
* `VERSION`: [required]

**Options**:

* `--host-os [darwin|linux|windows]`: [default: darwin]
* `--namespace TEXT`: Namespace where TAP should be installed  [default: tap-install]
* `--tap-values-file TEXT`
* `--skip-cluster-essentials / --no-skip-cluster-essentials`: Skip Cluster Essentials installation as its already installed or the user is using TKG or some flavor that already has it.  [default: False]
* `--wait / --no-wait`: Wait for the TAP install to complete  [default: False]
* `--help`: Show this message and exit.

### `tappr tap install-cluster-essentials`

Install only Cluster Essentials.

**Usage**:

```console
$ tappr tap install-cluster-essentials [OPTIONS]
```

**Options**:

* `--host-os [darwin|linux|windows]`: [default: darwin]
* `--help`: Show this message and exit.

### `tappr tap setup`

Setup Developer Namespace.

**Usage**:

```console
$ tappr tap setup [OPTIONS]
```

**Options**:

* `--namespace TEXT`: Developer namespace to setup  [default: default]
* `--help`: Show this message and exit.

### `tappr tap status`

Get TAP installation status.

**Usage**:

```console
$ tappr tap status [OPTIONS]
```

**Options**:

* `--namespace TEXT`: TAP installation namespace  [default: tap-install]
* `--help`: Show this message and exit.

### `tappr tap uninstall`

Uninstall TAP.

**Usage**:

```console
$ tappr tap uninstall [OPTIONS]
```

**Options**:

* `--package TEXT`: Package name to uninstall  [default: tap]
* `--namespace TEXT`: [default: tap-install]
* `--help`: Show this message and exit.

### `tappr tap upgrade`

Upgrade TAP to a higher version.

**Usage**:

```console
$ tappr tap upgrade [OPTIONS] VERSION
```

**Arguments**:

* `VERSION`: [required]

**Options**:

* `--namespace TEXT`: TAP installation namespace  [default: tap-install]
* `--wait / --no-wait`: Wait for the TAP install to complete  [default: False]
* `--help`: Show this message and exit.

## `tappr utils`

Random utils for making life easier.

**Usage**:

```console
$ tappr utils [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `changelog`: Generate changelog from git log.
* `local`: Helpers to setup your local environment.
* `registry`: Manage local docker registry.
* `release`: Generate GitHub/Gitlab release notes from git...
* `test`: Run pre-defined test on the tappr test...

### `tappr utils changelog`

Generate changelog from git log. You will have an easier time creating changelog if you use conventional commits.

Examples:

Generate a changelog for all commits starting from first commit to the tag v0.4.0.

$ tappr utils changelog --log-range v0.4.0

Generate a changelog for commits between tag v0.4.1 to the last commit

$ tappr utils changelog --log-range v0.4.1..HEAD

Generate a changelog for all commits between tag v0.4.1 and v0.5.0

$ tappr utils changelog --log-range v0.4.1..v0.5.0

**Usage**:

```console
$ tappr utils changelog [OPTIONS]
```

**Options**:

* `--log-range TEXT`: Determine which commits gets included for changelog. The log will be grouped by tags regardless of the range.  [default: all]
* `--ignore-dependabot-commits / --no-ignore-dependabot-commits`: Dependabot commits will be ignored from the changelog  [default: True]
* `--ignore-docs-commits / --no-ignore-docs-commits`: Docs commits will be ignored from the changelog  [default: True]
* `--output TEXT`: Filename where the changelog output will be stored  [default: stdout]
* `--help`: Show this message and exit.

### `tappr utils local`

Helpers to setup your local environment.

**Usage**:

```console
$ tappr utils local [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `check`: Run pre-checks for running tappr on the local...
* `cleanup`: Cleans up tanzu directories and CLI for a...
* `setup`: Set up your local with all required tools.

#### `tappr utils local check`

Run pre-checks for running tappr on the local environment.

**Usage**:

```console
$ tappr utils local check [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `tappr utils local cleanup`

Cleans up tanzu directories and CLI for a fresh installation.

**Usage**:

```console
$ tappr utils local cleanup [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `tappr utils local setup`

Set up your local with all required tools.

**Usage**:

```console
$ tappr utils local setup [OPTIONS]
```

**Options**:

* `--interactive / --no-interactive`: [default: True]
* `--help`: Show this message and exit.

### `tappr utils registry`

Manage local docker registry.

**Usage**:

```console
$ tappr utils registry [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `start`
* `stop`

#### `tappr utils registry start`

**Usage**:

```console
$ tappr utils registry start [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `tappr utils registry stop`

**Usage**:

```console
$ tappr utils registry stop [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `tappr utils release`

Generate GitHub/Gitlab release notes from git log. You will have an easier time creating release notes if you use conventional commits.

since_ver: is the previous version. This should be in a valid semver format.

release_ver: is the version you are trying to release. This should be in a valid semver format.

template_file: markdown template file to be used for creating releases

pr_path: is the path to PRs. For e.g. for this repo, its https://github.com/atmandhol/tappr/pull/. This is needed to generate PR links automatically in the release notes

output: Defaults to stdout. Change to something else for a file output

**Usage**:

```console
$ tappr utils release [OPTIONS] SINCE_VER RELEASE_VER TEMPLATE_FILE PR_PATH
```

**Arguments**:

* `SINCE_VER`: [required]
* `RELEASE_VER`: [required]
* `TEMPLATE_FILE`: [required]
* `PR_PATH`: [required]

**Options**:

* `--ignore-dependabot-commits / --no-ignore-dependabot-commits`: Dependabot commits will be ignored from the release notes  [default: True]
* `--ignore-docs-commits / --no-ignore-docs-commits`: Docs commits will be ignored from the release notes  [default: True]
* `--output TEXT`: Filename where the release notes output will be stored  [default: stdout]
* `--help`: Show this message and exit.

### `tappr utils test`

Run pre-defined test on the tappr test framework.

- test_file: test yaml file that defines the tests to run and context

output: Defaults to stdout. Change to something else for a file output

**Usage**:

```console
$ tappr utils test [OPTIONS] TEST_FILE
```

**Arguments**:

* `TEST_FILE`: [required]

**Options**:

* `--output TEXT`: [default: stdout]
* `--help`: Show this message and exit.

