# Linting

`lint_prj.sh` wraps the [ruff](https://github.com/astral-sh/ruff?tab=readme-ov-file) linting for convenience.
It will not automatically fix any issue instead just preview it. The script do not manipulate the output in any way.

If the script is unable to find `ruff` in the user $PATH, it can be used to install it together with [uv](https://docs.astral.sh/uv/#highlights).

## Source files
The script will check following directories:

* [rctabs](../../rctabs/)
* [rcfunc](../../rcfunc/)
* [tests](../../tests/)

## Ruleset
`ruff` default rules are used. No specific configuration is added.

## Usage
From repo root:
```bash
./tools/linting/lint_prj.sh
```

Help:
```bash
./tools/linting/lint_prj.sh -h
```
