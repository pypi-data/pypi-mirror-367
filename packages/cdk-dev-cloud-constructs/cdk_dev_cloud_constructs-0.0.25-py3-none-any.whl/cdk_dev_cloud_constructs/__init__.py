r'''
# TypeScript AWS CDK solution for setup a developer platform at AWS

This is TypeScript CDK constructs project to create an open source developer platform at AWS

## How it Works

This project uses projen for TypeScript sources, tooling and testing.
Just execute `npx projen help` to see what you can do.

**Current status:** Under development

## How to start

You will need to have Typescript 5.8 or newer version and Yarn installed.
This will also install AWS cdk command by calling `npm install -g aws-cdk`.

... Yada yada

main DevCloudConstruct

# cdk-dev-cloud-constructs

[![](https://constructs.dev/favicon.ico) Construct Hub](https://constructs.dev/packages/cdk-dev-cloud-constructs)

---


## Table of Contents

* [Installation](#installation)
* [License](#license)

## Installation

TypeScript/JavaScript:

```bash
npm i cdk-dev-cloud-constructs
```

Python:

```bash
pip install cdk-dev-cloud-constructs
```

## License

`cdk-pipeline-for-terraform` is distributed under the terms of the [MIT](https://opensource.org/license/mit/) license.

# replace this
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

import aws_cdk.aws_eks as _aws_cdk_aws_eks_ceddda9d
import constructs as _constructs_77d1e7e8


class GitlabConstruct(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-dev-cloud-constructs.GitlabConstruct",
):
    '''(experimental) GitLab Helm Chart construct for Kubernetes on AWS.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: _aws_cdk_aws_eks_ceddda9d.ICluster,
        chart_name: typing.Optional[builtins.str] = None,
        chart_version: typing.Optional[builtins.str] = None,
        domain_name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        values_override: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        values_yaml_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: (experimental) Gitlab full qualified domain name.
        :param chart_name: 
        :param chart_version: 
        :param domain_name: 
        :param namespace: 
        :param values_override: 
        :param values_yaml_file: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20b97d9969c599c19a466a004376fceb871af277a21d8ce6beea32fe12dd1da4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GitlabProps(
            cluster=cluster,
            chart_name=chart_name,
            chart_version=chart_version,
            domain_name=domain_name,
            namespace=namespace,
            values_override=values_override,
            values_yaml_file=values_yaml_file,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="chart")
    def chart(self) -> _aws_cdk_aws_eks_ceddda9d.HelmChart:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_eks_ceddda9d.HelmChart, jsii.get(self, "chart"))

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> _aws_cdk_aws_eks_ceddda9d.ICluster:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_eks_ceddda9d.ICluster, jsii.get(self, "cluster"))

    @builtins.property
    @jsii.member(jsii_name="defaultValues")
    def default_values(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "defaultValues"))

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property
    @jsii.member(jsii_name="fqdn")
    def fqdn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "fqdn"))

    @builtins.property
    @jsii.member(jsii_name="mergedValues")
    def merged_values(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "mergedValues"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @builtins.property
    @jsii.member(jsii_name="values")
    def values(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "values"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property
    @jsii.member(jsii_name="yamlValues")
    def yaml_values(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "yamlValues"))


@jsii.data_type(
    jsii_type="cdk-dev-cloud-constructs.GitlabProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster": "cluster",
        "chart_name": "chartName",
        "chart_version": "chartVersion",
        "domain_name": "domainName",
        "namespace": "namespace",
        "values_override": "valuesOverride",
        "values_yaml_file": "valuesYamlFile",
    },
)
class GitlabProps:
    def __init__(
        self,
        *,
        cluster: _aws_cdk_aws_eks_ceddda9d.ICluster,
        chart_name: typing.Optional[builtins.str] = None,
        chart_version: typing.Optional[builtins.str] = None,
        domain_name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        values_override: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        values_yaml_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for the GitLab Helm Chart construct.

        :param cluster: (experimental) Gitlab full qualified domain name.
        :param chart_name: 
        :param chart_version: 
        :param domain_name: 
        :param namespace: 
        :param values_override: 
        :param values_yaml_file: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74a002fc4709396e3fb919f7a515ced9e8876286c10d340756a4e473c09edd4f)
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument chart_name", value=chart_name, expected_type=type_hints["chart_name"])
            check_type(argname="argument chart_version", value=chart_version, expected_type=type_hints["chart_version"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument values_override", value=values_override, expected_type=type_hints["values_override"])
            check_type(argname="argument values_yaml_file", value=values_yaml_file, expected_type=type_hints["values_yaml_file"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster": cluster,
        }
        if chart_name is not None:
            self._values["chart_name"] = chart_name
        if chart_version is not None:
            self._values["chart_version"] = chart_version
        if domain_name is not None:
            self._values["domain_name"] = domain_name
        if namespace is not None:
            self._values["namespace"] = namespace
        if values_override is not None:
            self._values["values_override"] = values_override
        if values_yaml_file is not None:
            self._values["values_yaml_file"] = values_yaml_file

    @builtins.property
    def cluster(self) -> _aws_cdk_aws_eks_ceddda9d.ICluster:
        '''(experimental) Gitlab full qualified domain name.

        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(_aws_cdk_aws_eks_ceddda9d.ICluster, result)

    @builtins.property
    def chart_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("chart_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def chart_version(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("chart_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def values_override(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("values_override")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def values_yaml_file(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("values_yaml_file")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitlabProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Hello(metaclass=jsii.JSIIMeta, jsii_type="cdk-dev-cloud-constructs.Hello"):
    '''
    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="sayHello")
    def say_hello(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "sayHello", []))


__all__ = [
    "GitlabConstruct",
    "GitlabProps",
    "Hello",
]

publication.publish()

def _typecheckingstub__20b97d9969c599c19a466a004376fceb871af277a21d8ce6beea32fe12dd1da4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: _aws_cdk_aws_eks_ceddda9d.ICluster,
    chart_name: typing.Optional[builtins.str] = None,
    chart_version: typing.Optional[builtins.str] = None,
    domain_name: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    values_override: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    values_yaml_file: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74a002fc4709396e3fb919f7a515ced9e8876286c10d340756a4e473c09edd4f(
    *,
    cluster: _aws_cdk_aws_eks_ceddda9d.ICluster,
    chart_name: typing.Optional[builtins.str] = None,
    chart_version: typing.Optional[builtins.str] = None,
    domain_name: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    values_override: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    values_yaml_file: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
