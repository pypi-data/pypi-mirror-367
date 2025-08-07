BAKE_OPTIONS=--no-input
FIND_NAME = find . -path './.venv' -prune -o -name

.PHONY: bake help replay rundoc

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

COOKIECUTTER := uvx cookiecutter

bake:  ## Generate project using defaults
	$(COOKIECUTTER) $(BAKE_OPTIONS) . --overwrite-if-exists

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

replay: BAKE_OPTIONS=--replay
replay: watch
	;

rundoc: ## Run make doc
	make bake
	make -C python_boilerplate doc
