r'''
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
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import projen as _projen_04054675


@jsii.data_type(
    jsii_type="projen-practical-constructs.BasePublishOptions",
    jsii_struct_bases=[],
    name_mapping={"group": "group", "registry_url": "registryUrl"},
)
class BasePublishOptions:
    def __init__(
        self,
        *,
        group: typing.Optional[builtins.str] = None,
        registry_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param group: If defined, will suffix the task name by this name so that multiple publish tasks with different configurations can be defined in the same project. If not defined, the task name will be "publish-python". Default: ''
        :param registry_url: Sets the registry url to publish to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__739100f3446c486a63d16f0ecb589004c014d9dea8e406024a252595e4bc646c)
            check_type(argname="argument group", value=group, expected_type=type_hints["group"])
            check_type(argname="argument registry_url", value=registry_url, expected_type=type_hints["registry_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if group is not None:
            self._values["group"] = group
        if registry_url is not None:
            self._values["registry_url"] = registry_url

    @builtins.property
    def group(self) -> typing.Optional[builtins.str]:
        '''If defined, will suffix the task name by this name so that multiple publish tasks with different configurations can be defined in the same project.

        If not defined, the task name will be "publish-python".

        :default: ''
        '''
        result = self._values.get("group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry_url(self) -> typing.Optional[builtins.str]:
        '''Sets the registry url to publish to.'''
        result = self._values.get("registry_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BasePublishOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen-practical-constructs.BaseTasksOptions",
    jsii_struct_bases=[],
    name_mapping={
        "build_enable": "buildEnable",
        "cleanup_default_tasks": "cleanupDefaultTasks",
        "deploy_enable": "deployEnable",
        "lint_enable": "lintEnable",
        "publish_enable": "publishEnable",
        "release_enable": "releaseEnable",
        "release_opts": "releaseOpts",
        "test_enable": "testEnable",
    },
)
class BaseTasksOptions:
    def __init__(
        self,
        *,
        build_enable: typing.Optional[builtins.bool] = None,
        cleanup_default_tasks: typing.Optional[builtins.bool] = None,
        deploy_enable: typing.Optional[builtins.bool] = None,
        lint_enable: typing.Optional[builtins.bool] = None,
        publish_enable: typing.Optional[builtins.bool] = None,
        release_enable: typing.Optional[builtins.bool] = None,
        release_opts: typing.Optional[typing.Union["ReleaseOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        test_enable: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param build_enable: Whether to include the build task with all its default subtasks.
        :param cleanup_default_tasks: Whether to cleanup default tasks (build, test, compile, package, pre-compile, post-compile) before adding new ones. Default: true
        :param deploy_enable: Whether to include deploy tasks.
        :param lint_enable: Whether to include the lint tasks.
        :param publish_enable: Whether to include publish tasks.
        :param release_enable: Whether to include release tasks.
        :param release_opts: Release task options.
        :param test_enable: Whether to include the test tasks.
        '''
        if isinstance(release_opts, dict):
            release_opts = ReleaseOptions(**release_opts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fbe00fbf2112c6148f8298ce3d28f4cf74b9b66df64977e945cc317c1ab07f8)
            check_type(argname="argument build_enable", value=build_enable, expected_type=type_hints["build_enable"])
            check_type(argname="argument cleanup_default_tasks", value=cleanup_default_tasks, expected_type=type_hints["cleanup_default_tasks"])
            check_type(argname="argument deploy_enable", value=deploy_enable, expected_type=type_hints["deploy_enable"])
            check_type(argname="argument lint_enable", value=lint_enable, expected_type=type_hints["lint_enable"])
            check_type(argname="argument publish_enable", value=publish_enable, expected_type=type_hints["publish_enable"])
            check_type(argname="argument release_enable", value=release_enable, expected_type=type_hints["release_enable"])
            check_type(argname="argument release_opts", value=release_opts, expected_type=type_hints["release_opts"])
            check_type(argname="argument test_enable", value=test_enable, expected_type=type_hints["test_enable"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if build_enable is not None:
            self._values["build_enable"] = build_enable
        if cleanup_default_tasks is not None:
            self._values["cleanup_default_tasks"] = cleanup_default_tasks
        if deploy_enable is not None:
            self._values["deploy_enable"] = deploy_enable
        if lint_enable is not None:
            self._values["lint_enable"] = lint_enable
        if publish_enable is not None:
            self._values["publish_enable"] = publish_enable
        if release_enable is not None:
            self._values["release_enable"] = release_enable
        if release_opts is not None:
            self._values["release_opts"] = release_opts
        if test_enable is not None:
            self._values["test_enable"] = test_enable

    @builtins.property
    def build_enable(self) -> typing.Optional[builtins.bool]:
        '''Whether to include the build task with all its default subtasks.'''
        result = self._values.get("build_enable")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cleanup_default_tasks(self) -> typing.Optional[builtins.bool]:
        '''Whether to cleanup default tasks (build, test, compile, package, pre-compile, post-compile) before adding new ones.

        :default: true
        '''
        result = self._values.get("cleanup_default_tasks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deploy_enable(self) -> typing.Optional[builtins.bool]:
        '''Whether to include deploy tasks.'''
        result = self._values.get("deploy_enable")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def lint_enable(self) -> typing.Optional[builtins.bool]:
        '''Whether to include the lint tasks.'''
        result = self._values.get("lint_enable")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def publish_enable(self) -> typing.Optional[builtins.bool]:
        '''Whether to include publish tasks.'''
        result = self._values.get("publish_enable")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_enable(self) -> typing.Optional[builtins.bool]:
        '''Whether to include release tasks.'''
        result = self._values.get("release_enable")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_opts(self) -> typing.Optional["ReleaseOptions"]:
        '''Release task options.'''
        result = self._values.get("release_opts")
        return typing.cast(typing.Optional["ReleaseOptions"], result)

    @builtins.property
    def test_enable(self) -> typing.Optional[builtins.bool]:
        '''Whether to include the test tasks.'''
        result = self._values.get("test_enable")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseTasksOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BaseTooling(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.BaseTooling",
):
    '''Base tooling for projen projects Creates a Makefile-projen file with common targets used in projen projects and a Makefile file that can be edited by devs.'''

    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        additional_makefile_contents_user: typing.Optional[builtins.str] = None,
        additional_makefile_contents_projen: typing.Optional[builtins.str] = None,
        additional_makefile_contents_targets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        node_version: typing.Optional[builtins.str] = None,
        projen_lib_version: typing.Optional[builtins.str] = None,
        ts_node_lib_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param additional_makefile_contents_user: Additional contents to be added to Makefile, which is a sample and can be edited by devs after the initial generation.
        :param additional_makefile_contents_projen: Additional contents to be added to the Makefile on top of the default projen related targets. Default: - no additional rules
        :param additional_makefile_contents_targets: Additional contents to be added to each target of the Makefile.
        :param node_version: Node version to be added to the .nvmrc file. Default: '20.16.0'
        :param projen_lib_version: The version of projen lib to be used in "prepare" target of the Makefile to install tooling for Projen to work. Default: '0.91.13'
        :param ts_node_lib_version: The version of ts-node lib to be used in "prepare" target of the Makefile to install tooling for Projen to work. Default: '10.9.2'
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__436b158be7f28d681734521217f52de403cd8b97b08ab3c35b8eb11658f9bbce)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        opts = BaseToolingOptions(
            additional_makefile_contents_user=additional_makefile_contents_user,
            additional_makefile_contents_projen=additional_makefile_contents_projen,
            additional_makefile_contents_targets=additional_makefile_contents_targets,
            node_version=node_version,
            projen_lib_version=projen_lib_version,
            ts_node_lib_version=ts_node_lib_version,
        )

        jsii.create(self.__class__, self, [project, opts])


@jsii.data_type(
    jsii_type="projen-practical-constructs.Build0Options",
    jsii_struct_bases=[],
    name_mapping={"pip": "pip", "pkg": "pkg"},
)
class Build0Options:
    def __init__(
        self,
        *,
        pip: typing.Optional[typing.Union["PipOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        pkg: typing.Optional[typing.Union["PackageOptions", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param pip: 
        :param pkg: 
        '''
        if isinstance(pip, dict):
            pip = PipOptions(**pip)
        if isinstance(pkg, dict):
            pkg = PackageOptions(**pkg)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e20a491b2a5a4f8ee18f05888a4892e7e41c691d596b28ee23e4eec41be056ba)
            check_type(argname="argument pip", value=pip, expected_type=type_hints["pip"])
            check_type(argname="argument pkg", value=pkg, expected_type=type_hints["pkg"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if pip is not None:
            self._values["pip"] = pip
        if pkg is not None:
            self._values["pkg"] = pkg

    @builtins.property
    def pip(self) -> typing.Optional["PipOptions"]:
        result = self._values.get("pip")
        return typing.cast(typing.Optional["PipOptions"], result)

    @builtins.property
    def pkg(self) -> typing.Optional["PackageOptions"]:
        result = self._values.get("pkg")
        return typing.cast(typing.Optional["PackageOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Build0Options(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BuildTarget(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.BuildTarget",
):
    '''Python project build configurations.'''

    def __init__(
        self,
        project: _projen_04054675.Project,
        task_opts: typing.Union["TaskOptions", typing.Dict[builtins.str, typing.Any]],
        *,
        pip: typing.Optional[typing.Union["PipOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        pkg: typing.Optional[typing.Union["PackageOptions", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param project: -
        :param task_opts: -
        :param pip: 
        :param pkg: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7baf093ce1415d71f61d9818afeb26e3072bbd9a78db8ca4ffdf96dcf200c73)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument task_opts", value=task_opts, expected_type=type_hints["task_opts"])
        opts = Build0Options(pip=pip, pkg=pkg)

        jsii.create(self.__class__, self, [project, task_opts, opts])


@jsii.enum(jsii_type="projen-practical-constructs.CommonTargets")
class CommonTargets(enum.Enum):
    BUILD = "BUILD"
    INSTALL = "INSTALL"
    COMPILE = "COMPILE"
    PACKAGE = "PACKAGE"
    LINT = "LINT"
    LINT_FIX = "LINT_FIX"
    TEST = "TEST"
    RELEASE = "RELEASE"
    DEPLOY = "DEPLOY"
    PUBLISH = "PUBLISH"


class CommonTargetsTasks(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.CommonTargetsTasks",
):
    '''Base tasks for projen projects based on "common-targets" (https://github.com/flaviostutz/common-targets).'''

    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        build_enable: typing.Optional[builtins.bool] = None,
        cleanup_default_tasks: typing.Optional[builtins.bool] = None,
        deploy_enable: typing.Optional[builtins.bool] = None,
        lint_enable: typing.Optional[builtins.bool] = None,
        publish_enable: typing.Optional[builtins.bool] = None,
        release_enable: typing.Optional[builtins.bool] = None,
        release_opts: typing.Optional[typing.Union["ReleaseOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        test_enable: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param project: -
        :param build_enable: Whether to include the build task with all its default subtasks.
        :param cleanup_default_tasks: Whether to cleanup default tasks (build, test, compile, package, pre-compile, post-compile) before adding new ones. Default: true
        :param deploy_enable: Whether to include deploy tasks.
        :param lint_enable: Whether to include the lint tasks.
        :param publish_enable: Whether to include publish tasks.
        :param release_enable: Whether to include release tasks.
        :param release_opts: Release task options.
        :param test_enable: Whether to include the test tasks.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1518020ed9b2c4f61d13717bb8484f0d701535897dcf01674908de9a9faa98bd)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        opts = BaseTasksOptions(
            build_enable=build_enable,
            cleanup_default_tasks=cleanup_default_tasks,
            deploy_enable=deploy_enable,
            lint_enable=lint_enable,
            publish_enable=publish_enable,
            release_enable=release_enable,
            release_opts=release_opts,
            test_enable=test_enable,
        )

        jsii.create(self.__class__, self, [project, opts])


class CoveragercFile(
    _projen_04054675.FileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.CoveragercFile",
):
    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        format: typing.Optional[builtins.str] = None,
        min_coverage: typing.Optional[jsii.Number] = None,
        omit_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        skip_covered: typing.Optional[builtins.bool] = None,
        skip_empty: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param project: -
        :param format: Coverage report format. Default: 'text'
        :param min_coverage: Minimum coverage required to pass the test. Default: 80
        :param omit_patterns: List of file patterns to omit from coverage. Default: []
        :param skip_covered: Skip reporting files that are covered. Default: false
        :param skip_empty: Skip reporting files that are empty. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__159e518f7881abcb6abee9cf04ea6e882729784c5e0b7a737f6522baa1f5a152)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        opts = CoveragercFileOptions(
            format=format,
            min_coverage=min_coverage,
            omit_patterns=omit_patterns,
            skip_covered=skip_covered,
            skip_empty=skip_empty,
        )

        jsii.create(self.__class__, self, [project, opts])

    @jsii.member(jsii_name="synthesizeContent")
    def _synthesize_content(
        self,
        _resolver: _projen_04054675.IResolver,
    ) -> typing.Optional[builtins.str]:
        '''Implemented by derived classes and returns the contents of the file to emit.

        :param _resolver: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83d971dfa627ffd4740ef400fe2c07260cfc8a850bb5f15117be52c28cf8aacb)
            check_type(argname="argument _resolver", value=_resolver, expected_type=type_hints["_resolver"])
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "synthesizeContent", [_resolver]))


@jsii.data_type(
    jsii_type="projen-practical-constructs.CoveragercFileOptions",
    jsii_struct_bases=[],
    name_mapping={
        "format": "format",
        "min_coverage": "minCoverage",
        "omit_patterns": "omitPatterns",
        "skip_covered": "skipCovered",
        "skip_empty": "skipEmpty",
    },
)
class CoveragercFileOptions:
    def __init__(
        self,
        *,
        format: typing.Optional[builtins.str] = None,
        min_coverage: typing.Optional[jsii.Number] = None,
        omit_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        skip_covered: typing.Optional[builtins.bool] = None,
        skip_empty: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param format: Coverage report format. Default: 'text'
        :param min_coverage: Minimum coverage required to pass the test. Default: 80
        :param omit_patterns: List of file patterns to omit from coverage. Default: []
        :param skip_covered: Skip reporting files that are covered. Default: false
        :param skip_empty: Skip reporting files that are empty. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf0f342ecc7c849d461adb9b6dac4d82650ef73565eff25d53bbcfb2b3c5479d)
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
            check_type(argname="argument min_coverage", value=min_coverage, expected_type=type_hints["min_coverage"])
            check_type(argname="argument omit_patterns", value=omit_patterns, expected_type=type_hints["omit_patterns"])
            check_type(argname="argument skip_covered", value=skip_covered, expected_type=type_hints["skip_covered"])
            check_type(argname="argument skip_empty", value=skip_empty, expected_type=type_hints["skip_empty"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if format is not None:
            self._values["format"] = format
        if min_coverage is not None:
            self._values["min_coverage"] = min_coverage
        if omit_patterns is not None:
            self._values["omit_patterns"] = omit_patterns
        if skip_covered is not None:
            self._values["skip_covered"] = skip_covered
        if skip_empty is not None:
            self._values["skip_empty"] = skip_empty

    @builtins.property
    def format(self) -> typing.Optional[builtins.str]:
        '''Coverage report format.

        :default: 'text'
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_coverage(self) -> typing.Optional[jsii.Number]:
        '''Minimum coverage required to pass the test.

        :default: 80
        '''
        result = self._values.get("min_coverage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def omit_patterns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of file patterns to omit from coverage.

        :default: []
        '''
        result = self._values.get("omit_patterns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def skip_covered(self) -> typing.Optional[builtins.bool]:
        '''Skip reporting files that are covered.

        :default: false
        '''
        result = self._values.get("skip_covered")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def skip_empty(self) -> typing.Optional[builtins.bool]:
        '''Skip reporting files that are empty.

        :default: true
        '''
        result = self._values.get("skip_empty")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CoveragercFileOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LintTarget(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.LintTarget",
):
    '''Python project lint configurations.'''

    def __init__(
        self,
        project: _projen_04054675.Project,
        task_options: typing.Union["TaskOptions", typing.Dict[builtins.str, typing.Any]],
        *,
        attach_fix_task_to: typing.Optional[builtins.str] = None,
        add_to_existing_rules: typing.Optional[builtins.bool] = None,
        ignore_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
        mccabe_max_complexity: typing.Optional[jsii.Number] = None,
        per_file_ignores: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
        select_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_python_version: typing.Optional[builtins.str] = None,
        unsafe_fixes: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param project: -
        :param task_options: -
        :param attach_fix_task_to: Attach lint fix tasks to parent.
        :param add_to_existing_rules: Add rules defined here to the ignoreRules and selectRules (on top of the default rules) or replace them by this contents? Default: true
        :param ignore_rules: Default: pre-selected set of rules
        :param mccabe_max_complexity: Default: 14
        :param per_file_ignores: Default: ignore doc-string code format for test files
        :param select_rules: Default: pre-selected set of rules
        :param target_python_version: Default: py313
        :param unsafe_fixes: Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a024fae964b162f23bca5eaaea17d6482838424ff147cbcf777078f73bfeb68)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument task_options", value=task_options, expected_type=type_hints["task_options"])
        opts = LintOptions(
            attach_fix_task_to=attach_fix_task_to,
            add_to_existing_rules=add_to_existing_rules,
            ignore_rules=ignore_rules,
            mccabe_max_complexity=mccabe_max_complexity,
            per_file_ignores=per_file_ignores,
            select_rules=select_rules,
            target_python_version=target_python_version,
            unsafe_fixes=unsafe_fixes,
        )

        jsii.create(self.__class__, self, [project, task_options, opts])


class MakefileProjenFile(
    _projen_04054675.FileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.MakefileProjenFile",
):
    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        additional_makefile_contents_projen: typing.Optional[builtins.str] = None,
        additional_makefile_contents_targets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        node_version: typing.Optional[builtins.str] = None,
        projen_lib_version: typing.Optional[builtins.str] = None,
        ts_node_lib_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param additional_makefile_contents_projen: Additional contents to be added to the Makefile on top of the default projen related targets. Default: - no additional rules
        :param additional_makefile_contents_targets: Additional contents to be added to each target of the Makefile.
        :param node_version: Node version to be added to the .nvmrc file. Default: '20.16.0'
        :param projen_lib_version: The version of projen lib to be used in "prepare" target of the Makefile to install tooling for Projen to work. Default: '0.91.13'
        :param ts_node_lib_version: The version of ts-node lib to be used in "prepare" target of the Makefile to install tooling for Projen to work. Default: '10.9.2'
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__194924c3827e470ba642d1c88bb4907a87215e4b16aadd60a0d921ea7d4b1773)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        opts = MakefileProjenOptions(
            additional_makefile_contents_projen=additional_makefile_contents_projen,
            additional_makefile_contents_targets=additional_makefile_contents_targets,
            node_version=node_version,
            projen_lib_version=projen_lib_version,
            ts_node_lib_version=ts_node_lib_version,
        )

        jsii.create(self.__class__, self, [project, opts])

    @jsii.member(jsii_name="synthesizeContent")
    def _synthesize_content(
        self,
        _resolver: _projen_04054675.IResolver,
    ) -> typing.Optional[builtins.str]:
        '''Implemented by derived classes and returns the contents of the file to emit.

        :param _resolver: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dae95ffeccf6c3d4b413b4c0dce096bdaa222a21b141caf613a05718e6a8e70c)
            check_type(argname="argument _resolver", value=_resolver, expected_type=type_hints["_resolver"])
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "synthesizeContent", [_resolver]))


@jsii.data_type(
    jsii_type="projen-practical-constructs.MakefileProjenOptions",
    jsii_struct_bases=[],
    name_mapping={
        "additional_makefile_contents_projen": "additionalMakefileContentsProjen",
        "additional_makefile_contents_targets": "additionalMakefileContentsTargets",
        "node_version": "nodeVersion",
        "projen_lib_version": "projenLibVersion",
        "ts_node_lib_version": "tsNodeLibVersion",
    },
)
class MakefileProjenOptions:
    def __init__(
        self,
        *,
        additional_makefile_contents_projen: typing.Optional[builtins.str] = None,
        additional_makefile_contents_targets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        node_version: typing.Optional[builtins.str] = None,
        projen_lib_version: typing.Optional[builtins.str] = None,
        ts_node_lib_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param additional_makefile_contents_projen: Additional contents to be added to the Makefile on top of the default projen related targets. Default: - no additional rules
        :param additional_makefile_contents_targets: Additional contents to be added to each target of the Makefile.
        :param node_version: Node version to be added to the .nvmrc file. Default: '20.16.0'
        :param projen_lib_version: The version of projen lib to be used in "prepare" target of the Makefile to install tooling for Projen to work. Default: '0.91.13'
        :param ts_node_lib_version: The version of ts-node lib to be used in "prepare" target of the Makefile to install tooling for Projen to work. Default: '10.9.2'
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2645adc140a8ad315ff517954172686050477a4694117129efad8ba0a97669e9)
            check_type(argname="argument additional_makefile_contents_projen", value=additional_makefile_contents_projen, expected_type=type_hints["additional_makefile_contents_projen"])
            check_type(argname="argument additional_makefile_contents_targets", value=additional_makefile_contents_targets, expected_type=type_hints["additional_makefile_contents_targets"])
            check_type(argname="argument node_version", value=node_version, expected_type=type_hints["node_version"])
            check_type(argname="argument projen_lib_version", value=projen_lib_version, expected_type=type_hints["projen_lib_version"])
            check_type(argname="argument ts_node_lib_version", value=ts_node_lib_version, expected_type=type_hints["ts_node_lib_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if additional_makefile_contents_projen is not None:
            self._values["additional_makefile_contents_projen"] = additional_makefile_contents_projen
        if additional_makefile_contents_targets is not None:
            self._values["additional_makefile_contents_targets"] = additional_makefile_contents_targets
        if node_version is not None:
            self._values["node_version"] = node_version
        if projen_lib_version is not None:
            self._values["projen_lib_version"] = projen_lib_version
        if ts_node_lib_version is not None:
            self._values["ts_node_lib_version"] = ts_node_lib_version

    @builtins.property
    def additional_makefile_contents_projen(self) -> typing.Optional[builtins.str]:
        '''Additional contents to be added to the Makefile on top of the default projen related targets.

        :default: - no additional rules
        '''
        result = self._values.get("additional_makefile_contents_projen")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def additional_makefile_contents_targets(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Additional contents to be added to each target of the Makefile.'''
        result = self._values.get("additional_makefile_contents_targets")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def node_version(self) -> typing.Optional[builtins.str]:
        '''Node version to be added to the .nvmrc file.

        :default: '20.16.0'
        '''
        result = self._values.get("node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projen_lib_version(self) -> typing.Optional[builtins.str]:
        '''The version of projen lib to be used in "prepare" target of the Makefile to install tooling for Projen to work.

        :default: '0.91.13'
        '''
        result = self._values.get("projen_lib_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ts_node_lib_version(self) -> typing.Optional[builtins.str]:
        '''The version of ts-node lib to be used in "prepare" target of the Makefile to install tooling for Projen to work.

        :default: '10.9.2'
        '''
        result = self._values.get("ts_node_lib_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MakefileProjenOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MyPy(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.MyPy",
):
    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        venv_path: builtins.str,
    ) -> None:
        '''
        :param project: -
        :param venv_path: Path to the python virtual environment directory used in this project.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0a177ef285e9d814c79f51d94f6a5469ba5493c4e5b3b7f83c91a7cb2308c59)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        task_opts = TaskOptions(venv_path=venv_path)

        jsii.create(self.__class__, self, [project, task_opts])


class MyPyIniFile(
    _projen_04054675.FileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.MyPyIniFile",
):
    def __init__(self, project: _projen_04054675.Project) -> None:
        '''
        :param project: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4de587b589ba9e007f9440a8c64dc04332c03c6a61c1fbeab978cb77f04fc58)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        jsii.create(self.__class__, self, [project])

    @jsii.member(jsii_name="synthesizeContent")
    def _synthesize_content(
        self,
        _resolver: _projen_04054675.IResolver,
    ) -> typing.Optional[builtins.str]:
        '''Implemented by derived classes and returns the contents of the file to emit.

        :param _resolver: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05af635c22d0af271080341bf52a1ec29b58a9cb63c5ea1521a193ee6570270e)
            check_type(argname="argument _resolver", value=_resolver, expected_type=type_hints["_resolver"])
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "synthesizeContent", [_resolver]))


@jsii.data_type(
    jsii_type="projen-practical-constructs.NextTagOptions",
    jsii_struct_bases=[],
    name_mapping={
        "bump_action": "bumpAction",
        "bump_files": "bumpFiles",
        "changelog_file": "changelogFile",
        "from_ref": "fromRef",
        "git_email": "gitEmail",
        "git_username": "gitUsername",
        "max_version": "maxVersion",
        "min_version": "minVersion",
        "monotag_cmd": "monotagCmd",
        "monotag_extra_args": "monotagExtraArgs",
        "notes_file": "notesFile",
        "only_conv_commit": "onlyConvCommit",
        "path": "path",
        "pre_release": "preRelease",
        "pre_release_always_increment": "preReleaseAlwaysIncrement",
        "pre_release_identifier": "preReleaseIdentifier",
        "repo_dir": "repoDir",
        "semver_level": "semverLevel",
        "tag_file": "tagFile",
        "tag_prefix": "tagPrefix",
        "tag_suffix": "tagSuffix",
        "to_ref": "toRef",
        "verbose": "verbose",
        "version_file": "versionFile",
    },
)
class NextTagOptions:
    def __init__(
        self,
        *,
        bump_action: typing.Optional[builtins.str] = None,
        bump_files: typing.Optional[typing.Sequence[builtins.str]] = None,
        changelog_file: typing.Optional[builtins.str] = None,
        from_ref: typing.Optional[builtins.str] = None,
        git_email: typing.Optional[builtins.str] = None,
        git_username: typing.Optional[builtins.str] = None,
        max_version: typing.Optional[builtins.str] = None,
        min_version: typing.Optional[builtins.str] = None,
        monotag_cmd: typing.Optional[builtins.str] = None,
        monotag_extra_args: typing.Optional[builtins.str] = None,
        notes_file: typing.Optional[builtins.str] = None,
        only_conv_commit: typing.Optional[builtins.bool] = None,
        path: typing.Optional[builtins.str] = None,
        pre_release: typing.Optional[builtins.bool] = None,
        pre_release_always_increment: typing.Optional[builtins.bool] = None,
        pre_release_identifier: typing.Optional[builtins.str] = None,
        repo_dir: typing.Optional[builtins.str] = None,
        semver_level: typing.Optional[builtins.str] = None,
        tag_file: typing.Optional[builtins.str] = None,
        tag_prefix: typing.Optional[builtins.str] = None,
        tag_suffix: typing.Optional[builtins.str] = None,
        to_ref: typing.Optional[builtins.str] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Options for analyzing and generating a new tag.

        :param bump_action: Bump action to be performed after the tag is generated in regard to package files such as package.json, pyproject.yml etc Should be one of: - 'latest': bump the version field of the files to the calculated tag - 'zero': bump the version field of the files to 0.0.0 - 'none': won't change any files. Default: 'none'
        :param bump_files: Files to be bumped with the latest version It will search for a "version" attribute in the file, replace it with the new version and save If the field doesn't exist, it won't be changed. Default: ['package.json']
        :param changelog_file: File with the changelog that will be updated with the new version During update, this will check if the version is already present in the changelog and skip generation if it's already there. Normally this file is named CHANGELOG.md Default: undefined (won't be created)
        :param from_ref: Git ref range (starting point) for searching for changes in git log history. Default: latest tag
        :param git_email: Configure git cli with email Required if action is 'commit', 'tag' or 'push'.
        :param git_username: Configure git cli with username Required if action is 'commit', 'tag' or 'push'.
        :param max_version: Maximum version for the generated tag. If the generated version is higher than this, the operation will fail Default: no limit
        :param min_version: Minimum version for the generated tag. If the naturally incremented version is lower, this value will be used Default: no limit
        :param monotag_cmd: Command line used to invoke Monotag to perform tag calculations. Default: 'npx monotag@1.14.0'
        :param monotag_extra_args: Extra arguments to be added to every invocation of Monotag. Default: ''
        :param notes_file: File that will be written with the notes with the changes detected The content will be a markdown with a list of commits. Default: undefined (won't be created)
        :param only_conv_commit: Only take into consideration git commits that follows the conventional commits format while rendering release notes. Default: false
        :param path: Path inside repository for looking for changes Defaults to any path. Default: ''
        :param pre_release: If the generated version is a pre-release This will add a pre-release identifier to the version. E.g.: 1.0.0-beta This will automatically create a pre-release version depending on the semverLevel identified by commit message analysis based on conventional commits. For example, if the commits contain a breaking change, the version will be a major pre-release. So if it was 1.2.2, it will be 2.0.0-beta. If it was 3.2.1, it will be 4.0.0-beta. The same applies for minor and patch levels. Default: false
        :param pre_release_always_increment: If true, the pre-release version will always be incremented even if no changes are detected So subsequent calls to 'nextTag' will always increment the pre-release version. Default: false
        :param pre_release_identifier: Pre-release identifier. Default: 'beta'
        :param repo_dir: Directory where the git repository is located Defaults to local directory. Default: '.'
        :param semver_level: Which level to increment the version. If undefined, it will be automatic, based on commit messages Default: undefined
        :param tag_file: File that will be written with the tag name (e.g.: myservice/1.2.3-beta.0). Default: undefined (won't be created)
        :param tag_prefix: Tag prefix to look for latest tag and for generating the tag. Default: ''
        :param tag_suffix: Tag suffix to add to the generated tag When using pre-release capabilities, that will manage and increment prerelease versions, this will be added to the generated version. E.g.: 1.0.0-beta.1-MY_SUFFIX, if tagSuffix is '-MY_SUFFIX' Default: ''
        :param to_ref: Git ref range (ending point) for searching for changes in git log history Defaults to HEAD. Default: HEAD
        :param verbose: Output messages about what is being done Such as git commands being executed etc. Default: false
        :param version_file: File that will be written with the version (e.g.: 1.2.3-beta.0). Default: undefined (won't be created)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecd81b6dce26aa3ffbefaefa78378441a430787e56901243ad411e0e128c0f90)
            check_type(argname="argument bump_action", value=bump_action, expected_type=type_hints["bump_action"])
            check_type(argname="argument bump_files", value=bump_files, expected_type=type_hints["bump_files"])
            check_type(argname="argument changelog_file", value=changelog_file, expected_type=type_hints["changelog_file"])
            check_type(argname="argument from_ref", value=from_ref, expected_type=type_hints["from_ref"])
            check_type(argname="argument git_email", value=git_email, expected_type=type_hints["git_email"])
            check_type(argname="argument git_username", value=git_username, expected_type=type_hints["git_username"])
            check_type(argname="argument max_version", value=max_version, expected_type=type_hints["max_version"])
            check_type(argname="argument min_version", value=min_version, expected_type=type_hints["min_version"])
            check_type(argname="argument monotag_cmd", value=monotag_cmd, expected_type=type_hints["monotag_cmd"])
            check_type(argname="argument monotag_extra_args", value=monotag_extra_args, expected_type=type_hints["monotag_extra_args"])
            check_type(argname="argument notes_file", value=notes_file, expected_type=type_hints["notes_file"])
            check_type(argname="argument only_conv_commit", value=only_conv_commit, expected_type=type_hints["only_conv_commit"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument pre_release", value=pre_release, expected_type=type_hints["pre_release"])
            check_type(argname="argument pre_release_always_increment", value=pre_release_always_increment, expected_type=type_hints["pre_release_always_increment"])
            check_type(argname="argument pre_release_identifier", value=pre_release_identifier, expected_type=type_hints["pre_release_identifier"])
            check_type(argname="argument repo_dir", value=repo_dir, expected_type=type_hints["repo_dir"])
            check_type(argname="argument semver_level", value=semver_level, expected_type=type_hints["semver_level"])
            check_type(argname="argument tag_file", value=tag_file, expected_type=type_hints["tag_file"])
            check_type(argname="argument tag_prefix", value=tag_prefix, expected_type=type_hints["tag_prefix"])
            check_type(argname="argument tag_suffix", value=tag_suffix, expected_type=type_hints["tag_suffix"])
            check_type(argname="argument to_ref", value=to_ref, expected_type=type_hints["to_ref"])
            check_type(argname="argument verbose", value=verbose, expected_type=type_hints["verbose"])
            check_type(argname="argument version_file", value=version_file, expected_type=type_hints["version_file"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bump_action is not None:
            self._values["bump_action"] = bump_action
        if bump_files is not None:
            self._values["bump_files"] = bump_files
        if changelog_file is not None:
            self._values["changelog_file"] = changelog_file
        if from_ref is not None:
            self._values["from_ref"] = from_ref
        if git_email is not None:
            self._values["git_email"] = git_email
        if git_username is not None:
            self._values["git_username"] = git_username
        if max_version is not None:
            self._values["max_version"] = max_version
        if min_version is not None:
            self._values["min_version"] = min_version
        if monotag_cmd is not None:
            self._values["monotag_cmd"] = monotag_cmd
        if monotag_extra_args is not None:
            self._values["monotag_extra_args"] = monotag_extra_args
        if notes_file is not None:
            self._values["notes_file"] = notes_file
        if only_conv_commit is not None:
            self._values["only_conv_commit"] = only_conv_commit
        if path is not None:
            self._values["path"] = path
        if pre_release is not None:
            self._values["pre_release"] = pre_release
        if pre_release_always_increment is not None:
            self._values["pre_release_always_increment"] = pre_release_always_increment
        if pre_release_identifier is not None:
            self._values["pre_release_identifier"] = pre_release_identifier
        if repo_dir is not None:
            self._values["repo_dir"] = repo_dir
        if semver_level is not None:
            self._values["semver_level"] = semver_level
        if tag_file is not None:
            self._values["tag_file"] = tag_file
        if tag_prefix is not None:
            self._values["tag_prefix"] = tag_prefix
        if tag_suffix is not None:
            self._values["tag_suffix"] = tag_suffix
        if to_ref is not None:
            self._values["to_ref"] = to_ref
        if verbose is not None:
            self._values["verbose"] = verbose
        if version_file is not None:
            self._values["version_file"] = version_file

    @builtins.property
    def bump_action(self) -> typing.Optional[builtins.str]:
        '''Bump action to be performed after the tag is generated in regard to package files such as package.json, pyproject.yml etc Should be one of:   - 'latest': bump the version field of the files to the calculated tag   - 'zero': bump the version field of the files to 0.0.0   - 'none': won't change any files.

        :default: 'none'
        '''
        result = self._values.get("bump_action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bump_files(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Files to be bumped with the latest version It will search for a "version" attribute in the file, replace it with the new version and save If the field doesn't exist, it won't be changed.

        :default: ['package.json']
        '''
        result = self._values.get("bump_files")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def changelog_file(self) -> typing.Optional[builtins.str]:
        '''File with the changelog that will be updated with the new version During update, this will check if the version is already present in the changelog and skip generation if it's already there.

        Normally this file is named CHANGELOG.md

        :default: undefined (won't be created)
        '''
        result = self._values.get("changelog_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def from_ref(self) -> typing.Optional[builtins.str]:
        '''Git ref range (starting point) for searching for changes in git log history.

        :default: latest tag
        '''
        result = self._values.get("from_ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def git_email(self) -> typing.Optional[builtins.str]:
        '''Configure git cli with email Required if action is 'commit', 'tag' or 'push'.'''
        result = self._values.get("git_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def git_username(self) -> typing.Optional[builtins.str]:
        '''Configure git cli with username Required if action is 'commit', 'tag' or 'push'.'''
        result = self._values.get("git_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_version(self) -> typing.Optional[builtins.str]:
        '''Maximum version for the generated tag.

        If the generated version is higher than this, the operation will fail

        :default: no limit
        '''
        result = self._values.get("max_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_version(self) -> typing.Optional[builtins.str]:
        '''Minimum version for the generated tag.

        If the naturally incremented version is lower, this value will be used

        :default: no limit
        '''
        result = self._values.get("min_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def monotag_cmd(self) -> typing.Optional[builtins.str]:
        '''Command line used to invoke Monotag to perform tag calculations.

        :default: 'npx monotag@1.14.0'
        '''
        result = self._values.get("monotag_cmd")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def monotag_extra_args(self) -> typing.Optional[builtins.str]:
        '''Extra arguments to be added to every invocation of Monotag.

        :default: ''
        '''
        result = self._values.get("monotag_extra_args")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notes_file(self) -> typing.Optional[builtins.str]:
        '''File that will be written with the notes with the changes detected The content will be a markdown with a list of commits.

        :default: undefined (won't be created)
        '''
        result = self._values.get("notes_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def only_conv_commit(self) -> typing.Optional[builtins.bool]:
        '''Only take into consideration git commits that follows the conventional commits format while rendering release notes.

        :default: false
        '''
        result = self._values.get("only_conv_commit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Path inside repository for looking for changes Defaults to any path.

        :default: ''
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_release(self) -> typing.Optional[builtins.bool]:
        '''If the generated version is a pre-release This will add a pre-release identifier to the version.

        E.g.: 1.0.0-beta
        This will automatically create a pre-release version depending on the semverLevel
        identified by commit message analysis based on conventional commits.
        For example, if the commits contain a breaking change, the version will be a major pre-release.
        So if it was 1.2.2, it will be 2.0.0-beta. If it was 3.2.1, it will be 4.0.0-beta.
        The same applies for minor and patch levels.

        :default: false
        '''
        result = self._values.get("pre_release")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pre_release_always_increment(self) -> typing.Optional[builtins.bool]:
        '''If true, the pre-release version will always be incremented even if no changes are detected So subsequent calls to 'nextTag' will always increment the pre-release version.

        :default: false
        '''
        result = self._values.get("pre_release_always_increment")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pre_release_identifier(self) -> typing.Optional[builtins.str]:
        '''Pre-release identifier.

        :default: 'beta'
        '''
        result = self._values.get("pre_release_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repo_dir(self) -> typing.Optional[builtins.str]:
        '''Directory where the git repository is located Defaults to local directory.

        :default: '.'
        '''
        result = self._values.get("repo_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def semver_level(self) -> typing.Optional[builtins.str]:
        '''Which level to increment the version.

        If undefined, it will be automatic, based on commit messages

        :default: undefined
        '''
        result = self._values.get("semver_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag_file(self) -> typing.Optional[builtins.str]:
        '''File that will be written with the tag name (e.g.: myservice/1.2.3-beta.0).

        :default: undefined (won't be created)
        '''
        result = self._values.get("tag_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag_prefix(self) -> typing.Optional[builtins.str]:
        '''Tag prefix to look for latest tag and for generating the tag.

        :default: ''
        '''
        result = self._values.get("tag_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag_suffix(self) -> typing.Optional[builtins.str]:
        '''Tag suffix to add to the generated tag When using pre-release capabilities, that will manage and increment prerelease versions, this will be added to the generated version.

        E.g.: 1.0.0-beta.1-MY_SUFFIX, if tagSuffix is '-MY_SUFFIX'

        :default: ''
        '''
        result = self._values.get("tag_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def to_ref(self) -> typing.Optional[builtins.str]:
        '''Git ref range (ending point) for searching for changes in git log history Defaults to HEAD.

        :default: HEAD
        '''
        result = self._values.get("to_ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def verbose(self) -> typing.Optional[builtins.bool]:
        '''Output messages about what is being done Such as git commands being executed etc.

        :default: false
        '''
        result = self._values.get("verbose")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def version_file(self) -> typing.Optional[builtins.str]:
        '''File that will be written with the version (e.g.: 1.2.3-beta.0).

        :default: undefined (won't be created)
        '''
        result = self._values.get("version_file")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NextTagOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NvmRcFile(
    _projen_04054675.FileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.NvmRcFile",
):
    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        node_version: builtins.str,
    ) -> None:
        '''
        :param project: -
        :param node_version: The version of Python to be added to the file.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d9124a878d068673b1222734c071726026044ca4bce4ce1337a5245bfb74f48)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        opts = NvmRcOptions(node_version=node_version)

        jsii.create(self.__class__, self, [project, opts])

    @jsii.member(jsii_name="synthesizeContent")
    def _synthesize_content(
        self,
        _resolver: _projen_04054675.IResolver,
    ) -> typing.Optional[builtins.str]:
        '''Implemented by derived classes and returns the contents of the file to emit.

        :param _resolver: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__036c6a629a999381eb4d9cdab4d09599981a6c980fb93168dd8d8c725d0d2d7e)
            check_type(argname="argument _resolver", value=_resolver, expected_type=type_hints["_resolver"])
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "synthesizeContent", [_resolver]))


@jsii.data_type(
    jsii_type="projen-practical-constructs.NvmRcOptions",
    jsii_struct_bases=[],
    name_mapping={"node_version": "nodeVersion"},
)
class NvmRcOptions:
    def __init__(self, *, node_version: builtins.str) -> None:
        '''
        :param node_version: The version of Python to be added to the file.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b123193e84e1be30d14b96bef4c234361f129b3e7fea6b31925ac7e6d2500d6)
            check_type(argname="argument node_version", value=node_version, expected_type=type_hints["node_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "node_version": node_version,
        }

    @builtins.property
    def node_version(self) -> builtins.str:
        '''The version of Python to be added to the file.

        :required: true
        '''
        result = self._values.get("node_version")
        assert result is not None, "Required property 'node_version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NvmRcOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Package(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.Package",
):
    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        license: typing.Optional[builtins.str] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license_file: typing.Optional[builtins.str] = None,
        package_name: typing.Optional[builtins.str] = None,
        readme: typing.Optional[builtins.str] = None,
        requires_python: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param license: License name in spdx format. e.g: ``MIT``, ``Apache-2.0``
        :param author_email: Author's e-mail.
        :param author_name: Author's name.
        :param classifiers: A list of PyPI trove classifiers that describe the project.
        :param description: A short description of the package.
        :param homepage: A URL to the website of the project.
        :param keywords: Keywords to add to the package.
        :param license_file: License file.
        :param package_name: Name of the python package. E.g. "my_python_package". Must only consist of alphanumeric characters and underscores. Default: Name of the directory
        :param readme: README file.
        :param requires_python: Python version required to run this package.
        :param version: Version of the package.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62f3584f77ee44c76622dd4d1bcb61319421c6ff75dc347a3de1892c0baf9086)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        opts = PackageOptions(
            license=license,
            author_email=author_email,
            author_name=author_name,
            classifiers=classifiers,
            description=description,
            homepage=homepage,
            keywords=keywords,
            license_file=license_file,
            package_name=package_name,
            readme=readme,
            requires_python=requires_python,
            version=version,
        )

        jsii.create(self.__class__, self, [project, opts])


class Pip(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.Pip",
):
    def __init__(
        self,
        project: _projen_04054675.Project,
        task_opts: typing.Union["TaskOptions", typing.Dict[builtins.str, typing.Any]],
        *,
        lock_file: typing.Optional[builtins.str] = None,
        lock_file_dev: typing.Optional[builtins.str] = None,
        python_exec: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param task_opts: -
        :param lock_file: Name of the file used to install dependencies from This file is derived from pyproject.toml and have to be manually updated if pyproject.toml is updated by using the projen task 'update-lockfile'. This lock won't include "dev" dependencies Read more at https://stackoverflow.com/questions/34645821/pip-constraints-files. Default: constraints.txt
        :param lock_file_dev: Same as lockFile, but it includes all dev dependencies. Default: constraints-dev.txt
        :param python_exec: Python executable path to be used while creating the virtual environment used in this project. Default: python
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6c809477032f6e6abdbfbf18de97c940c11e01375028ae0f5ecb6b8e973a50f)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument task_opts", value=task_opts, expected_type=type_hints["task_opts"])
        opts = PipOptions(
            lock_file=lock_file, lock_file_dev=lock_file_dev, python_exec=python_exec
        )

        jsii.create(self.__class__, self, [project, task_opts, opts])

    @jsii.member(jsii_name="postSynthesize")
    def post_synthesize(self) -> None:
        '''Called after synthesis.

        Order is *not* guaranteed.
        '''
        return typing.cast(None, jsii.invoke(self, "postSynthesize", []))


class PipAudit(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.PipAudit",
):
    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        venv_path: builtins.str,
    ) -> None:
        '''
        :param project: -
        :param venv_path: Path to the python virtual environment directory used in this project.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82328de1f2fc16d559d0de14506a0fa6977eaf5050623900f5ab343c6be250cb)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        opts = TaskOptions(venv_path=venv_path)

        jsii.create(self.__class__, self, [project, opts])


@jsii.data_type(
    jsii_type="projen-practical-constructs.PipOptions",
    jsii_struct_bases=[],
    name_mapping={
        "lock_file": "lockFile",
        "lock_file_dev": "lockFileDev",
        "python_exec": "pythonExec",
    },
)
class PipOptions:
    def __init__(
        self,
        *,
        lock_file: typing.Optional[builtins.str] = None,
        lock_file_dev: typing.Optional[builtins.str] = None,
        python_exec: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param lock_file: Name of the file used to install dependencies from This file is derived from pyproject.toml and have to be manually updated if pyproject.toml is updated by using the projen task 'update-lockfile'. This lock won't include "dev" dependencies Read more at https://stackoverflow.com/questions/34645821/pip-constraints-files. Default: constraints.txt
        :param lock_file_dev: Same as lockFile, but it includes all dev dependencies. Default: constraints-dev.txt
        :param python_exec: Python executable path to be used while creating the virtual environment used in this project. Default: python
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ab0570fbeee15a743ac44aee78db6330a9da7a8cb0af29bcd9bbd26f212ec73)
            check_type(argname="argument lock_file", value=lock_file, expected_type=type_hints["lock_file"])
            check_type(argname="argument lock_file_dev", value=lock_file_dev, expected_type=type_hints["lock_file_dev"])
            check_type(argname="argument python_exec", value=python_exec, expected_type=type_hints["python_exec"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if lock_file is not None:
            self._values["lock_file"] = lock_file
        if lock_file_dev is not None:
            self._values["lock_file_dev"] = lock_file_dev
        if python_exec is not None:
            self._values["python_exec"] = python_exec

    @builtins.property
    def lock_file(self) -> typing.Optional[builtins.str]:
        '''Name of the file used to install dependencies from This file is derived from pyproject.toml and have to be manually updated if pyproject.toml is updated by using the projen task 'update-lockfile'. This lock won't include "dev" dependencies Read more at https://stackoverflow.com/questions/34645821/pip-constraints-files.

        :default: constraints.txt
        '''
        result = self._values.get("lock_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lock_file_dev(self) -> typing.Optional[builtins.str]:
        '''Same as lockFile, but it includes all dev dependencies.

        :default: constraints-dev.txt
        '''
        result = self._values.get("lock_file_dev")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def python_exec(self) -> typing.Optional[builtins.str]:
        '''Python executable path to be used while creating the virtual environment used in this project.

        :default: python
        '''
        result = self._values.get("python_exec")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen-practical-constructs.PublishNpmOptions",
    jsii_struct_bases=[BasePublishOptions],
    name_mapping={
        "group": "group",
        "registry_url": "registryUrl",
        "packages_dir": "packagesDir",
    },
)
class PublishNpmOptions(BasePublishOptions):
    def __init__(
        self,
        *,
        group: typing.Optional[builtins.str] = None,
        registry_url: typing.Optional[builtins.str] = None,
        packages_dir: builtins.str,
    ) -> None:
        '''
        :param group: If defined, will suffix the task name by this name so that multiple publish tasks with different configurations can be defined in the same project. If not defined, the task name will be "publish-python". Default: ''
        :param registry_url: Sets the registry url to publish to.
        :param packages_dir: All JS packages in this directory will be published (*.tgz). Fails if no package is found. Default: "dist/js"
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17c08f1d83ea1c68434cc706bd3ab3f0d86a9134d0afbe1bd10ef7bfc93879ce)
            check_type(argname="argument group", value=group, expected_type=type_hints["group"])
            check_type(argname="argument registry_url", value=registry_url, expected_type=type_hints["registry_url"])
            check_type(argname="argument packages_dir", value=packages_dir, expected_type=type_hints["packages_dir"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "packages_dir": packages_dir,
        }
        if group is not None:
            self._values["group"] = group
        if registry_url is not None:
            self._values["registry_url"] = registry_url

    @builtins.property
    def group(self) -> typing.Optional[builtins.str]:
        '''If defined, will suffix the task name by this name so that multiple publish tasks with different configurations can be defined in the same project.

        If not defined, the task name will be "publish-python".

        :default: ''
        '''
        result = self._values.get("group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry_url(self) -> typing.Optional[builtins.str]:
        '''Sets the registry url to publish to.'''
        result = self._values.get("registry_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def packages_dir(self) -> builtins.str:
        '''All JS packages in this directory will be published (*.tgz). Fails if no package is found.

        :default: "dist/js"
        '''
        result = self._values.get("packages_dir")
        assert result is not None, "Required property 'packages_dir' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PublishNpmOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PublishNpmTasks(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.PublishNpmTasks",
):
    '''Publish JS packages in a directoty to a Npm registry.'''

    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        packages_dir: builtins.str,
        group: typing.Optional[builtins.str] = None,
        registry_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param packages_dir: All JS packages in this directory will be published (*.tgz). Fails if no package is found. Default: "dist/js"
        :param group: If defined, will suffix the task name by this name so that multiple publish tasks with different configurations can be defined in the same project. If not defined, the task name will be "publish-python". Default: ''
        :param registry_url: Sets the registry url to publish to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb758ea416713f75fc2acbbcb87bcba07398ad01870730f548e260a3139fd382)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        opts = PublishNpmOptions(
            packages_dir=packages_dir, group=group, registry_url=registry_url
        )

        jsii.create(self.__class__, self, [project, opts])

    @builtins.property
    @jsii.member(jsii_name="taskName")
    def task_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskName"))

    @task_name.setter
    def task_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7778bb246ad316593449349e235db7d2104fe408eeac0a9f5efcda22aacb114)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskName", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="projen-practical-constructs.PublishOptions",
    jsii_struct_bases=[],
    name_mapping={
        "build_task": "buildTask",
        "group": "group",
        "monotag_options": "monotagOptions",
        "npm": "npm",
        "pypi": "pypi",
        "skip_bump": "skipBump",
        "skip_checks": "skipChecks",
    },
)
class PublishOptions:
    def __init__(
        self,
        *,
        build_task: typing.Optional[builtins.str] = None,
        group: typing.Optional[builtins.str] = None,
        monotag_options: typing.Optional[typing.Union[NextTagOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        npm: typing.Optional[typing.Union[PublishNpmOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        pypi: typing.Optional[typing.Union["PublishPypiOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        skip_bump: typing.Optional[builtins.bool] = None,
        skip_checks: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param build_task: The name of the task that will be invoked to generate package files to be published. Default: 'build', if exists in project. If not, no build task will be invoked.
        :param group: If defined, will suffix the task name by this name so that multiple publish tasks with different configurations can be defined in the same project.
        :param monotag_options: Options for next tag calculation. Used as the base options for monotag invocations during bumping and tagging checks
        :param npm: Options for npm publishing.
        :param pypi: Options for pypi publishing.
        :param skip_bump: If true, won't bump the version field of package.json, pyproject.toml etc to the latest tag found before invoking the build task. Default: false
        :param skip_checks: Disable checks before publishing. By default the following checks are performed: - The git working directory is clean (no uncommited changes) - The current commit is tagged with the latest version calculated for the package - The latest version tagged in git is equal to the version in the package file name being published This is useful to avoid publishing packages whose contents are not actually commited/tagged in git. In order to perform some of the checks, monotag will be invoked with action "current". If not, "tag" will be used. Default: false
        '''
        if isinstance(monotag_options, dict):
            monotag_options = NextTagOptions(**monotag_options)
        if isinstance(npm, dict):
            npm = PublishNpmOptions(**npm)
        if isinstance(pypi, dict):
            pypi = PublishPypiOptions(**pypi)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7986fd7f1b9f7afb7cf5bb1b36ea56b403fa42d6083b6fa58fb2cf65e9d5329b)
            check_type(argname="argument build_task", value=build_task, expected_type=type_hints["build_task"])
            check_type(argname="argument group", value=group, expected_type=type_hints["group"])
            check_type(argname="argument monotag_options", value=monotag_options, expected_type=type_hints["monotag_options"])
            check_type(argname="argument npm", value=npm, expected_type=type_hints["npm"])
            check_type(argname="argument pypi", value=pypi, expected_type=type_hints["pypi"])
            check_type(argname="argument skip_bump", value=skip_bump, expected_type=type_hints["skip_bump"])
            check_type(argname="argument skip_checks", value=skip_checks, expected_type=type_hints["skip_checks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if build_task is not None:
            self._values["build_task"] = build_task
        if group is not None:
            self._values["group"] = group
        if monotag_options is not None:
            self._values["monotag_options"] = monotag_options
        if npm is not None:
            self._values["npm"] = npm
        if pypi is not None:
            self._values["pypi"] = pypi
        if skip_bump is not None:
            self._values["skip_bump"] = skip_bump
        if skip_checks is not None:
            self._values["skip_checks"] = skip_checks

    @builtins.property
    def build_task(self) -> typing.Optional[builtins.str]:
        '''The name of the task that will be invoked to generate package files to be published.

        :default: 'build', if exists in project. If not, no build task will be invoked.
        '''
        result = self._values.get("build_task")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def group(self) -> typing.Optional[builtins.str]:
        '''If defined, will suffix the task name by this name so that multiple publish tasks with different configurations can be defined in the same project.'''
        result = self._values.get("group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def monotag_options(self) -> typing.Optional[NextTagOptions]:
        '''Options for next tag calculation.

        Used as the base options for monotag invocations during bumping and tagging checks
        '''
        result = self._values.get("monotag_options")
        return typing.cast(typing.Optional[NextTagOptions], result)

    @builtins.property
    def npm(self) -> typing.Optional[PublishNpmOptions]:
        '''Options for npm publishing.'''
        result = self._values.get("npm")
        return typing.cast(typing.Optional[PublishNpmOptions], result)

    @builtins.property
    def pypi(self) -> typing.Optional["PublishPypiOptions"]:
        '''Options for pypi publishing.'''
        result = self._values.get("pypi")
        return typing.cast(typing.Optional["PublishPypiOptions"], result)

    @builtins.property
    def skip_bump(self) -> typing.Optional[builtins.bool]:
        '''If true, won't bump the version field of package.json, pyproject.toml etc to the latest tag found before invoking the build task.

        :default: false
        '''
        result = self._values.get("skip_bump")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def skip_checks(self) -> typing.Optional[builtins.bool]:
        '''Disable checks before publishing.

        By default the following checks are performed:

        - The git working directory is clean (no uncommited changes)
        - The current commit is tagged with the latest version calculated for the package
        - The latest version tagged in git is equal to the version in the package file name being published
          This is useful to avoid publishing packages whose contents are not actually commited/tagged in git.
          In order to perform some of the checks, monotag will be invoked with action "current". If not, "tag" will be used.

        :default: false
        '''
        result = self._values.get("skip_checks")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PublishOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen-practical-constructs.PublishPypiOptions",
    jsii_struct_bases=[BasePublishOptions],
    name_mapping={
        "group": "group",
        "registry_url": "registryUrl",
        "packages_dir": "packagesDir",
    },
)
class PublishPypiOptions(BasePublishOptions):
    def __init__(
        self,
        *,
        group: typing.Optional[builtins.str] = None,
        registry_url: typing.Optional[builtins.str] = None,
        packages_dir: builtins.str,
    ) -> None:
        '''
        :param group: If defined, will suffix the task name by this name so that multiple publish tasks with different configurations can be defined in the same project. If not defined, the task name will be "publish-python". Default: ''
        :param registry_url: Sets the registry url to publish to.
        :param packages_dir: All Python packages in this directory will be published (*.whl). Fails if no package is found. Default: "dist/python"
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69d253711342d80bd6b3c0cc9cee6ed6f79c7030a125bc91eeb63c25f0079b27)
            check_type(argname="argument group", value=group, expected_type=type_hints["group"])
            check_type(argname="argument registry_url", value=registry_url, expected_type=type_hints["registry_url"])
            check_type(argname="argument packages_dir", value=packages_dir, expected_type=type_hints["packages_dir"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "packages_dir": packages_dir,
        }
        if group is not None:
            self._values["group"] = group
        if registry_url is not None:
            self._values["registry_url"] = registry_url

    @builtins.property
    def group(self) -> typing.Optional[builtins.str]:
        '''If defined, will suffix the task name by this name so that multiple publish tasks with different configurations can be defined in the same project.

        If not defined, the task name will be "publish-python".

        :default: ''
        '''
        result = self._values.get("group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry_url(self) -> typing.Optional[builtins.str]:
        '''Sets the registry url to publish to.'''
        result = self._values.get("registry_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def packages_dir(self) -> builtins.str:
        '''All Python packages in this directory will be published (*.whl). Fails if no package is found.

        :default: "dist/python"
        '''
        result = self._values.get("packages_dir")
        assert result is not None, "Required property 'packages_dir' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PublishPypiOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PublishPypiTasks(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.PublishPypiTasks",
):
    '''Publish Python packages in a directoty to a Pypi registry.'''

    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        packages_dir: builtins.str,
        group: typing.Optional[builtins.str] = None,
        registry_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param packages_dir: All Python packages in this directory will be published (*.whl). Fails if no package is found. Default: "dist/python"
        :param group: If defined, will suffix the task name by this name so that multiple publish tasks with different configurations can be defined in the same project. If not defined, the task name will be "publish-python". Default: ''
        :param registry_url: Sets the registry url to publish to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f190275a1c7b1eb98e8bfa49265a15457fa34e711c1f20eff6c87bdddfa24179)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        opts = PublishPypiOptions(
            packages_dir=packages_dir, group=group, registry_url=registry_url
        )

        jsii.create(self.__class__, self, [project, opts])

    @builtins.property
    @jsii.member(jsii_name="taskName")
    def task_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskName"))

    @task_name.setter
    def task_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b35920cfba1211e462004105e1006ed5609b4742a73ff015ee2be147a1e56eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskName", value) # pyright: ignore[reportArgumentType]


class PublishTasks(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.PublishTasks",
):
    '''Defines a set of tasks to publish packages to npm and/or pypi registries.'''

    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        build_task: typing.Optional[builtins.str] = None,
        group: typing.Optional[builtins.str] = None,
        monotag_options: typing.Optional[typing.Union[NextTagOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        npm: typing.Optional[typing.Union[PublishNpmOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        pypi: typing.Optional[typing.Union[PublishPypiOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        skip_bump: typing.Optional[builtins.bool] = None,
        skip_checks: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param project: -
        :param build_task: The name of the task that will be invoked to generate package files to be published. Default: 'build', if exists in project. If not, no build task will be invoked.
        :param group: If defined, will suffix the task name by this name so that multiple publish tasks with different configurations can be defined in the same project.
        :param monotag_options: Options for next tag calculation. Used as the base options for monotag invocations during bumping and tagging checks
        :param npm: Options for npm publishing.
        :param pypi: Options for pypi publishing.
        :param skip_bump: If true, won't bump the version field of package.json, pyproject.toml etc to the latest tag found before invoking the build task. Default: false
        :param skip_checks: Disable checks before publishing. By default the following checks are performed: - The git working directory is clean (no uncommited changes) - The current commit is tagged with the latest version calculated for the package - The latest version tagged in git is equal to the version in the package file name being published This is useful to avoid publishing packages whose contents are not actually commited/tagged in git. In order to perform some of the checks, monotag will be invoked with action "current". If not, "tag" will be used. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa8818e759d2ecb9be66a3ca05c6baf1b05c4553950364535f80d5211cb75411)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        opts = PublishOptions(
            build_task=build_task,
            group=group,
            monotag_options=monotag_options,
            npm=npm,
            pypi=pypi,
            skip_bump=skip_bump,
            skip_checks=skip_checks,
        )

        jsii.create(self.__class__, self, [project, opts])


class PyProjectTomlFile(
    _projen_04054675.FileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.PyProjectTomlFile",
):
    '''pyproject.toml synthetisation.'''

    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license_file: typing.Optional[builtins.str] = None,
        package_name: typing.Optional[builtins.str] = None,
        readme: typing.Optional[builtins.str] = None,
        requires_python: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param author_email: Author's e-mail.
        :param author_name: Author's name.
        :param classifiers: A list of PyPI trove classifiers that describe the project.
        :param description: A short description of the package.
        :param homepage: A URL to the website of the project.
        :param keywords: Keywords to add to the package.
        :param license_file: License file.
        :param package_name: Name of the python package. E.g. "my_python_package". Must only consist of alphanumeric characters and underscores. Default: Name of the directory
        :param readme: README file.
        :param requires_python: Python version required to run this package.
        :param version: Version of the package.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6d7a3b8b4177596f54f16f91bd9df59e0a45d86f401871b1e9b3b29ce78328b)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        opts = PyProjectTomlOptions(
            author_email=author_email,
            author_name=author_name,
            classifiers=classifiers,
            description=description,
            homepage=homepage,
            keywords=keywords,
            license_file=license_file,
            package_name=package_name,
            readme=readme,
            requires_python=requires_python,
            version=version,
        )

        jsii.create(self.__class__, self, [project, opts])

    @jsii.member(jsii_name="synthesizeContent")
    def _synthesize_content(
        self,
        _resolver: _projen_04054675.IResolver,
    ) -> typing.Optional[builtins.str]:
        '''Implemented by derived classes and returns the contents of the file to emit.

        :param _resolver: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4507ce8637891a717163abf9982165de1dcb742ca0621e122de9e18450c7727b)
            check_type(argname="argument _resolver", value=_resolver, expected_type=type_hints["_resolver"])
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "synthesizeContent", [_resolver]))


@jsii.data_type(
    jsii_type="projen-practical-constructs.PyProjectTomlOptions",
    jsii_struct_bases=[],
    name_mapping={
        "author_email": "authorEmail",
        "author_name": "authorName",
        "classifiers": "classifiers",
        "description": "description",
        "homepage": "homepage",
        "keywords": "keywords",
        "license_file": "licenseFile",
        "package_name": "packageName",
        "readme": "readme",
        "requires_python": "requiresPython",
        "version": "version",
    },
)
class PyProjectTomlOptions:
    def __init__(
        self,
        *,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license_file: typing.Optional[builtins.str] = None,
        package_name: typing.Optional[builtins.str] = None,
        readme: typing.Optional[builtins.str] = None,
        requires_python: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param author_email: Author's e-mail.
        :param author_name: Author's name.
        :param classifiers: A list of PyPI trove classifiers that describe the project.
        :param description: A short description of the package.
        :param homepage: A URL to the website of the project.
        :param keywords: Keywords to add to the package.
        :param license_file: License file.
        :param package_name: Name of the python package. E.g. "my_python_package". Must only consist of alphanumeric characters and underscores. Default: Name of the directory
        :param readme: README file.
        :param requires_python: Python version required to run this package.
        :param version: Version of the package.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05a4f19c0ac4e3b053533fffc4e6b5d4ec292f9c4073fe33392b6cfca5185ea0)
            check_type(argname="argument author_email", value=author_email, expected_type=type_hints["author_email"])
            check_type(argname="argument author_name", value=author_name, expected_type=type_hints["author_name"])
            check_type(argname="argument classifiers", value=classifiers, expected_type=type_hints["classifiers"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument homepage", value=homepage, expected_type=type_hints["homepage"])
            check_type(argname="argument keywords", value=keywords, expected_type=type_hints["keywords"])
            check_type(argname="argument license_file", value=license_file, expected_type=type_hints["license_file"])
            check_type(argname="argument package_name", value=package_name, expected_type=type_hints["package_name"])
            check_type(argname="argument readme", value=readme, expected_type=type_hints["readme"])
            check_type(argname="argument requires_python", value=requires_python, expected_type=type_hints["requires_python"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if author_email is not None:
            self._values["author_email"] = author_email
        if author_name is not None:
            self._values["author_name"] = author_name
        if classifiers is not None:
            self._values["classifiers"] = classifiers
        if description is not None:
            self._values["description"] = description
        if homepage is not None:
            self._values["homepage"] = homepage
        if keywords is not None:
            self._values["keywords"] = keywords
        if license_file is not None:
            self._values["license_file"] = license_file
        if package_name is not None:
            self._values["package_name"] = package_name
        if readme is not None:
            self._values["readme"] = readme
        if requires_python is not None:
            self._values["requires_python"] = requires_python
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def author_email(self) -> typing.Optional[builtins.str]:
        '''Author's e-mail.'''
        result = self._values.get("author_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_name(self) -> typing.Optional[builtins.str]:
        '''Author's name.'''
        result = self._values.get("author_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def classifiers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of PyPI trove classifiers that describe the project.

        :see: https://pypi.org/classifiers/
        '''
        result = self._values.get("classifiers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A short description of the package.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''A URL to the website of the project.'''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keywords(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Keywords to add to the package.'''
        result = self._values.get("keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def license_file(self) -> typing.Optional[builtins.str]:
        '''License file.'''
        result = self._values.get("license_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def package_name(self) -> typing.Optional[builtins.str]:
        '''Name of the python package.

        E.g. "my_python_package".
        Must only consist of alphanumeric characters and underscores.

        :default: Name of the directory
        '''
        result = self._values.get("package_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def readme(self) -> typing.Optional[builtins.str]:
        '''README file.'''
        result = self._values.get("readme")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def requires_python(self) -> typing.Optional[builtins.str]:
        '''Python version required to run this package.'''
        result = self._values.get("requires_python")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Version of the package.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PyProjectTomlOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PyTest(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.PyTest",
):
    def __init__(
        self,
        project: _projen_04054675.Project,
        task_opts: typing.Union["TaskOptions", typing.Dict[builtins.str, typing.Any]],
        *,
        format: typing.Optional[builtins.str] = None,
        min_coverage: typing.Optional[jsii.Number] = None,
        omit_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        skip_covered: typing.Optional[builtins.bool] = None,
        skip_empty: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param project: -
        :param task_opts: -
        :param format: Coverage report format. Default: 'text'
        :param min_coverage: Minimum coverage required to pass the test. Default: 80
        :param omit_patterns: List of file patterns to omit from coverage. Default: []
        :param skip_covered: Skip reporting files that are covered. Default: false
        :param skip_empty: Skip reporting files that are empty. Default: true
        :param verbose: Run pytest with the ``--verbose`` flag. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42e05408896599bbf022ad6a7e60a821d61cad81416e62f8e87333465af34cc8)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument task_opts", value=task_opts, expected_type=type_hints["task_opts"])
        opts = PyTestOptions(
            format=format,
            min_coverage=min_coverage,
            omit_patterns=omit_patterns,
            skip_covered=skip_covered,
            skip_empty=skip_empty,
            verbose=verbose,
        )

        jsii.create(self.__class__, self, [project, task_opts, opts])


class PyTestIniFile(
    _projen_04054675.FileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.PyTestIniFile",
):
    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        verbose: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param project: -
        :param verbose: Run pytest with the ``--verbose`` flag. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44a3acc3982cbac42b7f244f2b7a0629ea77dbb3fbeb16b462809daed3316bc1)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        opts = PyTestIniOptions(verbose=verbose)

        jsii.create(self.__class__, self, [project, opts])

    @jsii.member(jsii_name="synthesizeContent")
    def _synthesize_content(
        self,
        _resolver: _projen_04054675.IResolver,
    ) -> typing.Optional[builtins.str]:
        '''Implemented by derived classes and returns the contents of the file to emit.

        :param _resolver: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__975893dbb0771af51870157408a643ffcf74cf8fc037cc71b062959406638251)
            check_type(argname="argument _resolver", value=_resolver, expected_type=type_hints["_resolver"])
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "synthesizeContent", [_resolver]))

    @builtins.property
    @jsii.member(jsii_name="opts")
    def opts(self) -> "PyTestIniOptions":
        return typing.cast("PyTestIniOptions", jsii.get(self, "opts"))

    @opts.setter
    def opts(self, value: "PyTestIniOptions") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ef765f0b3b01e999545322392822791093e2b72fca8c2d619f6f3c52c5dfcd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "opts", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="projen-practical-constructs.PyTestIniOptions",
    jsii_struct_bases=[],
    name_mapping={"verbose": "verbose"},
)
class PyTestIniOptions:
    def __init__(self, *, verbose: typing.Optional[builtins.bool] = None) -> None:
        '''
        :param verbose: Run pytest with the ``--verbose`` flag. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d4ca4cf98a7701cf69a33f919512afaccabd7bb8ee6ac702d86b6b686e85c40)
            check_type(argname="argument verbose", value=verbose, expected_type=type_hints["verbose"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if verbose is not None:
            self._values["verbose"] = verbose

    @builtins.property
    def verbose(self) -> typing.Optional[builtins.bool]:
        '''Run pytest with the ``--verbose`` flag.

        :default: true
        '''
        result = self._values.get("verbose")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PyTestIniOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen-practical-constructs.PyTestOptions",
    jsii_struct_bases=[CoveragercFileOptions, PyTestIniOptions],
    name_mapping={
        "format": "format",
        "min_coverage": "minCoverage",
        "omit_patterns": "omitPatterns",
        "skip_covered": "skipCovered",
        "skip_empty": "skipEmpty",
        "verbose": "verbose",
    },
)
class PyTestOptions(CoveragercFileOptions, PyTestIniOptions):
    def __init__(
        self,
        *,
        format: typing.Optional[builtins.str] = None,
        min_coverage: typing.Optional[jsii.Number] = None,
        omit_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        skip_covered: typing.Optional[builtins.bool] = None,
        skip_empty: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param format: Coverage report format. Default: 'text'
        :param min_coverage: Minimum coverage required to pass the test. Default: 80
        :param omit_patterns: List of file patterns to omit from coverage. Default: []
        :param skip_covered: Skip reporting files that are covered. Default: false
        :param skip_empty: Skip reporting files that are empty. Default: true
        :param verbose: Run pytest with the ``--verbose`` flag. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__384e63be7810bf945d6fb782fc3c891fca1787094bf35586a2dcbb2d81ce2867)
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
            check_type(argname="argument min_coverage", value=min_coverage, expected_type=type_hints["min_coverage"])
            check_type(argname="argument omit_patterns", value=omit_patterns, expected_type=type_hints["omit_patterns"])
            check_type(argname="argument skip_covered", value=skip_covered, expected_type=type_hints["skip_covered"])
            check_type(argname="argument skip_empty", value=skip_empty, expected_type=type_hints["skip_empty"])
            check_type(argname="argument verbose", value=verbose, expected_type=type_hints["verbose"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if format is not None:
            self._values["format"] = format
        if min_coverage is not None:
            self._values["min_coverage"] = min_coverage
        if omit_patterns is not None:
            self._values["omit_patterns"] = omit_patterns
        if skip_covered is not None:
            self._values["skip_covered"] = skip_covered
        if skip_empty is not None:
            self._values["skip_empty"] = skip_empty
        if verbose is not None:
            self._values["verbose"] = verbose

    @builtins.property
    def format(self) -> typing.Optional[builtins.str]:
        '''Coverage report format.

        :default: 'text'
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_coverage(self) -> typing.Optional[jsii.Number]:
        '''Minimum coverage required to pass the test.

        :default: 80
        '''
        result = self._values.get("min_coverage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def omit_patterns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of file patterns to omit from coverage.

        :default: []
        '''
        result = self._values.get("omit_patterns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def skip_covered(self) -> typing.Optional[builtins.bool]:
        '''Skip reporting files that are covered.

        :default: false
        '''
        result = self._values.get("skip_covered")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def skip_empty(self) -> typing.Optional[builtins.bool]:
        '''Skip reporting files that are empty.

        :default: true
        '''
        result = self._values.get("skip_empty")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def verbose(self) -> typing.Optional[builtins.bool]:
        '''Run pytest with the ``--verbose`` flag.

        :default: true
        '''
        result = self._values.get("verbose")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PyTestOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PythonBasicProject(
    _projen_04054675.Project,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.PythonBasicProject",
):
    '''Python project with basic configurations for linting, testing, building etc.

    :pjid: python_basic
    '''

    def __init__(
        self,
        *,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        lint: typing.Optional[typing.Union["LintOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        publish: typing.Optional[typing.Union[PublishOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        release: typing.Optional[typing.Union["ReleaseOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        sample: typing.Optional[builtins.bool] = None,
        test: typing.Optional[typing.Union["TestOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        name: builtins.str,
        commit_generated: typing.Optional[builtins.bool] = None,
        git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_projen_04054675.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        pip: typing.Optional[typing.Union[PipOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        pkg: typing.Optional[typing.Union["PackageOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        attach_tasks_to: typing.Optional[builtins.str] = None,
        venv_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param deps: Package dependencies in format ``['package==1.0.0', 'package2==2.0.0']``.
        :param dev_deps: Development dependencies in format ``['package==1.0.0', 'package2==2.0.0']``.
        :param lint: Linting configurations such as rules selected etc This prepares the project with lint configurations such as rules selected, rules ignored etc.
        :param publish: Publish options for the "publish" task This prepares the project to be published to a package registry such as pypi or npm.
        :param release: Release options for the "release" task. This prepares the project to execute pre-publish actions such as changelog generation, version tagging in git etc
        :param sample: Create sample code and test (if dir doesn't exist yet). Default: true
        :param test: Test configurations This prepares the project with test configurations such as coverage threshold etc.
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param commit_generated: (experimental) Whether to commit the managed files by default. Default: true
        :param git_ignore_options: (experimental) Configuration options for .gitignore file.
        :param git_options: (experimental) Configuration options for git.
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other subprojects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options
        :param pip: 
        :param pkg: 
        :param attach_tasks_to: Existing task to attach new tasks to. It will be included as "spawn" tasks in new steps
        :param venv_path: Path to the python virtual environment directory used in this project. Default: .venv
        '''
        options = PythonBasicOptions(
            deps=deps,
            dev_deps=dev_deps,
            lint=lint,
            publish=publish,
            release=release,
            sample=sample,
            test=test,
            name=name,
            commit_generated=commit_generated,
            git_ignore_options=git_ignore_options,
            git_options=git_options,
            logging=logging,
            outdir=outdir,
            parent=parent,
            projen_command=projen_command,
            projenrc_json=projenrc_json,
            projenrc_json_options=projenrc_json_options,
            renovatebot=renovatebot,
            renovatebot_options=renovatebot_options,
            pip=pip,
            pkg=pkg,
            attach_tasks_to=attach_tasks_to,
            venv_path=venv_path,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="addDep")
    def add_dep(self, package_name_version: builtins.str) -> None:
        '''Add a runtime dependency in format [package-name][==version] E.g: ``addDep('package==1.0.0')``.

        :param package_name_version: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c514a60a75f071c20ec30de634506e6c296b1d91b281bd1a0ff69ec8551d7bf7)
            check_type(argname="argument package_name_version", value=package_name_version, expected_type=type_hints["package_name_version"])
        return typing.cast(None, jsii.invoke(self, "addDep", [package_name_version]))

    @jsii.member(jsii_name="addDevDep")
    def add_dev_dep(self, package_name_version: builtins.str) -> None:
        '''Add a development dependency in format [package-name][==version].

        :param package_name_version: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6803cea798ee4a60e65efc9b0cc675daf469d702cfb43e7595aed132004e56e3)
            check_type(argname="argument package_name_version", value=package_name_version, expected_type=type_hints["package_name_version"])
        return typing.cast(None, jsii.invoke(self, "addDevDep", [package_name_version]))


class PythonBasicSample(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.PythonBasicSample",
):
    '''Python code sample.'''

    def __init__(self, project: _projen_04054675.Project) -> None:
        '''
        :param project: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f89bc9b2d760f7dbf6c765c850ee98f08ad2b9abd29b30723839469f113ac71)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        jsii.create(self.__class__, self, [project])


class PythonVersionFile(
    _projen_04054675.FileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.PythonVersionFile",
):
    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        python_version: builtins.str,
    ) -> None:
        '''
        :param project: -
        :param python_version: The version of Python to be added to the file.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b56632f9602060a9026f4ff094af75115f54480ed5cffe451781d662b51d31f1)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        opts = PythonVersionOptions(python_version=python_version)

        jsii.create(self.__class__, self, [project, opts])

    @jsii.member(jsii_name="synthesizeContent")
    def _synthesize_content(
        self,
        _resolver: _projen_04054675.IResolver,
    ) -> typing.Optional[builtins.str]:
        '''Implemented by derived classes and returns the contents of the file to emit.

        :param _resolver: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3eb4c7d952a99bdea958131725c8145a2e4d0ef325b48ac55d83275c5cdd0c0)
            check_type(argname="argument _resolver", value=_resolver, expected_type=type_hints["_resolver"])
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "synthesizeContent", [_resolver]))


@jsii.data_type(
    jsii_type="projen-practical-constructs.PythonVersionOptions",
    jsii_struct_bases=[],
    name_mapping={"python_version": "pythonVersion"},
)
class PythonVersionOptions:
    def __init__(self, *, python_version: builtins.str) -> None:
        '''
        :param python_version: The version of Python to be added to the file.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fb02140f15e42d4186643add56e5f0ffe0d004d6540a470bf2ae03d136a627b)
            check_type(argname="argument python_version", value=python_version, expected_type=type_hints["python_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "python_version": python_version,
        }

    @builtins.property
    def python_version(self) -> builtins.str:
        '''The version of Python to be added to the file.

        :required: true
        '''
        result = self._values.get("python_version")
        assert result is not None, "Required property 'python_version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PythonVersionOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ReadmeFile(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.ReadmeFile",
):
    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        project_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param project_name: 
        :param description: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e121cdedc0beed1c682d7a460ce0e7ed3201b3597d0675df06b9bc467a25a42)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        opts = ReadmeOptions(project_name=project_name, description=description)

        jsii.create(self.__class__, self, [project, opts])


@jsii.data_type(
    jsii_type="projen-practical-constructs.ReadmeOptions",
    jsii_struct_bases=[],
    name_mapping={"project_name": "projectName", "description": "description"},
)
class ReadmeOptions:
    def __init__(
        self,
        *,
        project_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project_name: 
        :param description: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f16ff3cf7a0826918909ecb12dfd4f0ec1385aa6bdc84176767f6109162ecdc)
            check_type(argname="argument project_name", value=project_name, expected_type=type_hints["project_name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "project_name": project_name,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def project_name(self) -> builtins.str:
        result = self._values.get("project_name")
        assert result is not None, "Required property 'project_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ReadmeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen-practical-constructs.ReleaseOptions",
    jsii_struct_bases=[NextTagOptions],
    name_mapping={
        "bump_action": "bumpAction",
        "bump_files": "bumpFiles",
        "changelog_file": "changelogFile",
        "from_ref": "fromRef",
        "git_email": "gitEmail",
        "git_username": "gitUsername",
        "max_version": "maxVersion",
        "min_version": "minVersion",
        "monotag_cmd": "monotagCmd",
        "monotag_extra_args": "monotagExtraArgs",
        "notes_file": "notesFile",
        "only_conv_commit": "onlyConvCommit",
        "path": "path",
        "pre_release": "preRelease",
        "pre_release_always_increment": "preReleaseAlwaysIncrement",
        "pre_release_identifier": "preReleaseIdentifier",
        "repo_dir": "repoDir",
        "semver_level": "semverLevel",
        "tag_file": "tagFile",
        "tag_prefix": "tagPrefix",
        "tag_suffix": "tagSuffix",
        "to_ref": "toRef",
        "verbose": "verbose",
        "version_file": "versionFile",
        "action": "action",
        "name": "name",
    },
)
class ReleaseOptions(NextTagOptions):
    def __init__(
        self,
        *,
        bump_action: typing.Optional[builtins.str] = None,
        bump_files: typing.Optional[typing.Sequence[builtins.str]] = None,
        changelog_file: typing.Optional[builtins.str] = None,
        from_ref: typing.Optional[builtins.str] = None,
        git_email: typing.Optional[builtins.str] = None,
        git_username: typing.Optional[builtins.str] = None,
        max_version: typing.Optional[builtins.str] = None,
        min_version: typing.Optional[builtins.str] = None,
        monotag_cmd: typing.Optional[builtins.str] = None,
        monotag_extra_args: typing.Optional[builtins.str] = None,
        notes_file: typing.Optional[builtins.str] = None,
        only_conv_commit: typing.Optional[builtins.bool] = None,
        path: typing.Optional[builtins.str] = None,
        pre_release: typing.Optional[builtins.bool] = None,
        pre_release_always_increment: typing.Optional[builtins.bool] = None,
        pre_release_identifier: typing.Optional[builtins.str] = None,
        repo_dir: typing.Optional[builtins.str] = None,
        semver_level: typing.Optional[builtins.str] = None,
        tag_file: typing.Optional[builtins.str] = None,
        tag_prefix: typing.Optional[builtins.str] = None,
        tag_suffix: typing.Optional[builtins.str] = None,
        to_ref: typing.Optional[builtins.str] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_file: typing.Optional[builtins.str] = None,
        action: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bump_action: Bump action to be performed after the tag is generated in regard to package files such as package.json, pyproject.yml etc Should be one of: - 'latest': bump the version field of the files to the calculated tag - 'zero': bump the version field of the files to 0.0.0 - 'none': won't change any files. Default: 'none'
        :param bump_files: Files to be bumped with the latest version It will search for a "version" attribute in the file, replace it with the new version and save If the field doesn't exist, it won't be changed. Default: ['package.json']
        :param changelog_file: File with the changelog that will be updated with the new version During update, this will check if the version is already present in the changelog and skip generation if it's already there. Normally this file is named CHANGELOG.md Default: undefined (won't be created)
        :param from_ref: Git ref range (starting point) for searching for changes in git log history. Default: latest tag
        :param git_email: Configure git cli with email Required if action is 'commit', 'tag' or 'push'.
        :param git_username: Configure git cli with username Required if action is 'commit', 'tag' or 'push'.
        :param max_version: Maximum version for the generated tag. If the generated version is higher than this, the operation will fail Default: no limit
        :param min_version: Minimum version for the generated tag. If the naturally incremented version is lower, this value will be used Default: no limit
        :param monotag_cmd: Command line used to invoke Monotag to perform tag calculations. Default: 'npx monotag@1.14.0'
        :param monotag_extra_args: Extra arguments to be added to every invocation of Monotag. Default: ''
        :param notes_file: File that will be written with the notes with the changes detected The content will be a markdown with a list of commits. Default: undefined (won't be created)
        :param only_conv_commit: Only take into consideration git commits that follows the conventional commits format while rendering release notes. Default: false
        :param path: Path inside repository for looking for changes Defaults to any path. Default: ''
        :param pre_release: If the generated version is a pre-release This will add a pre-release identifier to the version. E.g.: 1.0.0-beta This will automatically create a pre-release version depending on the semverLevel identified by commit message analysis based on conventional commits. For example, if the commits contain a breaking change, the version will be a major pre-release. So if it was 1.2.2, it will be 2.0.0-beta. If it was 3.2.1, it will be 4.0.0-beta. The same applies for minor and patch levels. Default: false
        :param pre_release_always_increment: If true, the pre-release version will always be incremented even if no changes are detected So subsequent calls to 'nextTag' will always increment the pre-release version. Default: false
        :param pre_release_identifier: Pre-release identifier. Default: 'beta'
        :param repo_dir: Directory where the git repository is located Defaults to local directory. Default: '.'
        :param semver_level: Which level to increment the version. If undefined, it will be automatic, based on commit messages Default: undefined
        :param tag_file: File that will be written with the tag name (e.g.: myservice/1.2.3-beta.0). Default: undefined (won't be created)
        :param tag_prefix: Tag prefix to look for latest tag and for generating the tag. Default: ''
        :param tag_suffix: Tag suffix to add to the generated tag When using pre-release capabilities, that will manage and increment prerelease versions, this will be added to the generated version. E.g.: 1.0.0-beta.1-MY_SUFFIX, if tagSuffix is '-MY_SUFFIX' Default: ''
        :param to_ref: Git ref range (ending point) for searching for changes in git log history Defaults to HEAD. Default: HEAD
        :param verbose: Output messages about what is being done Such as git commands being executed etc. Default: false
        :param version_file: File that will be written with the version (e.g.: 1.2.3-beta.0). Default: undefined (won't be created)
        :param action: Action to be taken after calculating the next tag Options: - console: Print calculated tag/notes to console - tag: Calculate tag/notes, commit and tag (git) resources - push: Calculate tag/notes, commit, tag (git) and push resources to remote git. Default: 'console'
        :param name: Name of this release group of tasks Useful if you have multiple release tasks in the same project with different configurations. The release tasks will be named as "release:[name]:[task]" Default: ''
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fc118b5a89a887bbc9715306583b5d0cbd1825074a2b5a6fe6f64b81e9a4d38)
            check_type(argname="argument bump_action", value=bump_action, expected_type=type_hints["bump_action"])
            check_type(argname="argument bump_files", value=bump_files, expected_type=type_hints["bump_files"])
            check_type(argname="argument changelog_file", value=changelog_file, expected_type=type_hints["changelog_file"])
            check_type(argname="argument from_ref", value=from_ref, expected_type=type_hints["from_ref"])
            check_type(argname="argument git_email", value=git_email, expected_type=type_hints["git_email"])
            check_type(argname="argument git_username", value=git_username, expected_type=type_hints["git_username"])
            check_type(argname="argument max_version", value=max_version, expected_type=type_hints["max_version"])
            check_type(argname="argument min_version", value=min_version, expected_type=type_hints["min_version"])
            check_type(argname="argument monotag_cmd", value=monotag_cmd, expected_type=type_hints["monotag_cmd"])
            check_type(argname="argument monotag_extra_args", value=monotag_extra_args, expected_type=type_hints["monotag_extra_args"])
            check_type(argname="argument notes_file", value=notes_file, expected_type=type_hints["notes_file"])
            check_type(argname="argument only_conv_commit", value=only_conv_commit, expected_type=type_hints["only_conv_commit"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument pre_release", value=pre_release, expected_type=type_hints["pre_release"])
            check_type(argname="argument pre_release_always_increment", value=pre_release_always_increment, expected_type=type_hints["pre_release_always_increment"])
            check_type(argname="argument pre_release_identifier", value=pre_release_identifier, expected_type=type_hints["pre_release_identifier"])
            check_type(argname="argument repo_dir", value=repo_dir, expected_type=type_hints["repo_dir"])
            check_type(argname="argument semver_level", value=semver_level, expected_type=type_hints["semver_level"])
            check_type(argname="argument tag_file", value=tag_file, expected_type=type_hints["tag_file"])
            check_type(argname="argument tag_prefix", value=tag_prefix, expected_type=type_hints["tag_prefix"])
            check_type(argname="argument tag_suffix", value=tag_suffix, expected_type=type_hints["tag_suffix"])
            check_type(argname="argument to_ref", value=to_ref, expected_type=type_hints["to_ref"])
            check_type(argname="argument verbose", value=verbose, expected_type=type_hints["verbose"])
            check_type(argname="argument version_file", value=version_file, expected_type=type_hints["version_file"])
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bump_action is not None:
            self._values["bump_action"] = bump_action
        if bump_files is not None:
            self._values["bump_files"] = bump_files
        if changelog_file is not None:
            self._values["changelog_file"] = changelog_file
        if from_ref is not None:
            self._values["from_ref"] = from_ref
        if git_email is not None:
            self._values["git_email"] = git_email
        if git_username is not None:
            self._values["git_username"] = git_username
        if max_version is not None:
            self._values["max_version"] = max_version
        if min_version is not None:
            self._values["min_version"] = min_version
        if monotag_cmd is not None:
            self._values["monotag_cmd"] = monotag_cmd
        if monotag_extra_args is not None:
            self._values["monotag_extra_args"] = monotag_extra_args
        if notes_file is not None:
            self._values["notes_file"] = notes_file
        if only_conv_commit is not None:
            self._values["only_conv_commit"] = only_conv_commit
        if path is not None:
            self._values["path"] = path
        if pre_release is not None:
            self._values["pre_release"] = pre_release
        if pre_release_always_increment is not None:
            self._values["pre_release_always_increment"] = pre_release_always_increment
        if pre_release_identifier is not None:
            self._values["pre_release_identifier"] = pre_release_identifier
        if repo_dir is not None:
            self._values["repo_dir"] = repo_dir
        if semver_level is not None:
            self._values["semver_level"] = semver_level
        if tag_file is not None:
            self._values["tag_file"] = tag_file
        if tag_prefix is not None:
            self._values["tag_prefix"] = tag_prefix
        if tag_suffix is not None:
            self._values["tag_suffix"] = tag_suffix
        if to_ref is not None:
            self._values["to_ref"] = to_ref
        if verbose is not None:
            self._values["verbose"] = verbose
        if version_file is not None:
            self._values["version_file"] = version_file
        if action is not None:
            self._values["action"] = action
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def bump_action(self) -> typing.Optional[builtins.str]:
        '''Bump action to be performed after the tag is generated in regard to package files such as package.json, pyproject.yml etc Should be one of:   - 'latest': bump the version field of the files to the calculated tag   - 'zero': bump the version field of the files to 0.0.0   - 'none': won't change any files.

        :default: 'none'
        '''
        result = self._values.get("bump_action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bump_files(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Files to be bumped with the latest version It will search for a "version" attribute in the file, replace it with the new version and save If the field doesn't exist, it won't be changed.

        :default: ['package.json']
        '''
        result = self._values.get("bump_files")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def changelog_file(self) -> typing.Optional[builtins.str]:
        '''File with the changelog that will be updated with the new version During update, this will check if the version is already present in the changelog and skip generation if it's already there.

        Normally this file is named CHANGELOG.md

        :default: undefined (won't be created)
        '''
        result = self._values.get("changelog_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def from_ref(self) -> typing.Optional[builtins.str]:
        '''Git ref range (starting point) for searching for changes in git log history.

        :default: latest tag
        '''
        result = self._values.get("from_ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def git_email(self) -> typing.Optional[builtins.str]:
        '''Configure git cli with email Required if action is 'commit', 'tag' or 'push'.'''
        result = self._values.get("git_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def git_username(self) -> typing.Optional[builtins.str]:
        '''Configure git cli with username Required if action is 'commit', 'tag' or 'push'.'''
        result = self._values.get("git_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_version(self) -> typing.Optional[builtins.str]:
        '''Maximum version for the generated tag.

        If the generated version is higher than this, the operation will fail

        :default: no limit
        '''
        result = self._values.get("max_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_version(self) -> typing.Optional[builtins.str]:
        '''Minimum version for the generated tag.

        If the naturally incremented version is lower, this value will be used

        :default: no limit
        '''
        result = self._values.get("min_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def monotag_cmd(self) -> typing.Optional[builtins.str]:
        '''Command line used to invoke Monotag to perform tag calculations.

        :default: 'npx monotag@1.14.0'
        '''
        result = self._values.get("monotag_cmd")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def monotag_extra_args(self) -> typing.Optional[builtins.str]:
        '''Extra arguments to be added to every invocation of Monotag.

        :default: ''
        '''
        result = self._values.get("monotag_extra_args")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notes_file(self) -> typing.Optional[builtins.str]:
        '''File that will be written with the notes with the changes detected The content will be a markdown with a list of commits.

        :default: undefined (won't be created)
        '''
        result = self._values.get("notes_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def only_conv_commit(self) -> typing.Optional[builtins.bool]:
        '''Only take into consideration git commits that follows the conventional commits format while rendering release notes.

        :default: false
        '''
        result = self._values.get("only_conv_commit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Path inside repository for looking for changes Defaults to any path.

        :default: ''
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_release(self) -> typing.Optional[builtins.bool]:
        '''If the generated version is a pre-release This will add a pre-release identifier to the version.

        E.g.: 1.0.0-beta
        This will automatically create a pre-release version depending on the semverLevel
        identified by commit message analysis based on conventional commits.
        For example, if the commits contain a breaking change, the version will be a major pre-release.
        So if it was 1.2.2, it will be 2.0.0-beta. If it was 3.2.1, it will be 4.0.0-beta.
        The same applies for minor and patch levels.

        :default: false
        '''
        result = self._values.get("pre_release")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pre_release_always_increment(self) -> typing.Optional[builtins.bool]:
        '''If true, the pre-release version will always be incremented even if no changes are detected So subsequent calls to 'nextTag' will always increment the pre-release version.

        :default: false
        '''
        result = self._values.get("pre_release_always_increment")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pre_release_identifier(self) -> typing.Optional[builtins.str]:
        '''Pre-release identifier.

        :default: 'beta'
        '''
        result = self._values.get("pre_release_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repo_dir(self) -> typing.Optional[builtins.str]:
        '''Directory where the git repository is located Defaults to local directory.

        :default: '.'
        '''
        result = self._values.get("repo_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def semver_level(self) -> typing.Optional[builtins.str]:
        '''Which level to increment the version.

        If undefined, it will be automatic, based on commit messages

        :default: undefined
        '''
        result = self._values.get("semver_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag_file(self) -> typing.Optional[builtins.str]:
        '''File that will be written with the tag name (e.g.: myservice/1.2.3-beta.0).

        :default: undefined (won't be created)
        '''
        result = self._values.get("tag_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag_prefix(self) -> typing.Optional[builtins.str]:
        '''Tag prefix to look for latest tag and for generating the tag.

        :default: ''
        '''
        result = self._values.get("tag_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag_suffix(self) -> typing.Optional[builtins.str]:
        '''Tag suffix to add to the generated tag When using pre-release capabilities, that will manage and increment prerelease versions, this will be added to the generated version.

        E.g.: 1.0.0-beta.1-MY_SUFFIX, if tagSuffix is '-MY_SUFFIX'

        :default: ''
        '''
        result = self._values.get("tag_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def to_ref(self) -> typing.Optional[builtins.str]:
        '''Git ref range (ending point) for searching for changes in git log history Defaults to HEAD.

        :default: HEAD
        '''
        result = self._values.get("to_ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def verbose(self) -> typing.Optional[builtins.bool]:
        '''Output messages about what is being done Such as git commands being executed etc.

        :default: false
        '''
        result = self._values.get("verbose")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def version_file(self) -> typing.Optional[builtins.str]:
        '''File that will be written with the version (e.g.: 1.2.3-beta.0).

        :default: undefined (won't be created)
        '''
        result = self._values.get("version_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def action(self) -> typing.Optional[builtins.str]:
        '''Action to be taken after calculating the next tag Options:  - console: Print calculated tag/notes to console  - tag: Calculate tag/notes, commit and tag (git) resources  - push: Calculate tag/notes, commit, tag (git) and push resources to remote git.

        :default: 'console'
        '''
        result = self._values.get("action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of this release group of tasks Useful if you have multiple release tasks in the same project with different configurations.

        The release tasks will be named as "release:[name]:[task]"

        :default: ''
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ReleaseOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ReleaseTasks(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.ReleaseTasks",
):
    '''Create tasks to support the basics of creating a software release based on git tags.

    Uses monotag to calculate the next tag and release notes.

    Tasks:

    - release[:name]:current: Verifies if the current commit is already tagged with the latest calculated tag. If so, bumps files, saves version/tag/notes in output files/changelogs.
    - release[:name]: Will execute before -> next-tag -> generate -> [tag|push] -> after for this release group
    - release[:name]:before: executed before any other tasks in release. Placeholder for any pre-release related tasks
    - release[:name]:next-tag: Calculate the next version of the software, output tag and notes to console, write output files, bump files and append changelog. Supports complex release tagging in monorepos by using "npx monotag"
    - release[:name]:generate: executed after tag calculation and before git operations. Placeholder for custom tasks, such as doc generation, package build etc
    - release[:name]:git-tag: Tag the current commit with the calculated release tag on git repo (if action is 'tag')
    - release[:name]:git-push: Push the tagged commit to remote git (if action is 'push')
    - release[:name]:after: executed after all other tasks in release. Placeholder for any post-release related tasks
    '''

    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        action: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        bump_action: typing.Optional[builtins.str] = None,
        bump_files: typing.Optional[typing.Sequence[builtins.str]] = None,
        changelog_file: typing.Optional[builtins.str] = None,
        from_ref: typing.Optional[builtins.str] = None,
        git_email: typing.Optional[builtins.str] = None,
        git_username: typing.Optional[builtins.str] = None,
        max_version: typing.Optional[builtins.str] = None,
        min_version: typing.Optional[builtins.str] = None,
        monotag_cmd: typing.Optional[builtins.str] = None,
        monotag_extra_args: typing.Optional[builtins.str] = None,
        notes_file: typing.Optional[builtins.str] = None,
        only_conv_commit: typing.Optional[builtins.bool] = None,
        path: typing.Optional[builtins.str] = None,
        pre_release: typing.Optional[builtins.bool] = None,
        pre_release_always_increment: typing.Optional[builtins.bool] = None,
        pre_release_identifier: typing.Optional[builtins.str] = None,
        repo_dir: typing.Optional[builtins.str] = None,
        semver_level: typing.Optional[builtins.str] = None,
        tag_file: typing.Optional[builtins.str] = None,
        tag_prefix: typing.Optional[builtins.str] = None,
        tag_suffix: typing.Optional[builtins.str] = None,
        to_ref: typing.Optional[builtins.str] = None,
        verbose: typing.Optional[builtins.bool] = None,
        version_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param action: Action to be taken after calculating the next tag Options: - console: Print calculated tag/notes to console - tag: Calculate tag/notes, commit and tag (git) resources - push: Calculate tag/notes, commit, tag (git) and push resources to remote git. Default: 'console'
        :param name: Name of this release group of tasks Useful if you have multiple release tasks in the same project with different configurations. The release tasks will be named as "release:[name]:[task]" Default: ''
        :param bump_action: Bump action to be performed after the tag is generated in regard to package files such as package.json, pyproject.yml etc Should be one of: - 'latest': bump the version field of the files to the calculated tag - 'zero': bump the version field of the files to 0.0.0 - 'none': won't change any files. Default: 'none'
        :param bump_files: Files to be bumped with the latest version It will search for a "version" attribute in the file, replace it with the new version and save If the field doesn't exist, it won't be changed. Default: ['package.json']
        :param changelog_file: File with the changelog that will be updated with the new version During update, this will check if the version is already present in the changelog and skip generation if it's already there. Normally this file is named CHANGELOG.md Default: undefined (won't be created)
        :param from_ref: Git ref range (starting point) for searching for changes in git log history. Default: latest tag
        :param git_email: Configure git cli with email Required if action is 'commit', 'tag' or 'push'.
        :param git_username: Configure git cli with username Required if action is 'commit', 'tag' or 'push'.
        :param max_version: Maximum version for the generated tag. If the generated version is higher than this, the operation will fail Default: no limit
        :param min_version: Minimum version for the generated tag. If the naturally incremented version is lower, this value will be used Default: no limit
        :param monotag_cmd: Command line used to invoke Monotag to perform tag calculations. Default: 'npx monotag@1.14.0'
        :param monotag_extra_args: Extra arguments to be added to every invocation of Monotag. Default: ''
        :param notes_file: File that will be written with the notes with the changes detected The content will be a markdown with a list of commits. Default: undefined (won't be created)
        :param only_conv_commit: Only take into consideration git commits that follows the conventional commits format while rendering release notes. Default: false
        :param path: Path inside repository for looking for changes Defaults to any path. Default: ''
        :param pre_release: If the generated version is a pre-release This will add a pre-release identifier to the version. E.g.: 1.0.0-beta This will automatically create a pre-release version depending on the semverLevel identified by commit message analysis based on conventional commits. For example, if the commits contain a breaking change, the version will be a major pre-release. So if it was 1.2.2, it will be 2.0.0-beta. If it was 3.2.1, it will be 4.0.0-beta. The same applies for minor and patch levels. Default: false
        :param pre_release_always_increment: If true, the pre-release version will always be incremented even if no changes are detected So subsequent calls to 'nextTag' will always increment the pre-release version. Default: false
        :param pre_release_identifier: Pre-release identifier. Default: 'beta'
        :param repo_dir: Directory where the git repository is located Defaults to local directory. Default: '.'
        :param semver_level: Which level to increment the version. If undefined, it will be automatic, based on commit messages Default: undefined
        :param tag_file: File that will be written with the tag name (e.g.: myservice/1.2.3-beta.0). Default: undefined (won't be created)
        :param tag_prefix: Tag prefix to look for latest tag and for generating the tag. Default: ''
        :param tag_suffix: Tag suffix to add to the generated tag When using pre-release capabilities, that will manage and increment prerelease versions, this will be added to the generated version. E.g.: 1.0.0-beta.1-MY_SUFFIX, if tagSuffix is '-MY_SUFFIX' Default: ''
        :param to_ref: Git ref range (ending point) for searching for changes in git log history Defaults to HEAD. Default: HEAD
        :param verbose: Output messages about what is being done Such as git commands being executed etc. Default: false
        :param version_file: File that will be written with the version (e.g.: 1.2.3-beta.0). Default: undefined (won't be created)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba446ae8ee81ba2bd8583a5cf9965d6c1aa385438f34c06c5252b45b480469f1)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        opts = ReleaseOptions(
            action=action,
            name=name,
            bump_action=bump_action,
            bump_files=bump_files,
            changelog_file=changelog_file,
            from_ref=from_ref,
            git_email=git_email,
            git_username=git_username,
            max_version=max_version,
            min_version=min_version,
            monotag_cmd=monotag_cmd,
            monotag_extra_args=monotag_extra_args,
            notes_file=notes_file,
            only_conv_commit=only_conv_commit,
            path=path,
            pre_release=pre_release,
            pre_release_always_increment=pre_release_always_increment,
            pre_release_identifier=pre_release_identifier,
            repo_dir=repo_dir,
            semver_level=semver_level,
            tag_file=tag_file,
            tag_prefix=tag_prefix,
            tag_suffix=tag_suffix,
            to_ref=to_ref,
            verbose=verbose,
            version_file=version_file,
        )

        jsii.create(self.__class__, self, [project, opts])


class Ruff(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.Ruff",
):
    def __init__(
        self,
        project: _projen_04054675.Project,
        task_opts: typing.Union["TaskOptions", typing.Dict[builtins.str, typing.Any]],
        *,
        attach_fix_task_to: typing.Optional[builtins.str] = None,
        add_to_existing_rules: typing.Optional[builtins.bool] = None,
        ignore_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
        mccabe_max_complexity: typing.Optional[jsii.Number] = None,
        per_file_ignores: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
        select_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_python_version: typing.Optional[builtins.str] = None,
        unsafe_fixes: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param project: -
        :param task_opts: -
        :param attach_fix_task_to: Attach lint fix tasks to parent.
        :param add_to_existing_rules: Add rules defined here to the ignoreRules and selectRules (on top of the default rules) or replace them by this contents? Default: true
        :param ignore_rules: Default: pre-selected set of rules
        :param mccabe_max_complexity: Default: 14
        :param per_file_ignores: Default: ignore doc-string code format for test files
        :param select_rules: Default: pre-selected set of rules
        :param target_python_version: Default: py313
        :param unsafe_fixes: Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92e6719177912c0eae0ee85cfc203cb22854f3f273cc256898396282ba7d42fe)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument task_opts", value=task_opts, expected_type=type_hints["task_opts"])
        opts = RuffOptions(
            attach_fix_task_to=attach_fix_task_to,
            add_to_existing_rules=add_to_existing_rules,
            ignore_rules=ignore_rules,
            mccabe_max_complexity=mccabe_max_complexity,
            per_file_ignores=per_file_ignores,
            select_rules=select_rules,
            target_python_version=target_python_version,
            unsafe_fixes=unsafe_fixes,
        )

        jsii.create(self.__class__, self, [project, task_opts, opts])


class RuffTomlFile(
    _projen_04054675.TomlFile,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.RuffTomlFile",
):
    '''ruff.toml synthetisation.'''

    def __init__(
        self,
        project: _projen_04054675.Project,
        *,
        add_to_existing_rules: typing.Optional[builtins.bool] = None,
        ignore_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
        mccabe_max_complexity: typing.Optional[jsii.Number] = None,
        per_file_ignores: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
        select_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_python_version: typing.Optional[builtins.str] = None,
        unsafe_fixes: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param project: -
        :param add_to_existing_rules: Add rules defined here to the ignoreRules and selectRules (on top of the default rules) or replace them by this contents? Default: true
        :param ignore_rules: Default: pre-selected set of rules
        :param mccabe_max_complexity: Default: 14
        :param per_file_ignores: Default: ignore doc-string code format for test files
        :param select_rules: Default: pre-selected set of rules
        :param target_python_version: Default: py313
        :param unsafe_fixes: Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__515cf86a84df0b6b18941ab4c2a73e7eef40e0260fab3c698c6cabcef8227d71)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        opts = RuffTomlFileOptions(
            add_to_existing_rules=add_to_existing_rules,
            ignore_rules=ignore_rules,
            mccabe_max_complexity=mccabe_max_complexity,
            per_file_ignores=per_file_ignores,
            select_rules=select_rules,
            target_python_version=target_python_version,
            unsafe_fixes=unsafe_fixes,
        )

        jsii.create(self.__class__, self, [project, opts])


@jsii.data_type(
    jsii_type="projen-practical-constructs.RuffTomlFileOptions",
    jsii_struct_bases=[],
    name_mapping={
        "add_to_existing_rules": "addToExistingRules",
        "ignore_rules": "ignoreRules",
        "mccabe_max_complexity": "mccabeMaxComplexity",
        "per_file_ignores": "perFileIgnores",
        "select_rules": "selectRules",
        "target_python_version": "targetPythonVersion",
        "unsafe_fixes": "unsafeFixes",
    },
)
class RuffTomlFileOptions:
    def __init__(
        self,
        *,
        add_to_existing_rules: typing.Optional[builtins.bool] = None,
        ignore_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
        mccabe_max_complexity: typing.Optional[jsii.Number] = None,
        per_file_ignores: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
        select_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_python_version: typing.Optional[builtins.str] = None,
        unsafe_fixes: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param add_to_existing_rules: Add rules defined here to the ignoreRules and selectRules (on top of the default rules) or replace them by this contents? Default: true
        :param ignore_rules: Default: pre-selected set of rules
        :param mccabe_max_complexity: Default: 14
        :param per_file_ignores: Default: ignore doc-string code format for test files
        :param select_rules: Default: pre-selected set of rules
        :param target_python_version: Default: py313
        :param unsafe_fixes: Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce7087163e4218666b985f90db1006536d982decdeb6854261778dfc1f07f506)
            check_type(argname="argument add_to_existing_rules", value=add_to_existing_rules, expected_type=type_hints["add_to_existing_rules"])
            check_type(argname="argument ignore_rules", value=ignore_rules, expected_type=type_hints["ignore_rules"])
            check_type(argname="argument mccabe_max_complexity", value=mccabe_max_complexity, expected_type=type_hints["mccabe_max_complexity"])
            check_type(argname="argument per_file_ignores", value=per_file_ignores, expected_type=type_hints["per_file_ignores"])
            check_type(argname="argument select_rules", value=select_rules, expected_type=type_hints["select_rules"])
            check_type(argname="argument target_python_version", value=target_python_version, expected_type=type_hints["target_python_version"])
            check_type(argname="argument unsafe_fixes", value=unsafe_fixes, expected_type=type_hints["unsafe_fixes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if add_to_existing_rules is not None:
            self._values["add_to_existing_rules"] = add_to_existing_rules
        if ignore_rules is not None:
            self._values["ignore_rules"] = ignore_rules
        if mccabe_max_complexity is not None:
            self._values["mccabe_max_complexity"] = mccabe_max_complexity
        if per_file_ignores is not None:
            self._values["per_file_ignores"] = per_file_ignores
        if select_rules is not None:
            self._values["select_rules"] = select_rules
        if target_python_version is not None:
            self._values["target_python_version"] = target_python_version
        if unsafe_fixes is not None:
            self._values["unsafe_fixes"] = unsafe_fixes

    @builtins.property
    def add_to_existing_rules(self) -> typing.Optional[builtins.bool]:
        '''Add rules defined here to the ignoreRules and selectRules (on top of the default rules) or replace them by this contents?

        :default: true
        '''
        result = self._values.get("add_to_existing_rules")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ignore_rules(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :default: pre-selected set of rules
        '''
        result = self._values.get("ignore_rules")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def mccabe_max_complexity(self) -> typing.Optional[jsii.Number]:
        '''
        :default: 14
        '''
        result = self._values.get("mccabe_max_complexity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def per_file_ignores(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        '''
        :default: ignore doc-string code format for test files
        '''
        result = self._values.get("per_file_ignores")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.List[builtins.str]]], result)

    @builtins.property
    def select_rules(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :default: pre-selected set of rules
        '''
        result = self._values.get("select_rules")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_python_version(self) -> typing.Optional[builtins.str]:
        '''
        :default: py313
        '''
        result = self._values.get("target_python_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unsafe_fixes(self) -> typing.Optional[builtins.bool]:
        '''
        :default: false
        '''
        result = self._values.get("unsafe_fixes")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RuffTomlFileOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen-practical-constructs.TaskOptions",
    jsii_struct_bases=[],
    name_mapping={"venv_path": "venvPath"},
)
class TaskOptions:
    def __init__(self, *, venv_path: builtins.str) -> None:
        '''
        :param venv_path: Path to the python virtual environment directory used in this project.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60bbd600395432f8000b4758eea0d98c9c8e225b40399a70f2bd14d84ef3bb0f)
            check_type(argname="argument venv_path", value=venv_path, expected_type=type_hints["venv_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "venv_path": venv_path,
        }

    @builtins.property
    def venv_path(self) -> builtins.str:
        '''Path to the python virtual environment directory used in this project.'''
        result = self._values.get("venv_path")
        assert result is not None, "Required property 'venv_path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TaskOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen-practical-constructs.TaskOptionsTarget",
    jsii_struct_bases=[],
    name_mapping={"attach_tasks_to": "attachTasksTo", "venv_path": "venvPath"},
)
class TaskOptionsTarget:
    def __init__(
        self,
        *,
        attach_tasks_to: typing.Optional[builtins.str] = None,
        venv_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param attach_tasks_to: Existing task to attach new tasks to. It will be included as "spawn" tasks in new steps
        :param venv_path: Path to the python virtual environment directory used in this project. Default: .venv
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ebef6526107b290f8f3024aa58a74f546f6c2dcee9f6faa53295f3c7402ac4a)
            check_type(argname="argument attach_tasks_to", value=attach_tasks_to, expected_type=type_hints["attach_tasks_to"])
            check_type(argname="argument venv_path", value=venv_path, expected_type=type_hints["venv_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if attach_tasks_to is not None:
            self._values["attach_tasks_to"] = attach_tasks_to
        if venv_path is not None:
            self._values["venv_path"] = venv_path

    @builtins.property
    def attach_tasks_to(self) -> typing.Optional[builtins.str]:
        '''Existing task to attach new tasks to.

        It will be included as "spawn" tasks in new steps
        '''
        result = self._values.get("attach_tasks_to")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def venv_path(self) -> typing.Optional[builtins.str]:
        '''Path to the python virtual environment directory used in this project.

        :default: .venv
        '''
        result = self._values.get("venv_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TaskOptionsTarget(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen-practical-constructs.TestOptions",
    jsii_struct_bases=[PyTestOptions],
    name_mapping={
        "format": "format",
        "min_coverage": "minCoverage",
        "omit_patterns": "omitPatterns",
        "skip_covered": "skipCovered",
        "skip_empty": "skipEmpty",
        "verbose": "verbose",
    },
)
class TestOptions(PyTestOptions):
    def __init__(
        self,
        *,
        format: typing.Optional[builtins.str] = None,
        min_coverage: typing.Optional[jsii.Number] = None,
        omit_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        skip_covered: typing.Optional[builtins.bool] = None,
        skip_empty: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param format: Coverage report format. Default: 'text'
        :param min_coverage: Minimum coverage required to pass the test. Default: 80
        :param omit_patterns: List of file patterns to omit from coverage. Default: []
        :param skip_covered: Skip reporting files that are covered. Default: false
        :param skip_empty: Skip reporting files that are empty. Default: true
        :param verbose: Run pytest with the ``--verbose`` flag. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6ce63ffedc17816d4e10d303db52b112c4a018db5d7b81c720790d591a43e4e)
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
            check_type(argname="argument min_coverage", value=min_coverage, expected_type=type_hints["min_coverage"])
            check_type(argname="argument omit_patterns", value=omit_patterns, expected_type=type_hints["omit_patterns"])
            check_type(argname="argument skip_covered", value=skip_covered, expected_type=type_hints["skip_covered"])
            check_type(argname="argument skip_empty", value=skip_empty, expected_type=type_hints["skip_empty"])
            check_type(argname="argument verbose", value=verbose, expected_type=type_hints["verbose"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if format is not None:
            self._values["format"] = format
        if min_coverage is not None:
            self._values["min_coverage"] = min_coverage
        if omit_patterns is not None:
            self._values["omit_patterns"] = omit_patterns
        if skip_covered is not None:
            self._values["skip_covered"] = skip_covered
        if skip_empty is not None:
            self._values["skip_empty"] = skip_empty
        if verbose is not None:
            self._values["verbose"] = verbose

    @builtins.property
    def format(self) -> typing.Optional[builtins.str]:
        '''Coverage report format.

        :default: 'text'
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_coverage(self) -> typing.Optional[jsii.Number]:
        '''Minimum coverage required to pass the test.

        :default: 80
        '''
        result = self._values.get("min_coverage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def omit_patterns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of file patterns to omit from coverage.

        :default: []
        '''
        result = self._values.get("omit_patterns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def skip_covered(self) -> typing.Optional[builtins.bool]:
        '''Skip reporting files that are covered.

        :default: false
        '''
        result = self._values.get("skip_covered")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def skip_empty(self) -> typing.Optional[builtins.bool]:
        '''Skip reporting files that are empty.

        :default: true
        '''
        result = self._values.get("skip_empty")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def verbose(self) -> typing.Optional[builtins.bool]:
        '''Run pytest with the ``--verbose`` flag.

        :default: true
        '''
        result = self._values.get("verbose")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TestOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TestTarget(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen-practical-constructs.TestTarget",
):
    '''Python project lint configurations.'''

    def __init__(
        self,
        project: _projen_04054675.Project,
        task_opts: typing.Union[TaskOptions, typing.Dict[builtins.str, typing.Any]],
        *,
        format: typing.Optional[builtins.str] = None,
        min_coverage: typing.Optional[jsii.Number] = None,
        omit_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        skip_covered: typing.Optional[builtins.bool] = None,
        skip_empty: typing.Optional[builtins.bool] = None,
        verbose: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param project: -
        :param task_opts: -
        :param format: Coverage report format. Default: 'text'
        :param min_coverage: Minimum coverage required to pass the test. Default: 80
        :param omit_patterns: List of file patterns to omit from coverage. Default: []
        :param skip_covered: Skip reporting files that are covered. Default: false
        :param skip_empty: Skip reporting files that are empty. Default: true
        :param verbose: Run pytest with the ``--verbose`` flag. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0658c3d7fe54aaec02fcef6987c7705125d952a65e7b4f1cde8ad8b0b36e7aa8)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument task_opts", value=task_opts, expected_type=type_hints["task_opts"])
        opts = TestOptions(
            format=format,
            min_coverage=min_coverage,
            omit_patterns=omit_patterns,
            skip_covered=skip_covered,
            skip_empty=skip_empty,
            verbose=verbose,
        )

        jsii.create(self.__class__, self, [project, task_opts, opts])


@jsii.data_type(
    jsii_type="projen-practical-constructs.BaseToolingOptions",
    jsii_struct_bases=[MakefileProjenOptions],
    name_mapping={
        "additional_makefile_contents_projen": "additionalMakefileContentsProjen",
        "additional_makefile_contents_targets": "additionalMakefileContentsTargets",
        "node_version": "nodeVersion",
        "projen_lib_version": "projenLibVersion",
        "ts_node_lib_version": "tsNodeLibVersion",
        "additional_makefile_contents_user": "additionalMakefileContentsUser",
    },
)
class BaseToolingOptions(MakefileProjenOptions):
    def __init__(
        self,
        *,
        additional_makefile_contents_projen: typing.Optional[builtins.str] = None,
        additional_makefile_contents_targets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        node_version: typing.Optional[builtins.str] = None,
        projen_lib_version: typing.Optional[builtins.str] = None,
        ts_node_lib_version: typing.Optional[builtins.str] = None,
        additional_makefile_contents_user: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param additional_makefile_contents_projen: Additional contents to be added to the Makefile on top of the default projen related targets. Default: - no additional rules
        :param additional_makefile_contents_targets: Additional contents to be added to each target of the Makefile.
        :param node_version: Node version to be added to the .nvmrc file. Default: '20.16.0'
        :param projen_lib_version: The version of projen lib to be used in "prepare" target of the Makefile to install tooling for Projen to work. Default: '0.91.13'
        :param ts_node_lib_version: The version of ts-node lib to be used in "prepare" target of the Makefile to install tooling for Projen to work. Default: '10.9.2'
        :param additional_makefile_contents_user: Additional contents to be added to Makefile, which is a sample and can be edited by devs after the initial generation.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b76c94e731f66a8083161e79ab92ddf0b90fbe84267279e946aafacb6a0211a8)
            check_type(argname="argument additional_makefile_contents_projen", value=additional_makefile_contents_projen, expected_type=type_hints["additional_makefile_contents_projen"])
            check_type(argname="argument additional_makefile_contents_targets", value=additional_makefile_contents_targets, expected_type=type_hints["additional_makefile_contents_targets"])
            check_type(argname="argument node_version", value=node_version, expected_type=type_hints["node_version"])
            check_type(argname="argument projen_lib_version", value=projen_lib_version, expected_type=type_hints["projen_lib_version"])
            check_type(argname="argument ts_node_lib_version", value=ts_node_lib_version, expected_type=type_hints["ts_node_lib_version"])
            check_type(argname="argument additional_makefile_contents_user", value=additional_makefile_contents_user, expected_type=type_hints["additional_makefile_contents_user"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if additional_makefile_contents_projen is not None:
            self._values["additional_makefile_contents_projen"] = additional_makefile_contents_projen
        if additional_makefile_contents_targets is not None:
            self._values["additional_makefile_contents_targets"] = additional_makefile_contents_targets
        if node_version is not None:
            self._values["node_version"] = node_version
        if projen_lib_version is not None:
            self._values["projen_lib_version"] = projen_lib_version
        if ts_node_lib_version is not None:
            self._values["ts_node_lib_version"] = ts_node_lib_version
        if additional_makefile_contents_user is not None:
            self._values["additional_makefile_contents_user"] = additional_makefile_contents_user

    @builtins.property
    def additional_makefile_contents_projen(self) -> typing.Optional[builtins.str]:
        '''Additional contents to be added to the Makefile on top of the default projen related targets.

        :default: - no additional rules
        '''
        result = self._values.get("additional_makefile_contents_projen")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def additional_makefile_contents_targets(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Additional contents to be added to each target of the Makefile.'''
        result = self._values.get("additional_makefile_contents_targets")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def node_version(self) -> typing.Optional[builtins.str]:
        '''Node version to be added to the .nvmrc file.

        :default: '20.16.0'
        '''
        result = self._values.get("node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projen_lib_version(self) -> typing.Optional[builtins.str]:
        '''The version of projen lib to be used in "prepare" target of the Makefile to install tooling for Projen to work.

        :default: '0.91.13'
        '''
        result = self._values.get("projen_lib_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ts_node_lib_version(self) -> typing.Optional[builtins.str]:
        '''The version of ts-node lib to be used in "prepare" target of the Makefile to install tooling for Projen to work.

        :default: '10.9.2'
        '''
        result = self._values.get("ts_node_lib_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def additional_makefile_contents_user(self) -> typing.Optional[builtins.str]:
        '''Additional contents to be added to Makefile, which is a sample and can be edited by devs after the initial generation.'''
        result = self._values.get("additional_makefile_contents_user")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseToolingOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen-practical-constructs.PackageOptions",
    jsii_struct_bases=[PyProjectTomlOptions],
    name_mapping={
        "author_email": "authorEmail",
        "author_name": "authorName",
        "classifiers": "classifiers",
        "description": "description",
        "homepage": "homepage",
        "keywords": "keywords",
        "license_file": "licenseFile",
        "package_name": "packageName",
        "readme": "readme",
        "requires_python": "requiresPython",
        "version": "version",
        "license": "license",
    },
)
class PackageOptions(PyProjectTomlOptions):
    def __init__(
        self,
        *,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license_file: typing.Optional[builtins.str] = None,
        package_name: typing.Optional[builtins.str] = None,
        readme: typing.Optional[builtins.str] = None,
        requires_python: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param author_email: Author's e-mail.
        :param author_name: Author's name.
        :param classifiers: A list of PyPI trove classifiers that describe the project.
        :param description: A short description of the package.
        :param homepage: A URL to the website of the project.
        :param keywords: Keywords to add to the package.
        :param license_file: License file.
        :param package_name: Name of the python package. E.g. "my_python_package". Must only consist of alphanumeric characters and underscores. Default: Name of the directory
        :param readme: README file.
        :param requires_python: Python version required to run this package.
        :param version: Version of the package.
        :param license: License name in spdx format. e.g: ``MIT``, ``Apache-2.0``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__769a6aad7aea164b73af332f179b064a5d119bdb8838de929422452d3b88c50c)
            check_type(argname="argument author_email", value=author_email, expected_type=type_hints["author_email"])
            check_type(argname="argument author_name", value=author_name, expected_type=type_hints["author_name"])
            check_type(argname="argument classifiers", value=classifiers, expected_type=type_hints["classifiers"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument homepage", value=homepage, expected_type=type_hints["homepage"])
            check_type(argname="argument keywords", value=keywords, expected_type=type_hints["keywords"])
            check_type(argname="argument license_file", value=license_file, expected_type=type_hints["license_file"])
            check_type(argname="argument package_name", value=package_name, expected_type=type_hints["package_name"])
            check_type(argname="argument readme", value=readme, expected_type=type_hints["readme"])
            check_type(argname="argument requires_python", value=requires_python, expected_type=type_hints["requires_python"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument license", value=license, expected_type=type_hints["license"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if author_email is not None:
            self._values["author_email"] = author_email
        if author_name is not None:
            self._values["author_name"] = author_name
        if classifiers is not None:
            self._values["classifiers"] = classifiers
        if description is not None:
            self._values["description"] = description
        if homepage is not None:
            self._values["homepage"] = homepage
        if keywords is not None:
            self._values["keywords"] = keywords
        if license_file is not None:
            self._values["license_file"] = license_file
        if package_name is not None:
            self._values["package_name"] = package_name
        if readme is not None:
            self._values["readme"] = readme
        if requires_python is not None:
            self._values["requires_python"] = requires_python
        if version is not None:
            self._values["version"] = version
        if license is not None:
            self._values["license"] = license

    @builtins.property
    def author_email(self) -> typing.Optional[builtins.str]:
        '''Author's e-mail.'''
        result = self._values.get("author_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_name(self) -> typing.Optional[builtins.str]:
        '''Author's name.'''
        result = self._values.get("author_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def classifiers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of PyPI trove classifiers that describe the project.

        :see: https://pypi.org/classifiers/
        '''
        result = self._values.get("classifiers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A short description of the package.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''A URL to the website of the project.'''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keywords(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Keywords to add to the package.'''
        result = self._values.get("keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def license_file(self) -> typing.Optional[builtins.str]:
        '''License file.'''
        result = self._values.get("license_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def package_name(self) -> typing.Optional[builtins.str]:
        '''Name of the python package.

        E.g. "my_python_package".
        Must only consist of alphanumeric characters and underscores.

        :default: Name of the directory
        '''
        result = self._values.get("package_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def readme(self) -> typing.Optional[builtins.str]:
        '''README file.'''
        result = self._values.get("readme")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def requires_python(self) -> typing.Optional[builtins.str]:
        '''Python version required to run this package.'''
        result = self._values.get("requires_python")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Version of the package.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''License name in spdx format.

        e.g: ``MIT``, ``Apache-2.0``
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PackageOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen-practical-constructs.PythonBasicOptions",
    jsii_struct_bases=[
        _projen_04054675.ProjectOptions, Build0Options, TaskOptionsTarget
    ],
    name_mapping={
        "name": "name",
        "commit_generated": "commitGenerated",
        "git_ignore_options": "gitIgnoreOptions",
        "git_options": "gitOptions",
        "logging": "logging",
        "outdir": "outdir",
        "parent": "parent",
        "projen_command": "projenCommand",
        "projenrc_json": "projenrcJson",
        "projenrc_json_options": "projenrcJsonOptions",
        "renovatebot": "renovatebot",
        "renovatebot_options": "renovatebotOptions",
        "pip": "pip",
        "pkg": "pkg",
        "attach_tasks_to": "attachTasksTo",
        "venv_path": "venvPath",
        "deps": "deps",
        "dev_deps": "devDeps",
        "lint": "lint",
        "publish": "publish",
        "release": "release",
        "sample": "sample",
        "test": "test",
    },
)
class PythonBasicOptions(
    _projen_04054675.ProjectOptions,
    Build0Options,
    TaskOptionsTarget,
):
    def __init__(
        self,
        *,
        name: builtins.str,
        commit_generated: typing.Optional[builtins.bool] = None,
        git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_projen_04054675.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        pip: typing.Optional[typing.Union[PipOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        pkg: typing.Optional[typing.Union[PackageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        attach_tasks_to: typing.Optional[builtins.str] = None,
        venv_path: typing.Optional[builtins.str] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        lint: typing.Optional[typing.Union["LintOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        publish: typing.Optional[typing.Union[PublishOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        release: typing.Optional[typing.Union[ReleaseOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        sample: typing.Optional[builtins.bool] = None,
        test: typing.Optional[typing.Union[TestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param commit_generated: (experimental) Whether to commit the managed files by default. Default: true
        :param git_ignore_options: (experimental) Configuration options for .gitignore file.
        :param git_options: (experimental) Configuration options for git.
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other subprojects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options
        :param pip: 
        :param pkg: 
        :param attach_tasks_to: Existing task to attach new tasks to. It will be included as "spawn" tasks in new steps
        :param venv_path: Path to the python virtual environment directory used in this project. Default: .venv
        :param deps: Package dependencies in format ``['package==1.0.0', 'package2==2.0.0']``.
        :param dev_deps: Development dependencies in format ``['package==1.0.0', 'package2==2.0.0']``.
        :param lint: Linting configurations such as rules selected etc This prepares the project with lint configurations such as rules selected, rules ignored etc.
        :param publish: Publish options for the "publish" task This prepares the project to be published to a package registry such as pypi or npm.
        :param release: Release options for the "release" task. This prepares the project to execute pre-publish actions such as changelog generation, version tagging in git etc
        :param sample: Create sample code and test (if dir doesn't exist yet). Default: true
        :param test: Test configurations This prepares the project with test configurations such as coverage threshold etc.
        '''
        if isinstance(git_ignore_options, dict):
            git_ignore_options = _projen_04054675.IgnoreFileOptions(**git_ignore_options)
        if isinstance(git_options, dict):
            git_options = _projen_04054675.GitOptions(**git_options)
        if isinstance(logging, dict):
            logging = _projen_04054675.LoggerOptions(**logging)
        if isinstance(projenrc_json_options, dict):
            projenrc_json_options = _projen_04054675.ProjenrcJsonOptions(**projenrc_json_options)
        if isinstance(renovatebot_options, dict):
            renovatebot_options = _projen_04054675.RenovatebotOptions(**renovatebot_options)
        if isinstance(pip, dict):
            pip = PipOptions(**pip)
        if isinstance(pkg, dict):
            pkg = PackageOptions(**pkg)
        if isinstance(lint, dict):
            lint = LintOptions(**lint)
        if isinstance(publish, dict):
            publish = PublishOptions(**publish)
        if isinstance(release, dict):
            release = ReleaseOptions(**release)
        if isinstance(test, dict):
            test = TestOptions(**test)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c54d357164afec478ab317ef798bb3d8a0ac8c35182918abf6dfd0025c70bc86)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument commit_generated", value=commit_generated, expected_type=type_hints["commit_generated"])
            check_type(argname="argument git_ignore_options", value=git_ignore_options, expected_type=type_hints["git_ignore_options"])
            check_type(argname="argument git_options", value=git_options, expected_type=type_hints["git_options"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument outdir", value=outdir, expected_type=type_hints["outdir"])
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument projen_command", value=projen_command, expected_type=type_hints["projen_command"])
            check_type(argname="argument projenrc_json", value=projenrc_json, expected_type=type_hints["projenrc_json"])
            check_type(argname="argument projenrc_json_options", value=projenrc_json_options, expected_type=type_hints["projenrc_json_options"])
            check_type(argname="argument renovatebot", value=renovatebot, expected_type=type_hints["renovatebot"])
            check_type(argname="argument renovatebot_options", value=renovatebot_options, expected_type=type_hints["renovatebot_options"])
            check_type(argname="argument pip", value=pip, expected_type=type_hints["pip"])
            check_type(argname="argument pkg", value=pkg, expected_type=type_hints["pkg"])
            check_type(argname="argument attach_tasks_to", value=attach_tasks_to, expected_type=type_hints["attach_tasks_to"])
            check_type(argname="argument venv_path", value=venv_path, expected_type=type_hints["venv_path"])
            check_type(argname="argument deps", value=deps, expected_type=type_hints["deps"])
            check_type(argname="argument dev_deps", value=dev_deps, expected_type=type_hints["dev_deps"])
            check_type(argname="argument lint", value=lint, expected_type=type_hints["lint"])
            check_type(argname="argument publish", value=publish, expected_type=type_hints["publish"])
            check_type(argname="argument release", value=release, expected_type=type_hints["release"])
            check_type(argname="argument sample", value=sample, expected_type=type_hints["sample"])
            check_type(argname="argument test", value=test, expected_type=type_hints["test"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if commit_generated is not None:
            self._values["commit_generated"] = commit_generated
        if git_ignore_options is not None:
            self._values["git_ignore_options"] = git_ignore_options
        if git_options is not None:
            self._values["git_options"] = git_options
        if logging is not None:
            self._values["logging"] = logging
        if outdir is not None:
            self._values["outdir"] = outdir
        if parent is not None:
            self._values["parent"] = parent
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if projenrc_json is not None:
            self._values["projenrc_json"] = projenrc_json
        if projenrc_json_options is not None:
            self._values["projenrc_json_options"] = projenrc_json_options
        if renovatebot is not None:
            self._values["renovatebot"] = renovatebot
        if renovatebot_options is not None:
            self._values["renovatebot_options"] = renovatebot_options
        if pip is not None:
            self._values["pip"] = pip
        if pkg is not None:
            self._values["pkg"] = pkg
        if attach_tasks_to is not None:
            self._values["attach_tasks_to"] = attach_tasks_to
        if venv_path is not None:
            self._values["venv_path"] = venv_path
        if deps is not None:
            self._values["deps"] = deps
        if dev_deps is not None:
            self._values["dev_deps"] = dev_deps
        if lint is not None:
            self._values["lint"] = lint
        if publish is not None:
            self._values["publish"] = publish
        if release is not None:
            self._values["release"] = release
        if sample is not None:
            self._values["sample"] = sample
        if test is not None:
            self._values["test"] = test

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def commit_generated(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to commit the managed files by default.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("commit_generated")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def git_ignore_options(self) -> typing.Optional[_projen_04054675.IgnoreFileOptions]:
        '''(experimental) Configuration options for .gitignore file.

        :stability: experimental
        '''
        result = self._values.get("git_ignore_options")
        return typing.cast(typing.Optional[_projen_04054675.IgnoreFileOptions], result)

    @builtins.property
    def git_options(self) -> typing.Optional[_projen_04054675.GitOptions]:
        '''(experimental) Configuration options for git.

        :stability: experimental
        '''
        result = self._values.get("git_options")
        return typing.cast(typing.Optional[_projen_04054675.GitOptions], result)

    @builtins.property
    def logging(self) -> typing.Optional[_projen_04054675.LoggerOptions]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[_projen_04054675.LoggerOptions], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project.

        Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        subprojects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[_projen_04054675.Project]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[_projen_04054675.Project], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projenrc_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json_options(
        self,
    ) -> typing.Optional[_projen_04054675.ProjenrcJsonOptions]:
        '''(experimental) Options for .projenrc.json.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_json_options")
        return typing.cast(typing.Optional[_projen_04054675.ProjenrcJsonOptions], result)

    @builtins.property
    def renovatebot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use renovatebot to handle dependency upgrades.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("renovatebot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def renovatebot_options(
        self,
    ) -> typing.Optional[_projen_04054675.RenovatebotOptions]:
        '''(experimental) Options for renovatebot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("renovatebot_options")
        return typing.cast(typing.Optional[_projen_04054675.RenovatebotOptions], result)

    @builtins.property
    def pip(self) -> typing.Optional[PipOptions]:
        result = self._values.get("pip")
        return typing.cast(typing.Optional[PipOptions], result)

    @builtins.property
    def pkg(self) -> typing.Optional[PackageOptions]:
        result = self._values.get("pkg")
        return typing.cast(typing.Optional[PackageOptions], result)

    @builtins.property
    def attach_tasks_to(self) -> typing.Optional[builtins.str]:
        '''Existing task to attach new tasks to.

        It will be included as "spawn" tasks in new steps
        '''
        result = self._values.get("attach_tasks_to")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def venv_path(self) -> typing.Optional[builtins.str]:
        '''Path to the python virtual environment directory used in this project.

        :default: .venv
        '''
        result = self._values.get("venv_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Package dependencies in format ``['package==1.0.0', 'package2==2.0.0']``.'''
        result = self._values.get("deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dev_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Development dependencies in format ``['package==1.0.0', 'package2==2.0.0']``.'''
        result = self._values.get("dev_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def lint(self) -> typing.Optional["LintOptions"]:
        '''Linting configurations such as rules selected etc This prepares the project with lint configurations such as rules selected, rules ignored etc.'''
        result = self._values.get("lint")
        return typing.cast(typing.Optional["LintOptions"], result)

    @builtins.property
    def publish(self) -> typing.Optional[PublishOptions]:
        '''Publish options for the "publish" task This prepares the project to be published to a package registry such as pypi or npm.'''
        result = self._values.get("publish")
        return typing.cast(typing.Optional[PublishOptions], result)

    @builtins.property
    def release(self) -> typing.Optional[ReleaseOptions]:
        '''Release options for the "release" task.

        This prepares the project to execute pre-publish actions such as changelog generation, version tagging in git etc
        '''
        result = self._values.get("release")
        return typing.cast(typing.Optional[ReleaseOptions], result)

    @builtins.property
    def sample(self) -> typing.Optional[builtins.bool]:
        '''Create sample code and test (if dir doesn't exist yet).

        :default: true
        '''
        result = self._values.get("sample")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def test(self) -> typing.Optional[TestOptions]:
        '''Test configurations This prepares the project with test configurations such as coverage threshold etc.'''
        result = self._values.get("test")
        return typing.cast(typing.Optional[TestOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PythonBasicOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen-practical-constructs.RuffOptions",
    jsii_struct_bases=[RuffTomlFileOptions],
    name_mapping={
        "add_to_existing_rules": "addToExistingRules",
        "ignore_rules": "ignoreRules",
        "mccabe_max_complexity": "mccabeMaxComplexity",
        "per_file_ignores": "perFileIgnores",
        "select_rules": "selectRules",
        "target_python_version": "targetPythonVersion",
        "unsafe_fixes": "unsafeFixes",
        "attach_fix_task_to": "attachFixTaskTo",
    },
)
class RuffOptions(RuffTomlFileOptions):
    def __init__(
        self,
        *,
        add_to_existing_rules: typing.Optional[builtins.bool] = None,
        ignore_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
        mccabe_max_complexity: typing.Optional[jsii.Number] = None,
        per_file_ignores: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
        select_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_python_version: typing.Optional[builtins.str] = None,
        unsafe_fixes: typing.Optional[builtins.bool] = None,
        attach_fix_task_to: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param add_to_existing_rules: Add rules defined here to the ignoreRules and selectRules (on top of the default rules) or replace them by this contents? Default: true
        :param ignore_rules: Default: pre-selected set of rules
        :param mccabe_max_complexity: Default: 14
        :param per_file_ignores: Default: ignore doc-string code format for test files
        :param select_rules: Default: pre-selected set of rules
        :param target_python_version: Default: py313
        :param unsafe_fixes: Default: false
        :param attach_fix_task_to: Attach lint fix tasks to parent.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d207008bfccd269e92e2aa9ed31161d7e45bab33efb79344ae36a97c2eddcff)
            check_type(argname="argument add_to_existing_rules", value=add_to_existing_rules, expected_type=type_hints["add_to_existing_rules"])
            check_type(argname="argument ignore_rules", value=ignore_rules, expected_type=type_hints["ignore_rules"])
            check_type(argname="argument mccabe_max_complexity", value=mccabe_max_complexity, expected_type=type_hints["mccabe_max_complexity"])
            check_type(argname="argument per_file_ignores", value=per_file_ignores, expected_type=type_hints["per_file_ignores"])
            check_type(argname="argument select_rules", value=select_rules, expected_type=type_hints["select_rules"])
            check_type(argname="argument target_python_version", value=target_python_version, expected_type=type_hints["target_python_version"])
            check_type(argname="argument unsafe_fixes", value=unsafe_fixes, expected_type=type_hints["unsafe_fixes"])
            check_type(argname="argument attach_fix_task_to", value=attach_fix_task_to, expected_type=type_hints["attach_fix_task_to"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if add_to_existing_rules is not None:
            self._values["add_to_existing_rules"] = add_to_existing_rules
        if ignore_rules is not None:
            self._values["ignore_rules"] = ignore_rules
        if mccabe_max_complexity is not None:
            self._values["mccabe_max_complexity"] = mccabe_max_complexity
        if per_file_ignores is not None:
            self._values["per_file_ignores"] = per_file_ignores
        if select_rules is not None:
            self._values["select_rules"] = select_rules
        if target_python_version is not None:
            self._values["target_python_version"] = target_python_version
        if unsafe_fixes is not None:
            self._values["unsafe_fixes"] = unsafe_fixes
        if attach_fix_task_to is not None:
            self._values["attach_fix_task_to"] = attach_fix_task_to

    @builtins.property
    def add_to_existing_rules(self) -> typing.Optional[builtins.bool]:
        '''Add rules defined here to the ignoreRules and selectRules (on top of the default rules) or replace them by this contents?

        :default: true
        '''
        result = self._values.get("add_to_existing_rules")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ignore_rules(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :default: pre-selected set of rules
        '''
        result = self._values.get("ignore_rules")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def mccabe_max_complexity(self) -> typing.Optional[jsii.Number]:
        '''
        :default: 14
        '''
        result = self._values.get("mccabe_max_complexity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def per_file_ignores(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        '''
        :default: ignore doc-string code format for test files
        '''
        result = self._values.get("per_file_ignores")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.List[builtins.str]]], result)

    @builtins.property
    def select_rules(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :default: pre-selected set of rules
        '''
        result = self._values.get("select_rules")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_python_version(self) -> typing.Optional[builtins.str]:
        '''
        :default: py313
        '''
        result = self._values.get("target_python_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unsafe_fixes(self) -> typing.Optional[builtins.bool]:
        '''
        :default: false
        '''
        result = self._values.get("unsafe_fixes")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def attach_fix_task_to(self) -> typing.Optional[builtins.str]:
        '''Attach lint fix tasks to parent.'''
        result = self._values.get("attach_fix_task_to")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RuffOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen-practical-constructs.LintOptions",
    jsii_struct_bases=[RuffOptions],
    name_mapping={
        "add_to_existing_rules": "addToExistingRules",
        "ignore_rules": "ignoreRules",
        "mccabe_max_complexity": "mccabeMaxComplexity",
        "per_file_ignores": "perFileIgnores",
        "select_rules": "selectRules",
        "target_python_version": "targetPythonVersion",
        "unsafe_fixes": "unsafeFixes",
        "attach_fix_task_to": "attachFixTaskTo",
    },
)
class LintOptions(RuffOptions):
    def __init__(
        self,
        *,
        add_to_existing_rules: typing.Optional[builtins.bool] = None,
        ignore_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
        mccabe_max_complexity: typing.Optional[jsii.Number] = None,
        per_file_ignores: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
        select_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_python_version: typing.Optional[builtins.str] = None,
        unsafe_fixes: typing.Optional[builtins.bool] = None,
        attach_fix_task_to: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param add_to_existing_rules: Add rules defined here to the ignoreRules and selectRules (on top of the default rules) or replace them by this contents? Default: true
        :param ignore_rules: Default: pre-selected set of rules
        :param mccabe_max_complexity: Default: 14
        :param per_file_ignores: Default: ignore doc-string code format for test files
        :param select_rules: Default: pre-selected set of rules
        :param target_python_version: Default: py313
        :param unsafe_fixes: Default: false
        :param attach_fix_task_to: Attach lint fix tasks to parent.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3438e7eef6485f46108347648af5008e12c90c19bfd98c01816e34421622428c)
            check_type(argname="argument add_to_existing_rules", value=add_to_existing_rules, expected_type=type_hints["add_to_existing_rules"])
            check_type(argname="argument ignore_rules", value=ignore_rules, expected_type=type_hints["ignore_rules"])
            check_type(argname="argument mccabe_max_complexity", value=mccabe_max_complexity, expected_type=type_hints["mccabe_max_complexity"])
            check_type(argname="argument per_file_ignores", value=per_file_ignores, expected_type=type_hints["per_file_ignores"])
            check_type(argname="argument select_rules", value=select_rules, expected_type=type_hints["select_rules"])
            check_type(argname="argument target_python_version", value=target_python_version, expected_type=type_hints["target_python_version"])
            check_type(argname="argument unsafe_fixes", value=unsafe_fixes, expected_type=type_hints["unsafe_fixes"])
            check_type(argname="argument attach_fix_task_to", value=attach_fix_task_to, expected_type=type_hints["attach_fix_task_to"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if add_to_existing_rules is not None:
            self._values["add_to_existing_rules"] = add_to_existing_rules
        if ignore_rules is not None:
            self._values["ignore_rules"] = ignore_rules
        if mccabe_max_complexity is not None:
            self._values["mccabe_max_complexity"] = mccabe_max_complexity
        if per_file_ignores is not None:
            self._values["per_file_ignores"] = per_file_ignores
        if select_rules is not None:
            self._values["select_rules"] = select_rules
        if target_python_version is not None:
            self._values["target_python_version"] = target_python_version
        if unsafe_fixes is not None:
            self._values["unsafe_fixes"] = unsafe_fixes
        if attach_fix_task_to is not None:
            self._values["attach_fix_task_to"] = attach_fix_task_to

    @builtins.property
    def add_to_existing_rules(self) -> typing.Optional[builtins.bool]:
        '''Add rules defined here to the ignoreRules and selectRules (on top of the default rules) or replace them by this contents?

        :default: true
        '''
        result = self._values.get("add_to_existing_rules")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ignore_rules(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :default: pre-selected set of rules
        '''
        result = self._values.get("ignore_rules")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def mccabe_max_complexity(self) -> typing.Optional[jsii.Number]:
        '''
        :default: 14
        '''
        result = self._values.get("mccabe_max_complexity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def per_file_ignores(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        '''
        :default: ignore doc-string code format for test files
        '''
        result = self._values.get("per_file_ignores")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.List[builtins.str]]], result)

    @builtins.property
    def select_rules(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :default: pre-selected set of rules
        '''
        result = self._values.get("select_rules")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_python_version(self) -> typing.Optional[builtins.str]:
        '''
        :default: py313
        '''
        result = self._values.get("target_python_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unsafe_fixes(self) -> typing.Optional[builtins.bool]:
        '''
        :default: false
        '''
        result = self._values.get("unsafe_fixes")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def attach_fix_task_to(self) -> typing.Optional[builtins.str]:
        '''Attach lint fix tasks to parent.'''
        result = self._values.get("attach_fix_task_to")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LintOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BasePublishOptions",
    "BaseTasksOptions",
    "BaseTooling",
    "BaseToolingOptions",
    "Build0Options",
    "BuildTarget",
    "CommonTargets",
    "CommonTargetsTasks",
    "CoveragercFile",
    "CoveragercFileOptions",
    "LintOptions",
    "LintTarget",
    "MakefileProjenFile",
    "MakefileProjenOptions",
    "MyPy",
    "MyPyIniFile",
    "NextTagOptions",
    "NvmRcFile",
    "NvmRcOptions",
    "Package",
    "PackageOptions",
    "Pip",
    "PipAudit",
    "PipOptions",
    "PublishNpmOptions",
    "PublishNpmTasks",
    "PublishOptions",
    "PublishPypiOptions",
    "PublishPypiTasks",
    "PublishTasks",
    "PyProjectTomlFile",
    "PyProjectTomlOptions",
    "PyTest",
    "PyTestIniFile",
    "PyTestIniOptions",
    "PyTestOptions",
    "PythonBasicOptions",
    "PythonBasicProject",
    "PythonBasicSample",
    "PythonVersionFile",
    "PythonVersionOptions",
    "ReadmeFile",
    "ReadmeOptions",
    "ReleaseOptions",
    "ReleaseTasks",
    "Ruff",
    "RuffOptions",
    "RuffTomlFile",
    "RuffTomlFileOptions",
    "TaskOptions",
    "TaskOptionsTarget",
    "TestOptions",
    "TestTarget",
]

publication.publish()

def _typecheckingstub__739100f3446c486a63d16f0ecb589004c014d9dea8e406024a252595e4bc646c(
    *,
    group: typing.Optional[builtins.str] = None,
    registry_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fbe00fbf2112c6148f8298ce3d28f4cf74b9b66df64977e945cc317c1ab07f8(
    *,
    build_enable: typing.Optional[builtins.bool] = None,
    cleanup_default_tasks: typing.Optional[builtins.bool] = None,
    deploy_enable: typing.Optional[builtins.bool] = None,
    lint_enable: typing.Optional[builtins.bool] = None,
    publish_enable: typing.Optional[builtins.bool] = None,
    release_enable: typing.Optional[builtins.bool] = None,
    release_opts: typing.Optional[typing.Union[ReleaseOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    test_enable: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__436b158be7f28d681734521217f52de403cd8b97b08ab3c35b8eb11658f9bbce(
    project: _projen_04054675.Project,
    *,
    additional_makefile_contents_user: typing.Optional[builtins.str] = None,
    additional_makefile_contents_projen: typing.Optional[builtins.str] = None,
    additional_makefile_contents_targets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    node_version: typing.Optional[builtins.str] = None,
    projen_lib_version: typing.Optional[builtins.str] = None,
    ts_node_lib_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e20a491b2a5a4f8ee18f05888a4892e7e41c691d596b28ee23e4eec41be056ba(
    *,
    pip: typing.Optional[typing.Union[PipOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    pkg: typing.Optional[typing.Union[PackageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7baf093ce1415d71f61d9818afeb26e3072bbd9a78db8ca4ffdf96dcf200c73(
    project: _projen_04054675.Project,
    task_opts: typing.Union[TaskOptions, typing.Dict[builtins.str, typing.Any]],
    *,
    pip: typing.Optional[typing.Union[PipOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    pkg: typing.Optional[typing.Union[PackageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1518020ed9b2c4f61d13717bb8484f0d701535897dcf01674908de9a9faa98bd(
    project: _projen_04054675.Project,
    *,
    build_enable: typing.Optional[builtins.bool] = None,
    cleanup_default_tasks: typing.Optional[builtins.bool] = None,
    deploy_enable: typing.Optional[builtins.bool] = None,
    lint_enable: typing.Optional[builtins.bool] = None,
    publish_enable: typing.Optional[builtins.bool] = None,
    release_enable: typing.Optional[builtins.bool] = None,
    release_opts: typing.Optional[typing.Union[ReleaseOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    test_enable: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__159e518f7881abcb6abee9cf04ea6e882729784c5e0b7a737f6522baa1f5a152(
    project: _projen_04054675.Project,
    *,
    format: typing.Optional[builtins.str] = None,
    min_coverage: typing.Optional[jsii.Number] = None,
    omit_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
    skip_covered: typing.Optional[builtins.bool] = None,
    skip_empty: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83d971dfa627ffd4740ef400fe2c07260cfc8a850bb5f15117be52c28cf8aacb(
    _resolver: _projen_04054675.IResolver,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf0f342ecc7c849d461adb9b6dac4d82650ef73565eff25d53bbcfb2b3c5479d(
    *,
    format: typing.Optional[builtins.str] = None,
    min_coverage: typing.Optional[jsii.Number] = None,
    omit_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
    skip_covered: typing.Optional[builtins.bool] = None,
    skip_empty: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a024fae964b162f23bca5eaaea17d6482838424ff147cbcf777078f73bfeb68(
    project: _projen_04054675.Project,
    task_options: typing.Union[TaskOptions, typing.Dict[builtins.str, typing.Any]],
    *,
    attach_fix_task_to: typing.Optional[builtins.str] = None,
    add_to_existing_rules: typing.Optional[builtins.bool] = None,
    ignore_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
    mccabe_max_complexity: typing.Optional[jsii.Number] = None,
    per_file_ignores: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
    select_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_python_version: typing.Optional[builtins.str] = None,
    unsafe_fixes: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__194924c3827e470ba642d1c88bb4907a87215e4b16aadd60a0d921ea7d4b1773(
    project: _projen_04054675.Project,
    *,
    additional_makefile_contents_projen: typing.Optional[builtins.str] = None,
    additional_makefile_contents_targets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    node_version: typing.Optional[builtins.str] = None,
    projen_lib_version: typing.Optional[builtins.str] = None,
    ts_node_lib_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dae95ffeccf6c3d4b413b4c0dce096bdaa222a21b141caf613a05718e6a8e70c(
    _resolver: _projen_04054675.IResolver,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2645adc140a8ad315ff517954172686050477a4694117129efad8ba0a97669e9(
    *,
    additional_makefile_contents_projen: typing.Optional[builtins.str] = None,
    additional_makefile_contents_targets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    node_version: typing.Optional[builtins.str] = None,
    projen_lib_version: typing.Optional[builtins.str] = None,
    ts_node_lib_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0a177ef285e9d814c79f51d94f6a5469ba5493c4e5b3b7f83c91a7cb2308c59(
    project: _projen_04054675.Project,
    *,
    venv_path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4de587b589ba9e007f9440a8c64dc04332c03c6a61c1fbeab978cb77f04fc58(
    project: _projen_04054675.Project,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05af635c22d0af271080341bf52a1ec29b58a9cb63c5ea1521a193ee6570270e(
    _resolver: _projen_04054675.IResolver,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecd81b6dce26aa3ffbefaefa78378441a430787e56901243ad411e0e128c0f90(
    *,
    bump_action: typing.Optional[builtins.str] = None,
    bump_files: typing.Optional[typing.Sequence[builtins.str]] = None,
    changelog_file: typing.Optional[builtins.str] = None,
    from_ref: typing.Optional[builtins.str] = None,
    git_email: typing.Optional[builtins.str] = None,
    git_username: typing.Optional[builtins.str] = None,
    max_version: typing.Optional[builtins.str] = None,
    min_version: typing.Optional[builtins.str] = None,
    monotag_cmd: typing.Optional[builtins.str] = None,
    monotag_extra_args: typing.Optional[builtins.str] = None,
    notes_file: typing.Optional[builtins.str] = None,
    only_conv_commit: typing.Optional[builtins.bool] = None,
    path: typing.Optional[builtins.str] = None,
    pre_release: typing.Optional[builtins.bool] = None,
    pre_release_always_increment: typing.Optional[builtins.bool] = None,
    pre_release_identifier: typing.Optional[builtins.str] = None,
    repo_dir: typing.Optional[builtins.str] = None,
    semver_level: typing.Optional[builtins.str] = None,
    tag_file: typing.Optional[builtins.str] = None,
    tag_prefix: typing.Optional[builtins.str] = None,
    tag_suffix: typing.Optional[builtins.str] = None,
    to_ref: typing.Optional[builtins.str] = None,
    verbose: typing.Optional[builtins.bool] = None,
    version_file: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d9124a878d068673b1222734c071726026044ca4bce4ce1337a5245bfb74f48(
    project: _projen_04054675.Project,
    *,
    node_version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__036c6a629a999381eb4d9cdab4d09599981a6c980fb93168dd8d8c725d0d2d7e(
    _resolver: _projen_04054675.IResolver,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b123193e84e1be30d14b96bef4c234361f129b3e7fea6b31925ac7e6d2500d6(
    *,
    node_version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62f3584f77ee44c76622dd4d1bcb61319421c6ff75dc347a3de1892c0baf9086(
    project: _projen_04054675.Project,
    *,
    license: typing.Optional[builtins.str] = None,
    author_email: typing.Optional[builtins.str] = None,
    author_name: typing.Optional[builtins.str] = None,
    classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    homepage: typing.Optional[builtins.str] = None,
    keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
    license_file: typing.Optional[builtins.str] = None,
    package_name: typing.Optional[builtins.str] = None,
    readme: typing.Optional[builtins.str] = None,
    requires_python: typing.Optional[builtins.str] = None,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6c809477032f6e6abdbfbf18de97c940c11e01375028ae0f5ecb6b8e973a50f(
    project: _projen_04054675.Project,
    task_opts: typing.Union[TaskOptions, typing.Dict[builtins.str, typing.Any]],
    *,
    lock_file: typing.Optional[builtins.str] = None,
    lock_file_dev: typing.Optional[builtins.str] = None,
    python_exec: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82328de1f2fc16d559d0de14506a0fa6977eaf5050623900f5ab343c6be250cb(
    project: _projen_04054675.Project,
    *,
    venv_path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ab0570fbeee15a743ac44aee78db6330a9da7a8cb0af29bcd9bbd26f212ec73(
    *,
    lock_file: typing.Optional[builtins.str] = None,
    lock_file_dev: typing.Optional[builtins.str] = None,
    python_exec: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17c08f1d83ea1c68434cc706bd3ab3f0d86a9134d0afbe1bd10ef7bfc93879ce(
    *,
    group: typing.Optional[builtins.str] = None,
    registry_url: typing.Optional[builtins.str] = None,
    packages_dir: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb758ea416713f75fc2acbbcb87bcba07398ad01870730f548e260a3139fd382(
    project: _projen_04054675.Project,
    *,
    packages_dir: builtins.str,
    group: typing.Optional[builtins.str] = None,
    registry_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7778bb246ad316593449349e235db7d2104fe408eeac0a9f5efcda22aacb114(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7986fd7f1b9f7afb7cf5bb1b36ea56b403fa42d6083b6fa58fb2cf65e9d5329b(
    *,
    build_task: typing.Optional[builtins.str] = None,
    group: typing.Optional[builtins.str] = None,
    monotag_options: typing.Optional[typing.Union[NextTagOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    npm: typing.Optional[typing.Union[PublishNpmOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    pypi: typing.Optional[typing.Union[PublishPypiOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    skip_bump: typing.Optional[builtins.bool] = None,
    skip_checks: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69d253711342d80bd6b3c0cc9cee6ed6f79c7030a125bc91eeb63c25f0079b27(
    *,
    group: typing.Optional[builtins.str] = None,
    registry_url: typing.Optional[builtins.str] = None,
    packages_dir: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f190275a1c7b1eb98e8bfa49265a15457fa34e711c1f20eff6c87bdddfa24179(
    project: _projen_04054675.Project,
    *,
    packages_dir: builtins.str,
    group: typing.Optional[builtins.str] = None,
    registry_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b35920cfba1211e462004105e1006ed5609b4742a73ff015ee2be147a1e56eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa8818e759d2ecb9be66a3ca05c6baf1b05c4553950364535f80d5211cb75411(
    project: _projen_04054675.Project,
    *,
    build_task: typing.Optional[builtins.str] = None,
    group: typing.Optional[builtins.str] = None,
    monotag_options: typing.Optional[typing.Union[NextTagOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    npm: typing.Optional[typing.Union[PublishNpmOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    pypi: typing.Optional[typing.Union[PublishPypiOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    skip_bump: typing.Optional[builtins.bool] = None,
    skip_checks: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6d7a3b8b4177596f54f16f91bd9df59e0a45d86f401871b1e9b3b29ce78328b(
    project: _projen_04054675.Project,
    *,
    author_email: typing.Optional[builtins.str] = None,
    author_name: typing.Optional[builtins.str] = None,
    classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    homepage: typing.Optional[builtins.str] = None,
    keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
    license_file: typing.Optional[builtins.str] = None,
    package_name: typing.Optional[builtins.str] = None,
    readme: typing.Optional[builtins.str] = None,
    requires_python: typing.Optional[builtins.str] = None,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4507ce8637891a717163abf9982165de1dcb742ca0621e122de9e18450c7727b(
    _resolver: _projen_04054675.IResolver,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05a4f19c0ac4e3b053533fffc4e6b5d4ec292f9c4073fe33392b6cfca5185ea0(
    *,
    author_email: typing.Optional[builtins.str] = None,
    author_name: typing.Optional[builtins.str] = None,
    classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    homepage: typing.Optional[builtins.str] = None,
    keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
    license_file: typing.Optional[builtins.str] = None,
    package_name: typing.Optional[builtins.str] = None,
    readme: typing.Optional[builtins.str] = None,
    requires_python: typing.Optional[builtins.str] = None,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42e05408896599bbf022ad6a7e60a821d61cad81416e62f8e87333465af34cc8(
    project: _projen_04054675.Project,
    task_opts: typing.Union[TaskOptions, typing.Dict[builtins.str, typing.Any]],
    *,
    format: typing.Optional[builtins.str] = None,
    min_coverage: typing.Optional[jsii.Number] = None,
    omit_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
    skip_covered: typing.Optional[builtins.bool] = None,
    skip_empty: typing.Optional[builtins.bool] = None,
    verbose: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44a3acc3982cbac42b7f244f2b7a0629ea77dbb3fbeb16b462809daed3316bc1(
    project: _projen_04054675.Project,
    *,
    verbose: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__975893dbb0771af51870157408a643ffcf74cf8fc037cc71b062959406638251(
    _resolver: _projen_04054675.IResolver,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ef765f0b3b01e999545322392822791093e2b72fca8c2d619f6f3c52c5dfcd7(
    value: PyTestIniOptions,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d4ca4cf98a7701cf69a33f919512afaccabd7bb8ee6ac702d86b6b686e85c40(
    *,
    verbose: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__384e63be7810bf945d6fb782fc3c891fca1787094bf35586a2dcbb2d81ce2867(
    *,
    format: typing.Optional[builtins.str] = None,
    min_coverage: typing.Optional[jsii.Number] = None,
    omit_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
    skip_covered: typing.Optional[builtins.bool] = None,
    skip_empty: typing.Optional[builtins.bool] = None,
    verbose: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c514a60a75f071c20ec30de634506e6c296b1d91b281bd1a0ff69ec8551d7bf7(
    package_name_version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6803cea798ee4a60e65efc9b0cc675daf469d702cfb43e7595aed132004e56e3(
    package_name_version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f89bc9b2d760f7dbf6c765c850ee98f08ad2b9abd29b30723839469f113ac71(
    project: _projen_04054675.Project,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b56632f9602060a9026f4ff094af75115f54480ed5cffe451781d662b51d31f1(
    project: _projen_04054675.Project,
    *,
    python_version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3eb4c7d952a99bdea958131725c8145a2e4d0ef325b48ac55d83275c5cdd0c0(
    _resolver: _projen_04054675.IResolver,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fb02140f15e42d4186643add56e5f0ffe0d004d6540a470bf2ae03d136a627b(
    *,
    python_version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e121cdedc0beed1c682d7a460ce0e7ed3201b3597d0675df06b9bc467a25a42(
    project: _projen_04054675.Project,
    *,
    project_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f16ff3cf7a0826918909ecb12dfd4f0ec1385aa6bdc84176767f6109162ecdc(
    *,
    project_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fc118b5a89a887bbc9715306583b5d0cbd1825074a2b5a6fe6f64b81e9a4d38(
    *,
    bump_action: typing.Optional[builtins.str] = None,
    bump_files: typing.Optional[typing.Sequence[builtins.str]] = None,
    changelog_file: typing.Optional[builtins.str] = None,
    from_ref: typing.Optional[builtins.str] = None,
    git_email: typing.Optional[builtins.str] = None,
    git_username: typing.Optional[builtins.str] = None,
    max_version: typing.Optional[builtins.str] = None,
    min_version: typing.Optional[builtins.str] = None,
    monotag_cmd: typing.Optional[builtins.str] = None,
    monotag_extra_args: typing.Optional[builtins.str] = None,
    notes_file: typing.Optional[builtins.str] = None,
    only_conv_commit: typing.Optional[builtins.bool] = None,
    path: typing.Optional[builtins.str] = None,
    pre_release: typing.Optional[builtins.bool] = None,
    pre_release_always_increment: typing.Optional[builtins.bool] = None,
    pre_release_identifier: typing.Optional[builtins.str] = None,
    repo_dir: typing.Optional[builtins.str] = None,
    semver_level: typing.Optional[builtins.str] = None,
    tag_file: typing.Optional[builtins.str] = None,
    tag_prefix: typing.Optional[builtins.str] = None,
    tag_suffix: typing.Optional[builtins.str] = None,
    to_ref: typing.Optional[builtins.str] = None,
    verbose: typing.Optional[builtins.bool] = None,
    version_file: typing.Optional[builtins.str] = None,
    action: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba446ae8ee81ba2bd8583a5cf9965d6c1aa385438f34c06c5252b45b480469f1(
    project: _projen_04054675.Project,
    *,
    action: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    bump_action: typing.Optional[builtins.str] = None,
    bump_files: typing.Optional[typing.Sequence[builtins.str]] = None,
    changelog_file: typing.Optional[builtins.str] = None,
    from_ref: typing.Optional[builtins.str] = None,
    git_email: typing.Optional[builtins.str] = None,
    git_username: typing.Optional[builtins.str] = None,
    max_version: typing.Optional[builtins.str] = None,
    min_version: typing.Optional[builtins.str] = None,
    monotag_cmd: typing.Optional[builtins.str] = None,
    monotag_extra_args: typing.Optional[builtins.str] = None,
    notes_file: typing.Optional[builtins.str] = None,
    only_conv_commit: typing.Optional[builtins.bool] = None,
    path: typing.Optional[builtins.str] = None,
    pre_release: typing.Optional[builtins.bool] = None,
    pre_release_always_increment: typing.Optional[builtins.bool] = None,
    pre_release_identifier: typing.Optional[builtins.str] = None,
    repo_dir: typing.Optional[builtins.str] = None,
    semver_level: typing.Optional[builtins.str] = None,
    tag_file: typing.Optional[builtins.str] = None,
    tag_prefix: typing.Optional[builtins.str] = None,
    tag_suffix: typing.Optional[builtins.str] = None,
    to_ref: typing.Optional[builtins.str] = None,
    verbose: typing.Optional[builtins.bool] = None,
    version_file: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92e6719177912c0eae0ee85cfc203cb22854f3f273cc256898396282ba7d42fe(
    project: _projen_04054675.Project,
    task_opts: typing.Union[TaskOptions, typing.Dict[builtins.str, typing.Any]],
    *,
    attach_fix_task_to: typing.Optional[builtins.str] = None,
    add_to_existing_rules: typing.Optional[builtins.bool] = None,
    ignore_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
    mccabe_max_complexity: typing.Optional[jsii.Number] = None,
    per_file_ignores: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
    select_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_python_version: typing.Optional[builtins.str] = None,
    unsafe_fixes: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__515cf86a84df0b6b18941ab4c2a73e7eef40e0260fab3c698c6cabcef8227d71(
    project: _projen_04054675.Project,
    *,
    add_to_existing_rules: typing.Optional[builtins.bool] = None,
    ignore_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
    mccabe_max_complexity: typing.Optional[jsii.Number] = None,
    per_file_ignores: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
    select_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_python_version: typing.Optional[builtins.str] = None,
    unsafe_fixes: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce7087163e4218666b985f90db1006536d982decdeb6854261778dfc1f07f506(
    *,
    add_to_existing_rules: typing.Optional[builtins.bool] = None,
    ignore_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
    mccabe_max_complexity: typing.Optional[jsii.Number] = None,
    per_file_ignores: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
    select_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_python_version: typing.Optional[builtins.str] = None,
    unsafe_fixes: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60bbd600395432f8000b4758eea0d98c9c8e225b40399a70f2bd14d84ef3bb0f(
    *,
    venv_path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ebef6526107b290f8f3024aa58a74f546f6c2dcee9f6faa53295f3c7402ac4a(
    *,
    attach_tasks_to: typing.Optional[builtins.str] = None,
    venv_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6ce63ffedc17816d4e10d303db52b112c4a018db5d7b81c720790d591a43e4e(
    *,
    format: typing.Optional[builtins.str] = None,
    min_coverage: typing.Optional[jsii.Number] = None,
    omit_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
    skip_covered: typing.Optional[builtins.bool] = None,
    skip_empty: typing.Optional[builtins.bool] = None,
    verbose: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0658c3d7fe54aaec02fcef6987c7705125d952a65e7b4f1cde8ad8b0b36e7aa8(
    project: _projen_04054675.Project,
    task_opts: typing.Union[TaskOptions, typing.Dict[builtins.str, typing.Any]],
    *,
    format: typing.Optional[builtins.str] = None,
    min_coverage: typing.Optional[jsii.Number] = None,
    omit_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
    skip_covered: typing.Optional[builtins.bool] = None,
    skip_empty: typing.Optional[builtins.bool] = None,
    verbose: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b76c94e731f66a8083161e79ab92ddf0b90fbe84267279e946aafacb6a0211a8(
    *,
    additional_makefile_contents_projen: typing.Optional[builtins.str] = None,
    additional_makefile_contents_targets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    node_version: typing.Optional[builtins.str] = None,
    projen_lib_version: typing.Optional[builtins.str] = None,
    ts_node_lib_version: typing.Optional[builtins.str] = None,
    additional_makefile_contents_user: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__769a6aad7aea164b73af332f179b064a5d119bdb8838de929422452d3b88c50c(
    *,
    author_email: typing.Optional[builtins.str] = None,
    author_name: typing.Optional[builtins.str] = None,
    classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    homepage: typing.Optional[builtins.str] = None,
    keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
    license_file: typing.Optional[builtins.str] = None,
    package_name: typing.Optional[builtins.str] = None,
    readme: typing.Optional[builtins.str] = None,
    requires_python: typing.Optional[builtins.str] = None,
    version: typing.Optional[builtins.str] = None,
    license: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c54d357164afec478ab317ef798bb3d8a0ac8c35182918abf6dfd0025c70bc86(
    *,
    name: builtins.str,
    commit_generated: typing.Optional[builtins.bool] = None,
    git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    outdir: typing.Optional[builtins.str] = None,
    parent: typing.Optional[_projen_04054675.Project] = None,
    projen_command: typing.Optional[builtins.str] = None,
    projenrc_json: typing.Optional[builtins.bool] = None,
    projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    renovatebot: typing.Optional[builtins.bool] = None,
    renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    pip: typing.Optional[typing.Union[PipOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    pkg: typing.Optional[typing.Union[PackageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    attach_tasks_to: typing.Optional[builtins.str] = None,
    venv_path: typing.Optional[builtins.str] = None,
    deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    lint: typing.Optional[typing.Union[LintOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    publish: typing.Optional[typing.Union[PublishOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    release: typing.Optional[typing.Union[ReleaseOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    sample: typing.Optional[builtins.bool] = None,
    test: typing.Optional[typing.Union[TestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d207008bfccd269e92e2aa9ed31161d7e45bab33efb79344ae36a97c2eddcff(
    *,
    add_to_existing_rules: typing.Optional[builtins.bool] = None,
    ignore_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
    mccabe_max_complexity: typing.Optional[jsii.Number] = None,
    per_file_ignores: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
    select_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_python_version: typing.Optional[builtins.str] = None,
    unsafe_fixes: typing.Optional[builtins.bool] = None,
    attach_fix_task_to: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3438e7eef6485f46108347648af5008e12c90c19bfd98c01816e34421622428c(
    *,
    add_to_existing_rules: typing.Optional[builtins.bool] = None,
    ignore_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
    mccabe_max_complexity: typing.Optional[jsii.Number] = None,
    per_file_ignores: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
    select_rules: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_python_version: typing.Optional[builtins.str] = None,
    unsafe_fixes: typing.Optional[builtins.bool] = None,
    attach_fix_task_to: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
