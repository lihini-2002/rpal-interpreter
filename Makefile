# Makefile for RPAL Interpreter

# Python interpreter
PYTHON = python

# Default target
all: test

# Run the interpreter on a specific file
# Usage: make run FILE=path/to/file.rpal
run:
	@powershell -Command "if (-not '$(FILE)') { Write-Host 'Error: Please specify a file to run. Usage: make run FILE=path/to/file.rpal'; exit 1 }"
	$(PYTHON) myrpal.py $(FILE)

# Run the interpreter with AST output
# Usage: make ast FILE=path/to/file.rpal
ast:
	@powershell -Command "if (-not '$(FILE)') { Write-Host 'Error: Please specify a file to run. Usage: make ast FILE=path/to/file.rpal'; exit 1 }"
	$(PYTHON) myrpal.py -ast $(FILE)

# Run the interpreter with standardized AST output
# Usage: make st FILE=path/to/file.rpal
st:
	@powershell -Command "if (-not '$(FILE)') { Write-Host 'Error: Please specify a file to run. Usage: make st FILE=path/to/file.rpal'; exit 1 }"
	$(PYTHON) myrpal.py -st $(FILE)

# Run all tests
test:
	$(PYTHON) test_interpreter.py

# Clean up any generated files
clean:
	powershell -Command "Get-ChildItem -Recurse -Include '*.pyc','*.pyo','*.pyd','.coverage' | Remove-Item -Force"
	powershell -Command "Get-ChildItem -Recurse -Directory -Include '__pycache__','*.egg-info','*.egg','.pytest_cache','.coverage','htmlcov' | Remove-Item -Recurse -Force"

# Help target
help:
	@echo "Available targets:"
	@echo "  all        - Run all tests (default target)"
	@echo "  run        - Run the interpreter on a specific file (requires FILE=path/to/file.rpal)"
	@echo "  ast        - Run the interpreter and show AST (requires FILE=path/to/file.rpal)"
	@echo "  st         - Run the interpreter and show standardized AST (requires FILE=path/to/file.rpal)"
	@echo "  test       - Run all tests"
	@echo "  clean      - Remove all generated files"
	@echo "  help       - Show this help message"

.PHONY: all run ast st test clean help 