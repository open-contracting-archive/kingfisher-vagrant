# Technical Decisions

## This document

This document lists decisions already made in this project so far, to make sure there is an explicit record of the work 
we have done and for the benefit of new participants.

## Git

### New Work

See CONTRIBUTING.md for more guidelines

### Pull Requests

Each Pull Request needs to be approved by one other person.

Merging should be done using the "Create a merge commit" strategy.

## Python

### Python 3

Python 3 is a minimum requirement.

### PEP8

Code formatting follows PEP8 with the exception of line lengths.

flake8 is run in Travis. All code should be compliant before being sent for code review.

## Database 

### Postgres 10

Postgres 10 is a minimum requirement, to take advantage of the latest features.

### Table Names

Table names are Singular.

### ID columns

ID columns are called "id", not including the name of the table. eg "release.id", not "release.release_id"

## Automatic tests

Tests are written using pytest and are run in Travis. All tests should pass before a code is sent for code review.





