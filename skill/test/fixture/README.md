# Test Fixture Project

This is a deliberately incomplete project to test the MVP protocol skill.

## What it is
A Python CLI tool that processes text files and outputs word counts. Target user: developers who need quick text stats.

## Success
- Runs `python -m fixture textfile.txt` and prints word/line/char counts
- Handles UTF-8, large files (streaming), multiple files
- Has tests that pass
- Has a README with usage example

## Current State (Intentional Gaps)
- No tests
- No CI/CD
- No entry point (`__main__.py` missing)
- No type hints
- No lint config
- README is vague
- No error handling for missing files
- No streaming for large files
- No license

## Stack
Python 3.11+, stdlib only