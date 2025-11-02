############################################################
# 📘 Project Makefile
# 
# This Makefile defines reusable commands to:
#  - Format the project with Pyink
#  - Run your Python app with optional custom arguments
#  - Combine both actions into one "ble:run" command
#
# ✅ Usage examples:
#   make format                     → Format all code using Pyink
#   make run                        → Run main.py
#   make run ARGS="--debug"         → Run main.py with parameters
#   make ble:run                    → Format + run
#   make ble:run ARGS="--mode prod" → Format + run with arguments
#
# These commands are designed to be shared in GitHub, so
# everyone cloning the project can use them directly.
############################################################

# -------------------------------------------------------------------
# PHONY targets: these don’t correspond to actual files.
# They are “commands” rather than file outputs.
# -------------------------------------------------------------------
.PHONY: format run ble:run

# -------------------------------------------------------------------
# Variable for passing custom CLI args to Python.
# You can override it like:
#   make run ARGS="--debug"
# -------------------------------------------------------------------
ARGS ?=

# -------------------------------------------------------------------
# Format all Python files in the current folder using Pyink.
# Adjust to target only specific folders if needed.
# -------------------------------------------------------------------
format:
	@echo "✨ Formatting Python code with Pyink..."
	pyink .

# -------------------------------------------------------------------
# Run the main Python application.
# This will pass along any arguments given via ARGS.
# Example:
#   make run ARGS="--config dev.json"
# -------------------------------------------------------------------
run:
	@echo "🚀 Running main.py with args: $(ARGS)"
	python3 main.py $(ARGS)

# -------------------------------------------------------------------
# Full pipeline: format code first, then run the app.
# This is your custom “ble:run” command.
# Example:
#   make ble:run ARGS="--port 8080"
# -------------------------------------------------------------------
ble:run:
	@echo "✨ Formatting before run..."
	pyink .
	@echo "🚀 Running main.py with args: $(ARGS)"
	python3 main.py $(ARGS)

# -------------------------------------------------------------------
# OPTIONAL: Environment file loading (uncomment if needed)
# Example usage:
#   make ble:run ENV_FILE=.env.local ARGS="--debug"
# -------------------------------------------------------------------
# ENV_FILE ?= .env
# ble:run:
# 	@echo "🔧 Loading env from $(ENV_FILE)"
# 	export $$(grep -v '^#' $(ENV_FILE) | xargs) && \
# 	pyink . && \
# 	python3 main.py $(ARGS)
