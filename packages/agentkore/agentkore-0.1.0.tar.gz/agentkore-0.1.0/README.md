# agentkore

A Python library for building LLM-based agents.

## Features

- Simple agent scaffolding  
- Pluggable “tool” interface  
- Built-in OpenAI / LangChain adapters  

## Installation

```bash
pip install agentkore
```

### Using uv

You can also install and bootstrap the package using [uv](https://github.com/astral-sh/uv), a fast Python package installer and resolver:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install agentkore
uv pip install agentkore

# For development installation with all dependencies
git clone https://github.com/shipkode/agentkore.git
cd agentkore
uv pip install -e ".[dev]"

# Building the package with uv
uv pip install build
uv run -m build
# This will create distribution packages in the dist/ directory:
# - A source distribution (.tar.gz)
# - A wheel distribution (.whl)

# Publishing to PyPI
uv pip install twine

# First, create an account on TestPyPI (https://test.pypi.org/account/register/)
# and PyPI (https://pypi.org/account/register/) if you don't have one

# Generate an API token:
# - For TestPyPI: https://test.pypi.org/manage/account/token/
# - For PyPI: https://pypi.org/manage/account/token/

# Create or edit ~/.pypirc file with your tokens:
# [testpypi]
# username = __token__
# password = your-test-pypi-token
#
# [pypi]
# username = __token__
# password = your-pypi-token

# Upload to TestPyPI first to test
uv run -m twine upload --repository testpypi dist/*

# Once tested, upload to the real PyPI
# uv run -m twine upload dist/*

# You can also specify credentials directly if needed
# uv run -m twine upload --repository testpypi --username __token__ --password your-token dist/*
```

## Quickstart

```python
from agentkore import Agent

agent = Agent(name="hello-world")
response = agent.run("Say hello to the world")
print(response)
```

## Contributing

1. Fork the repo
2. Create a feature branch (git checkout -b feat/…)
3. Commit and push
4. Open a PR
