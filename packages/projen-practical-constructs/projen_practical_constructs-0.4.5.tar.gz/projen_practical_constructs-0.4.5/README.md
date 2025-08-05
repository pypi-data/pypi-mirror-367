# projen-practical-constructs

Constructs and utilities for managing projects with Projen enforcing solid build, test and linting structures.

This repo have additional Constructs not present in [official projen repo](https://github.com/projen/projen) such as RUFF, Makefile etc.

Currently there is support for Python projects, but in the future more will be added.

Check in /examples folder the target structure that these project types will produce.

## For Python project types

Project type name: python_basic

The basic stack supported by this project is:

* Makefile: scripts management
* pip: virtual environments management
* Mypy: code Type check
* RUFF: code formatting and linting
* pytest + coverage: test management
* pip-audit: dependencies vulnerability checks
* pip-tools: dependencies lock file generation (contrainsts.txt)
* vs-code plugins: code editor feedback

[This project](https://github.com/flaviostutz/monorepo-spikes/tree/main/shared/python/hello_world_reference) was used as reference for the target project structure created by this projen project type.

## Usage

```sh
npx projen new --from projen_practical_constructs python_basic
```

The constructs can be used separately to adapt to your specific needs, but you can use the PythonProject construct with a default configuration of the entire stack to easily have a full project structure with build, test and linting capabilities.

## Development

### Tests

* We use a lot of snapshots on our tests, which in general is not a good practice. But in our case we decided to use it because there are lots of files and the snapshots will check if the file contents were changed.
* Be careful checking manually the errors on snapshots before updating them to be sure that it's not a breaking change to the users of the library

### JSII

* The options of the constructs have to be "interface", not "types" because they are exposed to JSII and it works well only with interfaces
* The Project type must have an attribute with name "options" in constructor
* https://aws.github.io/jsii/specification/2-type-system/

### References

* Projen quick start: https://projen.io/docs/quick-starts/python/hello-world/
* https://projen.io/docs/concepts/projects/building-your-own/
* Sample code for Python contructs: https://github.com/projen/projen/blob/main/src/python/pip.ts
* https://kennethwinner.com/2021/03/07/projen-external-module-github/
* Example project of a Python Projen Type: https://github.com/kcwinner/projen-github-demo
