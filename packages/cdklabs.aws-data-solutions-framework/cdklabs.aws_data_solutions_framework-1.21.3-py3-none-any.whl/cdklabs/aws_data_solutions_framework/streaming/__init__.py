r'''
# MSK Provisioned

An MSK Provisioned cluster with helpers to manage topics, ACLs and IAM permissions.

## Overview

The construct creates an MSK Provisioned Cluster, with the latest Kafka version in MSK as default. You can change the defaults by passing your own parameters as a Resource property to construct initializer. The construct supports creating clusters with mTLS, IAM or both as authentication methods. The construct use IAM as authentication by default if none is provided. It offers methods to manage topics and ACLs. Last, it also provides methods to grant an existing principal (ie IAM Role or IAM User or CN -Common Name-) with the permission to `produce` or `consume` to/from a kafka topic. The diagram below shows the high level architecture.

![MSK Provisioned High level architecture](../../../website/static/img/msk-provisioned.png)

The construct can create a VPC on your behalf that is used to deploy MSK Provisioned cluster or you can provide your own VPC definition through the `vpcConfigs` property when you initialize the construct. The VPC that is created on your behalf has `10.0.0.0/16` CIDR range, and comes with an S3 VPC Endpoint Gateway attached to it. The construct also creates a security group that is attached to the brokers. It's also possible to encrypt the environment variables of the Lambda functions used within this construct using a specific AWS KMS Key through the `environmentEncryption` property. Note that you need to ensure the key policy does not block access for these Lambda roles, as this could prevent successful encryption and decryption operations.

### Construct cluster setup

The construct sets up a dedicated security group for Zookeeper as advised in the AWS [documentation](https://docs.aws.amazon.com/msk/latest/developerguide/zookeeper-security.html#zookeeper-security-group). When authentication is set to TLS, the construct apply ACLs on the provided principal in the props defined as `certificateDefinition`. This principal is used by the custom resource to manage ACL. Last, the construct applies MSK configuration setting `allow.everyone.if.no.acl.found` to `false`. You can also provide your own MSK configuration, in this case the construct does not create one and will apply the one you passed as part of the props.

### Interacting with cluster

The construct has the following methods, you will usage examples in the new sections:

```
*  setTopic: Perform create, update, and delete operations on Topics
*  setACL: Perform create, update, and delete operations on ACL
*  grantProduce: Attach an IAM policy to a principal to write to a topic
*  grantConsume: Attach an IAM policy to a principal to read from a topic
```

Below you can find an example of creating an MSK Provisioned configuration with the default options.

```python
msk = MskProvisioned(stack, "cluster")
```

## Usage

### Bring Your Own VPC

The construct allows you to provide your own VPC that was created outside the CDK Stack. Below you will find an example usage.

```python
vpc = Vpc.from_vpc_attributes(stack, "vpc",
    vpc_id="vpc-1111111111",
    vpc_cidr_block="10.0.0.0/16",
    availability_zones=["eu-west-1a", "eu-west-1b"],
    public_subnet_ids=["subnet-111111111", "subnet-11111111"],
    private_subnet_ids=["subnet-11111111", "subnet-1111111"]
)

msk = MskProvisioned(stack, "cluster",
    vpc=vpc,
    cluster_name="my-cluster",
    subnets=vpc.select_subnets()
)
```

### Create a cluster with mTLS authentication

The construct allows you to create a cluster with mTLS, below is a code snippet showing the configuration.

When using MSK with mTLS the constructs requires a principal that is assigned to the custom resources that manage ACLs and Topics. The certificate and private key are expected to be in a secret managed by [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html). The secret needs to be in the format defined below and stored a `JSON Key/value` and not `Plaintext` in the Secret. The construct grants the lambda that supports the Custom Resource read access to the secret as an `Identity based policy`.

```json
    {
      key : "-----BEGIN RSA PRIVATE KEY----- XXXXXXXXXXXXXXXXX -----END RSA PRIVATE KEY-----",

      cert : "-----BEGIN CERTIFICATE----- yyyyyyyyyyyyyyyy -----END CERTIFICATE-----"
    }
```

```python
certificate_authority = CertificateAuthority.from_certificate_authority_arn(stack, "certificateAuthority", "arn:aws:acm-pca:eu-west-1:123456789012:certificate-authority/aaaaaaaa-bbbb-454a-cccc-b454877f0d1b")

msk = MskProvisioned(stack, "cluster",
    client_authentication=ClientAuthentication.sasl_tls(
        iam=True,
        certificate_authorities=[certificate_authority]
    ),
    certificate_definition=AclAdminProps(
        admin_principal="User:CN=Admin",
        acl_admin_principal="User:CN=aclAdmin",
        secret_certificate=Secret.from_secret_complete_arn(stack, "secret", "arn:aws:secretsmanager:eu-west-1:123456789012:secret:dsf/mskCert-3UhUJJ")
    ),
    allow_everyone_if_no_acl_found=False
)
```

### setTopic

This method allows you to create, update or delete an ACL. Its backend uses [kafkajs](https://kafka.js.org/).
The topic is defined by the property type called `MskTopic`.
If your MSK cluster uses KRaft mode rather than ZooKeeper, we encourage you to set to the parameter `waitForLeaders = true`
and `timeout = 10000`.
Below you can see the definition of the topic as well as a usage.

```json
{
    topic: <String>,
    numPartitions: <Number>,     // default: -1 (uses broker `num.partitions` configuration)
    replicationFactor: <Number>, // default: -1 (uses broker `default.replication.factor` configuration)
    replicaAssignment: <Array>,  // Example: [{ partition: 0, replicas: [0,1,2] }] - default: []
    configEntries: <Array>       // Example: [{ name: 'cleanup.policy', value: 'compact' }] - default: []
}
```

Dependeding on the authentication type that is set in the cluster, you need to put the right parameter in authentication, for mTLS use `Authentitcation.MTLS` and for IAM use `Authentitcation.IAM`. The example below uses IAM as authentication.

```python
msk.set_topic("topic1", Authentication.IAM, MskTopic(
    topic="topic1",
    num_partitions=3,
    replication_factor=1,
    config_entries=[{
        "name": "retention.ms",
        "value": "90000"
    }, {
        "name": "retention.bytes",
        "value": "90000"
    }
    ]
), cdk.RemovalPolicy.DESTROY, False, 1500)
```

### setACL

This method allows you to create, update or delete a topic. Its backend uses [kafkajs](https://kafka.js.org/).
The topic is defined by the property type called `MskACL`. This method should be used only when the cluster authentication is set to `mTLS`. Below you can see the definition of the topic as well as an example of use.

```json
{
    resourceType: <AclResourceTypes>,
    resourceName: <String>,
    resourcePatternType: <ResourcePatternTypes>,
    principal: <String>,
    host: <String>,
    operation: <AclOperationTypes>,
    permissionType: <AclPermissionTypes>,
}
```

You can authenticate to your cluster using IAM or mTLS to create ACLs. These ACLs will be used later by a client that will authenticate to your cluster using mTLS. Dependeding on the authentication type that you would like to use to create the ACL, you need to put the right parameter in `clientAuthentication`: for mTLS use `Authentitcation.MTLS` and for IAM use `Authentitcation.IAM`. Default value is `Authentitcation.MTLS`. The example below uses IAM as authentication.

```python
msk.set_acl("acl", Acl(
    resource_type=AclResourceTypes.TOPIC,
    resource_name="topic-1",
    resource_pattern_type=ResourcePatternTypes.LITERAL,
    principal="User:Cn=Bar",
    host="*",
    operation=AclOperationTypes.CREATE,
    permission_type=AclPermissionTypes.ALLOW
), cdk.RemovalPolicy.DESTROY, Authentication.IAM)
```

### grantProduce

This method allows to grant a `Principal` the rights to write to a kafka topic.
In case of IAM authentication the method attachs an IAM policy as defined in the [AWS documentation](https://docs.aws.amazon.com/msk/latest/developerguide/iam-access-control.html#iam-access-control-use-cases) scoped only to the topic provided. For mTLS authentication, the method apply an ACL for the provided `Common Name` that allows it to write to the topic.

```python
msk.grant_produce("consume", "foo", Authentication.MTLS, "User:Cn=MyUser")
```

### grantConsume

This method allows to grant a `Principal` the rights to read to a kafka topic.
In case of IAM authentication the method attachs an IAM policy as defined in the [AWS documentation](https://docs.aws.amazon.com/msk/latest/developerguide/iam-access-control.html#iam-access-control-use-cases) scoped only to the topic provided. For mTLS authentication, the method apply an ACL for the provided `Common Name` that allows it to read from the topic.

```python
msk.grant_consume("consume", "foo", Authentication.MTLS, "User:Cn=MyUser")
```

### addCluster Policy

This method allows you to add IAM resource policy to your MSK cluster. This method can enable you for example to setup cross account access for your Amazon MSK cluster.

```python
msk = MskProvisioned(stack, "cluster")

cluter_policy = PolicyDocument(
    statements=[
        PolicyStatement(
            actions=["kafka:CreateVpcConnection", "kafka:GetBootstrapBrokers", "kafka:DescribeClusterV2"
            ],
            resources=[msk.cluster.attr_arn],
            effect=Effect.ALLOW,
            principals=[ServicePrincipal("firehose.amazonaws.com")]
        )
    ]
)

msk.add_cluster_policy(cluter_policy, "cluterPolicy")
```

# MSK Serverless

An MSK Serverless cluster with helpers to manage topics and IAM permissions.

## Overview

The construct creates an MSK Serverless Cluster, with the latest Kafka version in MSK as default. You can change the dafaults by passing your own parameters as a Resource property to construct initializer. There is also a method to create topics. Last, it also provides methods to grant an existing principal (ie IAM Role or IAM User) with the permission to `produce` or `consume` from a kafka topic. The diagram below shows the high level architecture.

![MSK Serverless High level architecture](../../../website/static/img/msk-serverless.png)

The construct can create a VPC on your behalf that is used to deploy MSK Serverless cluser or you can provide your own VPC definition through the `vpcConfigs` property when you initialize the construct. The VPC that is created on your behalf has `10.0.0.0/16` CIDR range, and comes with an S3 VPC Endpoint Gateway attached to it. The construct also creates a security group for that is attached to the brokers. It's also possible to encrypt the environment variables of the Lambda functions used within this construct using a specific AWS KMS Key through the `environmentEncryption` property. Note that you need to ensure the key policy does not block access for these Lambda roles, as this could prevent successful encryption and decryption operations.

The construct has the following interfaces, you will usage examples in the new sections:
*  setTopic: Perform create, update, and delete operations on Topics
*  grantProduce: Attach an IAM policy to a principal to write to a topic
*  grantConsume: Attach an IAM policy to a principal to read from a topic

Below you can find an example of creating an MSK Serverless configuration with the default options.

```python
msk = MskServerless(stack, "cluster")
```

## Usage

### Bring Your Own VPC

The construct allows you to provide your own VPC that was created outside the CDK Stack. Below you will find an example usage.

```python
vpc = Vpc.from_vpc_attributes(stack, "vpc",
    vpc_id="vpc-1111111111",
    vpc_cidr_block="10.0.0.0/16",
    availability_zones=["eu-west-1a", "eu-west-1b"],
    public_subnet_ids=["subnet-111111111", "subnet-11111111"],
    private_subnet_ids=["subnet-11111111", "subnet-1111111"]
)

msk = MskServerless(stack, "cluster",
    cluster_name="msk-byov",
    security_groups=[SecurityGroup.from_lookup_by_name(stack, "brokerSecurityGroup", "broker-sg", vpc)],
    subnets=vpc.select_subnets(),
    vpc=vpc
)
```

### setTopic

This method allows you to create, update or delete a topic. Its backend uses [kafkajs](https://kafka.js.org/).
The topic is defined by the property type called `MskTopic`.
If your MSK cluster uses KRaft mode rather than ZooKeeper, we encourage you to set to the parameter `waitForLeaders = true`
and `timeout = 10000`.
Below you can see the definition of the topic as well as a usage.

```json
{
    topic: <String>,
    numPartitions: <Number>,     // default: -1 (uses broker `num.partitions` configuration)
    replicationFactor: <Number>, // default: -1 (uses broker `default.replication.factor` configuration)
    configEntries: <Array>       // Example: [{ name: 'cleanup.policy', value: 'compact' }] - default: []
}
```

```python
msk = MskServerless(stack, "cluster")

topic = MskTopic(
    topic="topic1",
    num_partitions=3,
    replication_factor=1,
    config_entries=[{
        "name": "retention.ms",
        "value": "90000"
    }, {
        "name": "retention.bytes",
        "value": "90000"
    }
    ]
)

msk.add_topic("topic1", topic, cdk.RemovalPolicy.DESTROY, False, 1500)
```

### grantProduce

This method allows to grant a `Principal` the rights to write to a kafka topic.
The method attachs an IAM policy as defined in the [AWS documentation](https://docs.aws.amazon.com/msk/latest/developerguide/iam-access-control.html#iam-access-control-use-cases) scoped only to the topic provided.

```python
msk = MskServerless(stack, "cluster")

iam_role = Role.from_role_name(stack, "role", "role")

msk.grant_produce("topic1", iam_role)
```

### grantConsume

This method allows to grant a `Principal` the rights to read to a kafka topic.
The method attachs an IAM policy as defined in the [AWS documentation](https://docs.aws.amazon.com/msk/latest/developerguide/iam-access-control.html#iam-access-control-use-cases) scoped only to the topic provided.

```python
msk = MskServerless(stack, "cluster")

iam_role = Role.from_role_name(stack, "role", "role")

msk.grant_consume("topic1", iam_role)
```

### addClusterPolicy

This method allows you to add IAM resource policy to your MSK cluster. This method can enable you for example to setup cross account access for your Amazon MSK cluster.

```python
msk = MskServerless(stack, "cluster")

cluter_policy = PolicyDocument(
    statements=[
        PolicyStatement(
            actions=["kafka:CreateVpcConnection", "kafka:GetBootstrapBrokers", "kafka:DescribeClusterV2"
            ],
            resources=[msk.cluster.attr_arn],
            effect=Effect.ALLOW,
            principals=[ServicePrincipal("firehose.amazonaws.com")]
        )
    ]
)

msk.add_cluster_policy(cluter_policy, "cluterPolicy")
```

# Kafka Api - Bring your own cluster

Standalone access to Kafka data plane API to perform Create/Update/Delete operations for ACLs and Topics. The constructs support both MSK Serverless and MSK Provisioned, and is used when you need to bring your own cluster.

## Overview

The construct leverages the [CDK Provider Framework](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.custom_resources-readme.html#provider-framework) to deploy a custom resource to manage `topics`, and in case of `mTLS` authentication deploys also a custom resource to manage `ACLs`.

```python
certificate_authority = CertificateAuthority.from_certificate_authority_arn(stack, "certificateAuthority", "arn:aws:acm-pca:eu-west-1:12345678912:certificate-authority/dummy-ca")

secret = Secret.from_secret_complete_arn(stack, "secret", "arn:aws:secretsmanager:eu-west-1:12345678912:secret:dsf/mskCert-dummy")

vpc = Vpc.from_vpc_attributes(stack, "vpc",
    vpc_id="vpc-1111111111",
    vpc_cidr_block="10.0.0.0/16",
    availability_zones=["eu-west-1a", "eu-west-1b"],
    public_subnet_ids=["subnet-111111111", "subnet-11111111"],
    private_subnet_ids=["subnet-11111111", "subnet-1111111"]
)

kafka_api = KafkaApi(stack, "kafkaApi",
    vpc=vpc,
    cluster_arn="arn:aws:kafka:eu-west-1:12345678912:cluster/byo-msk/dummy-5cf3-42d5-aece-dummmy-2",
    cluster_type=MskClusterType.PROVISIONED,
    broker_security_group=SecurityGroup.from_security_group_id(stack, "brokerSecurityGroup", "sg-98237412hsa"),
    certficate_secret=secret,
    client_authentication=ClientAuthentication.sasl_tls(
        iam=True,
        certificate_authorities=[certificate_authority]
    ),
    kafka_client_log_level=KafkaClientLogLevel.DEBUG,
    service_token="arn:aws:lambda::XXXXXX:function:XXXXXX-kafkaApiMskIamProviderCustomResour-XXXXXX"
)
```

When deploying multiple stacks with the Kafka Api, if there is an already existing service token deployed for the custom resource, you can reuse it to reduce the number of resources created like lambdas and ENI that are used to create and manage the lifecycle the custom resources, like ACLs and Topics.
It's also possible to encrypt the environment variables of the Lambda functions used within this construct using a specific AWS KMS Key through the `environmentEncryption` property. Note that you need to ensure the key policy does not block access for these Lambda roles, as this could prevent successful encryption and decryption operations.

:::warning

The construct needs to be deployed in the same region as the MSK cluster.

:::

## Using mTLS authentication

When using MSK with mTLS the constructs requires a principal that is assigned to the custom resources that manage ACLs and Topics. The certificate and private key are expected to be in a secret managed by [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html). The secret needs to be in the format defined below and stored a `JSON Key/value` and not `Plaintext` in the Secret. The construct grants the lambda that supports the Custom Resource read access to the secret as an `Identity based policy`.

```json
    {
      key : "-----BEGIN RSA PRIVATE KEY----- XXXXXXXXXXXXXXXXX -----END RSA PRIVATE KEY-----",

      cert : "-----BEGIN CERTIFICATE----- yyyyyyyyyyyyyyyy -----END CERTIFICATE-----"
    }
```

You can create the secret with the following AWS CLI command:

```bash
aws secretsmanager create-secret --name my-secret \
    --secret-string '{"key": "PRIVATE-KEY", "cert": "CERTIFICATE"}'
```

:::danger

Do not create the secret as part of the CDK application. The secret contains the private key and the deployment is not secured.

:::

You can use this [utility](https://github.com/aws-samples/amazon-msk-client-authentication) to generate the certificates:

1. Build the tool
2. Run the following command to generate the certificates and print them

```bash
java -jar AuthMSK-1.0-SNAPSHOT.jar -caa <PCA_ARN> -ccf tmp/client_cert.pem -pem -pkf tmp/private_key.pem -ksp "XXXXXXXXXX" -ksl tmp/kafka.client.keystore.jks
cat tmp/client_cert.pem
cat tmp/private_key.pem
```

1. Copy/paste the value of the client certificate and the private key in the secret

### setTopic

This method allows you to create, update or delete a topic. Its backend uses [kafkajs](https://kafka.js.org/).
The topic is defined by the property type called `MskTopic`. Below you can see the definition of the topic.

```json
{
    topic: <String>,
    numPartitions: <Number>,     // default: -1 (uses broker `num.partitions` configuration)
    replicationFactor: <Number>, // default: -1 (uses broker `default.replication.factor` configuration)
    configEntries: <Array>       // Example: [{ name: 'cleanup.policy', value: 'compact' }] - default: []
}
```

Dependeding on the authentication type used in the cluster, you need to put the right parameter in authentication, for mTLS use `Authentitcation.MTLS` and for IAM use `Authentitcation.IAM`. The example below uses IAM as authentication.

```python
kafka_api.set_topic("topic1", Authentication.IAM, MskTopic(
    topic="topic1",
    num_partitions=3,
    replication_factor=1
), cdk.RemovalPolicy.DESTROY, False, 1500)
```

:::warning

Only the number of partitions can be updated after the creation of the topic.

:::

### setACL

This method allows you to create, update or delete an ACL. Its backend uses [kafkajs](https://kafka.js.org/).
The topic is defined by the property type called `MskACL`. This method can be used when the cluster authentication is set to `mTLS` or `IAM`+`mTLS`. Below you can see the definition of the ACL as well as an example of use.

```json
{
    resourceType: <AclResourceTypes>,
    resourceName: <String>,
    resourcePatternType: <ResourcePatternTypes>,
    principal: <String>,
    host: <String>,
    operation: <AclOperationTypes>,
    permissionType: <AclPermissionTypes>,
}
```

You can authenticate to your cluster using IAM or mTLS to create ACLs. These ACLs will be used later by a client that will authenticate to your cluster using mTLS. Dependeding on the authentication type that you would like to use to create the ACL, you need to put the right parameter in `clientAuthentication`: for mTLS use `Authentitcation.MTLS` and for IAM use `Authentitcation.IAM`. Default value is `Authentitcation.MTLS`. The example below uses mTLS as authentication.

```python
kafka_api.set_acl("acl", Acl(
    resource_type=AclResourceTypes.TOPIC,
    resource_name="topic-1",
    resource_pattern_type=ResourcePatternTypes.LITERAL,
    principal="User:Cn=MyUser",
    host="*",
    operation=AclOperationTypes.CREATE,
    permission_type=AclPermissionTypes.ALLOW
), cdk.RemovalPolicy.DESTROY, Authentication.MTLS)
```

### grantProduce

This method allows to grant a `Principal` the permissions to write to a kafka topic.
In case of IAM authentication the method attaches an IAM policy as defined in the [AWS documentation](https://docs.aws.amazon.com/msk/latest/developerguide/iam-access-control.html#iam-access-control-use-cases) scoped only to the topic provided. For mTLS authentication, the method applies an ACL for the provided `Common Name` that allow write operations on the topic.

```python
kafka_api.grant_produce("consume", "foo", Authentication.MTLS, "User:Cn=bar")
```

### grantConsume

This method allows to grant a `Principal` the permissions to read to a kafka topic.
In case of IAM authentication the method attachs an IAM policy as defined in the [AWS documentation](https://docs.aws.amazon.com/msk/latest/developerguide/iam-access-control.html#iam-access-control-use-cases) scoped only to the topic provided. For mTLS authentication, the method applies an ACL for the provided `Common Name` that allow read operations on the topic.

```python
kafka_api.grant_consume("consume", "foo", Authentication.MTLS, "User:Cn=bar")
```
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

from .._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_acmpca as _aws_cdk_aws_acmpca_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_msk as _aws_cdk_aws_msk_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.Acl",
    jsii_struct_bases=[],
    name_mapping={
        "host": "host",
        "operation": "operation",
        "permission_type": "permissionType",
        "principal": "principal",
        "resource_name": "resourceName",
        "resource_pattern_type": "resourcePatternType",
        "resource_type": "resourceType",
    },
)
class Acl:
    def __init__(
        self,
        *,
        host: builtins.str,
        operation: "AclOperationTypes",
        permission_type: "AclPermissionTypes",
        principal: builtins.str,
        resource_name: builtins.str,
        resource_pattern_type: "ResourcePatternTypes",
        resource_type: "AclResourceTypes",
    ) -> None:
        '''Kakfa ACL This is similar to the object used by ``kafkajs``, for more information see this `link <https://kafka.js.org/docs/admin#create-acl>`_.

        :param host: 
        :param operation: 
        :param permission_type: 
        :param principal: 
        :param resource_name: 
        :param resource_pattern_type: 
        :param resource_type: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b2c45eeb82912583d0e203bcc5f7cfa5d4679f4aa75359733b6a3b6d15aaa09)
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
            check_type(argname="argument permission_type", value=permission_type, expected_type=type_hints["permission_type"])
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
            check_type(argname="argument resource_name", value=resource_name, expected_type=type_hints["resource_name"])
            check_type(argname="argument resource_pattern_type", value=resource_pattern_type, expected_type=type_hints["resource_pattern_type"])
            check_type(argname="argument resource_type", value=resource_type, expected_type=type_hints["resource_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "host": host,
            "operation": operation,
            "permission_type": permission_type,
            "principal": principal,
            "resource_name": resource_name,
            "resource_pattern_type": resource_pattern_type,
            "resource_type": resource_type,
        }

    @builtins.property
    def host(self) -> builtins.str:
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def operation(self) -> "AclOperationTypes":
        result = self._values.get("operation")
        assert result is not None, "Required property 'operation' is missing"
        return typing.cast("AclOperationTypes", result)

    @builtins.property
    def permission_type(self) -> "AclPermissionTypes":
        result = self._values.get("permission_type")
        assert result is not None, "Required property 'permission_type' is missing"
        return typing.cast("AclPermissionTypes", result)

    @builtins.property
    def principal(self) -> builtins.str:
        result = self._values.get("principal")
        assert result is not None, "Required property 'principal' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_name(self) -> builtins.str:
        result = self._values.get("resource_name")
        assert result is not None, "Required property 'resource_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_pattern_type(self) -> "ResourcePatternTypes":
        result = self._values.get("resource_pattern_type")
        assert result is not None, "Required property 'resource_pattern_type' is missing"
        return typing.cast("ResourcePatternTypes", result)

    @builtins.property
    def resource_type(self) -> "AclResourceTypes":
        result = self._values.get("resource_type")
        assert result is not None, "Required property 'resource_type' is missing"
        return typing.cast("AclResourceTypes", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Acl(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.AclAdminProps",
    jsii_struct_bases=[],
    name_mapping={
        "acl_admin_principal": "aclAdminPrincipal",
        "admin_principal": "adminPrincipal",
        "secret_certificate": "secretCertificate",
    },
)
class AclAdminProps:
    def __init__(
        self,
        *,
        acl_admin_principal: builtins.str,
        admin_principal: builtins.str,
        secret_certificate: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> None:
        '''This Props allow you to define the principals that will be adminstartor as well as the principal that will be used by the CDK Custom resources to.

        :param acl_admin_principal: This Principal will be used by the CDK custom resource to set ACLs and Topics.
        :param admin_principal: The Principal that will have administrator privilege in MSK The MSK construct does not have access to this principal Keep this principal in a secure storage and should be only used in case you put an ACL that lock MSK access.
        :param secret_certificate: This is the TLS certificate of the Principal that is used by the CDK custom resource which set ACLs and Topics. The secret in AWS secrets manager must be a JSON in the following format { "key" : "PRIVATE-KEY", "cert" : "CERTIFICATE" } You can use the following utility to generate the certificates https://github.com/aws-samples/amazon-msk-client-authentication
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c2c48ca9218f0e3216c02f72ab5bacdfcd4861e0c07886b466905a0676baca8)
            check_type(argname="argument acl_admin_principal", value=acl_admin_principal, expected_type=type_hints["acl_admin_principal"])
            check_type(argname="argument admin_principal", value=admin_principal, expected_type=type_hints["admin_principal"])
            check_type(argname="argument secret_certificate", value=secret_certificate, expected_type=type_hints["secret_certificate"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "acl_admin_principal": acl_admin_principal,
            "admin_principal": admin_principal,
            "secret_certificate": secret_certificate,
        }

    @builtins.property
    def acl_admin_principal(self) -> builtins.str:
        '''This Principal will be used by the CDK custom resource to set ACLs and Topics.'''
        result = self._values.get("acl_admin_principal")
        assert result is not None, "Required property 'acl_admin_principal' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def admin_principal(self) -> builtins.str:
        '''The Principal that will have administrator privilege in MSK The MSK construct does not have access to this principal Keep this principal in a secure storage and should be only used in case you put an ACL that lock MSK access.'''
        result = self._values.get("admin_principal")
        assert result is not None, "Required property 'admin_principal' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secret_certificate(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''This is the TLS certificate of the Principal that is used by the CDK custom resource which set ACLs and Topics.

        The secret in AWS secrets manager must be a JSON in the following format
        {
        "key" : "PRIVATE-KEY",
        "cert" : "CERTIFICATE"
        }

        You can use the following utility to generate the certificates
        https://github.com/aws-samples/amazon-msk-client-authentication
        '''
        result = self._values.get("secret_certificate")
        assert result is not None, "Required property 'secret_certificate' is missing"
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AclAdminProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.AclOperationTypes"
)
class AclOperationTypes(enum.Enum):
    UNKNOWN = "UNKNOWN"
    ANY = "ANY"
    ALL = "ALL"
    READ = "READ"
    WRITE = "WRITE"
    CREATE = "CREATE"
    DELETE = "DELETE"
    ALTER = "ALTER"
    DESCRIBE = "DESCRIBE"
    CLUSTER_ACTION = "CLUSTER_ACTION"
    DESCRIBE_CONFIGS = "DESCRIBE_CONFIGS"
    ALTER_CONFIGS = "ALTER_CONFIGS"
    IDEMPOTENT_WRITE = "IDEMPOTENT_WRITE"


@jsii.enum(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.AclPermissionTypes"
)
class AclPermissionTypes(enum.Enum):
    UNKNOWN = "UNKNOWN"
    ANY = "ANY"
    DENY = "DENY"
    ALLOW = "ALLOW"


@jsii.enum(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.AclResourceTypes"
)
class AclResourceTypes(enum.Enum):
    UNKNOWN = "UNKNOWN"
    ANY = "ANY"
    TOPIC = "TOPIC"
    GROUP = "GROUP"
    CLUSTER = "CLUSTER"
    TRANSACTIONAL_ID = "TRANSACTIONAL_ID"
    DELEGATION_TOKEN = "DELEGATION_TOKEN"


@jsii.enum(jsii_type="@cdklabs/aws-data-solutions-framework.streaming.Authentication")
class Authentication(enum.Enum):
    IAM = "IAM"
    MTLS = "MTLS"


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.BrokerLogging",
    jsii_struct_bases=[],
    name_mapping={
        "cloudwatch_log_group": "cloudwatchLogGroup",
        "firehose_delivery_stream_name": "firehoseDeliveryStreamName",
        "s3": "s3",
    },
)
class BrokerLogging:
    def __init__(
        self,
        *,
        cloudwatch_log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        firehose_delivery_stream_name: typing.Optional[builtins.str] = None,
        s3: typing.Optional[typing.Union["S3LoggingConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Configuration details related to broker logs.

        :param cloudwatch_log_group: The CloudWatch Logs group that is the destination for broker logs. Default: - disabled
        :param firehose_delivery_stream_name: The Kinesis Data Firehose delivery stream that is the destination for broker logs. Default: - disabled
        :param s3: Details of the Amazon S3 destination for broker logs. Default: - disabled
        '''
        if isinstance(s3, dict):
            s3 = S3LoggingConfiguration(**s3)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcf29df229d45be6f58cf96f7c79a3fd20c67254205e0d4bf24c15fc1917467f)
            check_type(argname="argument cloudwatch_log_group", value=cloudwatch_log_group, expected_type=type_hints["cloudwatch_log_group"])
            check_type(argname="argument firehose_delivery_stream_name", value=firehose_delivery_stream_name, expected_type=type_hints["firehose_delivery_stream_name"])
            check_type(argname="argument s3", value=s3, expected_type=type_hints["s3"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cloudwatch_log_group is not None:
            self._values["cloudwatch_log_group"] = cloudwatch_log_group
        if firehose_delivery_stream_name is not None:
            self._values["firehose_delivery_stream_name"] = firehose_delivery_stream_name
        if s3 is not None:
            self._values["s3"] = s3

    @builtins.property
    def cloudwatch_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The CloudWatch Logs group that is the destination for broker logs.

        :default: - disabled
        '''
        result = self._values.get("cloudwatch_log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

    @builtins.property
    def firehose_delivery_stream_name(self) -> typing.Optional[builtins.str]:
        '''The Kinesis Data Firehose delivery stream that is the destination for broker logs.

        :default: - disabled
        '''
        result = self._values.get("firehose_delivery_stream_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3(self) -> typing.Optional["S3LoggingConfiguration"]:
        '''Details of the Amazon S3 destination for broker logs.

        :default: - disabled
        '''
        result = self._values.get("s3")
        return typing.cast(typing.Optional["S3LoggingConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BrokerLogging(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ClientAuthentication(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.ClientAuthentication",
):
    '''Configuration properties for client authentication.'''

    @jsii.member(jsii_name="sasl")
    @builtins.classmethod
    def sasl(
        cls,
        *,
        iam: typing.Optional[builtins.bool] = None,
    ) -> "ClientAuthentication":
        '''SASL authentication.

        :param iam: Enable IAM access control. Default: - false
        '''
        props = SaslAuthProps(iam=iam)

        return typing.cast("ClientAuthentication", jsii.sinvoke(cls, "sasl", [props]))

    @jsii.member(jsii_name="saslTls")
    @builtins.classmethod
    def sasl_tls(
        cls,
        *,
        iam: typing.Optional[builtins.bool] = None,
        certificate_authorities: typing.Optional[typing.Sequence[_aws_cdk_aws_acmpca_ceddda9d.ICertificateAuthority]] = None,
    ) -> "ClientAuthentication":
        '''SASL + TLS authentication.

        :param iam: Enable IAM access control. Default: - false
        :param certificate_authorities: List of ACM Certificate Authorities to enable TLS authentication. Default: - none
        '''
        sasl_tls_props = SaslTlsAuthProps(
            iam=iam, certificate_authorities=certificate_authorities
        )

        return typing.cast("ClientAuthentication", jsii.sinvoke(cls, "saslTls", [sasl_tls_props]))

    @jsii.member(jsii_name="tls")
    @builtins.classmethod
    def tls(
        cls,
        *,
        certificate_authorities: typing.Optional[typing.Sequence[_aws_cdk_aws_acmpca_ceddda9d.ICertificateAuthority]] = None,
    ) -> "ClientAuthentication":
        '''TLS authentication.

        :param certificate_authorities: List of ACM Certificate Authorities to enable TLS authentication. Default: - none
        '''
        props = TlsAuthProps(certificate_authorities=certificate_authorities)

        return typing.cast("ClientAuthentication", jsii.sinvoke(cls, "tls", [props]))

    @builtins.property
    @jsii.member(jsii_name="saslProps")
    def sasl_props(self) -> typing.Optional["SaslAuthProps"]:
        '''- properties for SASL authentication.'''
        return typing.cast(typing.Optional["SaslAuthProps"], jsii.get(self, "saslProps"))

    @builtins.property
    @jsii.member(jsii_name="tlsProps")
    def tls_props(self) -> typing.Optional["TlsAuthProps"]:
        '''- properties for TLS authentication.'''
        return typing.cast(typing.Optional["TlsAuthProps"], jsii.get(self, "tlsProps"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.ClusterConfigurationInfo",
    jsii_struct_bases=[],
    name_mapping={"arn": "arn", "revision": "revision"},
)
class ClusterConfigurationInfo:
    def __init__(self, *, arn: builtins.str, revision: jsii.Number) -> None:
        '''The Amazon MSK configuration to use for the cluster.

        Note: There is currently no Cloudformation Resource to create a Configuration

        :param arn: The Amazon Resource Name (ARN) of the MSK configuration to use. For example, arn:aws:kafka:us-east-1:123456789012:configuration/example-configuration-name/abcdabcd-1234-abcd-1234-abcd123e8e8e-1.
        :param revision: The revision of the Amazon MSK configuration to use.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3836211b99f5c6335752911fac90a01a7d51a80694071ca21e83d6ed9e4ccd6e)
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
            check_type(argname="argument revision", value=revision, expected_type=type_hints["revision"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "arn": arn,
            "revision": revision,
        }

    @builtins.property
    def arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the MSK configuration to use.

        For example, arn:aws:kafka:us-east-1:123456789012:configuration/example-configuration-name/abcdabcd-1234-abcd-1234-abcd123e8e8e-1.
        '''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def revision(self) -> jsii.Number:
        '''The revision of the Amazon MSK configuration to use.'''
        result = self._values.get("revision")
        assert result is not None, "Required property 'revision' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterConfigurationInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.ClusterMonitoringLevel"
)
class ClusterMonitoringLevel(enum.Enum):
    '''The level of monitoring for the MSK cluster.

    :see: https://docs.aws.amazon.com/msk/latest/developerguide/monitoring.html#metrics-details
    '''

    DEFAULT = "DEFAULT"
    '''Default metrics are the essential metrics to monitor.'''
    PER_BROKER = "PER_BROKER"
    '''Per Broker metrics give you metrics at the broker level.'''
    PER_TOPIC_PER_BROKER = "PER_TOPIC_PER_BROKER"
    '''Per Topic Per Broker metrics help you understand volume at the topic level.'''
    PER_TOPIC_PER_PARTITION = "PER_TOPIC_PER_PARTITION"
    '''Per Topic Per Partition metrics help you understand consumer group lag at the topic partition level.'''


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.EbsStorageInfo",
    jsii_struct_bases=[],
    name_mapping={"encryption_key": "encryptionKey", "volume_size": "volumeSize"},
)
class EbsStorageInfo:
    def __init__(
        self,
        *,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        volume_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''EBS volume information.

        :param encryption_key: The AWS KMS key for encrypting data at rest. Default: Uses AWS managed CMK (aws/kafka)
        :param volume_size: The size in GiB of the EBS volume for the data drive on each broker node. Default: 1000
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3425efae5f0d6400892f5926740e3aa84485ca386ae41ba733ecaca3e0d2825d)
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument volume_size", value=volume_size, expected_type=type_hints["volume_size"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if volume_size is not None:
            self._values["volume_size"] = volume_size

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The AWS KMS key for encrypting data at rest.

        :default: Uses AWS managed CMK (aws/kafka)
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def volume_size(self) -> typing.Optional[jsii.Number]:
        '''The size in GiB of the EBS volume for the data drive on each broker node.

        :default: 1000
        '''
        result = self._values.get("volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EbsStorageInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KafkaApi(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.KafkaApi",
):
    '''A construct to create a Kafka API admin client.

    :see: https://awslabs.github.io/data-solutions-framework-on-aws/
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        broker_security_group: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
        client_authentication: ClientAuthentication,
        cluster_arn: builtins.str,
        cluster_type: "MskClusterType",
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        certficate_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        environment_encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        iam_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        kafka_client_log_level: typing.Optional["KafkaClientLogLevel"] = None,
        mtls_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        service_token: typing.Optional[builtins.str] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Constructs a new instance of the Kafka API construct.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param broker_security_group: The AWS security groups to associate with the elastic network interfaces in order to specify who can connect to and communicate with the Amazon MSK cluster.
        :param client_authentication: Configuration properties for client authentication. MSK supports using private TLS certificates or SASL/SCRAM to authenticate the identity of clients.
        :param cluster_arn: The ARN of the cluster.
        :param cluster_type: The type of MSK cluster(provisioned or serverless).
        :param vpc: Defines the virtual networking environment for this cluster. Must have at least 2 subnets in two different AZs.
        :param certficate_secret: This is the TLS certificate of the Principal that is used by the CDK custom resource which set ACLs and Topics. It must be provided if the cluster is using mTLS authentication. The secret in AWS secrets manager must be a JSON in the following format { "key" : "PRIVATE-KEY", "cert" : "CERTIFICATE" } You can use the following utility to generate the certificates https://github.com/aws-samples/amazon-msk-client-authentication
        :param environment_encryption: The AWS KMS key to use to encrypt enviornment variable of lambda supporting the MSK Custom Resources creation.
        :param iam_handler_role: The IAM role to pass to IAM authentication lambda handler This role must be able to be assumed with ``lambda.amazonaws.com`` service principal.
        :param kafka_client_log_level: The log level for the lambda that support the Custom Resource for both Managing ACLs and Topics. Default: WARN
        :param mtls_handler_role: The IAM role to pass to mTLS lambda handler This role must be able to be assumed with ``lambda.amazonaws.com`` service principal.
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param service_token: If there is an already existing service token deployed for the custom resource you can reuse it to reduce the number of resource created.
        :param subnets: The subnets where the Custom Resource Lambda Function would be created in. Default: - One private subnet with egress is used per AZ.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11acb7f10ba2c540e3c133ed7f79f6ef73b1fa3e856e07fb966b40a1ffd34dc4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = KafkaApiProps(
            broker_security_group=broker_security_group,
            client_authentication=client_authentication,
            cluster_arn=cluster_arn,
            cluster_type=cluster_type,
            vpc=vpc,
            certficate_secret=certficate_secret,
            environment_encryption=environment_encryption,
            iam_handler_role=iam_handler_role,
            kafka_client_log_level=kafka_client_log_level,
            mtls_handler_role=mtls_handler_role,
            removal_policy=removal_policy,
            service_token=service_token,
            subnets=subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="grantConsume")
    def grant_consume(
        self,
        id: builtins.str,
        topic_name: builtins.str,
        client_authentication: Authentication,
        principal: typing.Union[builtins.str, _aws_cdk_aws_iam_ceddda9d.IPrincipal],
        host: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        custom_resource_authentication: typing.Optional[Authentication] = None,
    ) -> typing.Optional[_aws_cdk_ceddda9d.CustomResource]:
        '''Grant a principal permissions to consume from a topic.

        :param id: the CDK resource ID.
        :param topic_name: the target topic to grant consume permissions on.
        :param client_authentication: The authentication mode of the consumer.
        :param principal: the principal receiveing grant consume permissions.
        :param host: the host of the consumer.
        :param removal_policy: the removal policy to apply to the grant.
        :param custom_resource_authentication: The authentication used by the Kafka API admin client to create the ACL.

        :default: - clientAuthentication (same authentication as the target producer)

        :return: The MskAcl custom resource for MTLS clientAuthentication. Nothing for IAM clientAuthentication
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b17087c46184134a6bdd689601d720ab914b7b56ad32b934fcad3f4c51f29dd0)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument topic_name", value=topic_name, expected_type=type_hints["topic_name"])
            check_type(argname="argument client_authentication", value=client_authentication, expected_type=type_hints["client_authentication"])
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument custom_resource_authentication", value=custom_resource_authentication, expected_type=type_hints["custom_resource_authentication"])
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.CustomResource], jsii.invoke(self, "grantConsume", [id, topic_name, client_authentication, principal, host, removal_policy, custom_resource_authentication]))

    @jsii.member(jsii_name="grantProduce")
    def grant_produce(
        self,
        id: builtins.str,
        topic_name: builtins.str,
        client_authentication: Authentication,
        principal: typing.Union[builtins.str, _aws_cdk_aws_iam_ceddda9d.IPrincipal],
        host: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        custom_resource_authentication: typing.Optional[Authentication] = None,
    ) -> typing.Optional[_aws_cdk_ceddda9d.CustomResource]:
        '''Grant a principal permissions to produce to a topic.

        :param id: the CDK resource ID.
        :param topic_name: the target topic to grant produce permissions on.
        :param client_authentication: The authentication mode of the producer.
        :param principal: the principal receiving grant produce permissions.
        :param host: the host of the producer.
        :param removal_policy: the removal policy to apply to the grant.
        :param custom_resource_authentication: The authentication used by the Kafka API admin client to create the ACL.

        :default: - clientAuthentication (same authentication as the target producer)

        :return: The MskAcl custom resource for MTLS clientAuthentication. Nothing for IAM clientAuthentication
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c253515c374085f1ae8c19e0362e4924e1a2b781d754123dce2804908888e67)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument topic_name", value=topic_name, expected_type=type_hints["topic_name"])
            check_type(argname="argument client_authentication", value=client_authentication, expected_type=type_hints["client_authentication"])
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument custom_resource_authentication", value=custom_resource_authentication, expected_type=type_hints["custom_resource_authentication"])
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.CustomResource], jsii.invoke(self, "grantProduce", [id, topic_name, client_authentication, principal, host, removal_policy, custom_resource_authentication]))

    @jsii.member(jsii_name="retrieveVersion")
    def retrieve_version(self) -> typing.Any:
        '''Retrieve DSF package.json version.'''
        return typing.cast(typing.Any, jsii.invoke(self, "retrieveVersion", []))

    @jsii.member(jsii_name="setAcl")
    def set_acl(
        self,
        id: builtins.str,
        acl_definition: typing.Union[Acl, typing.Dict[builtins.str, typing.Any]],
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        client_authentication: typing.Optional[Authentication] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Creates a ACL in the MSK Cluster.

        :param id: the CDK ID of the ACL.
        :param acl_definition: the Kafka ACL definition.
        :param removal_policy: Wether to keep the ACL or delete it when removing the resource from the Stack.
        :param client_authentication: The authentication used by the Kafka API admin client to create the ACL.

        :default: - Authentication.MTLS

        :return: The MskAcl custom resource created by the Kafka API admin client
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d1c462aeb2582babda671003a454ea0e7a7fec802c2e877a39480d04de2a004)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument acl_definition", value=acl_definition, expected_type=type_hints["acl_definition"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument client_authentication", value=client_authentication, expected_type=type_hints["client_authentication"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "setAcl", [id, acl_definition, removal_policy, client_authentication]))

    @jsii.member(jsii_name="setTopic")
    def set_topic(
        self,
        id: builtins.str,
        client_authentication: Authentication,
        topic_definition: typing.Union["MskTopic", typing.Dict[builtins.str, typing.Any]],
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        wait_for_leaders: typing.Optional[builtins.bool] = None,
        timeout: typing.Optional[jsii.Number] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Creates a topic in the MSK Cluster.

        :param id: the CDK ID for Topic.
        :param client_authentication: The authentication used by the Kafka API admin client to create the topic.
        :param topic_definition: the Kafka topic definition.
        :param removal_policy: Wether to keep the topic or delete it when removing the resource from the Stack.
        :param wait_for_leaders: If set to true, waits until metadata for the new topics doesn't throw LEADER_NOT_AVAILABLE.
        :param timeout: The time in ms to wait for a topic to be completely created on the controller node.

        :default: - 5000

        :return: The MskTopic custom resource created by the Kafka API admin client
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0906adf996cc3e4500527d7cc602db45099025693a3968a806f5ecab7596d1bf)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument client_authentication", value=client_authentication, expected_type=type_hints["client_authentication"])
            check_type(argname="argument topic_definition", value=topic_definition, expected_type=type_hints["topic_definition"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument wait_for_leaders", value=wait_for_leaders, expected_type=type_hints["wait_for_leaders"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "setTopic", [id, client_authentication, topic_definition, removal_policy, wait_for_leaders, timeout]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_OWNED_TAG")
    def DSF_OWNED_TAG(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_OWNED_TAG"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_TRACKING_CODE")
    def DSF_TRACKING_CODE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_TRACKING_CODE"))

    @builtins.property
    @jsii.member(jsii_name="mskAclFunction")
    def msk_acl_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        '''The Lambda function used by the Custom Resource provider when MSK is using mTLS authentication.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], jsii.get(self, "mskAclFunction"))

    @builtins.property
    @jsii.member(jsii_name="mskAclLogGroup")
    def msk_acl_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The Cloudwatch Log Group used by the Custom Resource provider when MSK is using mTLS authentication.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "mskAclLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="mskAclRole")
    def msk_acl_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used by the Custom Resource provider when MSK is using mTLS authentication.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "mskAclRole"))

    @builtins.property
    @jsii.member(jsii_name="mskAclSecurityGroup")
    def msk_acl_security_group(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The Security Group used by the Custom Resource provider when MSK is using mTLS authentication.'''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], jsii.get(self, "mskAclSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="mskIamFunction")
    def msk_iam_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        '''The Lambda function used by the Custom Resource provider when MSK is using IAM authentication.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], jsii.get(self, "mskIamFunction"))

    @builtins.property
    @jsii.member(jsii_name="mskIamLogGroup")
    def msk_iam_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The Cloudwatch Log Group used by the Custom Resource provider when MSK is using IAM authentication.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "mskIamLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="mskIamRole")
    def msk_iam_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used by the Custom Resource provider when MSK is using IAM authentication.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "mskIamRole"))

    @builtins.property
    @jsii.member(jsii_name="mskIamSecurityGroup")
    def msk_iam_security_group(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The Security Group used by the Custom Resource provider when MSK is using IAM authentication.'''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], jsii.get(self, "mskIamSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> typing.Optional[builtins.str]:
        '''If there is an already existing service token deployed for the custom resource you can reuse it to reduce the number of resource created.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceToken"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.KafkaApiProps",
    jsii_struct_bases=[],
    name_mapping={
        "broker_security_group": "brokerSecurityGroup",
        "client_authentication": "clientAuthentication",
        "cluster_arn": "clusterArn",
        "cluster_type": "clusterType",
        "vpc": "vpc",
        "certficate_secret": "certficateSecret",
        "environment_encryption": "environmentEncryption",
        "iam_handler_role": "iamHandlerRole",
        "kafka_client_log_level": "kafkaClientLogLevel",
        "mtls_handler_role": "mtlsHandlerRole",
        "removal_policy": "removalPolicy",
        "service_token": "serviceToken",
        "subnets": "subnets",
    },
)
class KafkaApiProps:
    def __init__(
        self,
        *,
        broker_security_group: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
        client_authentication: ClientAuthentication,
        cluster_arn: builtins.str,
        cluster_type: "MskClusterType",
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        certficate_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        environment_encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        iam_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        kafka_client_log_level: typing.Optional["KafkaClientLogLevel"] = None,
        mtls_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        service_token: typing.Optional[builtins.str] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Properties for the ``KafkaApi`` construct.

        :param broker_security_group: The AWS security groups to associate with the elastic network interfaces in order to specify who can connect to and communicate with the Amazon MSK cluster.
        :param client_authentication: Configuration properties for client authentication. MSK supports using private TLS certificates or SASL/SCRAM to authenticate the identity of clients.
        :param cluster_arn: The ARN of the cluster.
        :param cluster_type: The type of MSK cluster(provisioned or serverless).
        :param vpc: Defines the virtual networking environment for this cluster. Must have at least 2 subnets in two different AZs.
        :param certficate_secret: This is the TLS certificate of the Principal that is used by the CDK custom resource which set ACLs and Topics. It must be provided if the cluster is using mTLS authentication. The secret in AWS secrets manager must be a JSON in the following format { "key" : "PRIVATE-KEY", "cert" : "CERTIFICATE" } You can use the following utility to generate the certificates https://github.com/aws-samples/amazon-msk-client-authentication
        :param environment_encryption: The AWS KMS key to use to encrypt enviornment variable of lambda supporting the MSK Custom Resources creation.
        :param iam_handler_role: The IAM role to pass to IAM authentication lambda handler This role must be able to be assumed with ``lambda.amazonaws.com`` service principal.
        :param kafka_client_log_level: The log level for the lambda that support the Custom Resource for both Managing ACLs and Topics. Default: WARN
        :param mtls_handler_role: The IAM role to pass to mTLS lambda handler This role must be able to be assumed with ``lambda.amazonaws.com`` service principal.
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param service_token: If there is an already existing service token deployed for the custom resource you can reuse it to reduce the number of resource created.
        :param subnets: The subnets where the Custom Resource Lambda Function would be created in. Default: - One private subnet with egress is used per AZ.
        '''
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8aa63759ad33545334567b3e848b5b426d5233e0f36e975fdd69080066c10ef2)
            check_type(argname="argument broker_security_group", value=broker_security_group, expected_type=type_hints["broker_security_group"])
            check_type(argname="argument client_authentication", value=client_authentication, expected_type=type_hints["client_authentication"])
            check_type(argname="argument cluster_arn", value=cluster_arn, expected_type=type_hints["cluster_arn"])
            check_type(argname="argument cluster_type", value=cluster_type, expected_type=type_hints["cluster_type"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument certficate_secret", value=certficate_secret, expected_type=type_hints["certficate_secret"])
            check_type(argname="argument environment_encryption", value=environment_encryption, expected_type=type_hints["environment_encryption"])
            check_type(argname="argument iam_handler_role", value=iam_handler_role, expected_type=type_hints["iam_handler_role"])
            check_type(argname="argument kafka_client_log_level", value=kafka_client_log_level, expected_type=type_hints["kafka_client_log_level"])
            check_type(argname="argument mtls_handler_role", value=mtls_handler_role, expected_type=type_hints["mtls_handler_role"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument service_token", value=service_token, expected_type=type_hints["service_token"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "broker_security_group": broker_security_group,
            "client_authentication": client_authentication,
            "cluster_arn": cluster_arn,
            "cluster_type": cluster_type,
            "vpc": vpc,
        }
        if certficate_secret is not None:
            self._values["certficate_secret"] = certficate_secret
        if environment_encryption is not None:
            self._values["environment_encryption"] = environment_encryption
        if iam_handler_role is not None:
            self._values["iam_handler_role"] = iam_handler_role
        if kafka_client_log_level is not None:
            self._values["kafka_client_log_level"] = kafka_client_log_level
        if mtls_handler_role is not None:
            self._values["mtls_handler_role"] = mtls_handler_role
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if service_token is not None:
            self._values["service_token"] = service_token
        if subnets is not None:
            self._values["subnets"] = subnets

    @builtins.property
    def broker_security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        '''The AWS security groups to associate with the elastic network interfaces in order to specify who can connect to and communicate with the Amazon MSK cluster.'''
        result = self._values.get("broker_security_group")
        assert result is not None, "Required property 'broker_security_group' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, result)

    @builtins.property
    def client_authentication(self) -> ClientAuthentication:
        '''Configuration properties for client authentication.

        MSK supports using private TLS certificates or SASL/SCRAM to authenticate the identity of clients.
        '''
        result = self._values.get("client_authentication")
        assert result is not None, "Required property 'client_authentication' is missing"
        return typing.cast(ClientAuthentication, result)

    @builtins.property
    def cluster_arn(self) -> builtins.str:
        '''The ARN of the cluster.'''
        result = self._values.get("cluster_arn")
        assert result is not None, "Required property 'cluster_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cluster_type(self) -> "MskClusterType":
        '''The type of MSK cluster(provisioned or serverless).'''
        result = self._values.get("cluster_type")
        assert result is not None, "Required property 'cluster_type' is missing"
        return typing.cast("MskClusterType", result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''Defines the virtual networking environment for this cluster.

        Must have at least 2 subnets in two different AZs.
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def certficate_secret(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        '''This is the TLS certificate of the Principal that is used by the CDK custom resource which set ACLs and Topics.

        It must be provided if the cluster is using mTLS authentication.
        The secret in AWS secrets manager must be a JSON in the following format
        {
        "key" : "PRIVATE-KEY",
        "cert" : "CERTIFICATE"
        }

        You can use the following utility to generate the certificates
        https://github.com/aws-samples/amazon-msk-client-authentication
        '''
        result = self._values.get("certficate_secret")
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], result)

    @builtins.property
    def environment_encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The AWS KMS key to use to encrypt  enviornment variable of lambda supporting the MSK Custom Resources creation.'''
        result = self._values.get("environment_encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def iam_handler_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role to pass to IAM authentication lambda handler This role must be able to be assumed with ``lambda.amazonaws.com`` service principal.'''
        result = self._values.get("iam_handler_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def kafka_client_log_level(self) -> typing.Optional["KafkaClientLogLevel"]:
        '''The log level for the lambda that support the Custom Resource for both Managing ACLs and Topics.

        :default: WARN
        '''
        result = self._values.get("kafka_client_log_level")
        return typing.cast(typing.Optional["KafkaClientLogLevel"], result)

    @builtins.property
    def mtls_handler_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role to pass to mTLS lambda handler This role must be able to be assumed with ``lambda.amazonaws.com`` service principal.'''
        result = self._values.get("mtls_handler_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def service_token(self) -> typing.Optional[builtins.str]:
        '''If there is an already existing service token deployed for the custom resource you can reuse it to reduce the number of resource created.'''
        result = self._values.get("service_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The subnets where the Custom Resource Lambda Function would be created in.

        :default: - One private subnet with egress is used per AZ.
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KafkaApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.KafkaClientLogLevel"
)
class KafkaClientLogLevel(enum.Enum):
    '''The CDK Custom resources uses KafkaJs.

    This enum allow you to set the log level
    '''

    WARN = "WARN"
    DEBUG = "DEBUG"
    INFO = "INFO"
    ERROR = "ERROR"


class KafkaVersion(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.KafkaVersion",
):
    '''Kafka cluster version.'''

    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, version: builtins.str) -> "KafkaVersion":
        '''Custom cluster version.

        :param version: custom version number.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0e8e81d0dac96cf7234f1a61b30d53c9a3d1a4d97fb2c0e99ddf481ddfdef08)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        return typing.cast("KafkaVersion", jsii.sinvoke(cls, "of", [version]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V1_1_1")
    def V1_1_1(cls) -> "KafkaVersion":
        '''(deprecated) **Deprecated by Amazon MSK. You can't create a Kafka cluster with a deprecated version.**.

        Kafka version 1.1.1

        :deprecated: use the latest runtime instead

        :stability: deprecated
        '''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V1_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_2_1")
    def V2_2_1(cls) -> "KafkaVersion":
        '''Kafka version 2.2.1.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_3_1")
    def V2_3_1(cls) -> "KafkaVersion":
        '''Kafka version 2.3.1.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_3_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_4_1_1")
    def V2_4_1_1(cls) -> "KafkaVersion":
        '''Kafka version 2.4.1.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_4_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_5_1")
    def V2_5_1(cls) -> "KafkaVersion":
        '''Kafka version 2.5.1.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_5_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_6_0")
    def V2_6_0(cls) -> "KafkaVersion":
        '''Kafka version 2.6.0.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_6_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_6_1")
    def V2_6_1(cls) -> "KafkaVersion":
        '''Kafka version 2.6.1.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_6_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_6_2")
    def V2_6_2(cls) -> "KafkaVersion":
        '''Kafka version 2.6.2.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_6_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_6_3")
    def V2_6_3(cls) -> "KafkaVersion":
        '''Kafka version 2.6.3.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_6_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_7_0")
    def V2_7_0(cls) -> "KafkaVersion":
        '''Kafka version 2.7.0.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_7_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_7_1")
    def V2_7_1(cls) -> "KafkaVersion":
        '''Kafka version 2.7.1.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_7_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_7_2")
    def V2_7_2(cls) -> "KafkaVersion":
        '''Kafka version 2.7.2.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_7_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_8_0")
    def V2_8_0(cls) -> "KafkaVersion":
        '''Kafka version 2.8.0.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_8_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_8_1")
    def V2_8_1(cls) -> "KafkaVersion":
        '''Kafka version 2.8.1.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_8_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_8_2_TIERED")
    def V2_8_2_TIERED(cls) -> "KafkaVersion":
        '''AWS MSK Kafka version 2.8.2.tiered.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_8_2_TIERED"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3_1_1")
    def V3_1_1(cls) -> "KafkaVersion":
        '''Kafka version 3.1.1.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V3_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3_2_0")
    def V3_2_0(cls) -> "KafkaVersion":
        '''Kafka version 3.2.0.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V3_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3_3_1")
    def V3_3_1(cls) -> "KafkaVersion":
        '''Kafka version 3.3.1.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V3_3_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3_3_2")
    def V3_3_2(cls) -> "KafkaVersion":
        '''Kafka version 3.3.2.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V3_3_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3_4_0")
    def V3_4_0(cls) -> "KafkaVersion":
        '''Kafka version 3.4.0.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V3_4_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3_5_1")
    def V3_5_1(cls) -> "KafkaVersion":
        '''Kafka version 3.5.1.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V3_5_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3_6_0")
    def V3_6_0(cls) -> "KafkaVersion":
        '''Kafka version 3.6.0.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V3_6_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3_7_X")
    def V3_7_X(cls) -> "KafkaVersion":
        '''Kafka version 3.7.x.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V3_7_X"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3_7_X_KRAFT")
    def V3_7_X_KRAFT(cls) -> "KafkaVersion":
        '''Kafka version 3.7.x.kraft.'''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V3_7_X_KRAFT"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''cluster version number.'''
        return typing.cast(builtins.str, jsii.get(self, "version"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.MonitoringConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_monitoring_level": "clusterMonitoringLevel",
        "enable_prometheus_jmx_exporter": "enablePrometheusJmxExporter",
        "enable_prometheus_node_exporter": "enablePrometheusNodeExporter",
    },
)
class MonitoringConfiguration:
    def __init__(
        self,
        *,
        cluster_monitoring_level: typing.Optional[ClusterMonitoringLevel] = None,
        enable_prometheus_jmx_exporter: typing.Optional[builtins.bool] = None,
        enable_prometheus_node_exporter: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Monitoring Configuration.

        :param cluster_monitoring_level: Specifies the level of monitoring for the MSK cluster. Default: DEFAULT
        :param enable_prometheus_jmx_exporter: Indicates whether you want to enable or disable the JMX Exporter. Default: false
        :param enable_prometheus_node_exporter: Indicates whether you want to enable or disable the Prometheus Node Exporter. You can use the Prometheus Node Exporter to get CPU and disk metrics for the broker nodes. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2cbd7fca2428428959aa1e6b26222a5eda1ac49ca65e935d98c608d20e95b2a)
            check_type(argname="argument cluster_monitoring_level", value=cluster_monitoring_level, expected_type=type_hints["cluster_monitoring_level"])
            check_type(argname="argument enable_prometheus_jmx_exporter", value=enable_prometheus_jmx_exporter, expected_type=type_hints["enable_prometheus_jmx_exporter"])
            check_type(argname="argument enable_prometheus_node_exporter", value=enable_prometheus_node_exporter, expected_type=type_hints["enable_prometheus_node_exporter"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cluster_monitoring_level is not None:
            self._values["cluster_monitoring_level"] = cluster_monitoring_level
        if enable_prometheus_jmx_exporter is not None:
            self._values["enable_prometheus_jmx_exporter"] = enable_prometheus_jmx_exporter
        if enable_prometheus_node_exporter is not None:
            self._values["enable_prometheus_node_exporter"] = enable_prometheus_node_exporter

    @builtins.property
    def cluster_monitoring_level(self) -> typing.Optional[ClusterMonitoringLevel]:
        '''Specifies the level of monitoring for the MSK cluster.

        :default: DEFAULT
        '''
        result = self._values.get("cluster_monitoring_level")
        return typing.cast(typing.Optional[ClusterMonitoringLevel], result)

    @builtins.property
    def enable_prometheus_jmx_exporter(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether you want to enable or disable the JMX Exporter.

        :default: false
        '''
        result = self._values.get("enable_prometheus_jmx_exporter")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_prometheus_node_exporter(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether you want to enable or disable the Prometheus Node Exporter.

        You can use the Prometheus Node Exporter to get CPU and disk metrics for the broker nodes.

        :default: false
        '''
        result = self._values.get("enable_prometheus_node_exporter")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MonitoringConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskBrokerInstanceType(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.MskBrokerInstanceType",
):
    '''Kafka cluster version.'''

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_M5_12XLARGE")
    def KAFKA_M5_12_XLARGE(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.m5.12xlarge.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_M5_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_M5_16XLARGE")
    def KAFKA_M5_16_XLARGE(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.m5.16xlarge.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_M5_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_M5_24XLARGE")
    def KAFKA_M5_24_XLARGE(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.m5.24xlarge.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_M5_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_M5_2XLARGE")
    def KAFKA_M5_2_XLARGE(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.m5.2xlarge.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_M5_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_M5_4XLARGE")
    def KAFKA_M5_4_XLARGE(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.m5.4xlarge.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_M5_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_M5_8XLARGE")
    def KAFKA_M5_8_XLARGE(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.m5.8xlarge.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_M5_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_M5_LARGE")
    def KAFKA_M5_LARGE(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.m5.large.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_M5_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_M5_XLARGE")
    def KAFKA_M5_XLARGE(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.m5.xlarge.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_M5_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_M7G_12XLARGE")
    def KAFKA_M7_G_12_XLARGE(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.m7g.12xlarge.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_M7G_12XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_M7G_16XLARGE")
    def KAFKA_M7_G_16_XLARGE(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.m7g.16xlarge.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_M7G_16XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_M7G_24XLARGE")
    def KAFKA_M7_G_24_XLARGE(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.m7g.24xlarge.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_M7G_24XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_M7G_2XLARGE")
    def KAFKA_M7_G_2_XLARGE(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.m7g.2xlarge.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_M7G_2XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_M7G_4XLARGE")
    def KAFKA_M7_G_4_XLARGE(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.m7g.4xlarge.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_M7G_4XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_M7G_8XLARGE")
    def KAFKA_M7_G_8_XLARGE(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.m7g.8xlarge.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_M7G_8XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_M7G_LARGE")
    def KAFKA_M7_G_LARGE(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.m7g.large.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_M7G_LARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_M7G_XLARGE")
    def KAFKA_M7_G_XLARGE(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.m7g.xlarge.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_M7G_XLARGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="KAFKA_T3_SMALL")
    def KAFKA_T3_SMALL(cls) -> "MskBrokerInstanceType":
        '''Borker instance type kafka.t3.small.'''
        return typing.cast("MskBrokerInstanceType", jsii.sget(cls, "KAFKA_T3_SMALL"))

    @builtins.property
    @jsii.member(jsii_name="instance")
    def instance(self) -> _aws_cdk_aws_ec2_ceddda9d.InstanceType:
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InstanceType, jsii.get(self, "instance"))


@jsii.enum(jsii_type="@cdklabs/aws-data-solutions-framework.streaming.MskClusterType")
class MskClusterType(enum.Enum):
    '''Enum for MSK cluster types.'''

    PROVISIONED = "PROVISIONED"
    SERVERLESS = "SERVERLESS"


class MskProvisioned(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.MskProvisioned",
):
    '''A construct to create an MSK Provisioned cluster.

    :see: https://awslabs.github.io/data-solutions-framework-on-aws/

    Example::

        msk = dsf.streaming.MskProvisioned(self, "cluster")
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        allow_everyone_if_no_acl_found: typing.Optional[builtins.bool] = None,
        broker_instance_type: typing.Optional[MskBrokerInstanceType] = None,
        broker_number: typing.Optional[jsii.Number] = None,
        certificate_definition: typing.Optional[typing.Union[AclAdminProps, typing.Dict[builtins.str, typing.Any]]] = None,
        client_authentication: typing.Optional[ClientAuthentication] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        configuration: typing.Optional[typing.Union[ClusterConfigurationInfo, typing.Dict[builtins.str, typing.Any]]] = None,
        current_version: typing.Optional[builtins.str] = None,
        ebs_storage: typing.Optional[typing.Union[EbsStorageInfo, typing.Dict[builtins.str, typing.Any]]] = None,
        environment_encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        kafka_client_log_level: typing.Optional[KafkaClientLogLevel] = None,
        kafka_version: typing.Optional[KafkaVersion] = None,
        logging: typing.Optional[typing.Union[BrokerLogging, typing.Dict[builtins.str, typing.Any]]] = None,
        monitoring: typing.Optional[typing.Union[MonitoringConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        place_cluster_handler_in_vpc: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        storage_mode: typing.Optional["StorageMode"] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_connectivity: typing.Optional["VpcClientAuthentication"] = None,
    ) -> None:
        '''Constructs a new instance of the MSK Provisioned cluster construct.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param allow_everyone_if_no_acl_found: if set the to true the following Kafka configuration ``allow.everyone.if.no.acl.found`` is set to true. When no Cluster Configuration is passed The construct create a cluster configuration and set the following configuration to false and apply it to the cluster. Default: - false
        :param broker_instance_type: The EC2 instance type that you want Amazon MSK to use when it creates your brokers. Default: kafka.m5.large
        :param broker_number: The number of Apache Kafka brokers deployed. It must be a multiple of the number of availability zones. Default: - 1 per availability zone.
        :param certificate_definition: This Props allow you to define the principals that will be adminstartor as well as the principal that will be used by the CDK Custom resources to.
        :param client_authentication: Configuration properties for client authentication. MSK supports using private TLS certificates or SASL/SCRAM to authenticate the identity of clients. Default: - IAM is used
        :param cluster_name: The name of the MSK provisioned cluster. Default: - default-msk-provisioned
        :param configuration: The Amazon MSK configuration to use for the cluster. Default: - none
        :param current_version: This parameter is required after executing the first ``cdk deploy`` It is the version of the MSK cluster that was deployed in the previous ``cdk deploy`` The cluster might fail in the subsequent updates if it is not set This parameter is obtained by running the following command ``aws kafka describe-cluster --cluster-arn YOUR_CLUSTER_ARN``.
        :param ebs_storage: Information about storage volumes attached to MSK broker nodes. Default: - 100 GiB EBS volume
        :param environment_encryption: The AWS KMS key to use to encrypt the function environment variables.
        :param kafka_client_log_level: The log level for the lambda that support the Custom Resource for both Managing ACLs and Topics. Default: - INFO
        :param kafka_version: The version of Apache Kafka. Default: - KafkaVersion.V3_5_1
        :param logging: Configure your MSK cluster to send broker logs to different destination types. Default: - A Cloudwatch log is created
        :param monitoring: Cluster monitoring configuration. Default: - DEFAULT monitoring level
        :param place_cluster_handler_in_vpc: If set to true, the cluster handler functions will be placed in the private subnets of the cluster vpc.
        :param removal_policy: What to do when this resource is deleted from a stack. Default: - RemovalPolicy.RETAIN
        :param security_groups: The AWS security groups to associate with the elastic network interfaces of the Amazon MSK cluster. Default: - create a new security group
        :param storage_mode: This controls storage mode for supported storage tiers. Default: - StorageMode.LOCAL
        :param subnets: The subnets where to deploy the MSK Provisioned cluster. Amazon MSK distributes the broker nodes evenly across these subnets. The subnets must be in distinct Availability Zones. Client subnets can't be in Availability Zone us-east-1e. Default: - the private subnets with egress.
        :param vpc: The VPC where to deploy the MSK Serverless cluster. Must have at least 2 subnets in two different AZs. Default: - A new VPC is created.
        :param vpc_connectivity: VPC connection control settings for brokers Defines all client authentication information for VpcConnectivity. When vpcConnectivity and you provide your own Msk Congifuration You must set ``allow.everyone.if.no.acl.found`` to ``false``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ca2efff56a789cd1b8df4e44c11ca8c4c57f1cc02116b9c269dcb507fc80d30)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MskProvisionedProps(
            allow_everyone_if_no_acl_found=allow_everyone_if_no_acl_found,
            broker_instance_type=broker_instance_type,
            broker_number=broker_number,
            certificate_definition=certificate_definition,
            client_authentication=client_authentication,
            cluster_name=cluster_name,
            configuration=configuration,
            current_version=current_version,
            ebs_storage=ebs_storage,
            environment_encryption=environment_encryption,
            kafka_client_log_level=kafka_client_log_level,
            kafka_version=kafka_version,
            logging=logging,
            monitoring=monitoring,
            place_cluster_handler_in_vpc=place_cluster_handler_in_vpc,
            removal_policy=removal_policy,
            security_groups=security_groups,
            storage_mode=storage_mode,
            subnets=subnets,
            vpc=vpc,
            vpc_connectivity=vpc_connectivity,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createClusterConfiguration")
    @builtins.classmethod
    def create_cluster_configuration(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
        server_properties_file_path: builtins.str,
        kafka_versions: typing.Optional[typing.Sequence[KafkaVersion]] = None,
        configuration_description: typing.Optional[builtins.str] = None,
        *,
        creation_time: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        revision: typing.Optional[jsii.Number] = None,
    ) -> _aws_cdk_aws_msk_ceddda9d.CfnConfiguration:
        '''
        :param scope: -
        :param id: -
        :param name: -
        :param server_properties_file_path: -
        :param kafka_versions: -
        :param configuration_description: -
        :param creation_time: The time when the configuration revision was created.
        :param description: The description of the configuration revision.
        :param revision: The revision number.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d369ff236b2de65a148f8f832bc5814ae684182e9e28ecd4d772aaeacce4a73e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument server_properties_file_path", value=server_properties_file_path, expected_type=type_hints["server_properties_file_path"])
            check_type(argname="argument kafka_versions", value=kafka_versions, expected_type=type_hints["kafka_versions"])
            check_type(argname="argument configuration_description", value=configuration_description, expected_type=type_hints["configuration_description"])
        latest_revision = _aws_cdk_aws_msk_ceddda9d.CfnConfiguration.LatestRevisionProperty(
            creation_time=creation_time, description=description, revision=revision
        )

        return typing.cast(_aws_cdk_aws_msk_ceddda9d.CfnConfiguration, jsii.sinvoke(cls, "createClusterConfiguration", [scope, id, name, server_properties_file_path, kafka_versions, configuration_description, latest_revision]))

    @jsii.member(jsii_name="addClusterPolicy")
    def add_cluster_policy(
        self,
        policy: _aws_cdk_aws_iam_ceddda9d.PolicyDocument,
        id: builtins.str,
    ) -> _aws_cdk_aws_msk_ceddda9d.CfnClusterPolicy:
        '''Add a cluster policy.

        :param policy: the IAM principal to grand the consume action.
        :param id: the CDK id for the Cluster Policy.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10676524f40fb6031b8159cf669604d3aa0f353edce8387b919edbe6e8964692)
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(_aws_cdk_aws_msk_ceddda9d.CfnClusterPolicy, jsii.invoke(self, "addClusterPolicy", [policy, id]))

    @jsii.member(jsii_name="deleteClusterPolicy")
    def delete_cluster_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "deleteClusterPolicy", []))

    @jsii.member(jsii_name="getBootstrapBrokers")
    def get_bootstrap_brokers(self, authentication: Authentication) -> builtins.str:
        '''Method to get bootstrap broker connection string based on the authentication mode.

        :param authentication: the authentication mode.

        :return: the MSK bootstrap URL
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d63f9e52742d09c41e16f3e104e38fe360fa7eefb1ad98b53fcd4ef441f4fc48)
            check_type(argname="argument authentication", value=authentication, expected_type=type_hints["authentication"])
        return typing.cast(builtins.str, jsii.invoke(self, "getBootstrapBrokers", [authentication]))

    @jsii.member(jsii_name="grantConsume")
    def grant_consume(
        self,
        id: builtins.str,
        topic_name: builtins.str,
        client_authentication: Authentication,
        principal: typing.Union[builtins.str, _aws_cdk_aws_iam_ceddda9d.IPrincipal],
        host: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        custom_resource_authentication: typing.Optional[Authentication] = None,
    ) -> typing.Optional[_aws_cdk_ceddda9d.CustomResource]:
        '''Grant a principal permissions to consume from a topic.

        :param id: the CDK resource ID.
        :param topic_name: the target topic to grant consume permissions on.
        :param client_authentication: The authentication mode of the consumer.
        :param principal: the principal receiveing grant consume permissions.
        :param host: the host of the consumer.
        :param removal_policy: the removal policy to apply to the grant.
        :param custom_resource_authentication: The authentication used by the Kafka API admin client to create the ACL.

        :default: - clientAuthentication (same authentication as the target producer)

        :return: The MskAcl custom resource for MTLS clientAuthentication. Nothing for IAM clientAuthentication
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14864c75a3d144ecd94cedde926f6cfd866bb41f5c6db2d3baf1fa9c82adcc8f)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument topic_name", value=topic_name, expected_type=type_hints["topic_name"])
            check_type(argname="argument client_authentication", value=client_authentication, expected_type=type_hints["client_authentication"])
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument custom_resource_authentication", value=custom_resource_authentication, expected_type=type_hints["custom_resource_authentication"])
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.CustomResource], jsii.invoke(self, "grantConsume", [id, topic_name, client_authentication, principal, host, removal_policy, custom_resource_authentication]))

    @jsii.member(jsii_name="grantProduce")
    def grant_produce(
        self,
        id: builtins.str,
        topic_name: builtins.str,
        client_authentication: Authentication,
        principal: typing.Union[builtins.str, _aws_cdk_aws_iam_ceddda9d.IPrincipal],
        host: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        custom_resource_authentication: typing.Optional[Authentication] = None,
    ) -> typing.Optional[_aws_cdk_ceddda9d.CustomResource]:
        '''Grant a principal permissions to produce to a topic.

        :param id: the CDK resource ID.
        :param topic_name: the target topic to grant produce permissions on.
        :param client_authentication: The authentication mode of the producer.
        :param principal: the principal receiving grant produce permissions.
        :param host: the host of the producer.
        :param removal_policy: the removal policy to apply to the grant.
        :param custom_resource_authentication: The authentication used by the Kafka API admin client to create the ACL.

        :default: - clientAuthentication (same authentication as the target producer)

        :return: The MskAcl custom resource for MTLS clientAuthentication. Nothing for IAM clientAuthentication
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cc63af365e833f5e62cbe4e823f9a183c658c413332b1277411ded29118ad1e)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument topic_name", value=topic_name, expected_type=type_hints["topic_name"])
            check_type(argname="argument client_authentication", value=client_authentication, expected_type=type_hints["client_authentication"])
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument custom_resource_authentication", value=custom_resource_authentication, expected_type=type_hints["custom_resource_authentication"])
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.CustomResource], jsii.invoke(self, "grantProduce", [id, topic_name, client_authentication, principal, host, removal_policy, custom_resource_authentication]))

    @jsii.member(jsii_name="putClusterPolicy")
    def put_cluster_policy(
        self,
        policy: builtins.str,
        id: builtins.str,
        current_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param policy: -
        :param id: -
        :param current_version: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e3702cd56a0669fff2b66b5876666a95e6729262702449992f06699c5278cb2)
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument current_version", value=current_version, expected_type=type_hints["current_version"])
        return typing.cast(None, jsii.invoke(self, "putClusterPolicy", [policy, id, current_version]))

    @jsii.member(jsii_name="retrieveVersion")
    def retrieve_version(self) -> typing.Any:
        '''Retrieve DSF package.json version.'''
        return typing.cast(typing.Any, jsii.invoke(self, "retrieveVersion", []))

    @jsii.member(jsii_name="setAcl")
    def set_acl(
        self,
        id: builtins.str,
        acl_definition: typing.Union[Acl, typing.Dict[builtins.str, typing.Any]],
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        client_authentication: typing.Optional[Authentication] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Creates ACL in the Msk Cluster.

        :param id: the CDK ID of the ACL.
        :param acl_definition: the Kafka Acl definition.
        :param removal_policy: Wether to keep the ACL or delete it when removing the resource from the Stack {@default RemovalPolicy.RETAIN}.
        :param client_authentication: The authentication used by the Kafka API admin client to create the ACL.

        :default: - Authentication.MTLS

        :return: The MskAcl custom resource created by the Kafka API admin client
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14aa4f0e49e9d332484ca339cf959127dc14dbd5782f41d66cabb4e0596724fd)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument acl_definition", value=acl_definition, expected_type=type_hints["acl_definition"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument client_authentication", value=client_authentication, expected_type=type_hints["client_authentication"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "setAcl", [id, acl_definition, removal_policy, client_authentication]))

    @jsii.member(jsii_name="setTopic")
    def set_topic(
        self,
        id: builtins.str,
        client_authentication: Authentication,
        topic_definition: typing.Union["MskTopic", typing.Dict[builtins.str, typing.Any]],
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        wait_for_leaders: typing.Optional[builtins.bool] = None,
        timeout: typing.Optional[jsii.Number] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Creates a topic in the Msk Cluster.

        :param id: the CDK ID of the Topic.
        :param client_authentication: The authentication used by the Kafka API admin client to create the topic.
        :param topic_definition: the Kafka topic definition.
        :param removal_policy: Wether to keep the topic or delete it when removing the resource from the Stack {@default RemovalPolicy.RETAIN}.
        :param wait_for_leaders: If this is true it will wait until metadata for the new topics doesn't throw LEADER_NOT_AVAILABLE.
        :param timeout: The time in ms to wait for a topic to be completely created on the controller node.

        :default: 5000

        :return: The MskTopic custom resource created by the Kafka API admin client
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7fa5e5d3f4a3ee0d52473cab439005e8198dc41d2d4509d5aa81557a4c4142b)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument client_authentication", value=client_authentication, expected_type=type_hints["client_authentication"])
            check_type(argname="argument topic_definition", value=topic_definition, expected_type=type_hints["topic_definition"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument wait_for_leaders", value=wait_for_leaders, expected_type=type_hints["wait_for_leaders"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "setTopic", [id, client_authentication, topic_definition, removal_policy, wait_for_leaders, timeout]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_OWNED_TAG")
    def DSF_OWNED_TAG(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_OWNED_TAG"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_TRACKING_CODE")
    def DSF_TRACKING_CODE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_TRACKING_CODE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MSK_DEFAULT_VERSION")
    def MSK_DEFAULT_VERSION(cls) -> KafkaVersion:
        return typing.cast(KafkaVersion, jsii.sget(cls, "MSK_DEFAULT_VERSION"))

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> _aws_cdk_aws_msk_ceddda9d.CfnCluster:
        '''The MSK cluster created by the construct.'''
        return typing.cast(_aws_cdk_aws_msk_ceddda9d.CfnCluster, jsii.get(self, "cluster"))

    @builtins.property
    @jsii.member(jsii_name="encryptionAtRestKey")
    def encryption_at_rest_key(self) -> _aws_cdk_aws_kms_ceddda9d.IKey:
        '''The KMS CMK key for encrypting data within the cluster.'''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.IKey, jsii.get(self, "encryptionAtRestKey"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC where the MSK cluster is deployed.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="applyConfigurationFunction")
    def apply_configuration_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        '''The Lambda function responsible for applying MSK configuration.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], jsii.get(self, "applyConfigurationFunction"))

    @builtins.property
    @jsii.member(jsii_name="applyConfigurationLogGroup")
    def apply_configuration_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The CloudWatch Log Group used by the Lambda responsible for applying MSK configuration.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "applyConfigurationLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="applyConfigurationRole")
    def apply_configuration_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used by the Lambda responsible for applying MSK configuration.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "applyConfigurationRole"))

    @builtins.property
    @jsii.member(jsii_name="applyConfigurationSecurityGroup")
    def apply_configuration_security_group(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The Security Group used by the Lambda responsible for applying MSK configuration.'''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], jsii.get(self, "applyConfigurationSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="brokerLogGroup")
    def broker_log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The CloudWatch log group associated with brokers activity.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "brokerLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="brokerSecurityGroup")
    def broker_security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group associated with the MSK brokers.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "brokerSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="clusterConfiguration")
    def cluster_configuration(
        self,
    ) -> typing.Optional[_aws_cdk_aws_msk_ceddda9d.CfnConfiguration]:
        '''The MSK cluster configuration.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_msk_ceddda9d.CfnConfiguration], jsii.get(self, "clusterConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="iamCrudAdminFunction")
    def iam_crud_admin_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        '''The Lambda function responsible for CRUD operations via IAM authentication.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], jsii.get(self, "iamCrudAdminFunction"))

    @builtins.property
    @jsii.member(jsii_name="iamCrudAdminLogGroup")
    def iam_crud_admin_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The CloudWatch Log Group used by the Lambda responsible for CRUD operations via IAM authentication.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "iamCrudAdminLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="iamCrudAdminRole")
    def iam_crud_admin_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role used by the Lambda responsible for CRUD operations via IAM authentication.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "iamCrudAdminRole"))

    @builtins.property
    @jsii.member(jsii_name="iamCrudAdminSecurityGroup")
    def iam_crud_admin_security_group(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The Security Group used by the Lambda responsible for CRUD operations via IAM authentication.'''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], jsii.get(self, "iamCrudAdminSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="inClusterAclFunction")
    def in_cluster_acl_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        '''The Lambda function responsible for CRUD operations via mTLS authentication.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], jsii.get(self, "inClusterAclFunction"))

    @builtins.property
    @jsii.member(jsii_name="inClusterAclLogGroup")
    def in_cluster_acl_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The CloudWatch Log Group used by the Lambda responsible for CRUD operations via mTLS authentication.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "inClusterAclLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="inClusterAclRole")
    def in_cluster_acl_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role used by the Lambda responsible for CRUD operations via mTLS authentication.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "inClusterAclRole"))

    @builtins.property
    @jsii.member(jsii_name="inClusterAclSecurityGroup")
    def in_cluster_acl_security_group(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The Security Group used by the Lambda responsible for CRUD operations via mTLS authentication.'''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], jsii.get(self, "inClusterAclSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> typing.Optional[builtins.str]:
        '''If there is an already existing service token deployed for the custom resource you can reuse it to reduce the number of resource created.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="updateConnectivityFunction")
    def update_connectivity_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        '''The Lambda function responsible for updating MSK Connectivity.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], jsii.get(self, "updateConnectivityFunction"))

    @builtins.property
    @jsii.member(jsii_name="updateConnectivityLogGroup")
    def update_connectivity_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The CloudWatch Log Group used by the Lambda responsible for updating MSK Connectivity.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "updateConnectivityLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="updateConnectivityRole")
    def update_connectivity_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used by the Lambda responsible for updating MSK Connectivity.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "updateConnectivityRole"))

    @builtins.property
    @jsii.member(jsii_name="updateConnectivitySecurityGroup")
    def update_connectivity_security_group(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The Security Group used by the Lambda responsible for updating MSK Connectivity.'''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], jsii.get(self, "updateConnectivitySecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="updateZookepeerFunction")
    def update_zookepeer_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        '''The Lambda function responsible for updating Zookeeper.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], jsii.get(self, "updateZookepeerFunction"))

    @builtins.property
    @jsii.member(jsii_name="updateZookepeerLogGroup")
    def update_zookepeer_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The CloudWatch Log Group used by the Lambda responsible for updating Zookeeper.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "updateZookepeerLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="updateZookepeerRole")
    def update_zookepeer_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used by the Lambda responsible for updating Zookeeper.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "updateZookepeerRole"))

    @builtins.property
    @jsii.member(jsii_name="updateZookepeerSecurityGroup")
    def update_zookepeer_security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''THe Security Group associated to the Lambda responsible for updating Zookeeper.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "updateZookepeerSecurityGroup"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.MskProvisionedProps",
    jsii_struct_bases=[],
    name_mapping={
        "allow_everyone_if_no_acl_found": "allowEveryoneIfNoAclFound",
        "broker_instance_type": "brokerInstanceType",
        "broker_number": "brokerNumber",
        "certificate_definition": "certificateDefinition",
        "client_authentication": "clientAuthentication",
        "cluster_name": "clusterName",
        "configuration": "configuration",
        "current_version": "currentVersion",
        "ebs_storage": "ebsStorage",
        "environment_encryption": "environmentEncryption",
        "kafka_client_log_level": "kafkaClientLogLevel",
        "kafka_version": "kafkaVersion",
        "logging": "logging",
        "monitoring": "monitoring",
        "place_cluster_handler_in_vpc": "placeClusterHandlerInVpc",
        "removal_policy": "removalPolicy",
        "security_groups": "securityGroups",
        "storage_mode": "storageMode",
        "subnets": "subnets",
        "vpc": "vpc",
        "vpc_connectivity": "vpcConnectivity",
    },
)
class MskProvisionedProps:
    def __init__(
        self,
        *,
        allow_everyone_if_no_acl_found: typing.Optional[builtins.bool] = None,
        broker_instance_type: typing.Optional[MskBrokerInstanceType] = None,
        broker_number: typing.Optional[jsii.Number] = None,
        certificate_definition: typing.Optional[typing.Union[AclAdminProps, typing.Dict[builtins.str, typing.Any]]] = None,
        client_authentication: typing.Optional[ClientAuthentication] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        configuration: typing.Optional[typing.Union[ClusterConfigurationInfo, typing.Dict[builtins.str, typing.Any]]] = None,
        current_version: typing.Optional[builtins.str] = None,
        ebs_storage: typing.Optional[typing.Union[EbsStorageInfo, typing.Dict[builtins.str, typing.Any]]] = None,
        environment_encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        kafka_client_log_level: typing.Optional[KafkaClientLogLevel] = None,
        kafka_version: typing.Optional[KafkaVersion] = None,
        logging: typing.Optional[typing.Union[BrokerLogging, typing.Dict[builtins.str, typing.Any]]] = None,
        monitoring: typing.Optional[typing.Union[MonitoringConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        place_cluster_handler_in_vpc: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        storage_mode: typing.Optional["StorageMode"] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_connectivity: typing.Optional["VpcClientAuthentication"] = None,
    ) -> None:
        '''
        :param allow_everyone_if_no_acl_found: if set the to true the following Kafka configuration ``allow.everyone.if.no.acl.found`` is set to true. When no Cluster Configuration is passed The construct create a cluster configuration and set the following configuration to false and apply it to the cluster. Default: - false
        :param broker_instance_type: The EC2 instance type that you want Amazon MSK to use when it creates your brokers. Default: kafka.m5.large
        :param broker_number: The number of Apache Kafka brokers deployed. It must be a multiple of the number of availability zones. Default: - 1 per availability zone.
        :param certificate_definition: This Props allow you to define the principals that will be adminstartor as well as the principal that will be used by the CDK Custom resources to.
        :param client_authentication: Configuration properties for client authentication. MSK supports using private TLS certificates or SASL/SCRAM to authenticate the identity of clients. Default: - IAM is used
        :param cluster_name: The name of the MSK provisioned cluster. Default: - default-msk-provisioned
        :param configuration: The Amazon MSK configuration to use for the cluster. Default: - none
        :param current_version: This parameter is required after executing the first ``cdk deploy`` It is the version of the MSK cluster that was deployed in the previous ``cdk deploy`` The cluster might fail in the subsequent updates if it is not set This parameter is obtained by running the following command ``aws kafka describe-cluster --cluster-arn YOUR_CLUSTER_ARN``.
        :param ebs_storage: Information about storage volumes attached to MSK broker nodes. Default: - 100 GiB EBS volume
        :param environment_encryption: The AWS KMS key to use to encrypt the function environment variables.
        :param kafka_client_log_level: The log level for the lambda that support the Custom Resource for both Managing ACLs and Topics. Default: - INFO
        :param kafka_version: The version of Apache Kafka. Default: - KafkaVersion.V3_5_1
        :param logging: Configure your MSK cluster to send broker logs to different destination types. Default: - A Cloudwatch log is created
        :param monitoring: Cluster monitoring configuration. Default: - DEFAULT monitoring level
        :param place_cluster_handler_in_vpc: If set to true, the cluster handler functions will be placed in the private subnets of the cluster vpc.
        :param removal_policy: What to do when this resource is deleted from a stack. Default: - RemovalPolicy.RETAIN
        :param security_groups: The AWS security groups to associate with the elastic network interfaces of the Amazon MSK cluster. Default: - create a new security group
        :param storage_mode: This controls storage mode for supported storage tiers. Default: - StorageMode.LOCAL
        :param subnets: The subnets where to deploy the MSK Provisioned cluster. Amazon MSK distributes the broker nodes evenly across these subnets. The subnets must be in distinct Availability Zones. Client subnets can't be in Availability Zone us-east-1e. Default: - the private subnets with egress.
        :param vpc: The VPC where to deploy the MSK Serverless cluster. Must have at least 2 subnets in two different AZs. Default: - A new VPC is created.
        :param vpc_connectivity: VPC connection control settings for brokers Defines all client authentication information for VpcConnectivity. When vpcConnectivity and you provide your own Msk Congifuration You must set ``allow.everyone.if.no.acl.found`` to ``false``
        '''
        if isinstance(certificate_definition, dict):
            certificate_definition = AclAdminProps(**certificate_definition)
        if isinstance(configuration, dict):
            configuration = ClusterConfigurationInfo(**configuration)
        if isinstance(ebs_storage, dict):
            ebs_storage = EbsStorageInfo(**ebs_storage)
        if isinstance(logging, dict):
            logging = BrokerLogging(**logging)
        if isinstance(monitoring, dict):
            monitoring = MonitoringConfiguration(**monitoring)
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98db44b174c86545933f6a4039565d1036f778e4d17ad18dce0b747d09167e8c)
            check_type(argname="argument allow_everyone_if_no_acl_found", value=allow_everyone_if_no_acl_found, expected_type=type_hints["allow_everyone_if_no_acl_found"])
            check_type(argname="argument broker_instance_type", value=broker_instance_type, expected_type=type_hints["broker_instance_type"])
            check_type(argname="argument broker_number", value=broker_number, expected_type=type_hints["broker_number"])
            check_type(argname="argument certificate_definition", value=certificate_definition, expected_type=type_hints["certificate_definition"])
            check_type(argname="argument client_authentication", value=client_authentication, expected_type=type_hints["client_authentication"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
            check_type(argname="argument current_version", value=current_version, expected_type=type_hints["current_version"])
            check_type(argname="argument ebs_storage", value=ebs_storage, expected_type=type_hints["ebs_storage"])
            check_type(argname="argument environment_encryption", value=environment_encryption, expected_type=type_hints["environment_encryption"])
            check_type(argname="argument kafka_client_log_level", value=kafka_client_log_level, expected_type=type_hints["kafka_client_log_level"])
            check_type(argname="argument kafka_version", value=kafka_version, expected_type=type_hints["kafka_version"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument monitoring", value=monitoring, expected_type=type_hints["monitoring"])
            check_type(argname="argument place_cluster_handler_in_vpc", value=place_cluster_handler_in_vpc, expected_type=type_hints["place_cluster_handler_in_vpc"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument storage_mode", value=storage_mode, expected_type=type_hints["storage_mode"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_connectivity", value=vpc_connectivity, expected_type=type_hints["vpc_connectivity"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allow_everyone_if_no_acl_found is not None:
            self._values["allow_everyone_if_no_acl_found"] = allow_everyone_if_no_acl_found
        if broker_instance_type is not None:
            self._values["broker_instance_type"] = broker_instance_type
        if broker_number is not None:
            self._values["broker_number"] = broker_number
        if certificate_definition is not None:
            self._values["certificate_definition"] = certificate_definition
        if client_authentication is not None:
            self._values["client_authentication"] = client_authentication
        if cluster_name is not None:
            self._values["cluster_name"] = cluster_name
        if configuration is not None:
            self._values["configuration"] = configuration
        if current_version is not None:
            self._values["current_version"] = current_version
        if ebs_storage is not None:
            self._values["ebs_storage"] = ebs_storage
        if environment_encryption is not None:
            self._values["environment_encryption"] = environment_encryption
        if kafka_client_log_level is not None:
            self._values["kafka_client_log_level"] = kafka_client_log_level
        if kafka_version is not None:
            self._values["kafka_version"] = kafka_version
        if logging is not None:
            self._values["logging"] = logging
        if monitoring is not None:
            self._values["monitoring"] = monitoring
        if place_cluster_handler_in_vpc is not None:
            self._values["place_cluster_handler_in_vpc"] = place_cluster_handler_in_vpc
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if storage_mode is not None:
            self._values["storage_mode"] = storage_mode
        if subnets is not None:
            self._values["subnets"] = subnets
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_connectivity is not None:
            self._values["vpc_connectivity"] = vpc_connectivity

    @builtins.property
    def allow_everyone_if_no_acl_found(self) -> typing.Optional[builtins.bool]:
        '''if set the to true the following Kafka configuration ``allow.everyone.if.no.acl.found`` is set to true. When no Cluster Configuration is passed The construct create a cluster configuration and set the following configuration to false and apply it to the cluster.

        :default: - false
        '''
        result = self._values.get("allow_everyone_if_no_acl_found")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def broker_instance_type(self) -> typing.Optional[MskBrokerInstanceType]:
        '''The EC2 instance type that you want Amazon MSK to use when it creates your brokers.

        :default: kafka.m5.large

        :see: https://docs.aws.amazon.com/msk/latest/developerguide/msk-create-cluster.html#broker-instance-types
        '''
        result = self._values.get("broker_instance_type")
        return typing.cast(typing.Optional[MskBrokerInstanceType], result)

    @builtins.property
    def broker_number(self) -> typing.Optional[jsii.Number]:
        '''The number of Apache Kafka brokers deployed.

        It must be a multiple of the number of availability zones.

        :default: - 1 per availability zone.
        '''
        result = self._values.get("broker_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def certificate_definition(self) -> typing.Optional[AclAdminProps]:
        '''This Props allow you to define the principals that will be adminstartor as well as the principal that will be used by the CDK Custom resources to.'''
        result = self._values.get("certificate_definition")
        return typing.cast(typing.Optional[AclAdminProps], result)

    @builtins.property
    def client_authentication(self) -> typing.Optional[ClientAuthentication]:
        '''Configuration properties for client authentication.

        MSK supports using private TLS certificates or SASL/SCRAM to authenticate the identity of clients.

        :default: - IAM is used
        '''
        result = self._values.get("client_authentication")
        return typing.cast(typing.Optional[ClientAuthentication], result)

    @builtins.property
    def cluster_name(self) -> typing.Optional[builtins.str]:
        '''The name of the MSK provisioned cluster.

        :default: - default-msk-provisioned
        '''
        result = self._values.get("cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def configuration(self) -> typing.Optional[ClusterConfigurationInfo]:
        '''The Amazon MSK configuration to use for the cluster.

        :default: - none
        '''
        result = self._values.get("configuration")
        return typing.cast(typing.Optional[ClusterConfigurationInfo], result)

    @builtins.property
    def current_version(self) -> typing.Optional[builtins.str]:
        '''This parameter is required after executing the first ``cdk deploy`` It is the version of the MSK cluster that was deployed in the previous ``cdk deploy`` The cluster might fail in the subsequent updates if it is not set This parameter is obtained by running the following command ``aws kafka describe-cluster --cluster-arn YOUR_CLUSTER_ARN``.'''
        result = self._values.get("current_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs_storage(self) -> typing.Optional[EbsStorageInfo]:
        '''Information about storage volumes attached to MSK broker nodes.

        :default: - 100 GiB EBS volume
        '''
        result = self._values.get("ebs_storage")
        return typing.cast(typing.Optional[EbsStorageInfo], result)

    @builtins.property
    def environment_encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The AWS KMS key to use to encrypt the function environment variables.'''
        result = self._values.get("environment_encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def kafka_client_log_level(self) -> typing.Optional[KafkaClientLogLevel]:
        '''The log level for the lambda that support the Custom Resource for both Managing ACLs and Topics.

        :default: - INFO
        '''
        result = self._values.get("kafka_client_log_level")
        return typing.cast(typing.Optional[KafkaClientLogLevel], result)

    @builtins.property
    def kafka_version(self) -> typing.Optional[KafkaVersion]:
        '''The version of Apache Kafka.

        :default: - KafkaVersion.V3_5_1
        '''
        result = self._values.get("kafka_version")
        return typing.cast(typing.Optional[KafkaVersion], result)

    @builtins.property
    def logging(self) -> typing.Optional[BrokerLogging]:
        '''Configure your MSK cluster to send broker logs to different destination types.

        :default: - A Cloudwatch log is created
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[BrokerLogging], result)

    @builtins.property
    def monitoring(self) -> typing.Optional[MonitoringConfiguration]:
        '''Cluster monitoring configuration.

        :default: - DEFAULT monitoring level
        '''
        result = self._values.get("monitoring")
        return typing.cast(typing.Optional[MonitoringConfiguration], result)

    @builtins.property
    def place_cluster_handler_in_vpc(self) -> typing.Optional[builtins.bool]:
        '''If set to true, the cluster handler functions will be placed in the private subnets of the cluster vpc.'''
        result = self._values.get("place_cluster_handler_in_vpc")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''What to do when this resource is deleted from a stack.

        :default: - RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The AWS security groups to associate with the elastic network interfaces of the Amazon MSK cluster.

        :default: - create a new security group
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def storage_mode(self) -> typing.Optional["StorageMode"]:
        '''This controls storage mode for supported storage tiers.

        :default: - StorageMode.LOCAL

        :see: https://docs.aws.amazon.com/msk/latest/developerguide/msk-tiered-storage.html
        '''
        result = self._values.get("storage_mode")
        return typing.cast(typing.Optional["StorageMode"], result)

    @builtins.property
    def subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The subnets where to deploy the MSK Provisioned cluster.

        Amazon MSK distributes the broker nodes evenly across these subnets.
        The subnets must be in distinct Availability Zones.
        Client subnets can't be in Availability Zone us-east-1e.

        :default: - the private subnets with egress.
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC where to deploy the MSK Serverless cluster.

        Must have at least 2 subnets in two different AZs.

        :default: - A new VPC is created.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def vpc_connectivity(self) -> typing.Optional["VpcClientAuthentication"]:
        '''VPC connection control settings for brokers Defines all client authentication information for VpcConnectivity.

        When vpcConnectivity and you provide your own Msk Congifuration
        You must set ``allow.everyone.if.no.acl.found`` to ``false``
        '''
        result = self._values.get("vpc_connectivity")
        return typing.cast(typing.Optional["VpcClientAuthentication"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskProvisionedProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskServerless(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.MskServerless",
):
    '''A construct to create an MSK Serverless cluster.

    :see: https://awslabs.github.io/data-solutions-framework-on-aws/

    Example::

        msk = dsf.streaming.MskServerless(self, "cluster")
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster_name: typing.Optional[builtins.str] = None,
        kafka_client_log_level: typing.Optional[KafkaClientLogLevel] = None,
        lambda_environment_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''Constructs a new instance of the EmrEksCluster construct.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param cluster_name: The name of the MSK Serverless cluster. Default: - default-msk-serverless
        :param kafka_client_log_level: The log level for the lambda that support the Custom Resource for both Managing ACLs and Topics. Default: WARN
        :param lambda_environment_encryption_key: The AWS KMS key to use to encrypt enviornment variable of lambda supporting the MSK Custom Resources creation.
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param security_groups: The AWS security groups to associate with the elastic network interfaces of the Amazon MSK cluster. Default: - create a new security group
        :param subnets: The subnets where to deploy the MSK Serverless cluster. The subnets must be in distinct Availability Zones. Client subnets can't be in Availability Zone us-east-1e. Default: - the Vpc default strategy if not specified.
        :param vpc: The VPC where to deploy the MSK Serverless cluster. The VPC must have at least 2 subnets in two different AZs. Default: - A new Vpc is created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__892439383b3bbcc44a88c08cac7c30302eb9872142a11061de472bdd8cd122a3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MskServerlessProps(
            cluster_name=cluster_name,
            kafka_client_log_level=kafka_client_log_level,
            lambda_environment_encryption_key=lambda_environment_encryption_key,
            removal_policy=removal_policy,
            security_groups=security_groups,
            subnets=subnets,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addClusterPolicy")
    def add_cluster_policy(
        self,
        policy: _aws_cdk_aws_iam_ceddda9d.PolicyDocument,
        id: builtins.str,
    ) -> _aws_cdk_aws_msk_ceddda9d.CfnClusterPolicy:
        '''Add a cluster policy.

        :param policy: the IAM principal to grand the consume action.
        :param id: the CDK id for the Cluster Policy.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b4db95c212f0bb70a0353161977a1d1bca0c43bf4f92fbd6fd38be1a8d2de2f)
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(_aws_cdk_aws_msk_ceddda9d.CfnClusterPolicy, jsii.invoke(self, "addClusterPolicy", [policy, id]))

    @jsii.member(jsii_name="addTopic")
    def add_topic(
        self,
        id: builtins.str,
        topic_definition: typing.Union["MskTopic", typing.Dict[builtins.str, typing.Any]],
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        wait_for_leaders: typing.Optional[builtins.bool] = None,
        timeout: typing.Optional[jsii.Number] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Creates a topic in the MSK Serverless.

        :param id: the CDK id for the topic.
        :param topic_definition: the Kafka topic definition.
        :param removal_policy: Wether to keep the topic or delete it when removing the resource from the Stack.
        :param wait_for_leaders: Wait until metadata for the new topics doesn't throw LEADER_NOT_AVAILABLE.
        :param timeout: The time in ms to wait for a topic to be completely created on the controller node.

        :default: - 5000

        :return: the custom resource used to create the topic
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69df34d7aac47110d360157179b00828e6290715371c5acf6957d879d73291a2)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument topic_definition", value=topic_definition, expected_type=type_hints["topic_definition"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument wait_for_leaders", value=wait_for_leaders, expected_type=type_hints["wait_for_leaders"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "addTopic", [id, topic_definition, removal_policy, wait_for_leaders, timeout]))

    @jsii.member(jsii_name="grantConsume")
    def grant_consume(
        self,
        topic_name: builtins.str,
        principal: _aws_cdk_aws_iam_ceddda9d.IPrincipal,
    ) -> typing.Optional[_aws_cdk_ceddda9d.CustomResource]:
        '''Grant a principal the right to consume data from a topic.

        :param topic_name: the topic to which the principal can consume data from.
        :param principal: the IAM principal to grand the consume action.

        :return: the custom resource used to grant the consumer permissions
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16064a175580bc53c74366cef05cabb5214b0c68a409083fab94d7292d4cb871)
            check_type(argname="argument topic_name", value=topic_name, expected_type=type_hints["topic_name"])
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.CustomResource], jsii.invoke(self, "grantConsume", [topic_name, principal]))

    @jsii.member(jsii_name="grantProduce")
    def grant_produce(
        self,
        topic_name: builtins.str,
        principal: _aws_cdk_aws_iam_ceddda9d.IPrincipal,
    ) -> typing.Optional[_aws_cdk_ceddda9d.CustomResource]:
        '''Grant a principal to produce data to a topic.

        :param topic_name: the name of the topic to grant producer permissions.
        :param principal: the IAM principal to grand producer permissions.

        :return: the custom resource used to grant the producer permissions
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85afb37728989db6694c9e1836cf0a7e3592598a813bbadeebd935ed4a168734)
            check_type(argname="argument topic_name", value=topic_name, expected_type=type_hints["topic_name"])
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.CustomResource], jsii.invoke(self, "grantProduce", [topic_name, principal]))

    @jsii.member(jsii_name="retrieveVersion")
    def retrieve_version(self) -> typing.Any:
        '''Retrieve DSF package.json version.'''
        return typing.cast(typing.Any, jsii.invoke(self, "retrieveVersion", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_OWNED_TAG")
    def DSF_OWNED_TAG(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_OWNED_TAG"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_TRACKING_CODE")
    def DSF_TRACKING_CODE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_TRACKING_CODE"))

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> _aws_cdk_aws_msk_ceddda9d.CfnServerlessCluster:
        '''The MSK cluster as a CloudFormation resource.'''
        return typing.cast(_aws_cdk_aws_msk_ceddda9d.CfnServerlessCluster, jsii.get(self, "cluster"))

    @builtins.property
    @jsii.member(jsii_name="clusterBoostrapBrokers")
    def cluster_boostrap_brokers(self) -> builtins.str:
        '''The list of bootstrap servers for client to connect.'''
        return typing.cast(builtins.str, jsii.get(self, "clusterBoostrapBrokers"))

    @builtins.property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        '''The name of the cluster.'''
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @builtins.property
    @jsii.member(jsii_name="lambdaSecurityGroup")
    def lambda_security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        '''The security group used by the configuration Lambda.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, jsii.get(self, "lambdaSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC where the MSK cluster is deployed.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="brokerSecurityGroup")
    def broker_security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group used by the cluster.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "brokerSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> typing.Optional[builtins.str]:
        '''If there is an already existing service token deployed for the custom resource you can reuse it to reduce the number of resource created.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceToken"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.MskServerlessProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_name": "clusterName",
        "kafka_client_log_level": "kafkaClientLogLevel",
        "lambda_environment_encryption_key": "lambdaEnvironmentEncryptionKey",
        "removal_policy": "removalPolicy",
        "security_groups": "securityGroups",
        "subnets": "subnets",
        "vpc": "vpc",
    },
)
class MskServerlessProps:
    def __init__(
        self,
        *,
        cluster_name: typing.Optional[builtins.str] = None,
        kafka_client_log_level: typing.Optional[KafkaClientLogLevel] = None,
        lambda_environment_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''Properties for the ``MskServerlessCluster`` construct.

        :param cluster_name: The name of the MSK Serverless cluster. Default: - default-msk-serverless
        :param kafka_client_log_level: The log level for the lambda that support the Custom Resource for both Managing ACLs and Topics. Default: WARN
        :param lambda_environment_encryption_key: The AWS KMS key to use to encrypt enviornment variable of lambda supporting the MSK Custom Resources creation.
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param security_groups: The AWS security groups to associate with the elastic network interfaces of the Amazon MSK cluster. Default: - create a new security group
        :param subnets: The subnets where to deploy the MSK Serverless cluster. The subnets must be in distinct Availability Zones. Client subnets can't be in Availability Zone us-east-1e. Default: - the Vpc default strategy if not specified.
        :param vpc: The VPC where to deploy the MSK Serverless cluster. The VPC must have at least 2 subnets in two different AZs. Default: - A new Vpc is created
        '''
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf5fa506d782f5db74510f3a1a6d6f6fcb92080eab7d42c2ae43730ca86e66ff)
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument kafka_client_log_level", value=kafka_client_log_level, expected_type=type_hints["kafka_client_log_level"])
            check_type(argname="argument lambda_environment_encryption_key", value=lambda_environment_encryption_key, expected_type=type_hints["lambda_environment_encryption_key"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cluster_name is not None:
            self._values["cluster_name"] = cluster_name
        if kafka_client_log_level is not None:
            self._values["kafka_client_log_level"] = kafka_client_log_level
        if lambda_environment_encryption_key is not None:
            self._values["lambda_environment_encryption_key"] = lambda_environment_encryption_key
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if subnets is not None:
            self._values["subnets"] = subnets
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def cluster_name(self) -> typing.Optional[builtins.str]:
        '''The name of the MSK Serverless cluster.

        :default: - default-msk-serverless
        '''
        result = self._values.get("cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kafka_client_log_level(self) -> typing.Optional[KafkaClientLogLevel]:
        '''The log level for the lambda that support the Custom Resource for both Managing ACLs and Topics.

        :default: WARN
        '''
        result = self._values.get("kafka_client_log_level")
        return typing.cast(typing.Optional[KafkaClientLogLevel], result)

    @builtins.property
    def lambda_environment_encryption_key(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The AWS KMS key to use to encrypt  enviornment variable of lambda supporting the MSK Custom Resources creation.'''
        result = self._values.get("lambda_environment_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The AWS security groups to associate with the elastic network interfaces of the Amazon MSK cluster.

        :default: - create a new security group
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The subnets where to deploy the MSK Serverless cluster.

        The subnets must be in distinct Availability Zones.
        Client subnets can't be in Availability Zone us-east-1e.

        :default: - the Vpc default strategy if not specified.
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC where to deploy the MSK Serverless cluster.

        The VPC must have at least 2 subnets in two different AZs.

        :default: - A new Vpc is created
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskServerlessProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.MskTopic",
    jsii_struct_bases=[],
    name_mapping={
        "num_partitions": "numPartitions",
        "topic": "topic",
        "config_entries": "configEntries",
        "replication_factor": "replicationFactor",
    },
)
class MskTopic:
    def __init__(
        self,
        *,
        num_partitions: jsii.Number,
        topic: builtins.str,
        config_entries: typing.Optional[typing.Sequence[typing.Mapping[builtins.str, builtins.str]]] = None,
        replication_factor: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Properties for the ``MskTopic`` As defined in ``ITopicConfig`` in `KafkaJS <https://kafka.js.org/docs/admin>`_ SDK.

        :param num_partitions: The number of partitions in the topic.
        :param topic: The name of the topic.
        :param config_entries: The topic level configurations. This parameter cannot be updated after the creation of the topic. Default: - no configuration is used
        :param replication_factor: The replication factor of the partitions. This parameter cannot be updated after the creation of the topic. This parameter should not be provided for MSK Serverless. Default: - For MSK Serverless, the number of AZ. For MSK Provisioned, the cluster default configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50999f64b2bf57e9a21df87c98a154cffadc71c2285baeebf0f8689e1e777429)
            check_type(argname="argument num_partitions", value=num_partitions, expected_type=type_hints["num_partitions"])
            check_type(argname="argument topic", value=topic, expected_type=type_hints["topic"])
            check_type(argname="argument config_entries", value=config_entries, expected_type=type_hints["config_entries"])
            check_type(argname="argument replication_factor", value=replication_factor, expected_type=type_hints["replication_factor"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "num_partitions": num_partitions,
            "topic": topic,
        }
        if config_entries is not None:
            self._values["config_entries"] = config_entries
        if replication_factor is not None:
            self._values["replication_factor"] = replication_factor

    @builtins.property
    def num_partitions(self) -> jsii.Number:
        '''The number of partitions in the topic.'''
        result = self._values.get("num_partitions")
        assert result is not None, "Required property 'num_partitions' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def topic(self) -> builtins.str:
        '''The name of the topic.'''
        result = self._values.get("topic")
        assert result is not None, "Required property 'topic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def config_entries(
        self,
    ) -> typing.Optional[typing.List[typing.Mapping[builtins.str, builtins.str]]]:
        '''The topic level configurations.

        This parameter cannot be updated after the creation of the topic.

        :default: - no configuration is used
        '''
        result = self._values.get("config_entries")
        return typing.cast(typing.Optional[typing.List[typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def replication_factor(self) -> typing.Optional[jsii.Number]:
        '''The replication factor of the partitions.

        This parameter cannot be updated after the creation of the topic.
        This parameter should not be provided for MSK Serverless.

        :default: - For MSK Serverless, the number of AZ. For MSK Provisioned, the cluster default configuration.
        '''
        result = self._values.get("replication_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskTopic(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.ResourcePatternTypes"
)
class ResourcePatternTypes(enum.Enum):
    UNKNOWN = "UNKNOWN"
    ANY = "ANY"
    MATCH = "MATCH"
    LITERAL = "LITERAL"
    PREFIXED = "PREFIXED"


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.S3LoggingConfiguration",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "prefix": "prefix"},
)
class S3LoggingConfiguration:
    def __init__(
        self,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Details of the Amazon S3 destination for broker logs.

        :param bucket: The S3 bucket that is the destination for broker logs.
        :param prefix: The S3 prefix that is the destination for broker logs. Default: - no prefix
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82ca97be2f9081adbed88410b7981d2cc7bbd6145b59a319f25c899a33c1587f)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
        }
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''The S3 bucket that is the destination for broker logs.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''The S3 prefix that is the destination for broker logs.

        :default: - no prefix
        '''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3LoggingConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.SaslAuthProps",
    jsii_struct_bases=[],
    name_mapping={"iam": "iam"},
)
class SaslAuthProps:
    def __init__(self, *, iam: typing.Optional[builtins.bool] = None) -> None:
        '''SASL authentication properties.

        :param iam: Enable IAM access control. Default: - false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a69cfaf96dab720314a86b2aba1a3764d5dad9597e92d15b07c21a58a886d884)
            check_type(argname="argument iam", value=iam, expected_type=type_hints["iam"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if iam is not None:
            self._values["iam"] = iam

    @builtins.property
    def iam(self) -> typing.Optional[builtins.bool]:
        '''Enable IAM access control.

        :default: - false
        '''
        result = self._values.get("iam")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SaslAuthProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/aws-data-solutions-framework.streaming.StorageMode")
class StorageMode(enum.Enum):
    '''The storage mode for the cluster brokers.'''

    LOCAL = "LOCAL"
    '''Local storage mode utilizes network attached EBS storage.'''
    TIERED = "TIERED"
    '''Tiered storage mode utilizes EBS storage and Tiered storage.'''


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.TlsAuthProps",
    jsii_struct_bases=[],
    name_mapping={"certificate_authorities": "certificateAuthorities"},
)
class TlsAuthProps:
    def __init__(
        self,
        *,
        certificate_authorities: typing.Optional[typing.Sequence[_aws_cdk_aws_acmpca_ceddda9d.ICertificateAuthority]] = None,
    ) -> None:
        '''TLS authentication properties.

        :param certificate_authorities: List of ACM Certificate Authorities to enable TLS authentication. Default: - none
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b75ace651f25eb081badf2271fb655bc4c0850e36bafe6b474f39e00935bb0c7)
            check_type(argname="argument certificate_authorities", value=certificate_authorities, expected_type=type_hints["certificate_authorities"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if certificate_authorities is not None:
            self._values["certificate_authorities"] = certificate_authorities

    @builtins.property
    def certificate_authorities(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_acmpca_ceddda9d.ICertificateAuthority]]:
        '''List of ACM Certificate Authorities to enable TLS authentication.

        :default: - none
        '''
        result = self._values.get("certificate_authorities")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_acmpca_ceddda9d.ICertificateAuthority]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TlsAuthProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VpcClientAuthentication(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.VpcClientAuthentication",
):
    '''Configuration properties for VPC client authentication.'''

    @jsii.member(jsii_name="sasl")
    @builtins.classmethod
    def sasl(
        cls,
        *,
        iam: typing.Optional[builtins.bool] = None,
    ) -> "VpcClientAuthentication":
        '''SASL authentication.

        :param iam: Enable IAM access control. Default: - false
        '''
        props = SaslAuthProps(iam=iam)

        return typing.cast("VpcClientAuthentication", jsii.sinvoke(cls, "sasl", [props]))

    @jsii.member(jsii_name="saslTls")
    @builtins.classmethod
    def sasl_tls(
        cls,
        *,
        iam: typing.Optional[builtins.bool] = None,
        tls: typing.Optional[builtins.bool] = None,
    ) -> "VpcClientAuthentication":
        '''SASL + TLS authentication.

        :param iam: Enable IAM access control. Default: - false
        :param tls: enable TLS authentication. Default: - none
        '''
        sasl_tls_props = SaslVpcTlsAuthProps(iam=iam, tls=tls)

        return typing.cast("VpcClientAuthentication", jsii.sinvoke(cls, "saslTls", [sasl_tls_props]))

    @jsii.member(jsii_name="tls")
    @builtins.classmethod
    def tls(
        cls,
        *,
        tls: typing.Optional[builtins.bool] = None,
    ) -> "VpcClientAuthentication":
        '''TLS authentication.

        :param tls: enable TLS authentication. Default: - none
        '''
        props = VpcTlsAuthProps(tls=tls)

        return typing.cast("VpcClientAuthentication", jsii.sinvoke(cls, "tls", [props]))

    @builtins.property
    @jsii.member(jsii_name="saslProps")
    def sasl_props(self) -> typing.Optional[SaslAuthProps]:
        '''- properties for SASL authentication.'''
        return typing.cast(typing.Optional[SaslAuthProps], jsii.get(self, "saslProps"))

    @builtins.property
    @jsii.member(jsii_name="tlsProps")
    def tls_props(self) -> typing.Optional["VpcTlsAuthProps"]:
        '''- properties for TLS authentication.'''
        return typing.cast(typing.Optional["VpcTlsAuthProps"], jsii.get(self, "tlsProps"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.VpcTlsAuthProps",
    jsii_struct_bases=[],
    name_mapping={"tls": "tls"},
)
class VpcTlsAuthProps:
    def __init__(self, *, tls: typing.Optional[builtins.bool] = None) -> None:
        '''TLS authentication properties.

        :param tls: enable TLS authentication. Default: - none
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfa989fad1cbc8518acad9bce75e30465e418b0228fe1dd3da8649e86a493beb)
            check_type(argname="argument tls", value=tls, expected_type=type_hints["tls"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if tls is not None:
            self._values["tls"] = tls

    @builtins.property
    def tls(self) -> typing.Optional[builtins.bool]:
        '''enable TLS authentication.

        :default: - none
        '''
        result = self._values.get("tls")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpcTlsAuthProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.SaslTlsAuthProps",
    jsii_struct_bases=[SaslAuthProps, TlsAuthProps],
    name_mapping={"iam": "iam", "certificate_authorities": "certificateAuthorities"},
)
class SaslTlsAuthProps(SaslAuthProps, TlsAuthProps):
    def __init__(
        self,
        *,
        iam: typing.Optional[builtins.bool] = None,
        certificate_authorities: typing.Optional[typing.Sequence[_aws_cdk_aws_acmpca_ceddda9d.ICertificateAuthority]] = None,
    ) -> None:
        '''SASL + TLS authentication properties.

        :param iam: Enable IAM access control. Default: - false
        :param certificate_authorities: List of ACM Certificate Authorities to enable TLS authentication. Default: - none
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b540b95307fdb73492eba61e5c3ad3f2ea64ba068d1b2d8d32d407a1f8dd7d37)
            check_type(argname="argument iam", value=iam, expected_type=type_hints["iam"])
            check_type(argname="argument certificate_authorities", value=certificate_authorities, expected_type=type_hints["certificate_authorities"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if iam is not None:
            self._values["iam"] = iam
        if certificate_authorities is not None:
            self._values["certificate_authorities"] = certificate_authorities

    @builtins.property
    def iam(self) -> typing.Optional[builtins.bool]:
        '''Enable IAM access control.

        :default: - false
        '''
        result = self._values.get("iam")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def certificate_authorities(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_acmpca_ceddda9d.ICertificateAuthority]]:
        '''List of ACM Certificate Authorities to enable TLS authentication.

        :default: - none
        '''
        result = self._values.get("certificate_authorities")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_acmpca_ceddda9d.ICertificateAuthority]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SaslTlsAuthProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.streaming.SaslVpcTlsAuthProps",
    jsii_struct_bases=[SaslAuthProps, VpcTlsAuthProps],
    name_mapping={"iam": "iam", "tls": "tls"},
)
class SaslVpcTlsAuthProps(SaslAuthProps, VpcTlsAuthProps):
    def __init__(
        self,
        *,
        iam: typing.Optional[builtins.bool] = None,
        tls: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''SASL + TLS authentication properties.

        :param iam: Enable IAM access control. Default: - false
        :param tls: enable TLS authentication. Default: - none
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0dd164ca1ef03c7ef58c6ede71291df119a9209e2a306b7a115179da71da707)
            check_type(argname="argument iam", value=iam, expected_type=type_hints["iam"])
            check_type(argname="argument tls", value=tls, expected_type=type_hints["tls"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if iam is not None:
            self._values["iam"] = iam
        if tls is not None:
            self._values["tls"] = tls

    @builtins.property
    def iam(self) -> typing.Optional[builtins.bool]:
        '''Enable IAM access control.

        :default: - false
        '''
        result = self._values.get("iam")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def tls(self) -> typing.Optional[builtins.bool]:
        '''enable TLS authentication.

        :default: - none
        '''
        result = self._values.get("tls")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SaslVpcTlsAuthProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Acl",
    "AclAdminProps",
    "AclOperationTypes",
    "AclPermissionTypes",
    "AclResourceTypes",
    "Authentication",
    "BrokerLogging",
    "ClientAuthentication",
    "ClusterConfigurationInfo",
    "ClusterMonitoringLevel",
    "EbsStorageInfo",
    "KafkaApi",
    "KafkaApiProps",
    "KafkaClientLogLevel",
    "KafkaVersion",
    "MonitoringConfiguration",
    "MskBrokerInstanceType",
    "MskClusterType",
    "MskProvisioned",
    "MskProvisionedProps",
    "MskServerless",
    "MskServerlessProps",
    "MskTopic",
    "ResourcePatternTypes",
    "S3LoggingConfiguration",
    "SaslAuthProps",
    "SaslTlsAuthProps",
    "SaslVpcTlsAuthProps",
    "StorageMode",
    "TlsAuthProps",
    "VpcClientAuthentication",
    "VpcTlsAuthProps",
]

publication.publish()

def _typecheckingstub__3b2c45eeb82912583d0e203bcc5f7cfa5d4679f4aa75359733b6a3b6d15aaa09(
    *,
    host: builtins.str,
    operation: AclOperationTypes,
    permission_type: AclPermissionTypes,
    principal: builtins.str,
    resource_name: builtins.str,
    resource_pattern_type: ResourcePatternTypes,
    resource_type: AclResourceTypes,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c2c48ca9218f0e3216c02f72ab5bacdfcd4861e0c07886b466905a0676baca8(
    *,
    acl_admin_principal: builtins.str,
    admin_principal: builtins.str,
    secret_certificate: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcf29df229d45be6f58cf96f7c79a3fd20c67254205e0d4bf24c15fc1917467f(
    *,
    cloudwatch_log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    firehose_delivery_stream_name: typing.Optional[builtins.str] = None,
    s3: typing.Optional[typing.Union[S3LoggingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3836211b99f5c6335752911fac90a01a7d51a80694071ca21e83d6ed9e4ccd6e(
    *,
    arn: builtins.str,
    revision: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3425efae5f0d6400892f5926740e3aa84485ca386ae41ba733ecaca3e0d2825d(
    *,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    volume_size: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11acb7f10ba2c540e3c133ed7f79f6ef73b1fa3e856e07fb966b40a1ffd34dc4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    broker_security_group: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
    client_authentication: ClientAuthentication,
    cluster_arn: builtins.str,
    cluster_type: MskClusterType,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    certficate_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    environment_encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    iam_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    kafka_client_log_level: typing.Optional[KafkaClientLogLevel] = None,
    mtls_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    service_token: typing.Optional[builtins.str] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b17087c46184134a6bdd689601d720ab914b7b56ad32b934fcad3f4c51f29dd0(
    id: builtins.str,
    topic_name: builtins.str,
    client_authentication: Authentication,
    principal: typing.Union[builtins.str, _aws_cdk_aws_iam_ceddda9d.IPrincipal],
    host: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    custom_resource_authentication: typing.Optional[Authentication] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c253515c374085f1ae8c19e0362e4924e1a2b781d754123dce2804908888e67(
    id: builtins.str,
    topic_name: builtins.str,
    client_authentication: Authentication,
    principal: typing.Union[builtins.str, _aws_cdk_aws_iam_ceddda9d.IPrincipal],
    host: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    custom_resource_authentication: typing.Optional[Authentication] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d1c462aeb2582babda671003a454ea0e7a7fec802c2e877a39480d04de2a004(
    id: builtins.str,
    acl_definition: typing.Union[Acl, typing.Dict[builtins.str, typing.Any]],
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    client_authentication: typing.Optional[Authentication] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0906adf996cc3e4500527d7cc602db45099025693a3968a806f5ecab7596d1bf(
    id: builtins.str,
    client_authentication: Authentication,
    topic_definition: typing.Union[MskTopic, typing.Dict[builtins.str, typing.Any]],
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    wait_for_leaders: typing.Optional[builtins.bool] = None,
    timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8aa63759ad33545334567b3e848b5b426d5233e0f36e975fdd69080066c10ef2(
    *,
    broker_security_group: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
    client_authentication: ClientAuthentication,
    cluster_arn: builtins.str,
    cluster_type: MskClusterType,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    certficate_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    environment_encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    iam_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    kafka_client_log_level: typing.Optional[KafkaClientLogLevel] = None,
    mtls_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    service_token: typing.Optional[builtins.str] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0e8e81d0dac96cf7234f1a61b30d53c9a3d1a4d97fb2c0e99ddf481ddfdef08(
    version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2cbd7fca2428428959aa1e6b26222a5eda1ac49ca65e935d98c608d20e95b2a(
    *,
    cluster_monitoring_level: typing.Optional[ClusterMonitoringLevel] = None,
    enable_prometheus_jmx_exporter: typing.Optional[builtins.bool] = None,
    enable_prometheus_node_exporter: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ca2efff56a789cd1b8df4e44c11ca8c4c57f1cc02116b9c269dcb507fc80d30(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    allow_everyone_if_no_acl_found: typing.Optional[builtins.bool] = None,
    broker_instance_type: typing.Optional[MskBrokerInstanceType] = None,
    broker_number: typing.Optional[jsii.Number] = None,
    certificate_definition: typing.Optional[typing.Union[AclAdminProps, typing.Dict[builtins.str, typing.Any]]] = None,
    client_authentication: typing.Optional[ClientAuthentication] = None,
    cluster_name: typing.Optional[builtins.str] = None,
    configuration: typing.Optional[typing.Union[ClusterConfigurationInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    current_version: typing.Optional[builtins.str] = None,
    ebs_storage: typing.Optional[typing.Union[EbsStorageInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    environment_encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    kafka_client_log_level: typing.Optional[KafkaClientLogLevel] = None,
    kafka_version: typing.Optional[KafkaVersion] = None,
    logging: typing.Optional[typing.Union[BrokerLogging, typing.Dict[builtins.str, typing.Any]]] = None,
    monitoring: typing.Optional[typing.Union[MonitoringConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    place_cluster_handler_in_vpc: typing.Optional[builtins.bool] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    storage_mode: typing.Optional[StorageMode] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_connectivity: typing.Optional[VpcClientAuthentication] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d369ff236b2de65a148f8f832bc5814ae684182e9e28ecd4d772aaeacce4a73e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
    server_properties_file_path: builtins.str,
    kafka_versions: typing.Optional[typing.Sequence[KafkaVersion]] = None,
    configuration_description: typing.Optional[builtins.str] = None,
    *,
    creation_time: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    revision: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10676524f40fb6031b8159cf669604d3aa0f353edce8387b919edbe6e8964692(
    policy: _aws_cdk_aws_iam_ceddda9d.PolicyDocument,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d63f9e52742d09c41e16f3e104e38fe360fa7eefb1ad98b53fcd4ef441f4fc48(
    authentication: Authentication,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14864c75a3d144ecd94cedde926f6cfd866bb41f5c6db2d3baf1fa9c82adcc8f(
    id: builtins.str,
    topic_name: builtins.str,
    client_authentication: Authentication,
    principal: typing.Union[builtins.str, _aws_cdk_aws_iam_ceddda9d.IPrincipal],
    host: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    custom_resource_authentication: typing.Optional[Authentication] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cc63af365e833f5e62cbe4e823f9a183c658c413332b1277411ded29118ad1e(
    id: builtins.str,
    topic_name: builtins.str,
    client_authentication: Authentication,
    principal: typing.Union[builtins.str, _aws_cdk_aws_iam_ceddda9d.IPrincipal],
    host: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    custom_resource_authentication: typing.Optional[Authentication] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e3702cd56a0669fff2b66b5876666a95e6729262702449992f06699c5278cb2(
    policy: builtins.str,
    id: builtins.str,
    current_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14aa4f0e49e9d332484ca339cf959127dc14dbd5782f41d66cabb4e0596724fd(
    id: builtins.str,
    acl_definition: typing.Union[Acl, typing.Dict[builtins.str, typing.Any]],
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    client_authentication: typing.Optional[Authentication] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7fa5e5d3f4a3ee0d52473cab439005e8198dc41d2d4509d5aa81557a4c4142b(
    id: builtins.str,
    client_authentication: Authentication,
    topic_definition: typing.Union[MskTopic, typing.Dict[builtins.str, typing.Any]],
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    wait_for_leaders: typing.Optional[builtins.bool] = None,
    timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98db44b174c86545933f6a4039565d1036f778e4d17ad18dce0b747d09167e8c(
    *,
    allow_everyone_if_no_acl_found: typing.Optional[builtins.bool] = None,
    broker_instance_type: typing.Optional[MskBrokerInstanceType] = None,
    broker_number: typing.Optional[jsii.Number] = None,
    certificate_definition: typing.Optional[typing.Union[AclAdminProps, typing.Dict[builtins.str, typing.Any]]] = None,
    client_authentication: typing.Optional[ClientAuthentication] = None,
    cluster_name: typing.Optional[builtins.str] = None,
    configuration: typing.Optional[typing.Union[ClusterConfigurationInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    current_version: typing.Optional[builtins.str] = None,
    ebs_storage: typing.Optional[typing.Union[EbsStorageInfo, typing.Dict[builtins.str, typing.Any]]] = None,
    environment_encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    kafka_client_log_level: typing.Optional[KafkaClientLogLevel] = None,
    kafka_version: typing.Optional[KafkaVersion] = None,
    logging: typing.Optional[typing.Union[BrokerLogging, typing.Dict[builtins.str, typing.Any]]] = None,
    monitoring: typing.Optional[typing.Union[MonitoringConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    place_cluster_handler_in_vpc: typing.Optional[builtins.bool] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    storage_mode: typing.Optional[StorageMode] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_connectivity: typing.Optional[VpcClientAuthentication] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__892439383b3bbcc44a88c08cac7c30302eb9872142a11061de472bdd8cd122a3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster_name: typing.Optional[builtins.str] = None,
    kafka_client_log_level: typing.Optional[KafkaClientLogLevel] = None,
    lambda_environment_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b4db95c212f0bb70a0353161977a1d1bca0c43bf4f92fbd6fd38be1a8d2de2f(
    policy: _aws_cdk_aws_iam_ceddda9d.PolicyDocument,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69df34d7aac47110d360157179b00828e6290715371c5acf6957d879d73291a2(
    id: builtins.str,
    topic_definition: typing.Union[MskTopic, typing.Dict[builtins.str, typing.Any]],
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    wait_for_leaders: typing.Optional[builtins.bool] = None,
    timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16064a175580bc53c74366cef05cabb5214b0c68a409083fab94d7292d4cb871(
    topic_name: builtins.str,
    principal: _aws_cdk_aws_iam_ceddda9d.IPrincipal,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85afb37728989db6694c9e1836cf0a7e3592598a813bbadeebd935ed4a168734(
    topic_name: builtins.str,
    principal: _aws_cdk_aws_iam_ceddda9d.IPrincipal,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf5fa506d782f5db74510f3a1a6d6f6fcb92080eab7d42c2ae43730ca86e66ff(
    *,
    cluster_name: typing.Optional[builtins.str] = None,
    kafka_client_log_level: typing.Optional[KafkaClientLogLevel] = None,
    lambda_environment_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50999f64b2bf57e9a21df87c98a154cffadc71c2285baeebf0f8689e1e777429(
    *,
    num_partitions: jsii.Number,
    topic: builtins.str,
    config_entries: typing.Optional[typing.Sequence[typing.Mapping[builtins.str, builtins.str]]] = None,
    replication_factor: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82ca97be2f9081adbed88410b7981d2cc7bbd6145b59a319f25c899a33c1587f(
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a69cfaf96dab720314a86b2aba1a3764d5dad9597e92d15b07c21a58a886d884(
    *,
    iam: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b75ace651f25eb081badf2271fb655bc4c0850e36bafe6b474f39e00935bb0c7(
    *,
    certificate_authorities: typing.Optional[typing.Sequence[_aws_cdk_aws_acmpca_ceddda9d.ICertificateAuthority]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfa989fad1cbc8518acad9bce75e30465e418b0228fe1dd3da8649e86a493beb(
    *,
    tls: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b540b95307fdb73492eba61e5c3ad3f2ea64ba068d1b2d8d32d407a1f8dd7d37(
    *,
    iam: typing.Optional[builtins.bool] = None,
    certificate_authorities: typing.Optional[typing.Sequence[_aws_cdk_aws_acmpca_ceddda9d.ICertificateAuthority]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0dd164ca1ef03c7ef58c6ede71291df119a9209e2a306b7a115179da71da707(
    *,
    iam: typing.Optional[builtins.bool] = None,
    tls: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass
