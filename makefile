############################################################
# 📘 Project Makefile
# 
# This Makefile defines reusable commands to:
#  - Format the project with Pyink
#  - Run the brios CLI with optional custom arguments
#  - Combine both actions into one "ble-run" command
#
# ✅ Usage examples:
#   make format                     → Format all code using Pyink
#   make run                        → Run brios
#   make run ARGS="--scanner 15 -m"         → Run brios with parameters
#   make ble-run                    → Format + run
#   make ble-run ARGS="--target-mac -v" → Format + run with arguments
#
# These commands are designed to be shared in GitHub, so
# everyone cloning the project can use them directly.
############################################################

# Variable for the virtual environment python
VENV_PYTHON = ./env/bin/python

# -------------------------------------------------------------------
# PHONY targets: these don’t correspond to actual files.
# They are “commands” rather than file outputs.
# -------------------------------------------------------------------
.PHONY: format run ble-run check

# -------------------------------------------------------------------
# Variable for passing custom CLI args to Python.
# You can override it like:
#   make run ARGS="--scanner 15 -m"
# -------------------------------------------------------------------
ARGS ?=

# -------------------------------------------------------------------
# Type-check everything.
# -------------------------------------------------------------------
check:
	@echo "🔍 Type-checking with mypy..."
	$(VENV_PYTHON) -m mypy brios/

# -------------------------------------------------------------------
# Format all Python files in the current folder using Pyink.
# Adjust to target only specific folders if needed.
# -------------------------------------------------------------------
format:
	@echo "✨ Formatting Python code with Pyink..."
	$(VENV_PYTHON) -m pyink .

# -------------------------------------------------------------------
# Run the brios application.
# This will pass along any arguments given via ARGS.
# Example:
#   make run ARGS="--scanner 15 -m"
# -------------------------------------------------------------------
run:
	@echo "🚀 Running brios with args: $(ARGS)"
	$(VENV_PYTHON) -m brios $(ARGS)

# -------------------------------------------------------------------
# Full pipeline: format code first, then run the app.
# This is your custom “ble-run” command.
# Example:
#   make ble-run ARGS="--target-mac -v"
# -------------------------------------------------------------------
ble-run:
	@echo "✨ Formatting before run..."
	$(VENV_PYTHON) -m pyink .
	@echo "🚀 Running brios with args: $(ARGS)"
	$(VENV_PYTHON) -m brios $(ARGS)

# -------------------------------------------------------------------
# OPTIONAL: Environment file loading (uncomment if needed)
# Example usage:
#   make ble-run ENV_FILE=.env.local ARGS="--scanner 15 -m"
# -------------------------------------------------------------------
# ENV_FILE ?= .env
# ble-run:
# 	@echo "🔧 Loading env from $(ENV_FILE)"
# 	export $$(grep -v '^#' $(ENV_FILE) | xargs) && \
# 	pyink . && \
# 	python3 -m brios $(ARGS)