# `tappr`

**Usage**:

```console
$ tappr [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--verbose / --no-verbose`: [default: False]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `create`: Create k8s clusters.
* `delete`: Delete k8s clusters.
* `init`: Initialize the tappr cli with required creds.
* `tap`: Tanzu Application Platform management.
* `test`: Run pre-defined test on the tappr test...
* `utils`: Random utils for making life easier.

## `tappr create`

Create k8s clusters.

**Usage**:

```console
$ tappr create [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `gke`: Create a GKE cluster.
* `kind`: Create a multi-node kind cluster.

### `tappr create gke`

Create a GKE cluster. Assumes gcloud is set to create clusters.

**Usage**:

```console
$ tappr create gke [OPTIONS]
```

**Options**:

* `--cluster-name TEXT`
* `--project TEXT`
* `--gcp-json TEXT`: A json file to override values in artifacts/gke_defaults.json
* `--help`: Show this message and exit.

### `tappr create kind`

Create a multi-node kind cluster.

**Usage**:

```console
$ tappr create kind [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `tappr delete`

Delete k8s clusters.

**Usage**:

```console
$ tappr delete [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `gke`: Delete a GKE cluster.
* `kind`: Delete a kind cluster.

### `tappr delete gke`

Delete a GKE cluster.

**Usage**:

```console
$ tappr delete gke [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--region TEXT`: [default: us-east4]
* `--help`: Show this message and exit.

### `tappr delete kind`

Delete a kind cluster.

**Usage**:

```console
$ tappr delete kind [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `tappr init`

Initialize the tappr cli with required creds.

**Usage**:

```console
$ tappr init [OPTIONS]
```

**Options**:

* `--tanzunet-username TEXT`: Tanzu Network Username.
* `--tanzunet-password TEXT`: Tanzu Network Password.
* `--pivnet-uaa-token TEXT`: Pivnet UAA Login Token used to download artifacts.
* `--default-registry-server TEXT`: Default registry server to use while installing tap. e.g. gcr.io, index.docker.io etc.
* `--default-registry-repo TEXT`: Default registry repo on the registry server to use for build service. Don't include the registry server or starting /.
* `--default-tap-install-registry TEXT`: Default registry to use while installing tap.  [default: registry.tanzu.vmware.com]
* `--default-registry-username TEXT`: Registry username to use while installing tap
* `--default-registry-password TEXT`: Registry password to use while installing tap. If using GCR set this as path to jsonkey file.
* `--vmware-username TEXT`: VMWare username
* `--vmware-password TEXT`: VMWare password
* `--help`: Show this message and exit.

## `tappr tap`

Tanzu Application Platform management.

**Usage**:

```console
$ tappr tap [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `edit`: Edit tap-values yaml file.
* `install`: Install TAP.
* `setup`: Setup Dev Namespace with Git and Registry...

### `tappr tap edit`

Edit tap-values yaml file.

**Usage**:

```console
$ tappr tap edit [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `tappr tap install`

Install TAP. Make sure to run tappr init before installing TAP.

**Usage**:

```console
$ tappr tap install [OPTIONS] PROFILE:[iterate-local|iterate-slim|iterate] VERSION
```

**Arguments**:

* `PROFILE:[iterate-local|iterate-slim|iterate]`: [required]
* `VERSION`: [required]

**Options**:

* `--host-os [darwin|linux|windows]`: [default: darwin]
* `--tap-values-file TEXT`
* `--help`: Show this message and exit.

### `tappr tap setup`

Setup Dev Namespace with Git and Registry secrets.

**Usage**:

```console
$ tappr tap setup [OPTIONS]
```

**Options**:

* `--namespace TEXT`: [default: default]
* `--help`: Show this message and exit.

## `tappr test`

Run pre-defined test on the tappr test framework.

- test_file: test yaml file that defines the tests to run and context

output: Defaults to stdout. Change to something else for a file output

**Usage**:

```console
$ tappr test [OPTIONS] TEST_FILE
```

**Arguments**:

* `TEST_FILE`: [required]

**Options**:

* `--output TEXT`: [default: stdout]
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

# `tappr`

**Usage**:

```console
$ tappr [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--verbose / --no-verbose`: [default: False]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `create`: Create k8s clusters.
* `delete`: Delete k8s clusters.
* `init`: Initialize the tappr cli with required creds.
* `tap`: Tanzu Application Platform management.
* `test`: Run pre-defined test on the tappr test...
* `utils`: Random utils for making life easier.

## `tappr create`

Create k8s clusters.

**Usage**:

```console
$ tappr create [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `gke`: Create a GKE cluster.
* `kind`: Create a multi-node kind cluster.

### `tappr create gke`

Create a GKE cluster. Assumes gcloud is set to create clusters.

**Usage**:

```console
$ tappr create gke [OPTIONS]
```

**Options**:

* `--cluster-name TEXT`
* `--project TEXT`
* `--gcp-json TEXT`: A json file to override values in artifacts/gke_defaults.json
* `--help`: Show this message and exit.

### `tappr create kind`

Create a multi-node kind cluster.

**Usage**:

```console
$ tappr create kind [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `tappr delete`

Delete k8s clusters.

**Usage**:

```console
$ tappr delete [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `gke`: Delete a GKE cluster.
* `kind`: Delete a kind cluster.

### `tappr delete gke`

Delete a GKE cluster.

**Usage**:

```console
$ tappr delete gke [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--region TEXT`: [default: us-east4]
* `--help`: Show this message and exit.

### `tappr delete kind`

Delete a kind cluster.

**Usage**:

```console
$ tappr delete kind [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `tappr init`

Initialize the tappr cli with required creds.

**Usage**:

```console
$ tappr init [OPTIONS]
```

**Options**:

* `--tanzunet-username TEXT`: Tanzu Network Username.
* `--tanzunet-password TEXT`: Tanzu Network Password.
* `--pivnet-uaa-token TEXT`: Pivnet UAA Login Token used to download artifacts.
* `--default-registry-server TEXT`: Default registry server to use while installing tap. e.g. gcr.io, index.docker.io etc.
* `--default-registry-repo TEXT`: Default registry repo on the registry server to use for build service. Don't include the registry server or starting /.
* `--default-tap-install-registry TEXT`: Default registry to use while installing tap.  [default: registry.tanzu.vmware.com]
* `--default-registry-username TEXT`: Registry username to use while installing tap
* `--default-registry-password TEXT`: Registry password to use while installing tap. If using GCR set this as path to jsonkey file.
* `--vmware-username TEXT`: VMWare username
* `--vmware-password TEXT`: VMWare password
* `--help`: Show this message and exit.

## `tappr tap`

Tanzu Application Platform management.

**Usage**:

```console
$ tappr tap [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `edit`: Edit tap-values yaml file.
* `install`: Install TAP.
* `setup`: Setup Dev Namespace with Git and Registry...

### `tappr tap edit`

Edit tap-values yaml file.

**Usage**:

```console
$ tappr tap edit [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `tappr tap install`

Install TAP. Make sure to run tappr init before installing TAP.

**Usage**:

```console
$ tappr tap install [OPTIONS] PROFILE:[iterate-local|iterate-slim|iterate] VERSION
```

**Arguments**:

* `PROFILE:[iterate-local|iterate-slim|iterate]`: [required]
* `VERSION`: [required]

**Options**:

* `--host-os [darwin|linux|windows]`: [default: darwin]
* `--tap-values-file TEXT`
* `--help`: Show this message and exit.

### `tappr tap setup`

Setup Dev Namespace with Git and Registry secrets.

**Usage**:

```console
$ tappr tap setup [OPTIONS]
```

**Options**:

* `--namespace TEXT`: [default: default]
* `--help`: Show this message and exit.

## `tappr test`

Run pre-defined test on the tappr test framework.

- test_file: test yaml file that defines the tests to run and context

output: Defaults to stdout. Change to something else for a file output

**Usage**:

```console
$ tappr test [OPTIONS] TEST_FILE
```

**Arguments**:

* `TEST_FILE`: [required]

**Options**:

* `--output TEXT`: [default: stdout]
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

# `tappr`

**Usage**:

```console
$ tappr [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--verbose / --no-verbose`: [default: False]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `create`: Create k8s clusters.
* `delete`: Delete k8s clusters.
* `init`: Initialize the tappr cli with required creds.
* `tap`: Tanzu Application Platform management.
* `test`: Run pre-defined test on the tappr test...
* `utils`: Random utils for making life easier.

## `tappr create`

Create k8s clusters.

**Usage**:

```console
$ tappr create [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `gke`: Create a GKE cluster.
* `kind`: Create a multi-node kind cluster.

### `tappr create gke`

Create a GKE cluster. Assumes gcloud is set to create clusters.

**Usage**:

```console
$ tappr create gke [OPTIONS]
```

**Options**:

* `--cluster-name TEXT`
* `--project TEXT`
* `--gcp-json TEXT`: A json file to override values in artifacts/gke_defaults.json
* `--help`: Show this message and exit.

### `tappr create kind`

Create a multi-node kind cluster.

**Usage**:

```console
$ tappr create kind [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `tappr delete`

Delete k8s clusters.

**Usage**:

```console
$ tappr delete [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `gke`: Delete a GKE cluster.
* `kind`: Delete a kind cluster.

### `tappr delete gke`

Delete a GKE cluster.

**Usage**:

```console
$ tappr delete gke [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--region TEXT`: [default: us-east4]
* `--help`: Show this message and exit.

### `tappr delete kind`

Delete a kind cluster.

**Usage**:

```console
$ tappr delete kind [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `tappr init`

Initialize the tappr cli with required creds.

**Usage**:

```console
$ tappr init [OPTIONS]
```

**Options**:

* `--tanzunet-username TEXT`: Tanzu Network Username.
* `--tanzunet-password TEXT`: Tanzu Network Password.
* `--pivnet-uaa-token TEXT`: Pivnet UAA Login Token used to download artifacts.
* `--default-registry-server TEXT`: Default registry server to use while installing tap. e.g. gcr.io, index.docker.io etc.
* `--default-registry-repo TEXT`: Default registry repo on the registry server to use for build service. Don't include the registry server or starting /.
* `--default-tap-install-registry TEXT`: Default registry to use while installing tap.  [default: registry.tanzu.vmware.com]
* `--default-registry-username TEXT`: Registry username to use while installing tap
* `--default-registry-password TEXT`: Registry password to use while installing tap. If using GCR set this as path to jsonkey file.
* `--vmware-username TEXT`: VMWare username
* `--vmware-password TEXT`: VMWare password
* `--help`: Show this message and exit.

## `tappr tap`

Tanzu Application Platform management.

**Usage**:

```console
$ tappr tap [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `edit`: Edit tap-values yaml file.
* `install`: Install TAP.
* `setup`: Setup Dev Namespace with Git and Registry...

### `tappr tap edit`

Edit tap-values yaml file.

**Usage**:

```console
$ tappr tap edit [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `tappr tap install`

Install TAP. Make sure to run tappr init before installing TAP.

**Usage**:

```console
$ tappr tap install [OPTIONS] PROFILE:[iterate-local|iterate-slim|iterate] VERSION
```

**Arguments**:

* `PROFILE:[iterate-local|iterate-slim|iterate]`: [required]
* `VERSION`: [required]

**Options**:

* `--host-os [darwin|linux|windows]`: [default: darwin]
* `--tap-values-file TEXT`
* `--help`: Show this message and exit.

### `tappr tap setup`

Setup Dev Namespace with Git and Registry secrets.

**Usage**:

```console
$ tappr tap setup [OPTIONS]
```

**Options**:

* `--namespace TEXT`: [default: default]
* `--help`: Show this message and exit.

## `tappr test`

Run pre-defined test on the tappr test framework.

- test_file: test yaml file that defines the tests to run and context

output: Defaults to stdout. Change to something else for a file output

**Usage**:

```console
$ tappr test [OPTIONS] TEST_FILE
```

**Arguments**:

* `TEST_FILE`: [required]

**Options**:

* `--output TEXT`: [default: stdout]
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

# `tappr`

**Usage**:

```console
$ tappr [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--verbose / --no-verbose`: [default: False]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `create`: Create k8s clusters.
* `delete`: Delete k8s clusters.
* `init`: Initialize the tappr cli with required creds.
* `tap`: Tanzu Application Platform management.
* `test`: Run pre-defined test on the tappr test...
* `utils`: Random utils for making life easier.

## `tappr create`

Create k8s clusters.

**Usage**:

```console
$ tappr create [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `gke`: Create a GKE cluster.
* `kind`: Create a multi-node kind cluster.

### `tappr create gke`

Create a GKE cluster. Assumes gcloud is set to create clusters.

**Usage**:

```console
$ tappr create gke [OPTIONS]
```

**Options**:

* `--cluster-name TEXT`
* `--project TEXT`
* `--gcp-json TEXT`: A json file to override values in artifacts/gke_defaults.json
* `--help`: Show this message and exit.

### `tappr create kind`

Create a multi-node kind cluster.

**Usage**:

```console
$ tappr create kind [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `tappr delete`

Delete k8s clusters.

**Usage**:

```console
$ tappr delete [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `gke`: Delete a GKE cluster.
* `kind`: Delete a kind cluster.

### `tappr delete gke`

Delete a GKE cluster.

**Usage**:

```console
$ tappr delete gke [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--region TEXT`: [default: us-east4]
* `--help`: Show this message and exit.

### `tappr delete kind`

Delete a kind cluster.

**Usage**:

```console
$ tappr delete kind [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `tappr init`

Initialize the tappr cli with required creds.

**Usage**:

```console
$ tappr init [OPTIONS]
```

**Options**:

* `--tanzunet-username TEXT`: Tanzu Network Username.
* `--tanzunet-password TEXT`: Tanzu Network Password.
* `--pivnet-uaa-token TEXT`: Pivnet UAA Login Token used to download artifacts.
* `--default-registry-server TEXT`: Default registry server to use while installing tap. e.g. gcr.io, index.docker.io etc.
* `--default-registry-repo TEXT`: Default registry repo on the registry server to use for build service. Don't include the registry server or starting /.
* `--default-tap-install-registry TEXT`: Default registry to use while installing tap.  [default: registry.tanzu.vmware.com]
* `--default-registry-username TEXT`: Registry username to use while installing tap
* `--default-registry-password TEXT`: Registry password to use while installing tap. If using GCR set this as path to jsonkey file.
* `--vmware-username TEXT`: VMWare username
* `--vmware-password TEXT`: VMWare password
* `--help`: Show this message and exit.

## `tappr tap`

Tanzu Application Platform management.

**Usage**:

```console
$ tappr tap [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `edit`: Edit tap-values yaml file.
* `install`: Install TAP.
* `setup`: Setup Dev Namespace with Git and Registry...

### `tappr tap edit`

Edit tap-values yaml file.

**Usage**:

```console
$ tappr tap edit [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `tappr tap install`

Install TAP. Make sure to run tappr init before installing TAP.

**Usage**:

```console
$ tappr tap install [OPTIONS] PROFILE:[iterate-local|iterate-slim|iterate] VERSION
```

**Arguments**:

* `PROFILE:[iterate-local|iterate-slim|iterate]`: [required]
* `VERSION`: [required]

**Options**:

* `--host-os [darwin|linux|windows]`: [default: darwin]
* `--tap-values-file TEXT`
* `--help`: Show this message and exit.

### `tappr tap setup`

Setup Dev Namespace with Git and Registry secrets.

**Usage**:

```console
$ tappr tap setup [OPTIONS]
```

**Options**:

* `--namespace TEXT`: [default: default]
* `--help`: Show this message and exit.

## `tappr test`

Run pre-defined test on the tappr test framework.

- test_file: test yaml file that defines the tests to run and context

output: Defaults to stdout. Change to something else for a file output

**Usage**:

```console
$ tappr test [OPTIONS] TEST_FILE
```

**Arguments**:

* `TEST_FILE`: [required]

**Options**:

* `--output TEXT`: [default: stdout]
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

# `tappr`

**Usage**:

```console
$ tappr [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--verbose / --no-verbose`: [default: False]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `create`: Create k8s clusters.
* `delete`: Delete k8s clusters.
* `init`: Initialize the tappr cli with required creds.
* `tap`: Tanzu Application Platform management.
* `test`: Run pre-defined test on the tappr test...
* `utils`: Random utils for making life easier.

## `tappr create`

Create k8s clusters.

**Usage**:

```console
$ tappr create [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `gke`: Create a GKE cluster.
* `kind`: Create a multi-node kind cluster.

### `tappr create gke`

Create a GKE cluster. Assumes gcloud is set to create clusters.

**Usage**:

```console
$ tappr create gke [OPTIONS]
```

**Options**:

* `--cluster-name TEXT`
* `--project TEXT`
* `--gcp-json TEXT`: A json file to override values in artifacts/gke_defaults.json
* `--help`: Show this message and exit.

### `tappr create kind`

Create a multi-node kind cluster.

**Usage**:

```console
$ tappr create kind [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `tappr delete`

Delete k8s clusters.

**Usage**:

```console
$ tappr delete [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `gke`: Delete a GKE cluster.
* `kind`: Delete a kind cluster.

### `tappr delete gke`

Delete a GKE cluster.

**Usage**:

```console
$ tappr delete gke [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--region TEXT`: [default: us-east4]
* `--help`: Show this message and exit.

### `tappr delete kind`

Delete a kind cluster.

**Usage**:

```console
$ tappr delete kind [OPTIONS] CLUSTER_NAME
```

**Arguments**:

* `CLUSTER_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `tappr init`

Initialize the tappr cli with required creds.

**Usage**:

```console
$ tappr init [OPTIONS]
```

**Options**:

* `--tanzunet-username TEXT`: Tanzu Network Username.
* `--tanzunet-password TEXT`: Tanzu Network Password.
* `--pivnet-uaa-token TEXT`: Pivnet UAA Login Token used to download artifacts.
* `--default-registry-server TEXT`: Default registry server to use while installing tap. e.g. gcr.io, index.docker.io etc.
* `--default-registry-repo TEXT`: Default registry repo on the registry server to use for build service. Don't include the registry server or starting /.
* `--default-tap-install-registry TEXT`: Default registry to use while installing tap.  [default: registry.tanzu.vmware.com]
* `--default-registry-username TEXT`: Registry username to use while installing tap
* `--default-registry-password TEXT`: Registry password to use while installing tap. If using GCR set this as path to jsonkey file.
* `--vmware-username TEXT`: VMWare username
* `--vmware-password TEXT`: VMWare password
* `--help`: Show this message and exit.

## `tappr tap`

Tanzu Application Platform management.

**Usage**:

```console
$ tappr tap [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `edit`: Edit tap-values yaml file.
* `install`: Install TAP.
* `setup`: Setup Dev Namespace with Git and Registry...

### `tappr tap edit`

Edit tap-values yaml file.

**Usage**:

```console
$ tappr tap edit [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `tappr tap install`

Install TAP. Make sure to run tappr init before installing TAP.

**Usage**:

```console
$ tappr tap install [OPTIONS] PROFILE:[iterate-local|iterate-slim|iterate] VERSION
```

**Arguments**:

* `PROFILE:[iterate-local|iterate-slim|iterate]`: [required]
* `VERSION`: [required]

**Options**:

* `--k8s-context TEXT`: Valid k8s context to install TAP. If this param is not provided, a picker will show up in case of multiple contexts
* `--host-os [darwin|linux|windows]`: [default: darwin]
* `--tap-values-file TEXT`
* `--help`: Show this message and exit.

### `tappr tap setup`

Setup Dev Namespace with Git and Registry secrets.

**Usage**:

```console
$ tappr tap setup [OPTIONS]
```

**Options**:

* `--namespace TEXT`: [default: default]
* `--help`: Show this message and exit.

## `tappr test`

Run pre-defined test on the tappr test framework.

- test_file: test yaml file that defines the tests to run and context

output: Defaults to stdout. Change to something else for a file output

**Usage**:

```console
$ tappr test [OPTIONS] TEST_FILE
```

**Arguments**:

* `TEST_FILE`: [required]

**Options**:

* `--output TEXT`: [default: stdout]
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

