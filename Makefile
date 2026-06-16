.PHONY: install test lint example-browser example-systemd

install:
	python -m pip install -e .

test:
	python -m pytest

lint:
	python -m ruff check core/python tests examples

example-browser:
	PYTHONPATH=core/python:. python examples/call_browser_mock.py

example-systemd:
	PYTHONPATH=core/python:. python examples/call_systemd_mock.py
