# Installation
## Python version requirements
- python 3.10+

We recommend that you use python 3.10+ to get the best performance and functionality. The entire project has passed all tests on python 3.10.0. If you are using a python version lower than 3.10, we cannot guarantee that the project will run correctly.

## Installation method
### Install via pip
```shell
pip install agentUniverse
```
More version information can be found on the
[PyPi agentUniverse](https://pypi.org/project/agentUniverse/)

### Install via poetry or other package management tools
In actual projects, we recommend that you use poetry or other tools to manage project dependencies. You can install it with the following command:

```shell
poetry add agentUniverse
```

Or add the following content to your `pyproject.toml` file:

```toml
[tool.poetry.dependencies]
agentUniverse = "^0.0.3"
```
A standard project's `pyproject.toml` can be found [here](../../../../sample_standard_app/pyproject.toml).

Use the `poetry update` command to update dependencies:
```shell
poetry update
```

## Verify installation
```shell
pip list | grep agentUniverse
```
If you see `agentUniverse` and its version number, the installation was successful.

![image](../../_picture/1_2_Installation_0.png)