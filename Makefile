.PHONY: test

test:
	PYTHONPATH=. pytest tests/ --maxfail=1 --disable-warnings -v

