PYTHON = python
PIP = $(PYTHON) -m pip

.PHONY: all
all: install

.PHONY: install
install:
	$(PIP) install --upgrade pip
	$(PIP) install .

.PHONY: build
build:
	$(PIP) install --upgrade pip
	$(PIP) install build
	$(PYTHON) -m build --wheel --sdist --outdir dist/

.PHONY: test
test: install
	ChefScript --help
	ChefScript tests/红烧肉.chefscript

.PHONY: lint
lint:
	$(PIP) install --upgrade pip
	$(PIP) install .[lint]

	isort src --check-only --diff
	black src --check
	flake8 src --max-line-length 88 --extend-ignore E203 --statistics
	mypy src

.PHONY: clean
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf **/__pycache__/
	rm -rf .mypy_cache/
	rm -rf **/*.egg-info/
