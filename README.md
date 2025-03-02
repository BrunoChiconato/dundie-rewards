# Dundie Rewards Project

[![CI](https://github.com/BrunoChiconato/dundie-rewards/actions/workflows/main.yml/badge.svg)](https://github.com/BrunoChiconato/dundie-rewards/actions/workflows/main.yml) [![Python 3.10|3.11|3.12|3.13](https://img.shields.io/badge/Python-3.10%20|%203.11%20|%203.12%20|%203.13-blue.svg)](#) [![codecov](https://codecov.io/gh/BrunoChiconato/dundie-rewards/graph/badge.svg?token=EGKFE6ZWQP)](https://codecov.io/gh/BrunoChiconato/dundie-rewards)

We have been hired by Dunder Mifflin, a major paper manufacturer, to develop a rewards system for their employees.

Michael, the company manager, wants to increase employee motivation by offering a points system that employees can accumulate according to their achieved goals, bonuses offered by the manager, and employees can also exchange points among themselves.

Employees can redeem their points once a year on a credit card to spend wherever they want.

We agreed in the contract that the MVP (Minimum Viable Product) will be a version to be executed in the terminal and that in the future it will also have UI, web, and API interfaces.

The current employee data will be provided in a file that can be in .csv or .json format and this same file can be used for future versions. Name, Department, Position, Email

## User Stories

### Epic: Administration

- As an ADMIN, I want to be able to EXECUTE THE COMMAND `dundie load assets/people.csv` to populate the database with employee information.
    - For each employee in the file, if they do not already exist in the database, they should be created with an initial score of 100 for managers and 500 for associates. If they already exist, different information should be updated and the score summed.
    - The system should avoid duplicate entries of associates and accept only valid emails.
    - The system should create an initial password for each employee and send it by email.
    - The data should be stored in an SQLite database.

- As an ADMIN, I want to be able to VIEW a report containing employee information in the terminal.
    - In the terminal, I want to see `Email`, `Balance`, `Last Movement`, `Name`, `Currency`, `Department`, `Role` and `Value`.
    - This report should have the option to be saved in a .json file.
    - Command: `dundie show --email|--dept|--output`

- As an ADMIN, I want to be able to assign points to a specific employee or an entire department.
    - Command: `dundie add --dept --value=100`

- As an ADMIN, I want ADMIN operations to be protected by username and password.

### Epic: Transactions

- As an EMPLOYEE, I want to be able to view my points balance and transaction history.

- As an EMPLOYEE, I want to be able to transfer points to another employee.

- As an EMPLOYEE, I want operations to be password-protected, preventing another user from altering my account.

## Pre-requirements

- Python 3.10

## Installation

```py
pip install dundie-rewards
```

```py
pip install -e '.[dev]'
```

## Usage

```py
dundie load assets/people.csv
```

## Issues

- [X] Write functional unit and integration tests.
- [ ] Write documentation.
- [X] Implement hashed passwords for employees.
- [X] Calculate code coverage.
- [X] Implement the `transfer` CLI command.
- [X] Implement the `movements` CLI command.
- **Managers** must pass their e-mail and password to access their account, view their points balance, transaction history, transfer points to other employees, assign points to a specific employee or an entire department, and load employee data.
    - Managers can execute the following comands:
        - [X] `dundie load`;
        - [X] `dundie show`;
        - [X] `dundie add`;
        - [X] `dundie remove`;
        - [X] `dundie transfer`;
        - [X] `dundie movements`;
- **Employees** must pass their e-mail and password to access their account and view their points balance, transaction history, and transfer points to other employees. Employees can't see other employees or deparment accounts and load employee data.
    - Employees can execute the following comands:
        - [X] `dundie show`;
        - [X] `dundie transfer`;
        - [X] `dundie movements`;
