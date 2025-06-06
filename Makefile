# Makefile for RPAL Interpreter

# Python interpreter
PYTHON = python

# Default target
all: test

# Run the interpreter on a specific file
# Usage: make run FILE=path/to/file.rpal
run:
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify a file to run. Usage: make run FILE=path/to/file.rpal"; \
		exit 1; \
	fi
	$(PYTHON) myrpal.py $(FILE)

# Run the interpreter with AST output
# Usage: make ast FILE=path/to/file.rpal
ast:
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify a file to run. Usage: make ast FILE=path/to/file.rpal"; \
		exit 1; \
	fi
	$(PYTHON) myrpal.py -ast $(FILE)

# Run the interpreter with standardized AST output
# Usage: make st FILE=path/to/file.rpal
st:
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify a file to run. Usage: make st FILE=path/to/file.rpal"; \
		exit 1; \
	fi
	$(PYTHON) myrpal.py -st $(FILE)

# Run all tests
test:
	$(PYTHON) test_interpreter.py

# Clean up any generated files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +

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