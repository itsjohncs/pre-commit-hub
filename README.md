# pre-commit-hub

A package manager for [pre-commit](https://pre-commit.com).

> [!WARNING]
> This project is a work-in-progress and is barely usable at the moment.

## Search

Search for pre-commit hooks for your favorite tools.

```
$ pre-commit-hub search black
Match score: 100
Repository: psf/black
Stars: 38035
Hook ID: black
Hook Name: black
Description: Black: The uncompromising Python code formatter
---
Match score: 100
Repository: psf/black
Stars: 38035
Hook ID: black-jupyter
Hook Name: black-jupyter
Description: Black: The uncompromising Python code formatter (with Jupyter Notebook support)
---
...
```

## Add

Add hooks to your repo.

```
$ pre-commit-hub add black
Added hook 'black' from 'psf/black' to config
```

> [!WARNING]
> TODO: This doesn't set the `rev` property correctly yet.

## Remove

Remove hooks from your repo.

```
$ pre-commit-hub remove black
Removed hook 'black' from config
```


