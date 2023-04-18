MYPY_DIRS := $(shell find functions layer -type d -maxdepth 1 -mindepth 1 | xargs)

.PHONY: test
test:
	pytest

.PHONY: mypy
mypy: $(MYPY_DIRS)
    $(foreach d, $(MYPY_DIRS), python -m mypy $(d);)

.PHONY: develop
develop:
	python -m pip install --editable .
	python -m pip install -U -r requirements-dev.txt
