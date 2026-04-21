# Shell Completion

The `todoist` command is built with Typer, so completion scripts can be
generated from the installed CLI.

Install the project first:

```bash
python3 -m pip install -e ".[dev]"
```

## Bash

```bash
todoist --install-completion bash
```

Restart the shell, or source the file printed by Typer if your shell does not
load it automatically.

To print the script without installing it:

```bash
todoist --show-completion bash
```

## Zsh

```bash
todoist --install-completion zsh
```

Restart the shell after installation. If completion does not load, confirm that
your `.zshrc` initializes completions with `autoload -Uz compinit && compinit`.

To print the script without installing it:

```bash
todoist --show-completion zsh
```

## Fish

```bash
todoist --install-completion fish
```

Open a new shell after installation.

To print the script without installing it:

```bash
todoist --show-completion fish
```

## CI And Containers

Completion installation modifies user shell startup files, so avoid
`--install-completion` in CI or container images. Use `--show-completion SHELL`
when an image build needs to place the generated script in a managed location.
