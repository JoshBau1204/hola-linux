# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Reglas

- Responder siempre en español.

## Project status

`hola-linux` is a small repository with no build system, tests, or lint tooling yet.

- `sysinfo.py`: standalone Python 3 script (standard library only, no `psutil`) that prints CPU, RAM, disk, and user info with ANSI colors. It reads `/proc`, so it is Linux-only. Run with `./sysinfo.py`. Colors are disabled automatically when stdout is not a TTY or `NO_COLOR` is set.

When tests or tooling are added, document the commands here (including how to run a single test).
