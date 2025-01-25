# Contributing to Dundie Project

Summary of the project

## Guidelines

- Backwards compatibility is important.
- Follow the [PEP 8](https://pep8.org/) style guide.
- Multiplatform compatibility is important.
- Python 3 only.

## Code of Conduct

- Be respectful.
- Be collaborative.
- Be open-minded.

## How to Contribute

### Fork the repository

- Click on the "Fork" button on the top right corner of the repository page.

### Clone to local dev environment

```bash
git clone git@github.com:BrunoChiconato/dundie-rewards.git
```

### Prepare virtual environment

```bash
de dundie-rewards
make virtualenv
make install
```

### Coding Style

```bash
make test
# or
make watch
```

### Commit rules

- We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.
- We require signed commits.

### Pull Request Rules

- We require all tests to pass.
- We require all code to be reviewed.

