r'''
# DataCatalogDatabase

AWS Glue Catalog database for an Amazon S3 dataset.

## Overview

`DataCatalogDatabase` is an [AWS Glue Data Catalog Database](https://docs.aws.amazon.com/glue/latest/dg/define-database.html) configured for an Amazon S3 based dataset:

* The database default location is pointing to an S3 bucket location `s3://<locationBucket>/<locationPrefix>/`
* The database can store various tables structured in their respective prefixes, for example: `s3://<locationBucket>/<locationPrefix>/<table_prefix>/`
* By default, a database level crawler is scheduled to run once a day (00:01h local timezone). The crawler can be disabled and the schedule/frequency of the crawler can be modified with a cron expression.
* The permission model of the database can use IAM, LakeFormation or Hybrid mode.

![Data Catalog Database](../../../website/static/img/adsf-data-catalog.png)

:::caution Data Catalog encryption
The AWS Glue Data Catalog resources created by the `DataCatalogDatabase` construct are not encrypted because the encryption is only available at the catalog level. Changing the encryption at the catalog level has a wide impact on existing Glue resources and producers/consumers. Similarly, changing the encryption configuration at the catalog level after this construct is deployed can break all the resources created as part of DSF on AWS.
:::

## Usage

```python
class ExampleDefaultDataCatalogDatabaseStack(cdk.Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)
        bucket = Bucket(self, "DataCatalogBucket")

        dsf.governance.DataCatalogDatabase(self, "DataCatalogDatabase",
            location_bucket=bucket,
            location_prefix="/databasePath",
            name="example-db"
        )
```

## Using Lake Formation permission model

You can change the default permission model of the database to use [Lake Formation](https://docs.aws.amazon.com/lake-formation/latest/dg/how-it-works.html) exclusively or [hybrid mode](https://docs.aws.amazon.com/lake-formation/latest/dg/hybrid-access-mode.html).

Changing the permission model to Lake Formation or Hybrid has the following impact:

* The CDK provisioning role is added as a Lake Formation administrator so it can perform Lake Formation operations
* The IAMAllowedPrincipal grant is removed from the database to enforce Lake Formation as the unique permission model (only for Lake Formation permission model)

:::caution Lake Formation Data Lake Settings
Lake Formation and Hybrid permission models are configured using PutDataLakeSettings API call. Concurrent API calls can lead to throttling. If you create multiple `DataCatalogDatabases`, it's recommended to create dependencies between the `dataLakeSettings` that are exposed in each database to avoid concurrent calls. See the example in the `DataLakeCatalog`construct [here](https://github.com/awslabs/data-solutions-framework-on-aws/blob/main/framework/src/governance/lib/data-lake-catalog.ts#L137)
:::

```python
class ExampleDefaultDataCatalogDatabaseStack(cdk.Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)
        bucket = Bucket(self, "DataCatalogBucket")

        dsf.governance.DataCatalogDatabase(self, "DataCatalogDatabase",
            location_bucket=bucket,
            location_prefix="/databasePath",
            name="example-db",
            permission_model=dsf.utils.PermissionModel.LAKE_FORMATION
        )
```

## Modifying the crawler behavior

You can change the default configuration of the AWS Glue Crawler to match your requirements:

* Enable or disable the crawler
* Change the crawler run frequency
* Provide your own key to encrypt the crawler logs

```python
encryption_key = Key(self, "CrawlerLogEncryptionKey")

dsf.governance.DataCatalogDatabase(self, "DataCatalogDatabase",
    location_bucket=bucket,
    location_prefix="/databasePath",
    name="example-db",
    auto_crawl=True,
    auto_crawl_schedule=cdk.aws_glue.CfnCrawler.ScheduleProperty(
        schedule_expression="cron(1 0 * * ? *)"
    ),
    crawler_log_encryption_key=encryption_key,
    crawler_table_level_depth=3
)
```

# DataLakeCatalog

AWS Glue Catalog databases on top of a DataLakeStorage.

## Overview

`DataLakeCatalog` is a data catalog for your data lake. It's a set of [AWS Glue Data Catalog Databases](https://docs.aws.amazon.com/glue/latest/dg/define-database.html) configured on top of a [`DataLakeStorage`](../storage/README.md#datalakestorage).
The construct creates three databases pointing to the respective medallion layers (bronze, silve or gold) of the `DataLakeStorage`:

* The database default location is pointing to the corresponding S3 bucket location `s3://<locationBucket>/<locationPrefix>/`
* By default, each database has an active crawler scheduled to run once a day (00:01h local timezone). The crawler can be disabled and the schedule/frequency of the crawler can be modified with a cron expression.

![Data Lake Catalog](../../../website/static/img/adsf-data-lake-catalog.png)

:::caution Data Catalog encryption
The AWS Glue Data Catalog resources created by the `DataCatalogDatabase` construct are not encrypted because the encryption is only available at the catalog level. Changing the encryption at the catalog level has a wide impact on existing Glue resources and producers/consumers. Similarly, changing the encryption configuration at the catalog level after this construct is deployed can break all the resources created as part of DSF on AWS.
:::

## Usage

```python
class ExampleDefaultDataLakeCatalogStack(cdk.Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)
        storage = dsf.storage.DataLakeStorage(self, "MyDataLakeStorage")

        dsf.governance.DataLakeCatalog(self, "DataCatalog",
            data_lake_storage=storage
        )
```

## Modifying the crawlers behavior for the entire catalog

You can change the default configuration of the AWS Glue Crawlers associated with the different databases to match your requirements:

* Enable or disable the crawlers
* Change the crawlers run frequency
* Provide your own key to encrypt the crawlers logs

The parameters apply to the three databases, if you need fine-grained configuration per database, you can use the [DataCatalogDatabase](#datacatalogdatabase) construct.

```python
encryption_key = Key(self, "CrawlerLogEncryptionKey")

dsf.governance.DataLakeCatalog(self, "DataCatalog",
    data_lake_storage=storage,
    auto_crawl=True,
    auto_crawl_schedule=cdk.aws_glue.CfnCrawler.ScheduleProperty(
        schedule_expression="cron(1 0 * * ? *)"
    ),
    crawler_log_encryption_key=encryption_key,
    crawler_table_level_depth=3
)
```

# DataZoneMskAuthorizer

Custom DataZone MSK authorizer for granting access to MSK topics via DataZone asset subscription workflow.

## Overview

The DataZone MSK Authorizer is a custom process integrated with DataZone that implements the [Subscription Grant](https://docs.aws.amazon.com/datazone/latest/userguide/grant-access-to-unmanaged-asset.html) concept for Kafka topics hosted on Amazon MSK (provisioned and Serverless),
secured by IAM policies, and registered in DataZone using the `DataZoneMskAssetType`.
It supports:

* cross account access with MSK Provisioned clusters.
* MSK managed VPC connectivity permissions with MSK Provisioned clusters
* Glue Schema Registry permissions when sharing in the same account

The authorizer is composed of 2 constructs:

* the `DataZoneMskCentralAuthorizer` is responsible for collecting metadata on the Subscription Grant, orchestrating the workflow and acknowledging the Subscription Grant creation. This construct must be deployed in the AWS root account of the DataZone Domain.
* the `DataZoneMskEnvironmentAuthorizer` is responsible for managing the permissions on the producer and consumer side. This construct must be deployed once per account associated with the DataZone Domain.

The cross-account synchronization is exclusively done via EventBridge bus to restrict cross account permissions to the minimum.

![DataZoneMskAuthorizer](../../../website/static/img/datazone-msk-authorizer.png)

## DataZoneMskCentralAuthorizer

The `DataZoneMskCentralAuthorizer` is the central component that receives all the Subscription Grant Requests from DataZone for the `MskTopicAssetType` and orchestrate the end-to-end workflow.
The workflow is a Step Functions State Machine that is triggered by [events emmitted by DataZone](https://docs.aws.amazon.com/datazone/latest/userguide/working-with-events-and-notifications.html) and contains the following steps:

1. Metadata collection: a Lambda Function collect additional information from DataZone on the producer, the subscriber and update the status of the Subscription Grant to `IN_PROGESS`.
2. Producer grant trigger: an event is sent to the producer account to request the creation of the grant on the producer MSK cluster (implemented in the `DataZoneMskEnvironmentAuthorizer`). This step is an asynchronous state using a callback mechanism from the `DataZoneMskEnvironmentAuthorizer`.
3. Consumer grant trigger: an event is sent to the consumer account to request the creation of the grant on the IAM consumer Role (implemented in the `DataZoneMskEnvironmentAuthorizer`). This step is an asynchronous state using a callback mechanism from the `DataZoneMskEnvironmentAuthorizer`.
4. DataZone Subscription Grant callback: a Lambda Function updates the status of the Subscription Grant in DataZone to `GRANTED` or `REVOKE` based on the initial request.

If any failure happens during the process, the Step Functions catch the exceptions and updates the status of the Subscription Grant to `GRANT_FAILED` or `REVOKE_FAILED`.

:::info Permission grant failure
If the grant fails for the consumer, the grant already done for the producer is not reverted but the user is notified within DataZone because the failure is propagated.
The authorizer process is idempotent so it's safe to replay the workflow and all the permissions will be deduplicated. If it's not replayed, the producer grant needs to be manually cleaned up.
:::

### Usage

```python
dsf.governance.DataZoneMskCentralAuthorizer(self, "MskAuthorizer",
    domain_id="aba_dc999t9ime9sss"
)
```

### Register producer and consumer accounts

The `DataZoneMskCentralAuthorizer` construct work in collaboration with the `DataZoneMskEnvironmentAuthorizer` construct which is deployed into the producers and consumers accounts.
To enable the integration, register accounts using the `registerAccount()` method on the `DataZoneMskCentralAuthorizer` object.
It will grant the required permissions so the central account and the environment accounts can communicate via EventBridge events.

```python
central_authorizer = dsf.governance.DataZoneMskCentralAuthorizer(self, "MskAuthorizer",
    domain_id="aba_dc999t9ime9sss"
)

# Add an account that is associated with the DataZone Domain
central_authorizer.register_account("AccountRegistration", "123456789012")
```

## DataZoneMskEnvironmentAuthorizer

The `DataZoneMskEnvironmentAuthorizer` is responsible from managing the permissions required to grant access on MSK Topics (and associated Glue Schema Registry) via IAM policies.
The workflow is a Step Functions State Machine that is triggered by events emitted by the `DataZoneMskCentralAuthorizer` and contains the following steps:

1. Grant the producer or consumer based on the request. If the event is a cross-account producer grant, a Lambda function adds an IAM policy statement to the MSK Cluster policy granting read access to the IAM consumer Role. Optionally, it can also grant the use of MSK Managed VPC.
2. Callback the `DataZoneMskCentralAuthorizer`: an EventBridge event is sent on the central EventBridge Bus to continue the workflow on the central account using the callback mechanism of Step Functions.

### Usage

```python
dsf.governance.DataZoneMskEnvironmentAuthorizer(self, "MskAuthorizer",
    domain_id="aba_dc999t9ime9sss"
)
```

### Restricting IAM permissions on consumer roles with IAM permissions boundary

The construct is based on a Lambda Function that grants IAM Roles with policies using the IAM API `PutRolePolicy`.
Permissions applied to the consumer Roles can be restricted using IAM Permissions Boundaries. The `DataZoneMskEnvironmentAuthorizer` construct provides a static member containing the IAM Statement to include in the IAM permission boundary of the consumer role.

```python
permission_boundary_policy = ManagedPolicy(self, "PermissionBoundaryPolicy",
    statements=[
        # example of other permissions needed by the consumer
        PolicyStatement(
            effect=Effect.ALLOW,
            actions=["s3:*"],
            resources=["*"]
        ), dsf.governance.DataZoneMskEnvironmentAuthorizer.PERMISSIONS_BOUNDARY_STATEMENTS
    ]
)

Role(self, "ConsumerRole",
    assumed_by=ServicePrincipal("lambda.amazonaws.com"),
    permissions_boundary=permission_boundary_policy
)
```

### Cross account workflow

If the `DataZoneMskEnvironmentAuthorizer` is deployed in a different account than the DataZone root account where the `DataZoneMskCentralAuthorizer` is deployed, you need to configure the central account ID to authorize cross-account communication:

```python
dsf.governance.DataZoneMskEnvironmentAuthorizer(self, "MskAuthorizer",
    domain_id="aba_dc999t9ime9sss",
    central_account_id="123456789012"
)
```

### Granting MSK Managed VPC connectivity

For easier cross-account Kafka consumption, MSK Provisioned clusters can use the [multi-VPC private connectivity](https://docs.aws.amazon.com/msk/latest/developerguide/aws-access-mult-vpc.html) feature which is a managed solution that simplifies the networking infrastructure for multi-VPC and cross-account connectivity.

By default, the multi-VPC private connectivity permissions are not configured. You can enable it using the construct properties:

```python
dsf.governance.DataZoneMskEnvironmentAuthorizer(self, "MskAuthorizer",
    domain_id="aba_dc999t9ime9sss",
    central_account_id="123456789012",
    grant_msk_managed_vpc=True
)
```

# DataZoneMskAssetType

DataZone custom asset type for MSK topics.

## Overview

`DataZoneMskAssetType` is a custom asset type implementation for Kafka topics hosted in MSK clusters. MSK clusters can be provisioned or serverless. Topics can be linked to a Glue Schema Registry.
The construct is a CDK custom resource that creates the corresponding DataZone Form Types and Asset Type required to store metadata related to MSK Topics. It includes:

* A MSK Source Reference Form Type containing metadata about the MSK Cluster including the cluster ARN and type.
* A Kafka Schema For Type containing metadata about the topic including the topic name, schema version, Glue Schema Registry ARN and Glue Schema ARN.

![DataZone MSK asset type](../../../website/static/img/datazone-msk-asset-type.png)

## Usage

```python
dsf.governance.DataZoneMskAssetType(self, "DataZoneMskAssetType",
    domain_id="aba_dc999t9ime9sss"
)
```

## Reusing an existing owner project

The `DataZoneMskAssetType` requires a DataZone project to own the custom asset type. By default, it will create a `MskGovernance` project within the domain but you pass an existing project.
The construct will make the IAM custom resource Role a member of the projectto be able to create the asset type and the form types.

```python
dsf.governance.DataZoneMskAssetType(self, "DataZoneMskAssetType",
    domain_id="aba_dc999t9ime9sss",
    project_id="xxxxxxxxxxx"
)
```

## Reusing a Custom Asset Type Factory

By default, the `DataZoneMskAssetType` creates its own factory resources required to connect to DataZone and create the custom asset type. But it's possible to reuse a Factory across multiple Custom Asset Types to limit the number of custom resource providers and DataZone project membership:

```python
data_zone_asset_factory = dsf.governance.DataZoneCustomAssetTypeFactory(self, "DataZoneCustomAssetTypeFactory",
    domain_id="aba_dc999t9ime9sss"
)

dsf.governance.DataZoneMskAssetType(self, "DataZoneMskAssetType",
    domain_id="aba_dc999t9ime9sss",
    project_id="xxxxxxxxxxx",
    dz_custom_asset_type_factory=data_zone_asset_factory
)
```

# DataZoneGsrMskDataSource

DataZone Data Source for MSK Topics assets backed by Glue Schema Registry.

## Overview

`DataZoneGsrMskDataSource` is custom data source for DataZone that can create/update/delete MSK topics assets in DataZone based on a Glue Schema Registry definition. The custom data source can be triggered by a schedule or based on Create or Registering a new Schema Version events from the Glue Schema Registry. The constructs implement:

* EventBridge Rules triggered either on a schedule or event based.
* A Lambda Function triggered from the EventBridge Rules and responsible for collecting metadata from The Glue Schema Registry and updating MSK Topic assets in DataZone.
* SSM Parameter Store Parameters to store required metadata

## Usage

```python
dsf.governance.DataZoneGsrMskDataSource(self, "DataZoneGsrMskDataSource",
    domain_id="aba_dc999t9ime9sss",
    registry_name="schema-registry",
    project_id="999a99aa9aaaaa",
    cluster_name="msk-cluster"
)
```

## Data Source trigger modes

The custom data source process can be triggered in two different ways. By default, if no schedule and events are not enabled, the construct creates a schedule every one hour.

* Based on a Schedule

```python
dsf.governance.DataZoneGsrMskDataSource(self, "DataZoneGsrMskDataSource",
    domain_id="aba_dc999t9ime9sss",
    registry_name="schema-registry",
    project_id="999a99aa9aaaaa",
    cluster_name="msk-cluster",
    run_schedule=events.Schedule.expression("cron(0 * * * * *)")
)
```

* Based on events received from the Glue Schema Registry

```python
dsf.governance.DataZoneGsrMskDataSource(self, "DataZoneGsrMskDataSource",
    domain_id="aba_dc999t9ime9sss",
    registry_name="schema-registry",
    project_id="999a99aa9aaaaa",
    cluster_name="msk-cluster",
    enable_schema_registry_event=True
)
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
import aws_cdk.aws_datazone as _aws_cdk_aws_datazone_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_glue as _aws_cdk_aws_glue_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lakeformation as _aws_cdk_aws_lakeformation_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import aws_cdk.aws_sqs as _aws_cdk_aws_sqs_ceddda9d
import aws_cdk.aws_stepfunctions as _aws_cdk_aws_stepfunctions_ceddda9d
import aws_cdk.custom_resources as _aws_cdk_custom_resources_ceddda9d
import constructs as _constructs_77d1e7e8
from ..storage import DataLakeStorage as _DataLakeStorage_c6c74eec
from ..utils import PermissionModel as _PermissionModel_2366961a


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.AuthorizerCentralWorflow",
    jsii_struct_bases=[],
    name_mapping={
        "authorizer_event_role": "authorizerEventRole",
        "authorizer_event_rule": "authorizerEventRule",
        "callback_role": "callbackRole",
        "dead_letter_key": "deadLetterKey",
        "dead_letter_queue": "deadLetterQueue",
        "state_machine": "stateMachine",
        "state_machine_log_group": "stateMachineLogGroup",
        "state_machine_role": "stateMachineRole",
    },
)
class AuthorizerCentralWorflow:
    def __init__(
        self,
        *,
        authorizer_event_role: _aws_cdk_aws_iam_ceddda9d.IRole,
        authorizer_event_rule: _aws_cdk_aws_events_ceddda9d.IRule,
        callback_role: _aws_cdk_aws_iam_ceddda9d.Role,
        dead_letter_key: _aws_cdk_aws_kms_ceddda9d.IKey,
        dead_letter_queue: _aws_cdk_aws_sqs_ceddda9d.IQueue,
        state_machine: _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine,
        state_machine_log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
        state_machine_role: _aws_cdk_aws_iam_ceddda9d.Role,
    ) -> None:
        '''Interface for the authorizer central workflow.

        :param authorizer_event_role: The authorizer event role for allowing events to invoke the workflow.
        :param authorizer_event_rule: The authorizer event rule for triggering the workflow.
        :param callback_role: The IAM Role used by the State Machine Call Back.
        :param dead_letter_key: The KMS Key used for encryption of the Dead Letter Queue.
        :param dead_letter_queue: The SQS Dead Letter Queue receiving events failure.
        :param state_machine: The authorizer Step Functions state machine.
        :param state_machine_log_group: The CloudWatch Log Group for logging the state machine.
        :param state_machine_role: The IAM Role used by the State Machine.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a11223a197a87f6709a9f284f5302fc9ff3607ce04757251f5664ba0419acfcb)
            check_type(argname="argument authorizer_event_role", value=authorizer_event_role, expected_type=type_hints["authorizer_event_role"])
            check_type(argname="argument authorizer_event_rule", value=authorizer_event_rule, expected_type=type_hints["authorizer_event_rule"])
            check_type(argname="argument callback_role", value=callback_role, expected_type=type_hints["callback_role"])
            check_type(argname="argument dead_letter_key", value=dead_letter_key, expected_type=type_hints["dead_letter_key"])
            check_type(argname="argument dead_letter_queue", value=dead_letter_queue, expected_type=type_hints["dead_letter_queue"])
            check_type(argname="argument state_machine", value=state_machine, expected_type=type_hints["state_machine"])
            check_type(argname="argument state_machine_log_group", value=state_machine_log_group, expected_type=type_hints["state_machine_log_group"])
            check_type(argname="argument state_machine_role", value=state_machine_role, expected_type=type_hints["state_machine_role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "authorizer_event_role": authorizer_event_role,
            "authorizer_event_rule": authorizer_event_rule,
            "callback_role": callback_role,
            "dead_letter_key": dead_letter_key,
            "dead_letter_queue": dead_letter_queue,
            "state_machine": state_machine,
            "state_machine_log_group": state_machine_log_group,
            "state_machine_role": state_machine_role,
        }

    @builtins.property
    def authorizer_event_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The authorizer event role for allowing events to invoke the workflow.'''
        result = self._values.get("authorizer_event_role")
        assert result is not None, "Required property 'authorizer_event_role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, result)

    @builtins.property
    def authorizer_event_rule(self) -> _aws_cdk_aws_events_ceddda9d.IRule:
        '''The authorizer event rule for triggering the workflow.'''
        result = self._values.get("authorizer_event_rule")
        assert result is not None, "Required property 'authorizer_event_rule' is missing"
        return typing.cast(_aws_cdk_aws_events_ceddda9d.IRule, result)

    @builtins.property
    def callback_role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''The IAM Role used by the State Machine Call Back.'''
        result = self._values.get("callback_role")
        assert result is not None, "Required property 'callback_role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, result)

    @builtins.property
    def dead_letter_key(self) -> _aws_cdk_aws_kms_ceddda9d.IKey:
        '''The KMS Key used for encryption of the Dead Letter Queue.'''
        result = self._values.get("dead_letter_key")
        assert result is not None, "Required property 'dead_letter_key' is missing"
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.IKey, result)

    @builtins.property
    def dead_letter_queue(self) -> _aws_cdk_aws_sqs_ceddda9d.IQueue:
        '''The SQS Dead Letter Queue receiving events failure.'''
        result = self._values.get("dead_letter_queue")
        assert result is not None, "Required property 'dead_letter_queue' is missing"
        return typing.cast(_aws_cdk_aws_sqs_ceddda9d.IQueue, result)

    @builtins.property
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''The authorizer Step Functions state machine.'''
        result = self._values.get("state_machine")
        assert result is not None, "Required property 'state_machine' is missing"
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, result)

    @builtins.property
    def state_machine_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Log Group for logging the state machine.'''
        result = self._values.get("state_machine_log_group")
        assert result is not None, "Required property 'state_machine_log_group' is missing"
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, result)

    @builtins.property
    def state_machine_role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''The IAM Role used by the State Machine.'''
        result = self._values.get("state_machine_role")
        assert result is not None, "Required property 'state_machine_role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthorizerCentralWorflow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.AuthorizerEnvironmentWorflow",
    jsii_struct_bases=[],
    name_mapping={
        "state_machine": "stateMachine",
        "state_machine_log_group": "stateMachineLogGroup",
        "state_machine_role": "stateMachineRole",
    },
)
class AuthorizerEnvironmentWorflow:
    def __init__(
        self,
        *,
        state_machine: _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine,
        state_machine_log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
        state_machine_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    ) -> None:
        '''The interface representing the environment custom authorizer workflow.

        :param state_machine: The state machine that orchestrates the workflow.
        :param state_machine_log_group: The log group where the state machine logs are stored.
        :param state_machine_role: The IAM Role used by the State Machine.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43c8d2aeb019754a37ab8cb0270e859bdb56b4b38d6a38bd4ad62e3b3bd43c2d)
            check_type(argname="argument state_machine", value=state_machine, expected_type=type_hints["state_machine"])
            check_type(argname="argument state_machine_log_group", value=state_machine_log_group, expected_type=type_hints["state_machine_log_group"])
            check_type(argname="argument state_machine_role", value=state_machine_role, expected_type=type_hints["state_machine_role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "state_machine": state_machine,
            "state_machine_log_group": state_machine_log_group,
            "state_machine_role": state_machine_role,
        }

    @builtins.property
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine:
        '''The state machine that orchestrates the workflow.'''
        result = self._values.get("state_machine")
        assert result is not None, "Required property 'state_machine' is missing"
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine, result)

    @builtins.property
    def state_machine_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The log group where the state machine logs are stored.'''
        result = self._values.get("state_machine_log_group")
        assert result is not None, "Required property 'state_machine_log_group' is missing"
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, result)

    @builtins.property
    def state_machine_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM Role used by the State Machine.'''
        result = self._values.get("state_machine_role")
        assert result is not None, "Required property 'state_machine_role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthorizerEnvironmentWorflow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.CustomAssetType",
    jsii_struct_bases=[],
    name_mapping={
        "domain_id": "domainId",
        "name": "name",
        "project_identifier": "projectIdentifier",
        "revision": "revision",
    },
)
class CustomAssetType:
    def __init__(
        self,
        *,
        domain_id: builtins.str,
        name: builtins.str,
        project_identifier: builtins.str,
        revision: builtins.str,
    ) -> None:
        '''Interface representing a DataZone custom asset type.

        :param domain_id: The domain identifier of the custom asset type.
        :param name: The name of the custom asset type.
        :param project_identifier: The project identifier owner of the custom asset type.
        :param revision: The revision of the custom asset type.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3fac04e77ad4ffe8a8908a1aac9c24ed840e843b1f58f5f3959e5ccf35cbc84)
            check_type(argname="argument domain_id", value=domain_id, expected_type=type_hints["domain_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument project_identifier", value=project_identifier, expected_type=type_hints["project_identifier"])
            check_type(argname="argument revision", value=revision, expected_type=type_hints["revision"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_id": domain_id,
            "name": name,
            "project_identifier": project_identifier,
            "revision": revision,
        }

    @builtins.property
    def domain_id(self) -> builtins.str:
        '''The domain identifier of the custom asset type.'''
        result = self._values.get("domain_id")
        assert result is not None, "Required property 'domain_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the custom asset type.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_identifier(self) -> builtins.str:
        '''The project identifier owner of the custom asset type.'''
        result = self._values.get("project_identifier")
        assert result is not None, "Required property 'project_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def revision(self) -> builtins.str:
        '''The revision of the custom asset type.'''
        result = self._values.get("revision")
        assert result is not None, "Required property 'revision' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomAssetType(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataCatalogDatabase(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataCatalogDatabase",
):
    '''An AWS Glue Data Catalog Database configured with the location and a crawler.

    :see: https://awslabs.github.io/data-solutions-framework-on-aws/docs/constructs/library/Governance/data-catalog-database

    Example::

        from aws_cdk.aws_s3 import Bucket
        
        
        dsf.governance.DataCatalogDatabase(self, "ExampleDatabase",
            location_bucket=Bucket(scope, "LocationBucket"),
            location_prefix="/databasePath",
            name="example-db"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        auto_crawl: typing.Optional[builtins.bool] = None,
        auto_crawl_schedule: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.ScheduleProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        crawler_log_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        crawler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        crawler_table_level_depth: typing.Optional[jsii.Number] = None,
        glue_connection_name: typing.Optional[builtins.str] = None,
        jdbc_path: typing.Optional[builtins.str] = None,
        jdbc_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        jdbc_secret_kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lake_formation_configuration_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        lake_formation_data_access_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        location_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        location_prefix: typing.Optional[builtins.str] = None,
        permission_model: typing.Optional[_PermissionModel_2366961a] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name: Database name. Construct would add a randomize suffix as part of the name to prevent name collisions.
        :param auto_crawl: When enabled, this automatically creates a top level Glue Crawler that would run based on the defined schedule in the ``autoCrawlSchedule`` parameter. Default: - True
        :param auto_crawl_schedule: The schedule to run the Glue Crawler. Default is once a day at 00:01h. Default: - ``cron(1 0 * * ? *)``
        :param crawler_log_encryption_key: KMS encryption Key used for the Glue Crawler logs. Default: - Create a new key if none is provided
        :param crawler_role: The IAM Role used by the Glue Crawler when ``autoCrawl`` is set to ``True``. Additional permissions are granted to this role such as S3 Bucket read only permissions and KMS encrypt/decrypt on the key used by the Glue Crawler logging to CloudWatch Logs. Default: - When ``autoCrawl`` is enabled, a new role is created with least privilege permissions to run the crawler
        :param crawler_table_level_depth: Directory depth where the table folders are located. This helps the Glue Crawler understand the layout of the folders in S3. Default: - calculated based on ``locationPrefix``
        :param glue_connection_name: The connection that would be used by the crawler.
        :param jdbc_path: The JDBC path that would be included by the crawler.
        :param jdbc_secret: The secret associated with the JDBC connection.
        :param jdbc_secret_kms_key: The KMS key used by the JDBC secret.
        :param lake_formation_configuration_role: The IAM Role assumed by the construct resources to perform Lake Formation configuration. The role is assumed by Lambda functions to perform Lake Formation related operations. Only needed when permissionModel is set to Lake Formation or Hybrid Default: - A new role is created
        :param lake_formation_data_access_role: The IAM Role used by Lake Formation for `data access <https://docs.aws.amazon.com/lake-formation/latest/dg/registration-role.html>`_. The role is assumed by Lake Formation to provide temporary credentials to query engines. Only needed when permissionModel is set to Lake Formation or Hybrid. Default: - A new role is created
        :param location_bucket: S3 bucket where data is stored.
        :param location_prefix: Top level location where table data is stored. Default: - the root of the bucket is used as the location prefix.
        :param permission_model: The permission model to apply to the Glue Database. Default: - IAM permission model is used
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bdf34484b2d4ebd1a8f3a29baa43bc5474f4f0d5c594cf16af37af6e8b0946e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DataCatalogDatabaseProps(
            name=name,
            auto_crawl=auto_crawl,
            auto_crawl_schedule=auto_crawl_schedule,
            crawler_log_encryption_key=crawler_log_encryption_key,
            crawler_role=crawler_role,
            crawler_table_level_depth=crawler_table_level_depth,
            glue_connection_name=glue_connection_name,
            jdbc_path=jdbc_path,
            jdbc_secret=jdbc_secret,
            jdbc_secret_kms_key=jdbc_secret_kms_key,
            lake_formation_configuration_role=lake_formation_configuration_role,
            lake_formation_data_access_role=lake_formation_data_access_role,
            location_bucket=location_bucket,
            location_prefix=location_prefix,
            permission_model=permission_model,
            removal_policy=removal_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="grantReadOnlyAccess")
    def grant_read_only_access(
        self,
        principal: _aws_cdk_aws_iam_ceddda9d.IPrincipal,
    ) -> _aws_cdk_aws_iam_ceddda9d.AddToPrincipalPolicyResult:
        '''Grants read access via identity based policy to the principal.

        This would attach an IAM Policy to the principal allowing read access to the Glue Database and all its Glue Tables.
        Only valid for IAM permission model.

        :param principal: Principal to attach the Glue Database read access to.

        :return: ``AddToPrincipalPolicyResult``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__822d38f353e70d056dab26de7762635d594eaa647844feb41d648fcfe3e931df)
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.AddToPrincipalPolicyResult, jsii.invoke(self, "grantReadOnlyAccess", [principal]))

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
    @jsii.member(jsii_name="database")
    def database(self) -> _aws_cdk_aws_glue_ceddda9d.CfnDatabase:
        '''The Glue Database that's created.'''
        return typing.cast(_aws_cdk_aws_glue_ceddda9d.CfnDatabase, jsii.get(self, "database"))

    @builtins.property
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        '''The Glue Database name with the randomized suffix to prevent name collisions in the catalog.'''
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @builtins.property
    @jsii.member(jsii_name="crawler")
    def crawler(self) -> typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnCrawler]:
        '''The Glue Crawler created when ``autoCrawl`` is set to ``true`` (default value).

        This property can be undefined if ``autoCrawl`` is set to ``false``.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnCrawler], jsii.get(self, "crawler"))

    @builtins.property
    @jsii.member(jsii_name="crawlerLakeFormationDatabaseGrant")
    def crawler_lake_formation_database_grant(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lakeformation_ceddda9d.CfnPrincipalPermissions]:
        '''The Lake Formation grant on the database for the Crawler when Lake Formation or Hybrid is used.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_lakeformation_ceddda9d.CfnPrincipalPermissions], jsii.get(self, "crawlerLakeFormationDatabaseGrant"))

    @builtins.property
    @jsii.member(jsii_name="crawlerLakeFormationLocationGrant")
    def crawler_lake_formation_location_grant(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lakeformation_ceddda9d.CfnPrincipalPermissions]:
        '''The Lake Formation grant on the data location for the Crawler when Lake Formation or Hybrid is used.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_lakeformation_ceddda9d.CfnPrincipalPermissions], jsii.get(self, "crawlerLakeFormationLocationGrant"))

    @builtins.property
    @jsii.member(jsii_name="crawlerLakeFormationTablesGrant")
    def crawler_lake_formation_tables_grant(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lakeformation_ceddda9d.CfnPrincipalPermissions]:
        '''The Lake Formation grant on the tables for the Crawler when Lake Formation or Hybrid is used.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_lakeformation_ceddda9d.CfnPrincipalPermissions], jsii.get(self, "crawlerLakeFormationTablesGrant"))

    @builtins.property
    @jsii.member(jsii_name="crawlerLogEncryptionKey")
    def crawler_log_encryption_key(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''KMS encryption Key used by the Crawler.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "crawlerLogEncryptionKey"))

    @builtins.property
    @jsii.member(jsii_name="crawlerRole")
    def crawler_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used by the Glue crawler when created.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "crawlerRole"))

    @builtins.property
    @jsii.member(jsii_name="crawlerSecurityConfiguration")
    def crawler_security_configuration(
        self,
    ) -> typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnSecurityConfiguration]:
        '''The Glue security configuration used by the Glue Crawler when created.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnSecurityConfiguration], jsii.get(self, "crawlerSecurityConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="dataLakeLocation")
    def data_lake_location(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lakeformation_ceddda9d.CfnResource]:
        '''The Lake Formation data lake location.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_lakeformation_ceddda9d.CfnResource], jsii.get(self, "dataLakeLocation"))

    @builtins.property
    @jsii.member(jsii_name="dataLakeSettings")
    def data_lake_settings(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lakeformation_ceddda9d.CfnDataLakeSettings]:
        '''The DataLakeSettings for Lake Formation.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_lakeformation_ceddda9d.CfnDataLakeSettings], jsii.get(self, "dataLakeSettings"))

    @builtins.property
    @jsii.member(jsii_name="lakeFormationDataAccessRole")
    def lake_formation_data_access_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used by Lake Formation to access data.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "lakeFormationDataAccessRole"))

    @builtins.property
    @jsii.member(jsii_name="lakeFormationRevokeRole")
    def lake_formation_revoke_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used to revoke LakeFormation IAMAllowedPrincipals.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "lakeFormationRevokeRole"))

    @builtins.property
    @jsii.member(jsii_name="revokeIamAllowedPrincipal")
    def revoke_iam_allowed_principal(
        self,
    ) -> typing.Optional[_aws_cdk_custom_resources_ceddda9d.AwsCustomResource]:
        '''The custom resource for revoking IAM permissions from the database.'''
        return typing.cast(typing.Optional[_aws_cdk_custom_resources_ceddda9d.AwsCustomResource], jsii.get(self, "revokeIamAllowedPrincipal"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataCatalogDatabaseProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "auto_crawl": "autoCrawl",
        "auto_crawl_schedule": "autoCrawlSchedule",
        "crawler_log_encryption_key": "crawlerLogEncryptionKey",
        "crawler_role": "crawlerRole",
        "crawler_table_level_depth": "crawlerTableLevelDepth",
        "glue_connection_name": "glueConnectionName",
        "jdbc_path": "jdbcPath",
        "jdbc_secret": "jdbcSecret",
        "jdbc_secret_kms_key": "jdbcSecretKMSKey",
        "lake_formation_configuration_role": "lakeFormationConfigurationRole",
        "lake_formation_data_access_role": "lakeFormationDataAccessRole",
        "location_bucket": "locationBucket",
        "location_prefix": "locationPrefix",
        "permission_model": "permissionModel",
        "removal_policy": "removalPolicy",
    },
)
class DataCatalogDatabaseProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        auto_crawl: typing.Optional[builtins.bool] = None,
        auto_crawl_schedule: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.ScheduleProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        crawler_log_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        crawler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        crawler_table_level_depth: typing.Optional[jsii.Number] = None,
        glue_connection_name: typing.Optional[builtins.str] = None,
        jdbc_path: typing.Optional[builtins.str] = None,
        jdbc_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        jdbc_secret_kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        lake_formation_configuration_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        lake_formation_data_access_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        location_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        location_prefix: typing.Optional[builtins.str] = None,
        permission_model: typing.Optional[_PermissionModel_2366961a] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''Properties for the ``DataCatalogDatabase`` construct.

        :param name: Database name. Construct would add a randomize suffix as part of the name to prevent name collisions.
        :param auto_crawl: When enabled, this automatically creates a top level Glue Crawler that would run based on the defined schedule in the ``autoCrawlSchedule`` parameter. Default: - True
        :param auto_crawl_schedule: The schedule to run the Glue Crawler. Default is once a day at 00:01h. Default: - ``cron(1 0 * * ? *)``
        :param crawler_log_encryption_key: KMS encryption Key used for the Glue Crawler logs. Default: - Create a new key if none is provided
        :param crawler_role: The IAM Role used by the Glue Crawler when ``autoCrawl`` is set to ``True``. Additional permissions are granted to this role such as S3 Bucket read only permissions and KMS encrypt/decrypt on the key used by the Glue Crawler logging to CloudWatch Logs. Default: - When ``autoCrawl`` is enabled, a new role is created with least privilege permissions to run the crawler
        :param crawler_table_level_depth: Directory depth where the table folders are located. This helps the Glue Crawler understand the layout of the folders in S3. Default: - calculated based on ``locationPrefix``
        :param glue_connection_name: The connection that would be used by the crawler.
        :param jdbc_path: The JDBC path that would be included by the crawler.
        :param jdbc_secret: The secret associated with the JDBC connection.
        :param jdbc_secret_kms_key: The KMS key used by the JDBC secret.
        :param lake_formation_configuration_role: The IAM Role assumed by the construct resources to perform Lake Formation configuration. The role is assumed by Lambda functions to perform Lake Formation related operations. Only needed when permissionModel is set to Lake Formation or Hybrid Default: - A new role is created
        :param lake_formation_data_access_role: The IAM Role used by Lake Formation for `data access <https://docs.aws.amazon.com/lake-formation/latest/dg/registration-role.html>`_. The role is assumed by Lake Formation to provide temporary credentials to query engines. Only needed when permissionModel is set to Lake Formation or Hybrid. Default: - A new role is created
        :param location_bucket: S3 bucket where data is stored.
        :param location_prefix: Top level location where table data is stored. Default: - the root of the bucket is used as the location prefix.
        :param permission_model: The permission model to apply to the Glue Database. Default: - IAM permission model is used
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        if isinstance(auto_crawl_schedule, dict):
            auto_crawl_schedule = _aws_cdk_aws_glue_ceddda9d.CfnCrawler.ScheduleProperty(**auto_crawl_schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05679d2111c852774397fc96ba1786e51a6f337987ccb847a7924c7d5cca2929)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument auto_crawl", value=auto_crawl, expected_type=type_hints["auto_crawl"])
            check_type(argname="argument auto_crawl_schedule", value=auto_crawl_schedule, expected_type=type_hints["auto_crawl_schedule"])
            check_type(argname="argument crawler_log_encryption_key", value=crawler_log_encryption_key, expected_type=type_hints["crawler_log_encryption_key"])
            check_type(argname="argument crawler_role", value=crawler_role, expected_type=type_hints["crawler_role"])
            check_type(argname="argument crawler_table_level_depth", value=crawler_table_level_depth, expected_type=type_hints["crawler_table_level_depth"])
            check_type(argname="argument glue_connection_name", value=glue_connection_name, expected_type=type_hints["glue_connection_name"])
            check_type(argname="argument jdbc_path", value=jdbc_path, expected_type=type_hints["jdbc_path"])
            check_type(argname="argument jdbc_secret", value=jdbc_secret, expected_type=type_hints["jdbc_secret"])
            check_type(argname="argument jdbc_secret_kms_key", value=jdbc_secret_kms_key, expected_type=type_hints["jdbc_secret_kms_key"])
            check_type(argname="argument lake_formation_configuration_role", value=lake_formation_configuration_role, expected_type=type_hints["lake_formation_configuration_role"])
            check_type(argname="argument lake_formation_data_access_role", value=lake_formation_data_access_role, expected_type=type_hints["lake_formation_data_access_role"])
            check_type(argname="argument location_bucket", value=location_bucket, expected_type=type_hints["location_bucket"])
            check_type(argname="argument location_prefix", value=location_prefix, expected_type=type_hints["location_prefix"])
            check_type(argname="argument permission_model", value=permission_model, expected_type=type_hints["permission_model"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if auto_crawl is not None:
            self._values["auto_crawl"] = auto_crawl
        if auto_crawl_schedule is not None:
            self._values["auto_crawl_schedule"] = auto_crawl_schedule
        if crawler_log_encryption_key is not None:
            self._values["crawler_log_encryption_key"] = crawler_log_encryption_key
        if crawler_role is not None:
            self._values["crawler_role"] = crawler_role
        if crawler_table_level_depth is not None:
            self._values["crawler_table_level_depth"] = crawler_table_level_depth
        if glue_connection_name is not None:
            self._values["glue_connection_name"] = glue_connection_name
        if jdbc_path is not None:
            self._values["jdbc_path"] = jdbc_path
        if jdbc_secret is not None:
            self._values["jdbc_secret"] = jdbc_secret
        if jdbc_secret_kms_key is not None:
            self._values["jdbc_secret_kms_key"] = jdbc_secret_kms_key
        if lake_formation_configuration_role is not None:
            self._values["lake_formation_configuration_role"] = lake_formation_configuration_role
        if lake_formation_data_access_role is not None:
            self._values["lake_formation_data_access_role"] = lake_formation_data_access_role
        if location_bucket is not None:
            self._values["location_bucket"] = location_bucket
        if location_prefix is not None:
            self._values["location_prefix"] = location_prefix
        if permission_model is not None:
            self._values["permission_model"] = permission_model
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def name(self) -> builtins.str:
        '''Database name.

        Construct would add a randomize suffix as part of the name to prevent name collisions.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_crawl(self) -> typing.Optional[builtins.bool]:
        '''When enabled, this automatically creates a top level Glue Crawler that would run based on the defined schedule in the ``autoCrawlSchedule`` parameter.

        :default: - True
        '''
        result = self._values.get("auto_crawl")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_crawl_schedule(
        self,
    ) -> typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.ScheduleProperty]:
        '''The schedule to run the Glue Crawler.

        Default is once a day at 00:01h.

        :default: - ``cron(1 0 * * ? *)``
        '''
        result = self._values.get("auto_crawl_schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.ScheduleProperty], result)

    @builtins.property
    def crawler_log_encryption_key(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''KMS encryption Key used for the Glue Crawler logs.

        :default: - Create a new key if none is provided
        '''
        result = self._values.get("crawler_log_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def crawler_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used by the Glue Crawler when ``autoCrawl`` is set to ``True``.

        Additional permissions are granted to this role such as S3 Bucket read only permissions and KMS encrypt/decrypt on the key used by the Glue Crawler logging to CloudWatch Logs.

        :default: - When ``autoCrawl`` is enabled, a new role is created with least privilege permissions to run the crawler
        '''
        result = self._values.get("crawler_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def crawler_table_level_depth(self) -> typing.Optional[jsii.Number]:
        '''Directory depth where the table folders are located.

        This helps the Glue Crawler understand the layout of the folders in S3.

        :default: - calculated based on ``locationPrefix``
        '''
        result = self._values.get("crawler_table_level_depth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def glue_connection_name(self) -> typing.Optional[builtins.str]:
        '''The connection that would be used by the crawler.'''
        result = self._values.get("glue_connection_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jdbc_path(self) -> typing.Optional[builtins.str]:
        '''The JDBC path that would be included by the crawler.'''
        result = self._values.get("jdbc_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jdbc_secret(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        '''The secret associated with the JDBC connection.'''
        result = self._values.get("jdbc_secret")
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], result)

    @builtins.property
    def jdbc_secret_kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS key used by the JDBC secret.'''
        result = self._values.get("jdbc_secret_kms_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def lake_formation_configuration_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role assumed by the construct resources to perform Lake Formation configuration.

        The role is assumed by Lambda functions to perform Lake Formation related operations.
        Only needed when permissionModel is set to Lake Formation or Hybrid

        :default: - A new role is created
        '''
        result = self._values.get("lake_formation_configuration_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def lake_formation_data_access_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used by Lake Formation for `data access <https://docs.aws.amazon.com/lake-formation/latest/dg/registration-role.html>`_. The role is assumed by Lake Formation to provide temporary credentials to query engines. Only needed when permissionModel is set to Lake Formation or Hybrid.

        :default: - A new role is created
        '''
        result = self._values.get("lake_formation_data_access_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def location_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''S3 bucket where data is stored.'''
        result = self._values.get("location_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def location_prefix(self) -> typing.Optional[builtins.str]:
        '''Top level location where table data is stored.

        :default: - the root of the bucket is used as the location prefix.
        '''
        result = self._values.get("location_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permission_model(self) -> typing.Optional[_PermissionModel_2366961a]:
        '''The permission model to apply to the Glue Database.

        :default: - IAM permission model is used
        '''
        result = self._values.get("permission_model")
        return typing.cast(typing.Optional[_PermissionModel_2366961a], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataCatalogDatabaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataLakeCatalog(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataLakeCatalog",
):
    '''Creates a Data Lake Catalog on top of a ``DataLakeStorage``.

    The Data Lake Catalog is composed of 3 ``DataCatalogDatabase``, one for each storage layer.

    :see: https://awslabs.github.io/data-solutions-framework-on-aws/docs/constructs/library/Governance/data-lake-catalog

    Example::

        from aws_cdk.aws_kms import Key
        
        
        log_encryption_key = Key(self, "ExampleLogKey")
        storage = dsf.storage.DataLakeStorage(self, "ExampleStorage")
        data_lake_catalog = dsf.governance.DataLakeCatalog(self, "ExampleDataLakeCatalog",
            data_lake_storage=storage,
            database_name="exampledb",
            crawler_log_encryption_key=log_encryption_key
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        data_lake_storage: _DataLakeStorage_c6c74eec,
        auto_crawl: typing.Optional[builtins.bool] = None,
        auto_crawl_schedule: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.ScheduleProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        crawler_log_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        crawler_table_level_depth: typing.Optional[jsii.Number] = None,
        database_name: typing.Optional[builtins.str] = None,
        lake_formation_configuration_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        lake_formation_data_access_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        permission_model: typing.Optional[_PermissionModel_2366961a] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''Constructs a new instance of DataLakeCatalog.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param data_lake_storage: The DataLakeStorage object to create the data catalog on.
        :param auto_crawl: When enabled, creates a top level Glue Crawler that would run based on the defined schedule in the ``autoCrawlSchedule`` parameter. Default: - True
        :param auto_crawl_schedule: The schedule when the Glue Crawler runs, if enabled. Default is once a day at 00:01h. Default: - ``cron(1 0 * * ? *)``
        :param crawler_log_encryption_key: The KMS encryption Key used for the Glue Crawler logs. Default: - Create a new KMS Key if none is provided
        :param crawler_table_level_depth: Directory depth where the table folders are located. This helps the Glue Crawler understand the layout of the folders in S3. Default: - calculated based on ``locationPrefix``
        :param database_name: The suffix of the Glue Data Catalog Database. The name of the Glue Database is composed of the S3 Bucket name and this suffix. The suffix is also added to the S3 location inside the data lake S3 Buckets. Default: - Use the bucket name as the database name and as the S3 location
        :param lake_formation_configuration_role: The IAM Role assumed by the construct resources to perform Lake Formation configuration. Only needed when permissionModel is set to Lake Formation or Hybrid Default: - A new role is created for the entire Data Lake
        :param lake_formation_data_access_role: The IAM Role used by Lake Formation for `data access <https://docs.aws.amazon.com/lake-formation/latest/dg/access-control-underlying-data.html>`_. The role will be used for accessing all the layers of the data lake (bronze, silver, gold). Only needed when permissionModel is set to Lake Formation or Hybrid. Default: - A new role is created for the entire Data Lake
        :param permission_model: The permission model to apply to the Glue Database. Default: - IAM permission model is used
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7805f98b85e606ebfe36a50c42afa1e8c258fbc8c6dac7b7f9d5233436f5185)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DataLakeCatalogProps(
            data_lake_storage=data_lake_storage,
            auto_crawl=auto_crawl,
            auto_crawl_schedule=auto_crawl_schedule,
            crawler_log_encryption_key=crawler_log_encryption_key,
            crawler_table_level_depth=crawler_table_level_depth,
            database_name=database_name,
            lake_formation_configuration_role=lake_formation_configuration_role,
            lake_formation_data_access_role=lake_formation_data_access_role,
            permission_model=permission_model,
            removal_policy=removal_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

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
    @jsii.member(jsii_name="bronzeCatalogDatabase")
    def bronze_catalog_database(self) -> DataCatalogDatabase:
        '''The Glue Database for the Bronze S3 Bucket.'''
        return typing.cast(DataCatalogDatabase, jsii.get(self, "bronzeCatalogDatabase"))

    @builtins.property
    @jsii.member(jsii_name="goldCatalogDatabase")
    def gold_catalog_database(self) -> DataCatalogDatabase:
        '''The Glue Database for the Gold S3 Bucket.'''
        return typing.cast(DataCatalogDatabase, jsii.get(self, "goldCatalogDatabase"))

    @builtins.property
    @jsii.member(jsii_name="silverCatalogDatabase")
    def silver_catalog_database(self) -> DataCatalogDatabase:
        '''The Glue Database for the Silver S3 Bucket.'''
        return typing.cast(DataCatalogDatabase, jsii.get(self, "silverCatalogDatabase"))

    @builtins.property
    @jsii.member(jsii_name="crawlerLogEncryptionKey")
    def crawler_log_encryption_key(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS Key used to encrypt the Glue Crawler logs.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "crawlerLogEncryptionKey"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataLakeCatalogProps",
    jsii_struct_bases=[],
    name_mapping={
        "data_lake_storage": "dataLakeStorage",
        "auto_crawl": "autoCrawl",
        "auto_crawl_schedule": "autoCrawlSchedule",
        "crawler_log_encryption_key": "crawlerLogEncryptionKey",
        "crawler_table_level_depth": "crawlerTableLevelDepth",
        "database_name": "databaseName",
        "lake_formation_configuration_role": "lakeFormationConfigurationRole",
        "lake_formation_data_access_role": "lakeFormationDataAccessRole",
        "permission_model": "permissionModel",
        "removal_policy": "removalPolicy",
    },
)
class DataLakeCatalogProps:
    def __init__(
        self,
        *,
        data_lake_storage: _DataLakeStorage_c6c74eec,
        auto_crawl: typing.Optional[builtins.bool] = None,
        auto_crawl_schedule: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.ScheduleProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        crawler_log_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        crawler_table_level_depth: typing.Optional[jsii.Number] = None,
        database_name: typing.Optional[builtins.str] = None,
        lake_formation_configuration_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        lake_formation_data_access_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        permission_model: typing.Optional[_PermissionModel_2366961a] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''Properties for the ``DataLakeCatalog`` Construct.

        :param data_lake_storage: The DataLakeStorage object to create the data catalog on.
        :param auto_crawl: When enabled, creates a top level Glue Crawler that would run based on the defined schedule in the ``autoCrawlSchedule`` parameter. Default: - True
        :param auto_crawl_schedule: The schedule when the Glue Crawler runs, if enabled. Default is once a day at 00:01h. Default: - ``cron(1 0 * * ? *)``
        :param crawler_log_encryption_key: The KMS encryption Key used for the Glue Crawler logs. Default: - Create a new KMS Key if none is provided
        :param crawler_table_level_depth: Directory depth where the table folders are located. This helps the Glue Crawler understand the layout of the folders in S3. Default: - calculated based on ``locationPrefix``
        :param database_name: The suffix of the Glue Data Catalog Database. The name of the Glue Database is composed of the S3 Bucket name and this suffix. The suffix is also added to the S3 location inside the data lake S3 Buckets. Default: - Use the bucket name as the database name and as the S3 location
        :param lake_formation_configuration_role: The IAM Role assumed by the construct resources to perform Lake Formation configuration. Only needed when permissionModel is set to Lake Formation or Hybrid Default: - A new role is created for the entire Data Lake
        :param lake_formation_data_access_role: The IAM Role used by Lake Formation for `data access <https://docs.aws.amazon.com/lake-formation/latest/dg/access-control-underlying-data.html>`_. The role will be used for accessing all the layers of the data lake (bronze, silver, gold). Only needed when permissionModel is set to Lake Formation or Hybrid. Default: - A new role is created for the entire Data Lake
        :param permission_model: The permission model to apply to the Glue Database. Default: - IAM permission model is used
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        if isinstance(auto_crawl_schedule, dict):
            auto_crawl_schedule = _aws_cdk_aws_glue_ceddda9d.CfnCrawler.ScheduleProperty(**auto_crawl_schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f05863c5bf0bd06a92af0ed9b7016cd4acb82ea34d32e2e98e60b1386da1af7f)
            check_type(argname="argument data_lake_storage", value=data_lake_storage, expected_type=type_hints["data_lake_storage"])
            check_type(argname="argument auto_crawl", value=auto_crawl, expected_type=type_hints["auto_crawl"])
            check_type(argname="argument auto_crawl_schedule", value=auto_crawl_schedule, expected_type=type_hints["auto_crawl_schedule"])
            check_type(argname="argument crawler_log_encryption_key", value=crawler_log_encryption_key, expected_type=type_hints["crawler_log_encryption_key"])
            check_type(argname="argument crawler_table_level_depth", value=crawler_table_level_depth, expected_type=type_hints["crawler_table_level_depth"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument lake_formation_configuration_role", value=lake_formation_configuration_role, expected_type=type_hints["lake_formation_configuration_role"])
            check_type(argname="argument lake_formation_data_access_role", value=lake_formation_data_access_role, expected_type=type_hints["lake_formation_data_access_role"])
            check_type(argname="argument permission_model", value=permission_model, expected_type=type_hints["permission_model"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "data_lake_storage": data_lake_storage,
        }
        if auto_crawl is not None:
            self._values["auto_crawl"] = auto_crawl
        if auto_crawl_schedule is not None:
            self._values["auto_crawl_schedule"] = auto_crawl_schedule
        if crawler_log_encryption_key is not None:
            self._values["crawler_log_encryption_key"] = crawler_log_encryption_key
        if crawler_table_level_depth is not None:
            self._values["crawler_table_level_depth"] = crawler_table_level_depth
        if database_name is not None:
            self._values["database_name"] = database_name
        if lake_formation_configuration_role is not None:
            self._values["lake_formation_configuration_role"] = lake_formation_configuration_role
        if lake_formation_data_access_role is not None:
            self._values["lake_formation_data_access_role"] = lake_formation_data_access_role
        if permission_model is not None:
            self._values["permission_model"] = permission_model
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def data_lake_storage(self) -> _DataLakeStorage_c6c74eec:
        '''The DataLakeStorage object to create the data catalog on.'''
        result = self._values.get("data_lake_storage")
        assert result is not None, "Required property 'data_lake_storage' is missing"
        return typing.cast(_DataLakeStorage_c6c74eec, result)

    @builtins.property
    def auto_crawl(self) -> typing.Optional[builtins.bool]:
        '''When enabled, creates a top level Glue Crawler that would run based on the defined schedule in the ``autoCrawlSchedule`` parameter.

        :default: - True
        '''
        result = self._values.get("auto_crawl")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_crawl_schedule(
        self,
    ) -> typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.ScheduleProperty]:
        '''The schedule when the Glue Crawler runs, if enabled.

        Default is once a day at 00:01h.

        :default: - ``cron(1 0 * * ? *)``
        '''
        result = self._values.get("auto_crawl_schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.ScheduleProperty], result)

    @builtins.property
    def crawler_log_encryption_key(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS encryption Key used for the Glue Crawler logs.

        :default: - Create a new KMS Key if none is provided
        '''
        result = self._values.get("crawler_log_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def crawler_table_level_depth(self) -> typing.Optional[jsii.Number]:
        '''Directory depth where the table folders are located.

        This helps the Glue Crawler understand the layout of the folders in S3.

        :default: - calculated based on ``locationPrefix``
        '''
        result = self._values.get("crawler_table_level_depth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''The suffix of the Glue Data Catalog Database.

        The name of the Glue Database is composed of the S3 Bucket name and this suffix.
        The suffix is also added to the S3 location inside the data lake S3 Buckets.

        :default: - Use the bucket name as the database name and as the S3 location
        '''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lake_formation_configuration_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role assumed by the construct resources to perform Lake Formation configuration.

        Only needed when permissionModel is set to Lake Formation or Hybrid

        :default: - A new role is created for the entire Data Lake
        '''
        result = self._values.get("lake_formation_configuration_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def lake_formation_data_access_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role used by Lake Formation for `data access <https://docs.aws.amazon.com/lake-formation/latest/dg/access-control-underlying-data.html>`_. The role will be used for accessing all the layers of the data lake (bronze, silver, gold). Only needed when permissionModel is set to Lake Formation or Hybrid.

        :default: - A new role is created for the entire Data Lake
        '''
        result = self._values.get("lake_formation_data_access_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def permission_model(self) -> typing.Optional[_PermissionModel_2366961a]:
        '''The permission model to apply to the Glue Database.

        :default: - IAM permission model is used
        '''
        result = self._values.get("permission_model")
        return typing.cast(typing.Optional[_PermissionModel_2366961a], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataLakeCatalogProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataZoneCustomAssetTypeFactory(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataZoneCustomAssetTypeFactory",
):
    '''Factory construct providing resources to create a DataZone custom asset type.

    Example::

        dsf.governance.DataZoneCustomAssetTypeFactory(self, "CustomAssetTypeFactory",
            domain_id="aba_dc999t9ime9sss"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain_id: builtins.str,
        lambda_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''Constructs a new instance of DataZoneCustomAssetTypeFactory.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param domain_id: The DataZone domain identifier.
        :param lambda_role: The Lambda role used by the custom resource provider. Default: - A new role is created
        :param removal_policy: The removal policy for the custom resource. Default: RemovalPolicy.RETAIN
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3e829786e2edaf038bb2bf63a73c2446d5dec4537dd369c061adb99c3113e85)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DataZoneCustomAssetTypeFactoryProps(
            domain_id=domain_id, lambda_role=lambda_role, removal_policy=removal_policy
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createCustomAssetType")
    def create_custom_asset_type(
        self,
        id: builtins.str,
        *,
        asset_type_name: builtins.str,
        form_types: typing.Sequence[typing.Union["DataZoneFormType", typing.Dict[builtins.str, typing.Any]]],
        project_id: builtins.str,
        asset_type_description: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> CustomAssetType:
        '''Creates a DataZone custom asset type based on the provided properties.

        :param id: the ID of the CDK Construct.
        :param asset_type_name: The name of the custom asset type.
        :param form_types: The form types of the custom asset type.
        :param project_id: The project identifier owner of the custom asset type.
        :param asset_type_description: The description of the custom asset type. Default: - No description provided
        :param removal_policy: The removal policy of the custom asset type. Default: - RETAIN

        :return: the custom asset type
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17f585ce7728100b3d9bc62a14fad1d9d7183135fee8102e4785ada50622eb63)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        custom_asset_type = DataZoneCustomAssetTypeProps(
            asset_type_name=asset_type_name,
            form_types=form_types,
            project_id=project_id,
            asset_type_description=asset_type_description,
            removal_policy=removal_policy,
        )

        return typing.cast(CustomAssetType, jsii.invoke(self, "createCustomAssetType", [id, custom_asset_type]))

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
    @jsii.member(jsii_name="createFunction")
    def create_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda Function for the DataZone custom asset type creation.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "createFunction"))

    @builtins.property
    @jsii.member(jsii_name="createLogGroup")
    def create_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Logs Log Group for the DataZone custom asset type creation.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "createLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="createRole")
    def create_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM Role for the DataZone custom asset type creation.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "createRole"))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> builtins.str:
        '''The service token for the custom resource.'''
        return typing.cast(builtins.str, jsii.get(self, "serviceToken"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataZoneCustomAssetTypeFactoryProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_id": "domainId",
        "lambda_role": "lambdaRole",
        "removal_policy": "removalPolicy",
    },
)
class DataZoneCustomAssetTypeFactoryProps:
    def __init__(
        self,
        *,
        domain_id: builtins.str,
        lambda_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''Properties for the DataZoneCustomAssetTypeFactory construct.

        :param domain_id: The DataZone domain identifier.
        :param lambda_role: The Lambda role used by the custom resource provider. Default: - A new role is created
        :param removal_policy: The removal policy for the custom resource. Default: RemovalPolicy.RETAIN
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee6024b134ed7d73c0dbd1fb944a1e39305a5e43ed1b87f7e4a5717193796909)
            check_type(argname="argument domain_id", value=domain_id, expected_type=type_hints["domain_id"])
            check_type(argname="argument lambda_role", value=lambda_role, expected_type=type_hints["lambda_role"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_id": domain_id,
        }
        if lambda_role is not None:
            self._values["lambda_role"] = lambda_role
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def domain_id(self) -> builtins.str:
        '''The DataZone domain identifier.'''
        result = self._values.get("domain_id")
        assert result is not None, "Required property 'domain_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The Lambda role used by the custom resource provider.

        :default: - A new role is created
        '''
        result = self._values.get("lambda_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy for the custom resource.

        :default: RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataZoneCustomAssetTypeFactoryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataZoneCustomAssetTypeProps",
    jsii_struct_bases=[],
    name_mapping={
        "asset_type_name": "assetTypeName",
        "form_types": "formTypes",
        "project_id": "projectId",
        "asset_type_description": "assetTypeDescription",
        "removal_policy": "removalPolicy",
    },
)
class DataZoneCustomAssetTypeProps:
    def __init__(
        self,
        *,
        asset_type_name: builtins.str,
        form_types: typing.Sequence[typing.Union["DataZoneFormType", typing.Dict[builtins.str, typing.Any]]],
        project_id: builtins.str,
        asset_type_description: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''Properties for the DataZoneCustomAssetType construct.

        :param asset_type_name: The name of the custom asset type.
        :param form_types: The form types of the custom asset type.
        :param project_id: The project identifier owner of the custom asset type.
        :param asset_type_description: The description of the custom asset type. Default: - No description provided
        :param removal_policy: The removal policy of the custom asset type. Default: - RETAIN
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0124a367195e1e26d791477ca0b81aa895c81298dc32fed18527ea6431891dc9)
            check_type(argname="argument asset_type_name", value=asset_type_name, expected_type=type_hints["asset_type_name"])
            check_type(argname="argument form_types", value=form_types, expected_type=type_hints["form_types"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument asset_type_description", value=asset_type_description, expected_type=type_hints["asset_type_description"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "asset_type_name": asset_type_name,
            "form_types": form_types,
            "project_id": project_id,
        }
        if asset_type_description is not None:
            self._values["asset_type_description"] = asset_type_description
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def asset_type_name(self) -> builtins.str:
        '''The name of the custom asset type.'''
        result = self._values.get("asset_type_name")
        assert result is not None, "Required property 'asset_type_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def form_types(self) -> typing.List["DataZoneFormType"]:
        '''The form types of the custom asset type.

        Example::

            [{"name": "userForm", "model": [{"name": "firstName", "type": "String", "required": True}]}]
        '''
        result = self._values.get("form_types")
        assert result is not None, "Required property 'form_types' is missing"
        return typing.cast(typing.List["DataZoneFormType"], result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''The project identifier owner of the custom asset type.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def asset_type_description(self) -> typing.Optional[builtins.str]:
        '''The description of the custom asset type.

        :default: - No description provided
        '''
        result = self._values.get("asset_type_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy of the custom asset type.

        :default: - RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataZoneCustomAssetTypeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataZoneFormType",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "model": "model", "required": "required"},
)
class DataZoneFormType:
    def __init__(
        self,
        *,
        name: builtins.str,
        model: typing.Optional[typing.Sequence[typing.Union["DataZoneFormTypeField", typing.Dict[builtins.str, typing.Any]]]] = None,
        required: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Interface representing a DataZoneFormType.

        :param name: The name of the form.
        :param model: The fields of the form. Default: - No model is required. The form is already configured in DataZone.
        :param required: Whether the form is required. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10188afe361c73d3e16fca8ff5a59651fc0a05b635e0e1bbcca2336fbc5fe25a)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument model", value=model, expected_type=type_hints["model"])
            check_type(argname="argument required", value=required, expected_type=type_hints["required"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if model is not None:
            self._values["model"] = model
        if required is not None:
            self._values["required"] = required

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the form.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def model(self) -> typing.Optional[typing.List["DataZoneFormTypeField"]]:
        '''The fields of the form.

        :default: - No model is required. The form is already configured in DataZone.

        Example::

            [{"name": "firstName", "type": "String", "required": True}]
        '''
        result = self._values.get("model")
        return typing.cast(typing.Optional[typing.List["DataZoneFormTypeField"]], result)

    @builtins.property
    def required(self) -> typing.Optional[builtins.bool]:
        '''Whether the form is required.

        :default: false
        '''
        result = self._values.get("required")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataZoneFormType(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataZoneFormTypeField",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "type": "type", "required": "required"},
)
class DataZoneFormTypeField:
    def __init__(
        self,
        *,
        name: builtins.str,
        type: builtins.str,
        required: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Interface representing a DataZoneFormTypeField.

        :param name: The name of the field.
        :param type: The type of the field.
        :param required: Whether the field is required. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1a760da7e1eeaf369a9c0daf5ba43b7a4b4e242d408a905fab17bd3a56d94f8)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument required", value=required, expected_type=type_hints["required"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "type": type,
        }
        if required is not None:
            self._values["required"] = required

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the field.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of the field.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def required(self) -> typing.Optional[builtins.bool]:
        '''Whether the field is required.

        :default: false
        '''
        result = self._values.get("required")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataZoneFormTypeField(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataZoneGsrMskDataSource(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataZoneGsrMskDataSource",
):
    '''A DataZone custom data source for MSK (Managed Streaming for Kafka) with integration for Glue Schema Registry.

    The construct creates assets with the MskTopicAssetType in DataZone based on schema definitions in a Glue Schema Registry.
    It can be either scheduled or react on Schema Registry events (Create Schema, Update Schema, Create Schema Revision).

    Example::

        from aws_cdk.aws_events import Schedule
        
        
        dsf.governance.DataZoneGsrMskDataSource(self, "MskDatasource",
            domain_id="aba_dc999t9ime9sss",
            project_id="999999b3m5cpz",
            registry_name="MyRegistry",
            cluster_name="MyCluster",
            run_schedule=Schedule.cron(minute="0", hour="12"),  # Trigger daily at noon
            enable_schema_registry_event=True
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster_name: builtins.str,
        domain_id: builtins.str,
        project_id: builtins.str,
        registry_name: builtins.str,
        enable_schema_registry_event: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        lambda_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        run_schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        ssm_parameter_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    ) -> None:
        '''Build an instance of the DataZoneGsrMskDataSource.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param cluster_name: The name of the MSK (Managed Streaming for Apache Kafka) cluster to use.
        :param domain_id: The unique identifier for the DataZone domain where the datasource resides.
        :param project_id: The unique identifier for the project associated with this datasource.
        :param registry_name: The name of the registry for schema management.
        :param enable_schema_registry_event: A flag to trigger the data source based on the Glue Schema Registry events. The data source can be triggered by events independently of the schedule configured with ``runSchedule``. Default: - false, meaning the EventBridge listener for schema changes is disabled.
        :param encryption_key: The KMS encryption key used to encrypt lambda environment, lambda logs and SSM parameters. Default: - AWS managed customer master key (CMK) is used
        :param lambda_role: The Role used by the Lambda responsible to manage DataZone MskTopicAssets. Default: - A new role is created
        :param removal_policy: The removal policy to apply to the data source. Default: - RemovalPolicy.RETAIN
        :param run_schedule: The cron schedule to run the data source and synchronize DataZone assets with the Glue Schema Registry. The data source can be scheduled independently of the event based trigger configured with ``enableSchemaRegistryEvent``. Default: - ``cron(1 0 * * ? *)`` if ``enableSchemaRegistryEvent`` is false or undefined, otherwise no schedule.
        :param ssm_parameter_key: The KMS Key used to encrypt the SSM parameter for storing asset information. Default: - A new key is created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__777b020b14e4944617cbffabef212b020286697b0aa83dba2824898c0166fb1b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DataZoneGsrMskDataSourceProps(
            cluster_name=cluster_name,
            domain_id=domain_id,
            project_id=project_id,
            registry_name=registry_name,
            enable_schema_registry_event=enable_schema_registry_event,
            encryption_key=encryption_key,
            lambda_role=lambda_role,
            removal_policy=removal_policy,
            run_schedule=run_schedule,
            ssm_parameter_key=ssm_parameter_key,
        )

        jsii.create(self.__class__, self, [scope, id, props])

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
    @jsii.member(jsii_name="dataZoneMembership")
    def data_zone_membership(
        self,
    ) -> _aws_cdk_aws_datazone_ceddda9d.CfnProjectMembership:
        '''The membership of the Lambda Role on the DataZone Project.'''
        return typing.cast(_aws_cdk_aws_datazone_ceddda9d.CfnProjectMembership, jsii.get(self, "dataZoneMembership"))

    @builtins.property
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda Function creating DataZone Inventory Assets.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "lambdaFunction"))

    @builtins.property
    @jsii.member(jsii_name="lambdaLogGroup")
    def lambda_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The Log Group for the Lambda Function creating DataZone Inventory Assets.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "lambdaLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="lambdaRole")
    def lambda_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM Role of the Lambda Function interacting with DataZone API to create inventory assets.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "lambdaRole"))

    @builtins.property
    @jsii.member(jsii_name="ssmParameterKey")
    def ssm_parameter_key(self) -> _aws_cdk_aws_kms_ceddda9d.Key:
        '''The KMS Key used to encrypt the SSM Parameter storing assets information.'''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.Key, jsii.get(self, "ssmParameterKey"))

    @builtins.property
    @jsii.member(jsii_name="createUpdateEventRule")
    def create_update_event_rule(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.IRule]:
        '''The Event Bridge Rule for schema creation and update.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.IRule], jsii.get(self, "createUpdateEventRule"))

    @builtins.property
    @jsii.member(jsii_name="deleteEventRule")
    def delete_event_rule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.IRule]:
        '''The Event Bridge Rule for schema deletion.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.IRule], jsii.get(self, "deleteEventRule"))

    @builtins.property
    @jsii.member(jsii_name="scheduleRule")
    def schedule_rule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.IRule]:
        '''The Event Bridge Rule for trigger the data source execution.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.IRule], jsii.get(self, "scheduleRule"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataZoneGsrMskDataSourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_name": "clusterName",
        "domain_id": "domainId",
        "project_id": "projectId",
        "registry_name": "registryName",
        "enable_schema_registry_event": "enableSchemaRegistryEvent",
        "encryption_key": "encryptionKey",
        "lambda_role": "lambdaRole",
        "removal_policy": "removalPolicy",
        "run_schedule": "runSchedule",
        "ssm_parameter_key": "ssmParameterKey",
    },
)
class DataZoneGsrMskDataSourceProps:
    def __init__(
        self,
        *,
        cluster_name: builtins.str,
        domain_id: builtins.str,
        project_id: builtins.str,
        registry_name: builtins.str,
        enable_schema_registry_event: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        lambda_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        run_schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        ssm_parameter_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    ) -> None:
        '''Properties for configuring a DataZone GSR MSK datasource.

        :param cluster_name: The name of the MSK (Managed Streaming for Apache Kafka) cluster to use.
        :param domain_id: The unique identifier for the DataZone domain where the datasource resides.
        :param project_id: The unique identifier for the project associated with this datasource.
        :param registry_name: The name of the registry for schema management.
        :param enable_schema_registry_event: A flag to trigger the data source based on the Glue Schema Registry events. The data source can be triggered by events independently of the schedule configured with ``runSchedule``. Default: - false, meaning the EventBridge listener for schema changes is disabled.
        :param encryption_key: The KMS encryption key used to encrypt lambda environment, lambda logs and SSM parameters. Default: - AWS managed customer master key (CMK) is used
        :param lambda_role: The Role used by the Lambda responsible to manage DataZone MskTopicAssets. Default: - A new role is created
        :param removal_policy: The removal policy to apply to the data source. Default: - RemovalPolicy.RETAIN
        :param run_schedule: The cron schedule to run the data source and synchronize DataZone assets with the Glue Schema Registry. The data source can be scheduled independently of the event based trigger configured with ``enableSchemaRegistryEvent``. Default: - ``cron(1 0 * * ? *)`` if ``enableSchemaRegistryEvent`` is false or undefined, otherwise no schedule.
        :param ssm_parameter_key: The KMS Key used to encrypt the SSM parameter for storing asset information. Default: - A new key is created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d54035a511eab1e2be24af8ec3033b00b5d4d081d5fdbba22cb4a167ea8ac2c)
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument domain_id", value=domain_id, expected_type=type_hints["domain_id"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument registry_name", value=registry_name, expected_type=type_hints["registry_name"])
            check_type(argname="argument enable_schema_registry_event", value=enable_schema_registry_event, expected_type=type_hints["enable_schema_registry_event"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument lambda_role", value=lambda_role, expected_type=type_hints["lambda_role"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument run_schedule", value=run_schedule, expected_type=type_hints["run_schedule"])
            check_type(argname="argument ssm_parameter_key", value=ssm_parameter_key, expected_type=type_hints["ssm_parameter_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster_name": cluster_name,
            "domain_id": domain_id,
            "project_id": project_id,
            "registry_name": registry_name,
        }
        if enable_schema_registry_event is not None:
            self._values["enable_schema_registry_event"] = enable_schema_registry_event
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if lambda_role is not None:
            self._values["lambda_role"] = lambda_role
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if run_schedule is not None:
            self._values["run_schedule"] = run_schedule
        if ssm_parameter_key is not None:
            self._values["ssm_parameter_key"] = ssm_parameter_key

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''The name of the MSK (Managed Streaming for Apache Kafka) cluster to use.'''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_id(self) -> builtins.str:
        '''The unique identifier for the DataZone domain where the datasource resides.'''
        result = self._values.get("domain_id")
        assert result is not None, "Required property 'domain_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''The unique identifier for the project associated with this datasource.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def registry_name(self) -> builtins.str:
        '''The name of the registry for schema management.'''
        result = self._values.get("registry_name")
        assert result is not None, "Required property 'registry_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enable_schema_registry_event(self) -> typing.Optional[builtins.bool]:
        '''A flag to trigger the data source based on the Glue Schema Registry events.

        The data source can be triggered by events independently of the schedule configured with ``runSchedule``.

        :default: - false, meaning the EventBridge listener for schema changes is disabled.
        '''
        result = self._values.get("enable_schema_registry_event")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''The KMS encryption key used to encrypt lambda environment, lambda logs and SSM parameters.

        :default: - AWS managed customer master key (CMK) is used
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def lambda_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        '''The Role used by the Lambda responsible to manage DataZone MskTopicAssets.

        :default: - A new role is created
        '''
        result = self._values.get("lambda_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy to apply to the data source.

        :default: - RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def run_schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        '''The cron schedule to run the data source and synchronize DataZone assets with the Glue Schema Registry.

        The data source can be scheduled independently of the event based trigger configured with ``enableSchemaRegistryEvent``.

        :default: - ``cron(1 0 * * ? *)`` if ``enableSchemaRegistryEvent`` is false or undefined, otherwise no schedule.
        '''
        result = self._values.get("run_schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    @builtins.property
    def ssm_parameter_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''The KMS Key used to encrypt the SSM parameter for storing asset information.

        :default: - A new key is created
        '''
        result = self._values.get("ssm_parameter_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataZoneGsrMskDataSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataZoneHelpers(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataZoneHelpers",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="buildModelString")
    @builtins.classmethod
    def build_model_string(
        cls,
        *,
        name: builtins.str,
        model: typing.Optional[typing.Sequence[typing.Union[DataZoneFormTypeField, typing.Dict[builtins.str, typing.Any]]]] = None,
        required: typing.Optional[builtins.bool] = None,
    ) -> typing.Optional[builtins.str]:
        '''Build a Smithy model string from model fields.

        :param name: The name of the form.
        :param model: The fields of the form. Default: - No model is required. The form is already configured in DataZone.
        :param required: Whether the form is required. Default: false

        :return: The Smithy model string.
        '''
        form_type = DataZoneFormType(name=name, model=model, required=required)

        return typing.cast(typing.Optional[builtins.str], jsii.sinvoke(cls, "buildModelString", [form_type]))

    @jsii.member(jsii_name="createSubscriptionTarget")
    @builtins.classmethod
    def create_subscription_target(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        custom_asset_type: typing.Union[CustomAssetType, typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        provider: builtins.str,
        environment_id: builtins.str,
        authorized_principals: typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole],
        manage_access_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    ) -> _aws_cdk_aws_datazone_ceddda9d.CfnSubscriptionTarget:
        '''Creates a DataZone subscription target for a custom asset type.

        Subscription targets are used to automatically add asset to environments when a custom asset is subscribed by a project.

        :param scope: The scope of the construct.
        :param id: The id of the construct.
        :param custom_asset_type: The custom asset type that can be added to the environment.
        :param name: The name of the subscription target.
        :param provider: The provider of the subscription target.
        :param environment_id: The DataZone environment identifier.
        :param authorized_principals: The authorized principals to be granted when assets are subscribed.
        :param manage_access_role: The IAM role creating the subscription target.

        :return: The DataZone subscription target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c273620808c8d09b20e7a2d3bbd734c113fbee108680ae0aeede083d6305aa4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument custom_asset_type", value=custom_asset_type, expected_type=type_hints["custom_asset_type"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument environment_id", value=environment_id, expected_type=type_hints["environment_id"])
            check_type(argname="argument authorized_principals", value=authorized_principals, expected_type=type_hints["authorized_principals"])
            check_type(argname="argument manage_access_role", value=manage_access_role, expected_type=type_hints["manage_access_role"])
        return typing.cast(_aws_cdk_aws_datazone_ceddda9d.CfnSubscriptionTarget, jsii.sinvoke(cls, "createSubscriptionTarget", [scope, id, custom_asset_type, name, provider, environment_id, authorized_principals, manage_access_role]))


class DataZoneMskAssetType(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataZoneMskAssetType",
):
    '''A DataZone custom asset type representing an MSK topic.

    Example::

        dsf.governance.DataZoneMskAssetType(self, "MskAssetType",
            domain_id="aba_dc999t9ime9sss",
            project_id="999999b3m5cpz"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain_id: builtins.str,
        dz_custom_asset_type_factory: typing.Optional[DataZoneCustomAssetTypeFactory] = None,
        project_id: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''Construct an instance of the DataZoneMskAssetType.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param domain_id: The DataZone domain identifier.
        :param dz_custom_asset_type_factory: The factory to create the custom asset type. Default: - A new factory is created
        :param project_id: The project identifier owner of the custom asset type. Default: - A new project called MskGovernance is created
        :param removal_policy: The removal policy to apply to the asset type. Default: - RemovalPolicy.RETAIN
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__faafe3790fbe2687657d0680437ee386924310f5c699ac78af3a552f47a2e849)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DataZoneMskAssetTypeProps(
            domain_id=domain_id,
            dz_custom_asset_type_factory=dz_custom_asset_type_factory,
            project_id=project_id,
            removal_policy=removal_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

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
    @jsii.member(jsii_name="mskCustomAssetType")
    def msk_custom_asset_type(self) -> CustomAssetType:
        '''The custom asset type for MSK.'''
        return typing.cast(CustomAssetType, jsii.get(self, "mskCustomAssetType"))

    @builtins.property
    @jsii.member(jsii_name="owningProject")
    def owning_project(
        self,
    ) -> typing.Optional[_aws_cdk_aws_datazone_ceddda9d.CfnProject]:
        '''The project owning the MSK asset type.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_datazone_ceddda9d.CfnProject], jsii.get(self, "owningProject"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataZoneMskAssetTypeProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_id": "domainId",
        "dz_custom_asset_type_factory": "dzCustomAssetTypeFactory",
        "project_id": "projectId",
        "removal_policy": "removalPolicy",
    },
)
class DataZoneMskAssetTypeProps:
    def __init__(
        self,
        *,
        domain_id: builtins.str,
        dz_custom_asset_type_factory: typing.Optional[DataZoneCustomAssetTypeFactory] = None,
        project_id: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''The properties for the DataZoneMskAssetType construct.

        :param domain_id: The DataZone domain identifier.
        :param dz_custom_asset_type_factory: The factory to create the custom asset type. Default: - A new factory is created
        :param project_id: The project identifier owner of the custom asset type. Default: - A new project called MskGovernance is created
        :param removal_policy: The removal policy to apply to the asset type. Default: - RemovalPolicy.RETAIN
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5841ff088dfbbfd92e3471afad7142fcd97f8a979e708e2f4cf90286768892e6)
            check_type(argname="argument domain_id", value=domain_id, expected_type=type_hints["domain_id"])
            check_type(argname="argument dz_custom_asset_type_factory", value=dz_custom_asset_type_factory, expected_type=type_hints["dz_custom_asset_type_factory"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_id": domain_id,
        }
        if dz_custom_asset_type_factory is not None:
            self._values["dz_custom_asset_type_factory"] = dz_custom_asset_type_factory
        if project_id is not None:
            self._values["project_id"] = project_id
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def domain_id(self) -> builtins.str:
        '''The DataZone domain identifier.'''
        result = self._values.get("domain_id")
        assert result is not None, "Required property 'domain_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dz_custom_asset_type_factory(
        self,
    ) -> typing.Optional[DataZoneCustomAssetTypeFactory]:
        '''The factory to create the custom asset type.

        :default: - A new factory is created
        '''
        result = self._values.get("dz_custom_asset_type_factory")
        return typing.cast(typing.Optional[DataZoneCustomAssetTypeFactory], result)

    @builtins.property
    def project_id(self) -> typing.Optional[builtins.str]:
        '''The project identifier owner of the custom asset type.

        :default: - A new project called MskGovernance is created
        '''
        result = self._values.get("project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy to apply to the asset type.

        :default: - RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataZoneMskAssetTypeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataZoneMskCentralAuthorizer(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataZoneMskCentralAuthorizer",
):
    '''A central authorizer workflow for granting read access to Kafka topics.

    The workflow is triggered by an event sent to the DataZone event bus.
    First, it collects metadata from DataZone about the Kafka topics.
    Then, it grants access to the relevant IAM roles.
    Finally acknowledge the subscription grant in DataZone.

    Example::

        dsf.governance.DataZoneMskCentralAuthorizer(self, "MskAuthorizer",
            domain_id="aba_dc999t9ime9sss"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain_id: builtins.str,
        callback_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
        datazone_event_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
        dead_letter_queue_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        metadata_collector_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        state_machine_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    ) -> None:
        '''Construct an instance of the DataZoneMskCentralAuthorizer.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param domain_id: The DataZone Domain ID.
        :param callback_role: The IAM Role used to callback DataZone and acknowledge the subscription grant. Default: - A new role will be created
        :param datazone_event_role: The IAM Role used by the Event Bridge event to trigger the authorizer. Default: - A new role will be created
        :param dead_letter_queue_key: The KMS Key used to encrypt the SQS Dead Letter Queue receiving failed events from DataZone. Default: - A new Key is created
        :param log_retention: Cloudwatch Logs retention. Default: - 7 days
        :param metadata_collector_role: The IAM Role used to collect metadata on DataZone assets. Default: - A new role will be created
        :param removal_policy: The removal policy to apply to the asset type. Default: - RemovalPolicy.RETAIN
        :param state_machine_role: The IAM Role used by the Step Function state machine. Default: - A new role will be created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74bdaadb6eea7be2270d7869600adaf27913e077c3ace97ec3c946c865c68aff)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DataZoneMskCentralAuthorizerProps(
            domain_id=domain_id,
            callback_role=callback_role,
            datazone_event_role=datazone_event_role,
            dead_letter_queue_key=dead_letter_queue_key,
            log_retention=log_retention,
            metadata_collector_role=metadata_collector_role,
            removal_policy=removal_policy,
            state_machine_role=state_machine_role,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="registerAccount")
    def register_account(self, id: builtins.str, account_id: builtins.str) -> None:
        '''Connect the central authorizer workflow with environment authorizer workflows in other accounts.

        This method grants the environment workflow to send events in the default Event Bridge bus for orchestration.

        :param id: The construct ID to use.
        :param account_id: The account ID to register the authorizer with.

        :return: The CfnEventBusPolicy created to grant the account
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1129c0a9838ab97f76ba2799feb6d5db45770dd873f771e19d883c37de62d102)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
        return typing.cast(None, jsii.invoke(self, "registerAccount", [id, account_id]))

    @jsii.member(jsii_name="retrieveVersion")
    def retrieve_version(self) -> typing.Any:
        '''Retrieve DSF package.json version.'''
        return typing.cast(typing.Any, jsii.invoke(self, "retrieveVersion", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AUTHORIZER_NAME")
    def AUTHORIZER_NAME(cls) -> builtins.str:
        '''The name of the authorizer.'''
        return typing.cast(builtins.str, jsii.sget(cls, "AUTHORIZER_NAME"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_OWNED_TAG")
    def DSF_OWNED_TAG(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_OWNED_TAG"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_TRACKING_CODE")
    def DSF_TRACKING_CODE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_TRACKING_CODE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MSK_ASSET_TYPE")
    def MSK_ASSET_TYPE(cls) -> builtins.str:
        '''The asset type for the DataZone custom asset type.'''
        return typing.cast(builtins.str, jsii.sget(cls, "MSK_ASSET_TYPE"))

    @builtins.property
    @jsii.member(jsii_name="datazoneCallbackFunction")
    def datazone_callback_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda function used to acknowledge the subscription grant in DataZone.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "datazoneCallbackFunction"))

    @builtins.property
    @jsii.member(jsii_name="datazoneCallbackLogGroup")
    def datazone_callback_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The Cloudwatch Log Group for logging the datazone callback.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "datazoneCallbackLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="datazoneCallbackRole")
    def datazone_callback_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The role used to acknowledge the subscription grant in DataZone.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "datazoneCallbackRole"))

    @builtins.property
    @jsii.member(jsii_name="datazoneEventRole")
    def datazone_event_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The role used by the DataZone event to trigger the authorizer workflow.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "datazoneEventRole"))

    @builtins.property
    @jsii.member(jsii_name="datazoneEventRule")
    def datazone_event_rule(self) -> _aws_cdk_aws_events_ceddda9d.IRule:
        '''The event rule used to trigger the authorizer workflow.'''
        return typing.cast(_aws_cdk_aws_events_ceddda9d.IRule, jsii.get(self, "datazoneEventRule"))

    @builtins.property
    @jsii.member(jsii_name="deadLetterKey")
    def dead_letter_key(self) -> _aws_cdk_aws_kms_ceddda9d.IKey:
        '''The key used to encrypt the dead letter queue.'''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.IKey, jsii.get(self, "deadLetterKey"))

    @builtins.property
    @jsii.member(jsii_name="deadLetterQueue")
    def dead_letter_queue(self) -> _aws_cdk_aws_sqs_ceddda9d.IQueue:
        '''The SQS Queue used as a dead letter queue for the authorizer workflow.'''
        return typing.cast(_aws_cdk_aws_sqs_ceddda9d.IQueue, jsii.get(self, "deadLetterQueue"))

    @builtins.property
    @jsii.member(jsii_name="metadataCollectorFunction")
    def metadata_collector_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda function used to collect metadata from DataZone.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "metadataCollectorFunction"))

    @builtins.property
    @jsii.member(jsii_name="metadataCollectorLogGroup")
    def metadata_collector_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The Cloudwatch Log Group for logging the metadata collector.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "metadataCollectorLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="metadataCollectorRole")
    def metadata_collector_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The role used to collect metadata from DataZone.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "metadataCollectorRole"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''The state machine used to orchestrate the authorizer workflow.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))

    @builtins.property
    @jsii.member(jsii_name="stateMachineCallbackRole")
    def state_machine_callback_role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''The IAM Role used by the authorizer workflow callback.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "stateMachineCallbackRole"))

    @builtins.property
    @jsii.member(jsii_name="stateMachineRole")
    def state_machine_role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''The IAM Role used by the authorizer workflow State Machine.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "stateMachineRole"))

    @builtins.property
    @jsii.member(jsii_name="stateMachineLogGroup")
    def state_machine_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Log Group used to log the authorizer state machine.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "stateMachineLogGroup"))

    @state_machine_log_group.setter
    def state_machine_log_group(
        self,
        value: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08bb050ed5229fae3c672168e99cf82c1b079ba126e18c165f9bf8d55f373cdf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stateMachineLogGroup", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataZoneMskCentralAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_id": "domainId",
        "callback_role": "callbackRole",
        "datazone_event_role": "datazoneEventRole",
        "dead_letter_queue_key": "deadLetterQueueKey",
        "log_retention": "logRetention",
        "metadata_collector_role": "metadataCollectorRole",
        "removal_policy": "removalPolicy",
        "state_machine_role": "stateMachineRole",
    },
)
class DataZoneMskCentralAuthorizerProps:
    def __init__(
        self,
        *,
        domain_id: builtins.str,
        callback_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
        datazone_event_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
        dead_letter_queue_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        metadata_collector_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        state_machine_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    ) -> None:
        '''The properties for the DataZoneMskCentralAuthorizer construct.

        :param domain_id: The DataZone Domain ID.
        :param callback_role: The IAM Role used to callback DataZone and acknowledge the subscription grant. Default: - A new role will be created
        :param datazone_event_role: The IAM Role used by the Event Bridge event to trigger the authorizer. Default: - A new role will be created
        :param dead_letter_queue_key: The KMS Key used to encrypt the SQS Dead Letter Queue receiving failed events from DataZone. Default: - A new Key is created
        :param log_retention: Cloudwatch Logs retention. Default: - 7 days
        :param metadata_collector_role: The IAM Role used to collect metadata on DataZone assets. Default: - A new role will be created
        :param removal_policy: The removal policy to apply to the asset type. Default: - RemovalPolicy.RETAIN
        :param state_machine_role: The IAM Role used by the Step Function state machine. Default: - A new role will be created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6c2dc3062a5b07073d27d1d484c63bb8c419a85763acaa99c290ebd32b7facc)
            check_type(argname="argument domain_id", value=domain_id, expected_type=type_hints["domain_id"])
            check_type(argname="argument callback_role", value=callback_role, expected_type=type_hints["callback_role"])
            check_type(argname="argument datazone_event_role", value=datazone_event_role, expected_type=type_hints["datazone_event_role"])
            check_type(argname="argument dead_letter_queue_key", value=dead_letter_queue_key, expected_type=type_hints["dead_letter_queue_key"])
            check_type(argname="argument log_retention", value=log_retention, expected_type=type_hints["log_retention"])
            check_type(argname="argument metadata_collector_role", value=metadata_collector_role, expected_type=type_hints["metadata_collector_role"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument state_machine_role", value=state_machine_role, expected_type=type_hints["state_machine_role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_id": domain_id,
        }
        if callback_role is not None:
            self._values["callback_role"] = callback_role
        if datazone_event_role is not None:
            self._values["datazone_event_role"] = datazone_event_role
        if dead_letter_queue_key is not None:
            self._values["dead_letter_queue_key"] = dead_letter_queue_key
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if metadata_collector_role is not None:
            self._values["metadata_collector_role"] = metadata_collector_role
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if state_machine_role is not None:
            self._values["state_machine_role"] = state_machine_role

    @builtins.property
    def domain_id(self) -> builtins.str:
        '''The DataZone Domain ID.'''
        result = self._values.get("domain_id")
        assert result is not None, "Required property 'domain_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def callback_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        '''The IAM Role used to callback DataZone and acknowledge the subscription grant.

        :default: - A new role will be created
        '''
        result = self._values.get("callback_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    @builtins.property
    def datazone_event_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        '''The IAM Role used by the Event Bridge event to trigger the authorizer.

        :default: - A new role will be created
        '''
        result = self._values.get("datazone_event_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    @builtins.property
    def dead_letter_queue_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''The KMS Key used to encrypt the SQS Dead Letter Queue receiving failed events from DataZone.

        :default: - A new Key is created
        '''
        result = self._values.get("dead_letter_queue_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def log_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''Cloudwatch Logs retention.

        :default: - 7 days
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def metadata_collector_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        '''The IAM Role used to collect metadata on DataZone assets.

        :default: - A new role will be created
        '''
        result = self._values.get("metadata_collector_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy to apply to the asset type.

        :default: - RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def state_machine_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        '''The IAM Role used by the Step Function state machine.

        :default: - A new role will be created
        '''
        result = self._values.get("state_machine_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataZoneMskCentralAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataZoneMskEnvironmentAuthorizer(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataZoneMskEnvironmentAuthorizer",
):
    '''An environment authorizer workflow for granting read access to Kafka topics.

    The workflow is triggered by an event sent by the central authorizer construct.
    It creates IAM policies required for the Kafka client to access the relevant topics.
    It supports MSK provisioned and serverless, in single and cross accounts, and grant/revoke requests.

    Example::

        dsf.governance.DataZoneMskEnvironmentAuthorizer(self, "MskAuthorizer",
            domain_id="aba_dc999t9ime9sss"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain_id: builtins.str,
        central_account_id: typing.Optional[builtins.str] = None,
        grant_msk_managed_vpc: typing.Optional[builtins.bool] = None,
        grant_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
        log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        state_machine_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    ) -> None:
        '''Create an instance of the DataZoneMskEnvironmentAuthorizer construct.

        :param scope: The CDK Construct scope.
        :param id: The CDK Construct id.
        :param domain_id: The DataZone Domain ID.
        :param central_account_id: The central account Id.
        :param grant_msk_managed_vpc: If the authorizer is granting MSK managed VPC permissions. Default: - false
        :param grant_role: The IAM Role used to grant MSK topics. Default: - A new role will be created
        :param log_retention: Cloudwatch Logs retention. Default: - 7 days
        :param removal_policy: The removal policy to apply to the asset type. Default: - RemovalPolicy.RETAIN
        :param state_machine_role: The IAM Role used by the Step Function state machine. Default: - A new role will be created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f2613b455377ea64aad04f21691c84f9787e6ef95b2a834f2c5e684c00212e1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DataZoneMskEnvironmentAuthorizerProps(
            domain_id=domain_id,
            central_account_id=central_account_id,
            grant_msk_managed_vpc=grant_msk_managed_vpc,
            grant_role=grant_role,
            log_retention=log_retention,
            removal_policy=removal_policy,
            state_machine_role=state_machine_role,
        )

        jsii.create(self.__class__, self, [scope, id, props])

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

    @jsii.python.classproperty
    @jsii.member(jsii_name="PERMISSIONS_BOUNDARY_STATEMENTS")
    def PERMISSIONS_BOUNDARY_STATEMENTS(
        cls,
    ) -> _aws_cdk_aws_iam_ceddda9d.PolicyStatement:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.PolicyStatement, jsii.sget(cls, "PERMISSIONS_BOUNDARY_STATEMENTS"))

    @builtins.property
    @jsii.member(jsii_name="grantFunction")
    def grant_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The lambda function used to grant access to Kafka topics.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "grantFunction"))

    @builtins.property
    @jsii.member(jsii_name="grantLogGroup")
    def grant_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.LogGroup:
        '''The CloudWatch Log Group used by the grant function.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.LogGroup, jsii.get(self, "grantLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="grantRole")
    def grant_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM role used to grant access to Kafka topics.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "grantRole"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine:
        '''The environment authorizer State Machine.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine, jsii.get(self, "stateMachine"))

    @builtins.property
    @jsii.member(jsii_name="stateMachineLogGroup")
    def state_machine_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Log Group used by the Step Functions state machine.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "stateMachineLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="stateMachineRole")
    def state_machine_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM role used by the environment authorizer State Machine.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "stateMachineRole"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.governance.DataZoneMskEnvironmentAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_id": "domainId",
        "central_account_id": "centralAccountId",
        "grant_msk_managed_vpc": "grantMskManagedVpc",
        "grant_role": "grantRole",
        "log_retention": "logRetention",
        "removal_policy": "removalPolicy",
        "state_machine_role": "stateMachineRole",
    },
)
class DataZoneMskEnvironmentAuthorizerProps:
    def __init__(
        self,
        *,
        domain_id: builtins.str,
        central_account_id: typing.Optional[builtins.str] = None,
        grant_msk_managed_vpc: typing.Optional[builtins.bool] = None,
        grant_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
        log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        state_machine_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    ) -> None:
        '''
        :param domain_id: The DataZone Domain ID.
        :param central_account_id: The central account Id.
        :param grant_msk_managed_vpc: If the authorizer is granting MSK managed VPC permissions. Default: - false
        :param grant_role: The IAM Role used to grant MSK topics. Default: - A new role will be created
        :param log_retention: Cloudwatch Logs retention. Default: - 7 days
        :param removal_policy: The removal policy to apply to the asset type. Default: - RemovalPolicy.RETAIN
        :param state_machine_role: The IAM Role used by the Step Function state machine. Default: - A new role will be created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b640245f9a00c6cb0fee007719c55123eba64c51f23e25dbbb61121757e1edb1)
            check_type(argname="argument domain_id", value=domain_id, expected_type=type_hints["domain_id"])
            check_type(argname="argument central_account_id", value=central_account_id, expected_type=type_hints["central_account_id"])
            check_type(argname="argument grant_msk_managed_vpc", value=grant_msk_managed_vpc, expected_type=type_hints["grant_msk_managed_vpc"])
            check_type(argname="argument grant_role", value=grant_role, expected_type=type_hints["grant_role"])
            check_type(argname="argument log_retention", value=log_retention, expected_type=type_hints["log_retention"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument state_machine_role", value=state_machine_role, expected_type=type_hints["state_machine_role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_id": domain_id,
        }
        if central_account_id is not None:
            self._values["central_account_id"] = central_account_id
        if grant_msk_managed_vpc is not None:
            self._values["grant_msk_managed_vpc"] = grant_msk_managed_vpc
        if grant_role is not None:
            self._values["grant_role"] = grant_role
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if state_machine_role is not None:
            self._values["state_machine_role"] = state_machine_role

    @builtins.property
    def domain_id(self) -> builtins.str:
        '''The DataZone Domain ID.'''
        result = self._values.get("domain_id")
        assert result is not None, "Required property 'domain_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def central_account_id(self) -> typing.Optional[builtins.str]:
        '''The central account Id.'''
        result = self._values.get("central_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def grant_msk_managed_vpc(self) -> typing.Optional[builtins.bool]:
        '''If the authorizer is granting MSK managed VPC permissions.

        :default: - false
        '''
        result = self._values.get("grant_msk_managed_vpc")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def grant_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        '''The IAM Role used to grant MSK topics.

        :default: - A new role will be created
        '''
        result = self._values.get("grant_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    @builtins.property
    def log_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''Cloudwatch Logs retention.

        :default: - 7 days
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy to apply to the asset type.

        :default: - RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def state_machine_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        '''The IAM Role used by the Step Function state machine.

        :default: - A new role will be created
        '''
        result = self._values.get("state_machine_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataZoneMskEnvironmentAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AuthorizerCentralWorflow",
    "AuthorizerEnvironmentWorflow",
    "CustomAssetType",
    "DataCatalogDatabase",
    "DataCatalogDatabaseProps",
    "DataLakeCatalog",
    "DataLakeCatalogProps",
    "DataZoneCustomAssetTypeFactory",
    "DataZoneCustomAssetTypeFactoryProps",
    "DataZoneCustomAssetTypeProps",
    "DataZoneFormType",
    "DataZoneFormTypeField",
    "DataZoneGsrMskDataSource",
    "DataZoneGsrMskDataSourceProps",
    "DataZoneHelpers",
    "DataZoneMskAssetType",
    "DataZoneMskAssetTypeProps",
    "DataZoneMskCentralAuthorizer",
    "DataZoneMskCentralAuthorizerProps",
    "DataZoneMskEnvironmentAuthorizer",
    "DataZoneMskEnvironmentAuthorizerProps",
]

publication.publish()

def _typecheckingstub__a11223a197a87f6709a9f284f5302fc9ff3607ce04757251f5664ba0419acfcb(
    *,
    authorizer_event_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    authorizer_event_rule: _aws_cdk_aws_events_ceddda9d.IRule,
    callback_role: _aws_cdk_aws_iam_ceddda9d.Role,
    dead_letter_key: _aws_cdk_aws_kms_ceddda9d.IKey,
    dead_letter_queue: _aws_cdk_aws_sqs_ceddda9d.IQueue,
    state_machine: _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine,
    state_machine_log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
    state_machine_role: _aws_cdk_aws_iam_ceddda9d.Role,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43c8d2aeb019754a37ab8cb0270e859bdb56b4b38d6a38bd4ad62e3b3bd43c2d(
    *,
    state_machine: _aws_cdk_aws_stepfunctions_ceddda9d.IStateMachine,
    state_machine_log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
    state_machine_role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3fac04e77ad4ffe8a8908a1aac9c24ed840e843b1f58f5f3959e5ccf35cbc84(
    *,
    domain_id: builtins.str,
    name: builtins.str,
    project_identifier: builtins.str,
    revision: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bdf34484b2d4ebd1a8f3a29baa43bc5474f4f0d5c594cf16af37af6e8b0946e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    auto_crawl: typing.Optional[builtins.bool] = None,
    auto_crawl_schedule: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.ScheduleProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    crawler_log_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    crawler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    crawler_table_level_depth: typing.Optional[jsii.Number] = None,
    glue_connection_name: typing.Optional[builtins.str] = None,
    jdbc_path: typing.Optional[builtins.str] = None,
    jdbc_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    jdbc_secret_kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lake_formation_configuration_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    lake_formation_data_access_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    location_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    location_prefix: typing.Optional[builtins.str] = None,
    permission_model: typing.Optional[_PermissionModel_2366961a] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__822d38f353e70d056dab26de7762635d594eaa647844feb41d648fcfe3e931df(
    principal: _aws_cdk_aws_iam_ceddda9d.IPrincipal,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05679d2111c852774397fc96ba1786e51a6f337987ccb847a7924c7d5cca2929(
    *,
    name: builtins.str,
    auto_crawl: typing.Optional[builtins.bool] = None,
    auto_crawl_schedule: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.ScheduleProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    crawler_log_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    crawler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    crawler_table_level_depth: typing.Optional[jsii.Number] = None,
    glue_connection_name: typing.Optional[builtins.str] = None,
    jdbc_path: typing.Optional[builtins.str] = None,
    jdbc_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    jdbc_secret_kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    lake_formation_configuration_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    lake_formation_data_access_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    location_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    location_prefix: typing.Optional[builtins.str] = None,
    permission_model: typing.Optional[_PermissionModel_2366961a] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7805f98b85e606ebfe36a50c42afa1e8c258fbc8c6dac7b7f9d5233436f5185(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    data_lake_storage: _DataLakeStorage_c6c74eec,
    auto_crawl: typing.Optional[builtins.bool] = None,
    auto_crawl_schedule: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.ScheduleProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    crawler_log_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    crawler_table_level_depth: typing.Optional[jsii.Number] = None,
    database_name: typing.Optional[builtins.str] = None,
    lake_formation_configuration_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    lake_formation_data_access_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    permission_model: typing.Optional[_PermissionModel_2366961a] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f05863c5bf0bd06a92af0ed9b7016cd4acb82ea34d32e2e98e60b1386da1af7f(
    *,
    data_lake_storage: _DataLakeStorage_c6c74eec,
    auto_crawl: typing.Optional[builtins.bool] = None,
    auto_crawl_schedule: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnCrawler.ScheduleProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    crawler_log_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    crawler_table_level_depth: typing.Optional[jsii.Number] = None,
    database_name: typing.Optional[builtins.str] = None,
    lake_formation_configuration_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    lake_formation_data_access_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    permission_model: typing.Optional[_PermissionModel_2366961a] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3e829786e2edaf038bb2bf63a73c2446d5dec4537dd369c061adb99c3113e85(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain_id: builtins.str,
    lambda_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17f585ce7728100b3d9bc62a14fad1d9d7183135fee8102e4785ada50622eb63(
    id: builtins.str,
    *,
    asset_type_name: builtins.str,
    form_types: typing.Sequence[typing.Union[DataZoneFormType, typing.Dict[builtins.str, typing.Any]]],
    project_id: builtins.str,
    asset_type_description: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee6024b134ed7d73c0dbd1fb944a1e39305a5e43ed1b87f7e4a5717193796909(
    *,
    domain_id: builtins.str,
    lambda_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0124a367195e1e26d791477ca0b81aa895c81298dc32fed18527ea6431891dc9(
    *,
    asset_type_name: builtins.str,
    form_types: typing.Sequence[typing.Union[DataZoneFormType, typing.Dict[builtins.str, typing.Any]]],
    project_id: builtins.str,
    asset_type_description: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10188afe361c73d3e16fca8ff5a59651fc0a05b635e0e1bbcca2336fbc5fe25a(
    *,
    name: builtins.str,
    model: typing.Optional[typing.Sequence[typing.Union[DataZoneFormTypeField, typing.Dict[builtins.str, typing.Any]]]] = None,
    required: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1a760da7e1eeaf369a9c0daf5ba43b7a4b4e242d408a905fab17bd3a56d94f8(
    *,
    name: builtins.str,
    type: builtins.str,
    required: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__777b020b14e4944617cbffabef212b020286697b0aa83dba2824898c0166fb1b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster_name: builtins.str,
    domain_id: builtins.str,
    project_id: builtins.str,
    registry_name: builtins.str,
    enable_schema_registry_event: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    lambda_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    run_schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    ssm_parameter_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d54035a511eab1e2be24af8ec3033b00b5d4d081d5fdbba22cb4a167ea8ac2c(
    *,
    cluster_name: builtins.str,
    domain_id: builtins.str,
    project_id: builtins.str,
    registry_name: builtins.str,
    enable_schema_registry_event: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    lambda_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    run_schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    ssm_parameter_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c273620808c8d09b20e7a2d3bbd734c113fbee108680ae0aeede083d6305aa4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    custom_asset_type: typing.Union[CustomAssetType, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    provider: builtins.str,
    environment_id: builtins.str,
    authorized_principals: typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole],
    manage_access_role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faafe3790fbe2687657d0680437ee386924310f5c699ac78af3a552f47a2e849(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain_id: builtins.str,
    dz_custom_asset_type_factory: typing.Optional[DataZoneCustomAssetTypeFactory] = None,
    project_id: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5841ff088dfbbfd92e3471afad7142fcd97f8a979e708e2f4cf90286768892e6(
    *,
    domain_id: builtins.str,
    dz_custom_asset_type_factory: typing.Optional[DataZoneCustomAssetTypeFactory] = None,
    project_id: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74bdaadb6eea7be2270d7869600adaf27913e077c3ace97ec3c946c865c68aff(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain_id: builtins.str,
    callback_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    datazone_event_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    dead_letter_queue_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    metadata_collector_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    state_machine_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1129c0a9838ab97f76ba2799feb6d5db45770dd873f771e19d883c37de62d102(
    id: builtins.str,
    account_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08bb050ed5229fae3c672168e99cf82c1b079ba126e18c165f9bf8d55f373cdf(
    value: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6c2dc3062a5b07073d27d1d484c63bb8c419a85763acaa99c290ebd32b7facc(
    *,
    domain_id: builtins.str,
    callback_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    datazone_event_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    dead_letter_queue_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    metadata_collector_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    state_machine_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f2613b455377ea64aad04f21691c84f9787e6ef95b2a834f2c5e684c00212e1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain_id: builtins.str,
    central_account_id: typing.Optional[builtins.str] = None,
    grant_msk_managed_vpc: typing.Optional[builtins.bool] = None,
    grant_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    state_machine_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b640245f9a00c6cb0fee007719c55123eba64c51f23e25dbbb61121757e1edb1(
    *,
    domain_id: builtins.str,
    central_account_id: typing.Optional[builtins.str] = None,
    grant_msk_managed_vpc: typing.Optional[builtins.bool] = None,
    grant_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    state_machine_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
) -> None:
    """Type checking stubs"""
    pass
