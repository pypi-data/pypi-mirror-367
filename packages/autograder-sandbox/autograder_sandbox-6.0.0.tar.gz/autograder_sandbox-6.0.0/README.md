# Autograder Sandbox

This Python library uses Docker container functionality to create a secure, isolated environment for running untrusted code.
Full API documentation can be found at http://autograder-sandbox.readthedocs.io

## Requirements
- Python >= 3.10
- Docker

## Installation
1. Install [Docker](https://docs.docker.com/engine/installation/)
1. Install this library with pip: `pip install autograder-sandbox`
The first time you start a sandbox (using a context manager), the appropriate Docker image will be downloaded automatically.

## Configuration
### Docker Image
The Docker image used by default is `eecsautograder/ubuntu22:latest`. Custom images should be based on one of the images defined in the [base-docker-images repo](https://github.com/eecs-autograder/base-docker-images).

To specify which image to use, pass the name of the image as the `docker_image` parameter to the `AutograderSandbox` constructor. You can also set the `SANDBOX_DOCKER_IMAGE` environment variable to specify a new default value for that parameter.

```
with AutograderSandbox(docker_image='some_other_image:latest') as sandbox:
    ...
```

### Environment Variables
These variables can be used to override the default values of certain AutograderSandbox constructor parameters. In particular, we recommend setting `SANDBOX_MEM_LIMIT` to a value appropriate for your hardware.

`SANDBOX_DOCKER_IMAGE`: The default docker image to use for new sandbox instances.\
`SANDBOX_MEM_LIMIT`: The default container-level physical memory limit. Defaults to "4g" (4GB). See https://docs.docker.com/config/containers/resource_constraints/#memory for allowed values.\
`SANDBOX_PIDS_LIMIT`: The default container-level process spawn limit. Defaults to 512.\
`SANDBOX_CPU_CORE_LIMIT`: The number of CPU cores the container can use. Not set by default. Seehttps://docs.docker.com/config/containers/resource_constraints/#cpu for allowed values.

## Basic usage
```
from autograder_sandbox import AutograderSandbox

with AutograderSandbox() as sandbox:
    result = sandbox.run_command(['echo', 'hello world'], timeout=10)
    print(result.stdout.read().decode())
```

## Versioning
We use semantic versioning according to python conventions:
- 0.0.x releases contain minor tweaks or bug fixes.
- 0.x.0 releases contain new features.
- x.0.0 releases may contain backwards-incompatible changes.

### Development & Release Branches: Protocols and Workflow
This section is intended for developers.

#### "develop" branch
Use feature branches for all changes, and make a pull request against the `develop` branch.

#### "release-*" branches
Name release branches as `release-x.x.x`, where `x.x.x` is the semantic version.
Minor releases should get their own release branch (e.g., 6.0.x).
Patch fixes should be handled as described on their own.

Do NOT merge or rebase directly between the develop and release branches.
Once a release branch is created, it should only be updated with feature- or bugfix-style branches.
We generally recommend a squash-and-merge for these types of PRs.
After the squashed feature/bugfix branch is merged into a release branch, cherry-pick the squashed commit on top of `develop` and open a pull request to merge the changes into `develop`.

The version of `README.md` (this file) on the `develop` branch is the source of truth.
Update this file on release branches just before publishing a release.
If instructions differ across releases, include both, and label which version the instructions apply to.

#### Publishing a release
To create a github release, tag the latest commit on the release branch.
For example, to create the first non-dev 6.0.x release, we'd run:
```
git checkout release-6.0.x
git tag 6.0.0
git push --tags
```
CI will build and test the package, publish to pypi, and create a GitHub release.

## Changelog
6.0.0 - Restructuring of command-running implementation to support in-container process reaping and prevent rare circumstances when a command hitting the memory limit causes docker to stall.
- The main change that accomplishes this is enabling the OOM killer. We restructured how commands are run to avoid situations where the OOM killer kills the container's entrypoint process.
  - We also added extra layers of timeout + fallback behavior during key steps such as container teardown. At a certain point, a critical error is raised that users of the library can catch and then alert sysadmins.
- We also added a thin layer of abstraction that lets us identify the container's entrypoint process and specific commands run inside the container. Using a special "reaper" container mounted in the same PID namespace as the sandbox, we can clean up problematic processes.
- Other minor fixes:
  - Containers are now always started as root, even if another user is specified in the Dockerfile. This should help avoid a common pitfall where custom images forget to re-specify `USER root` and then the container fails on startup when trying to set permissions on the entrypoint script.
    - Similarly, when `as_root` is True, we now explicitly set the user and group to root instead of relying on the default user set in the Dockerfile being root.      
- A full list of issues and PRs in this release can be found [here](https://github.com/orgs/eecs-autograder/projects/4/views/1)

5.0.0 - Backwards-incompatible change to process spawn limit.
- Issues fixed:
    - [#41](https://github.com/eecs-autograder/autograder-sandbox/issues/41)
        - Removed the ability to place a specific nproc ulimit on commands.
          Instead, there is now a "block_process_spawn" option that sets the limit to 0 for the command. This let us remove the various hacks that we were using to work around the problem of "same UID in different containers, processes count towards same limit."
          See also https://github.com/eecs-autograder/autograder-sandbox/pull/46
    - [#43](https://github.com/eecs-autograder/autograder-sandbox/issues/43)
        - Added mypy to the CI toolchain and added py.typed in order to make type annotations usable externally.
- Other changes:
    - Lowered the default container-level memory limit to 4GB.

4.0.2 - Bug fix involving computing output size of TemporaryFile vs NamedTemporaryFile.

4.0.1 - Container-level process limits
- See https://github.com/eecs-autograder/autograder-sandbox/projects/2 for a full list of issues fixed.
- Significant changes:
    - Added container-level memory and process limits using Docker's cgroup options.
    - cmd_runner.py no longer has to be baked into images.

3.1.2 - Stdin /dev/null and Ubuntu version lock
- Issues fixed:
    - [#20](https://github.com/eecs-autograder/autograder-sandbox/issues/20)
- In autograder-sandbox/autograder_sandbox/docker-image-setup/Dockerfile, locked Ubuntu version to Xenial instead of using latest.

3.1.0 - Output truncating
- Issues fixed:
    - [#13](https://github.com/eecs280staff/autograder-sandbox/issues/13)
    - [#14](https://github.com/eecs280staff/autograder-sandbox/issues/14)
- Changes to `run_command` function:
    - Added optional `truncate_stdout` and `truncate_stderr` parameters that specify the maximum length of stdout and stderr to return in the command result.

3.0.0 - Better handling of large IO
- Issues fixed:
    - [#12](https://github.com/eecs280staff/autograder-sandbox/issues/12)
- Changes to `run_command` function:
    - `input` is now called `stdin` and takes in a file object.
    - The return value is now a `CompletedCommand`
    - `TimeoutExpired` is not raised on command timeout. Instead, `CompletedCommand` has a `timed_out` attribute.
    - The `stdout` and `stderr` fields of `CompletedCommand` are file objects.

2.1.0 - Permissions for files added to sandbox
- Issues fixed:
    - [#10](https://github.com/eecs280staff/autograder-sandbox/issues/10)
        - Added two arguments to the `add_files` function: `owner` and `read_only`.
          This gives the user the option to decide whether files added to the sandbox should be owned by
          'autograder' or 'root' and whether the files should be read-only.

2.0.1 - Hotfix for output decoding issue.
- Previously, stdout and stderr were not being decoded on TimeoutExpired or CalledProcessError. This release fixes this.

2.0.0 - Removes support for versions of Python < 3.5
- Issues fixed:
    - [#4](/james-perretta/autograder-sandbox/issues/4)
    - [#5](/james-perretta/autograder-sandbox/issues/5)
    - [#6](/james-perretta/autograder-sandbox/issues/6)
- Changes to AutograderSandbox constructor parameters:
    - Added `docker_image` and `container_create_timeout`
- Changes to AutograderSandbox.run_command() parameters:
    - Added `encoding` and `errors`
    - Renamed `input_content` to `input`
    - Renamed `raise_on_failure` to `check`
- AutograderSandbox.run_command() now returns subprocess.CompletedProcess. The `stdout` and `stderr` fields of the returned objects will always be strings.
- AutograderSandbox.run_command() now raises subprocess.TimeoutExpired if the time limit is exceeded. There is no longer a `timed_out` field of the returned object.

1.0.0 - Initial release

