PY ?= python3

.PHONY: venv demo test clean

venv:
	$(PY) -m venv .venv
	@echo "Now run: source .venv/bin/activate"

demo:
	./demo.sh

test:
	$(PY) -m unittest discover -s tests -v

clean:
	rm -rf reports replay*.html __pycache__ bots/__pycache__ tests/__pycache__
