MYPY_DIRS := $(shell find functions layer -type d -maxdepth 1 -mindepth 1 | xargs)
ARTIFACTS_DIR ?= build

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

.PHONY: build
build:
	rm -rf dist || true
	python -m build -w

.PHONY: build_layer
build_layer: build
	rm -rf "$(ARTIFACTS_DIR)/python" || true
	mkdir -p "$(ARTIFACTS_DIR)/python"
	python -m pip install -r requirements.txt -t "$(ARTIFACTS_DIR)/python"
	python -m pip install dist/*.whl -t "$(ARTIFACTS_DIR)/python"

.PHONY: package_layer
package_layer: build build_layer
	cd "$(ARTIFACTS_DIR)"; zip -rq ../layer.zip python

.PHONY: build-ServerlessProjectLayer
build-ServerlessProjectLayer: build build_layer
