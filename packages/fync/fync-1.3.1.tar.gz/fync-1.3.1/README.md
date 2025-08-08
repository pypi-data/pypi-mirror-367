# fync - Automated File Sync

`fync` is a tool for automated command synchronization.
It allows you to observe file changes and execute a sync command
based on the specified options.

## Installation

Install `fync` using `pip` from [PyPI](https://pypi.org/project/fync/):

```bash
pip install fync
```

Install from GitHub

```bash
pip install git+https://github.com/fanuware/fync.git
```

### Usage

fync[OPTIONS] COMMAND

#### Example fync

Observe changes in a specific directory and run a command

```bash
fync --path=/path/to/observe command
```

Use `cp`

```bash
fync cp source destination
```

Use `rsync`

```bash
fync rsync -av source destination
```

#### Example fync-get

Authenticated file download

```bash
fync-get <URL>
fync-get --update <URL>
```

For example, you can download using **Bearer** or **Basic Authentication**.

```bash
fync-get https://httpbin.org/bearer
fync-get https://httpbin.org/basic-auth/test-user/test-password
```
