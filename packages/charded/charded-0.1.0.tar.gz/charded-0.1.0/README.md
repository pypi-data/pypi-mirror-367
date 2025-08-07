# Simple project for Python 3.10+
#### All-in-one repository with supervisor, crontab, linters and many useful tools

**Version control** is handled using [Astral UV](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) tool. When building the image, uv is sourced from the official repository by copying the binary. Installation on a developer's machine can be done in various ways, which we'll cover shortly.

**Managing the interpreter version**, project environment variables, and setting up the virtual environment is done with the [Mise](https://mise.jdx.dev/installing-mise.html) tool. It automatically install any interpreter version by reading it from the project description and/or the version bound by uv. It can also fetch the appropriate uv binary for the platform and architecture.

## How to install required tools?

#### A. Quick start for test

Therefore, the quickest and most minimal way to get touch is to install mise on your system and prepare tools with mise, **not for development**:

1. `brew install mise`

That's all, go to **Shell configuration** section.

#### B. Engineer full-featured setup

**True engineer way** it's prepare rust environment, build mise and configure shell:

1. Install Cargo via [Rustup](https://doc.rust-lang.org/book/ch01-01-installation.html).
2. Do not forget add cargo path for your shell:
   - `export PATH="~/.cargo/bin:$PATH"`
3. Install sccache to avoid electricity bills:
   - `cargo install sccache`
4. Activate sccache:
   - `export RUSTC_WRAPPER="~/.cargo/bin/sccache"` (and add it to your shell)
5. Install cargo packages updater and mise:
   - `cargo install cargo-update mise`
6. Install uv:
   - `mise install uv@latest && mise use -g uv@latest`
7. That's all, you have last version of optimized tools; for update all packages just run sometime:
   - `rustup update && cargo install-update --all`

### Shell configuration

1. **Mise provide dotenv functionality** (automatic read per-project environment variables from .env file and from .mise.toml config) from the box with batteries, but your shell must have entry hook, add to your shell it, example for zsh (your can replace it for bash, fish, etc):
   - `eval "$(mise activate zsh)"`
2. Also you can want using autocompletion, same story for zsh:
   - `eval "$(mise completion zsh && uv generate-shell-completion zsh)"`
3. Restart your shell session:
   - `exec "$SHELL"`

### Kickstart

1. Go to project root.
2. Just run `make`:
   - mise will mark project directory as trusted
   - mise copy sample development environment variables to .env
   - mise grab environment variables defined in project .env, evaluate it and provide to current shell session
   - mise checks what project python versions is installed, otherwise download and install it
   - uv make virtual environment in project root (`uv venv`)
   - uv read project packages list, download, install and link it (via `uv sync` run, read Makefile)
   - uv install pre-commit and pre-push hooks

## Work with project

### Warning about pip

**NEVER CALL pip, NEVER!** Instead it use native uv calls, [read uv manual](https://docs.astral.sh/uv/guides/projects/#managing-dependencies), it's very easy, for example:

1. Set or change python version (when python 3.11 already installed), before run do not forget change your python version in pyproject.toml:
   - `uv python pin 3.11 && make sync`

2. If python 3.11 isn't installed, run `mise install python@3.11` and mise download and install python 3.11, recreate virtual environment with 3.11 context. Do not forget to pin python version by uv from previous step (and, may be you need to update your pyproject.toml).

2. Just add new dependency:
   - `uv add phpbb<=1.2`

3. Add some development library:
   - `uv add --group development backyard-memleak`

4. Work with locally cloned repository:
   - `uv add --editable ~/src/lib/chrome-v8-core`

### Common workflow

1. `make`:
   - same as `mise install`, but also call `mise trust --yes` for initial deployment
   - call `make sync`

2. `make sync`
   - drop and recreate .venv by `uv venv`
   - read project dependencies graph from pyproject.toml and install it to virtual environment by `uv sync`)
   - call `make freeze`

3. `make freeze`:
   - dump state to uv.lock by `uv lock`
   - for development and debugging puproses uv save all used packages in current virtual environment to `packages.json` (with all development packages!) by `uv pip list`
   - for repeatable production purposes uv save project dependencies to `packages.txt` with hashes for release builds strict version checks, read Dockerfile example (only project dependencies!) by `uv pip compile`

4. `make upgrade`:
   - read project dependencies graph from pyproject.toml
   - fetch information about all updated packages, recreate dependencies graph and install it to virtual environment by `uv sync --upgrade`
   - update `uv.lock` with updated packages version by `uv lock --upgrade`
   - call `make freeze`
   - show all installed packages in local virtual environment
   - all you need it's just manually update versions in pyproject.toml

5. `make check`:
   It's non-destructive action, just run all checks and stop at first fail.

6. `make lint`:
   **Destructive action**, always commit all changes before run it. Runs all compatible linters with --fix and --edit mode, after it call `make check` for final polishing.
