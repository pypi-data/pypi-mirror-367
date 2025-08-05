r'''
# RedshiftServerlessNamespace

A [Redshift Serverless Namespace](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-workgroup-namespace.html) with secrets manager integration for admin credentials management and rotation.

## Overview

`RedshiftServerlessNamespace` is a [Redshift Serverless Namespace](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-workgroup-namespace.html) with the following options:

* Encrypt data with a customer managed KMS Key.
* Create Redshift superuser credentials managed by Redshift service: stored in Secrets Manager, encrypted with a KMS Key, and with automatic rotation.
* Attach multiple IAM roles that can be used by Redshift Serverless users to interact with other AWS services.
* Set an [IAM role as default](https://docs.aws.amazon.com/redshift/latest/mgmt/default-iam-role.html)

## Usage

```python
class ExampleDefaultRedshiftServerlessNamespaceStack(Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)
        dsf.consumption.RedshiftServerlessNamespace(self, "RedshiftServerlessNamespace",
            db_name="database",
            name="example-namespace"
        )
```

## Attaching IAM Roles to Redshift Serverless Namespace

To allow Redshift Serverless to access other AWS services on your behalf (eg. data ingestion from S3 via the COPY command, accessing data in S3 via Redshift Spectrum, exporting data from Redshift to S3 via the UNLOAD command.), the preferred method is to specify an IAM role. High-level steps are as follows:

1. Create an IAM role with a trust relationship of `redshift.amazonaws.com`.
2. Attach policy/permissions to the role to give it access to specific AWS services.
3. Configure the role when creating the Redshift Serverless Namespace
4. Run the relevant SQL command referencing the attached IAM role via its ARN (or the `default` keyword if a default IAM role is configured)

```python
class ExampleRedshiftServerlessNamespaceRolesStack(Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)

        bucket = Bucket(self, "ExampleBucket")

        ingestion_role = Role(self, "IngestionRole",
            assumed_by=ServicePrincipal("redshift.amazonaws.com"),
            managed_policies=[
                ManagedPolicy.from_aws_managed_policy_name("AmazonRedshiftAllCommandsFullAccess")
            ]
        )

        bucket.grant_read(ingestion_role)

        dsf.consumption.RedshiftServerlessNamespace(self, "RedshiftServerlessNamespace",
            db_name="database",
            name="example-namespace",
            default_iAMRole=ingestion_role
        )
```

# RedshiftServerlessWorkgroup

A [Redshift Serverless Workgroup](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-workgroup-namespace.html) with helpers method for Redshift administration.

## Overview

`RedshiftServerlessWorkgroup` is a [Redshift Serverless Workgroup](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-workgroup-namespace.html) with the following options/capabilities:

* Deployed in a VPC in private subnets. The network configuation can be customized.
* Provide helper methods for running SQL commands via the Redshift Data API. Commands can be custom or predefined for common administration tasks like creating and granting roles.
* Initialize a Glue Data Catalog integration with auto crawling via Glue Crawlers. This would allow tables in Redshift Serverless to appear in the [Glue Data Catalog](https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html) for the purposes of discovery and integration.

:::warning
The default VPC created by the construct follows the [standard implementation of the VPC L2 CDK Construct](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2-readme.html#control-over-availability-zones). As a result, if no account ID and no region are configured in the CDK Stack, the VPC will only contain 2 AZ and the [Redshift Serverless Workgroup will fail to deploy](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-usage-considerations.html). Be sure to configure the account ID and region to create a 3 AZ VPC.
:::

## Usage

```python
class ExampleDefaultRedshiftServerlessWorkgroupStack(Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)

        namespace = dsf.consumption.RedshiftServerlessNamespace(self, "DefaultRedshiftServerlessNamespace",
            name="default",
            db_name="defaultdb"
        )

        dsf.consumption.RedshiftServerlessWorkgroup(self, "DefaultRedshiftServerlessWorkgroup",
            name="default",
            namespace=namespace
        )
```

## Bootstrapping Redshift Serverless w/ RedshiftData Construct

The `RedshiftData` construct allows custom SQLs to run against the `RedshiftServerlessWorkgroup` via the Data API. This allows users to bootstrap Redshift directly from CDK.

The `RedshiftData` construct provides the following helpers for bootstrapping Redshift databases:

* Run a custom SQL command
* Create Redshift roles
* Grant Redshift roles full access to schemas
* Grant Redshift roles read only access
* Run a COPY command to load data

```python
workgroup = dsf.consumption.RedshiftServerlessWorkgroup(self, "DefaultRedshiftServerlessWorkgroup",
    name="default",
    namespace=namespace
)

# Run a custom SQL to create a customer table
create_table = workgroup.run_custom_sQL("CreateCustomerTable", "defaultdb", """
          CREATE TABLE customer(
            customer_id varchar(50),
            salutation varchar(5),
            first_name varchar(50),
            last_name varchar(50),
            email_address varchar(100)
          )
          diststyle even
          """, "drop table customer")

# Run a COPY command to load data into the customer table
ingestion = workgroup.ingest_data("ExampleCopy", "defaultdb", "customer", bucket, "data-products/customer/", "csv ignoreheader 1")

# Add dependencies between Redshift Data API commands because CDK cannot infer them
ingestion.node.add_dependency(create_table)

# Create an engineering role in the defaultdb
db_role = workgroup.create_db_role("EngineeringRole", "defaultdb", "engineering")

# Grant the engineering role full access to the public schema in the defaultdb
db_schema = workgroup.grant_db_schema_to_role("EngineeringGrant", "defaultdb", "public", "engineering")

# Enforce dependencies
db_schema.node.add_dependency(db_role)
```

## Cataloging Redshift Serverless Tables

Redshift tables and databases can also be automatically catalog in Glue Data Catalog using an helper method. This method creates a Glue Catalog database as well as a crawler to populate the database with table metadata from your Redshift database.

The default value of the path that the crawler would use is `<databaseName>/public/%` which translates to all the tables in the public schema. Please refer to the [crawler documentation](https://docs.aws.amazon.com/glue/latest/dg/define-crawler.html#define-crawler-choose-data-sources) for more information for JDBC data sources.

```python
class ExampleRedshiftServerlessWorkgroupCatalogStack(Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)

        namespace = dsf.consumption.RedshiftServerlessNamespace(self, "DefaultRedshiftServerlessNamespace",
            name="default",
            db_name="defaultdb"
        )

        workgroup = dsf.consumption.RedshiftServerlessWorkgroup(self, "DefaultRedshiftServerlessWorkgroup",
            name="default",
            namespace=namespace
        )

        workgroup.catalog_tables("RedshiftCatalog", "example-redshift-db", "defaultdb/public/%")
```

# Redshift Data Sharing

The `RedshiftDataSharing` construct allows [Redshift data sharing](https://docs.aws.amazon.com/redshift/latest/dg/datashare-overview.html) management for both producers and consumers.

## Overview

The `RedshiftDataSharing` construct provides the following functionality:

* Create a new data share
* Grants access to the data share to another Redshift namespace or to another AWS account (provides auto data share authorization for cross-account grants)
* Create a database from the data share (and for cross-account grants, auto association of the data share to the consumer's Redshift Namespace)

## Usage

Single account data sharing:

```python
class ExampleRedshiftDataSharingSameAccountStack(Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)

        db_name = "defaultdb"

        producer_namespace = RedshiftServerlessNamespace(self, "ProducerNamespace",
            name="producer-namespace",
            db_name=db_name
        )

        producer_workgroup = RedshiftServerlessWorkgroup(self, "ProducerRSWorkgroup",
            name="producer-workgroup",
            namespace=producer_namespace
        )

        consumer_namespace = RedshiftServerlessNamespace(self, "ConsumerNamespace",
            name="consumer-namespace",
            db_name=db_name
        )

        consumer_workgroup = RedshiftServerlessWorkgroup(self, "ConsumerRSWorkgroup",
            name="consumer-workgroup",
            namespace=consumer_namespace
        )

        share_name = "testshare"

        create_customers_table = producer_workgroup.run_custom_sQL("CreateCustomerTable", db_name, "create table public.customers (id varchar(100) not null, first_name varchar(50) not null, last_name varchar(50) not null, email varchar(100) not null)", "drop table public.customers")

        new_share = producer_workgroup.create_share("producer-share", db_name, share_name, "public", ["public.customers"])
        new_share.new_share_custom_resource.node.add_dependency(create_customers_table)

        grant_to_consumer = producer_workgroup.grant_access_to_share("GrantToConsumer", new_share, consumer_namespace.namespace_id)

        grant_to_consumer.resource.node.add_dependency(new_share)
        grant_to_consumer.resource.node.add_dependency(consumer_namespace)

        consume_share = consumer_workgroup.create_database_from_share("consume-datashare", "db_from_share", share_name, producer_namespace.namespace_id)

        consume_share.resource.node.add_dependency(grant_to_consumer)
```

Cross-account data sharing:

```python
class ExampleRedshiftDataSharingCrossAccountAStack(Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)

        db_name = "defaultdb"

        producer_namespace = RedshiftServerlessNamespace(self, "ProducerNamespace",
            name="producer-namespace",
            db_name=db_name
        )

        producer_workgroup = RedshiftServerlessWorkgroup(self, "ProducerRSWorkgroup",
            name="producer-workgroup",
            namespace=producer_namespace
        )

        share_name = "testshare"

        create_customers_table = producer_workgroup.run_custom_sQL("CreateCustomerTable", db_name, "create table public.customers (id varchar(100) not null, first_name varchar(50) not null, last_name varchar(50) not null, email varchar(100) not null)", "drop table public.customers")

        new_share = producer_workgroup.create_share("producer-share", db_name, share_name, "public", ["public.customers"])
        new_share.new_share_custom_resource.node.add_dependency(create_customers_table)

        grant_to_consumer = producer_workgroup.grant_access_to_share("GrantToConsumer", new_share, undefined, "<CONSUMER-ACCOUNT-ID>", True)

        grant_to_consumer.resource.node.add_dependency(new_share)

class ExampleRedshiftDataSharingCrossAccountBStack(Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)

        db_name = "defaultdb"

        consumer_namespace = RedshiftServerlessNamespace(self, "ConsumerNamespace",
            name="consumer-namespace",
            db_name=db_name
        )

        consumer_workgroup = RedshiftServerlessWorkgroup(self, "ConsumerRSWorkgroup",
            name="consumer-workgroup",
            namespace=consumer_namespace
        )

        share_name = "testshare"

        consumer_workgroup.create_database_from_share("consume-datashare", "db_from_share", share_name, "<PRODUCER NAMESPACE>", "<PRODUCER ACCOUNT>")
```

# Athena Workgroup

An [Amazon Athena workgroup](https://docs.aws.amazon.com/athena/latest/ug/manage-queries-control-costs-with-workgroups.html) with provided configuration.

## Overview

`AthenaWorkGroup` provides Athena workgroup configuration with best-practices:

* Amazon S3 bucket for query results, based on [`AnalyticsBucket`](https://awslabs.github.io/data-solutions-framework-on-aws/docs/constructs/library/Storage/analytics-bucket).
* Query results are encrypted using AWS KMS Key.
* Execution Role for the PySpark query engine.
* A grant method to allow principals to run queries.

## Usage

```python
dsf.consumption.AthenaWorkGroup(self, "AthenaWorkGroupDefault",
    name="athena-default",
    result_location_prefix="athena-default-results/"
)
```

## User provided S3 bucket for query results

You can provide your own S3 bucket for query results. If you do so, you are required to provide a KMS Key that will be used to encrypt query results.

:::caution Results encryption
If you provide your own S3 bucket, you also need to provide KMS encryption key to encrypt query results. You also need to
grant access to this key for AthenaWorkGroup's executionRole (if Spark engine is used), or for principals that were granted to run
queries using AthenaWorkGroup's `grantRunQueries` method.
:::caution

You can also decide to provide your KMS Key to encrypt query results with S3 bucket that is provided by the construct (i.e. if you are not providing your own S3 bucket).

```python
dsf.consumption.AthenaWorkGroup(self, "AthenaWorkGroupDefault",
    name="athena-user-bucket",
    result_bucket=user_results_bucket,
    results_encryption_key=user_data_key,
    result_location_prefix="athena-wg-results/"
)
```

## Apache Spark (PySpark) Engine version

You can choose Athena query engine from the available options:

* [Athena engine version 3](https://docs.aws.amazon.com/athena/latest/ug/engine-versions-reference-0003.html)
* [PySpark engine version 3](https://docs.aws.amazon.com/athena/latest/ug/notebooks-spark.html)

The `default` is set to `AUTO` which will choose Athena engine version 3.

If you wish to change query engine to PySpark, you will also be able to access the `executionRole` IAM Role that will be created for you if you don't provide it.
You can access the execution role via `executionRole` property.

```python
spark_engine_version = dsf.consumption.EngineVersion.PYSPARK_V3

dsf.consumption.AthenaWorkGroup(self, "AthenaWorkGroupSpark",
    name="athena-spark",
    engine_version=spark_engine_version,
    result_location_prefix="athena-wg-results/"
)
```

## Construct properties

You can leverage different properties to customize your Athena workgroup. For example, you can use `resultsRetentionPeriod` to specify the retention period for your query results. You can provide your KMS Key for encryption even if you use provided results bucket. You can explore other properties available in `AthenaWorkGroupProps`.

```python
dsf.consumption.AthenaWorkGroup(self, "AthenaWorkGroupProperties",
    name="athena-properties",
    bytes_scanned_cutoff_per_query=104857600,
    result_location_prefix="athena-results/",
    results_encryption_key=user_data_key,
    results_retention_period=Duration.days(1)
)
```

## Grant permission to run queries

We provide `grantRunQueries` method to grant permission to principals to run queries using the workgroup.

```python
athena_wg = dsf.consumption.AthenaWorkGroup(self, "AthenaWorkGroupGrant",
    name="athena-grant",
    result_location_prefix="athena-results/"
)

athena_wg.grant_run_queries(athena_example_role)
```

## Workgroup removal

You can specify if Athena Workgroup construct resources should be deleted when CDK Stack is destroyed using `removalPolicy`. To have an additional layer of protection, we require users to set a global context value for data removal in their CDK applications.

Athena workgroup will be destroyed only if **both** the removal policy parameter of the construct and DSF global removal policy are set to remove objects.

If set to be destroyed, Athena workgroup construct will use `recursiveDeleteOption`, that will delete the workgroup and its contents even if it contains any named queries.

You can set `@data-solutions-framework-on-aws/removeDataOnDestroy` (`true` or `false`) global data removal policy in `cdk.json`:

```json title="cdk.json"
{
  "context": {
    "@data-solutions-framework-on-aws/removeDataOnDestroy": true
  }
}
```

# OpenSearch

An Amazon OpenSearch Domain with SAML integration and access to OpenSearch REST API.

## Overview

The `OpenSearchCluster` construct implements an OpenSeach Domain following best practises including:

* private deployment in VPC
* SAML-authentication plugin to access OpenSearch Dashboards via a SAML2.0-compatible IdP
* access to the OpenSeach REST API to interact with OpenSearch objects like Roles, Indexes, Mappings...

By default VPC also creates VPN client endpoint with SAML-authentication to allow secure access to the dashboards. Optionally, you can also provide your own VPC or choose to deploy internet-facing OpenSearch domain by setting `deployInVpc=false` in construct parameters.

SAML-authentication can work with any SAML2.0-compatible provider like Okta. If you use AWS IAM Identity center please check the section below for details. The construct require at least admin role to be provided as parameters.

For mapping additional IdP roles to OpenSearch dashboard roles, you can use `addRoleMapping` method.

## Configure IAM Identity center

You need to have IAM Identity center enabled in the same region you plan to deploy your solution.
To configure SAML integration with OpenSearch you will need to create a custom SAML 2.0 Application and have at least one user group created and attached to the application.
Please follow the [step-by-step guidance](https://aws.amazon.com/blogs/big-data/role-based-access-control-in-amazon-opensearch-service-via-saml-integration-with-aws-iam-identity-center/) to set up IAM Identity center SAML application.

Main steps are:

1. In the region where you deploy OpenSearch, enable IAM Identity Center with AWS Organizations
2. Create a IAM Identity Center group. Use its group ID in the `saml_master_backend_role` parameter of the construct
3. Create a custom application in IAM Identity Center and provide fake URLs as temporary
4. Download the IAM Identity Center SAML metadata file
5. Extract the entityID URL from the metadata file and pass it to `samlEntityId` parameter of the construct
6. Use the content of the metadata file in the `samlMetadataContent` parameter of the construct
7. Provision the construct
8. Update the IAM Identity Center application attribute mappings by adding

   1. `${user:email}` as the `Subject` with `emailAddress` format. `Subject` is the default subject key used in OpenSearch construct, modify the mapping according to your configuration.
   2. `${user:groups}`as the `Role` with `unspecified` format. `Role` is the default role key used in OpenSearch construct, modify the mapping according to your configuration.
9. Update the IAM Identity Center application configuration

   1. Set the `Application ACS URL` to the `OpenSearch SSO URL (IdP initiated)` from the OpenSearch Domain security configuration
   2. Set the `Application SAML audience` to the `Service provider entity ID` from the OpenSearch Domain security configuration

## Usage

Default configuration

```python
os_cluster = dsf.consumption.OpenSearchCluster(self, "MyOpenSearchCluster",
    domain_name="mycluster",
    saml_entity_id="<IdpIdentityId>",
    saml_metadata_content="<IdpMetadataXml>",
    saml_master_backend_role="<IAMIdentityCenterAdminGroupId>",
    deploy_in_vpc=True,
    removal_policy=cdk.RemovalPolicy.DESTROY
)

os_cluster.add_role_mapping("DashboardOsUser", "dashboards_user", "<IAMIdentityCenterDashboardUsersGroupId>")
os_cluster.add_role_mapping("ReadAllOsRole", "readall", "<IAMIdentityCenterDashboardUsersGroupId>")
```

Using Client VPN Endpoint

```python
vpc_vpn = dsf.utils.DataVpc(self, "VpcWithVpn",
    vpc_cidr="10.0.0.0/16",
    client_vpn_endpoint_props=dsf.utils.DataVpcClientVpnEndpointProps(
        server_certificate_arn="<ACMCertificateArn>",
        saml_metadata_document="<IdpClientVpnApplicationMetadataXml>",
        self_service_portal=False
    )
)
os_cluster = dsf.consumption.OpenSearchCluster(self, "MyOpenSearchCluster",
    domain_name="mycluster",
    saml_entity_id="<IdpIdentityId>",
    saml_metadata_content="<IdpOpenSearchApplicationMetadataXml>",
    saml_master_backend_role="<IAMIdentityCenterAdminGroupId>",
    deploy_in_vpc=True,
    vpc=vpc_vpn.vpc
)

os_cluster.add_role_mapping("DashboardOsUser", "dashboards_user", "<IAMIdentityCenterDashboardUsersGroupId>")
os_cluster.add_role_mapping("ReadAllOsRole", "readall", "<IAMIdentityCenterDashboardUsersGroupId>")
```

# OpenSearch API - Bring you own Opensearch cluster

OpenSearch API client that allows to prepare the data or setup access roles for existing Opensearch clusters. The construct supports both OpenSearch provisioned clusters and OpenSearch Serverless collections.

## Overview

The construct leverages the [CDK Provider Framework](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.custom_resources-readme.html#provider-framework) to deploy a custom resource to manage, and provide `addRoleMapping` and `callOpenSearchApi` methods. Both methods return the custom resource so that allows to enforce sequental execution of the API calls. By default all API calls will be executed simultaneously and are independent of each other.

```python
domain_endpoint = "search-XXXXXX.XXXXXX.es.amazonaws.com"
api_role = Role.from_role_name(self, "ApiRole", "<IAMRoleWithOpenSearchPermissions>")
os_api = dsf.consumption.OpenSearchApi(self, "MyOpenSearchApi",
    iam_handler_role=api_role,
    open_search_endpoint=domain_endpoint,
    open_search_cluster_type=dsf.consumption.OpenSearchClusterType.PROVISIONED,
    removal_policy=cdk.RemovalPolicy.DESTROY
)
```

:::warning

The IAM Role passed as `iamHandlerRole` property has to have all necessary permissions to execute API calls to the cluster.

:::

## callOpenSearchApi

Generic method to execute any Opensearch API, subject to correct permissions attached to the IAM Role.

```python
# create index template
index_template_cr = os_api.call_open_search_api("CreateIndexTemplate", "_index_template/movies", {
    "index_patterns": ["movies-*"
    ],
    "template": {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        },
        "mappings": {
            "properties": {
                "title": {
                    "type": "text"
                },
                "year": {
                    "type": "integer"
                }
            }
        }
    }
})
metadata = "{ \"index\" : { \"_index\" : \"movies-02\"}}"
bulk = f"""{metadata}
      {\"title\": \"Barbie\", \"year\": 2023}
      {metadata}
      {\"title\": \"Openheimer\", \"year\": 2023}"""

# bulk ingestion using POST
bulk_cr = os_api.call_open_search_api("AddBulk", "_bulk", bulk + "\n\n", "POST")
# dependency to enforce sequential API calls
bulk_cr.node.add_dependency(index_template_cr)

add1_cr = os_api.call_open_search_api("AddData1", "movies-01/_doc/1111", {"title": "Rush", "year": 2013}, "PUT")
add1_cr.node.add_dependency(index_template_cr)
add2_cr = os_api.call_open_search_api("AddData3", "movies-01/_doc/2222", {"title": "Toy Story", "year": 2014}, "PUT")
add2_cr.node.add_dependency(index_template_cr)
add3_cr = os_api.call_open_search_api("AddData4", "movies-01/_doc", {"title": "The Little Mermaid", "year": 2015}, "POST")
add3_cr.node.add_dependency(index_template_cr)
```

## addRoleMapping

Use this method to add role mappings to OpenSearch cluster using `_security` plugin.
This method is only applicable to provisioned OpenSearch clusters.

[OpenSearch Roles API](https://opensearch.org/docs/2.13/security/access-control/api#create-role-mapping) does not allow to update individual roles, requiring to pass array of roles that needs to be applied.
To avoid overwriting prevously added roles `addRoleMapping` method provides `persist` parameter to store previously added roles inside the construct. To avoid racing conditions you also need to execute multiple `addRoleMapping` calls sequentionally as shown below.

```python
domain_endpoint = "search-XXXXXX.XXXXXX.es.amazonaws.com"
api_role = Role.from_role_name(self, "ApiRole", "<IAMRoleWithOpenSearchPermissions>")
os_api = dsf.consumption.OpenSearchApi(self, "MyOpenSearchApi",
    iam_handler_role=api_role,
    open_search_endpoint=domain_endpoint,
    open_search_cluster_type=dsf.consumption.OpenSearchClusterType.PROVISIONED,
    removal_policy=cdk.RemovalPolicy.DESTROY
)

first_call = os_api.add_role_mapping("AnotherAdmin", "all_access", "<IAMRole>", True)
second_call = os_api.add_role_mapping("AnotherAdmin", "all_access", "<IAMRole>", True)

# dependency to enforce sequential API calls
second_call.node.add_dependency(first_call)
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
import aws_cdk.aws_athena as _aws_cdk_aws_athena_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_glue as _aws_cdk_aws_glue_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_opensearchservice as _aws_cdk_aws_opensearchservice_ceddda9d
import aws_cdk.aws_redshiftserverless as _aws_cdk_aws_redshiftserverless_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import aws_cdk.custom_resources as _aws_cdk_custom_resources_ceddda9d
import constructs as _constructs_77d1e7e8
from ..governance import DataCatalogDatabase as _DataCatalogDatabase_925dcbbb
from ..utils import CreateServiceLinkedRole as _CreateServiceLinkedRole_fba94500


class AthenaWorkGroup(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.AthenaWorkGroup",
):
    '''An Amazon Athena Workgroup configured with default result bucket.

    Example::

        dsf.consumption.AthenaWorkGroup(self, "AthenaWorkGroupDefault",
            name="athena-default",
            result_location_prefix="athena-default-results/"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        result_location_prefix: builtins.str,
        bytes_scanned_cutoff_per_query: typing.Optional[jsii.Number] = None,
        enforce_work_group_configuration: typing.Optional[builtins.bool] = None,
        engine_version: typing.Optional["EngineVersion"] = None,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        publish_cloud_watch_metrics_enabled: typing.Optional[builtins.bool] = None,
        recursive_delete_option: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        requester_pays_enabled: typing.Optional[builtins.bool] = None,
        result_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        result_bucket_name: typing.Optional[builtins.str] = None,
        results_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        results_retention_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        state: typing.Optional["State"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name: Name of the Workgroup.
        :param result_location_prefix: Specifies the location in Amazon S3 where query results are stored.
        :param bytes_scanned_cutoff_per_query: Indicates the number of days after creation when objects are deleted from the Result bucket.
        :param enforce_work_group_configuration: If set to "true", the settings for the workgroup override client-side settings. Default: - True.
        :param engine_version: The engine version on which the query runs. Default: - AUTO.
        :param execution_role: Role used to access user resources in an Athena for Apache Spark session. Default: - The role is created if PySpark engine version is selected and no role is provided.
        :param publish_cloud_watch_metrics_enabled: Indicates that the Amazon CloudWatch metrics are enabled for the workgroup. Default: - True.
        :param recursive_delete_option: The option to delete a workgroup and its contents even if the workgroup contains any named queries. Default: - Workgroup is retained.
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param requester_pays_enabled: Allows members assigned to a workgroup to reference Amazon S3 Requester Pays buckets in queries. Default: - False.
        :param result_bucket: Amazon S3 Bucket where query results are stored. Default: - Create a new bucket with SSE encryption using AnalyticsBucket if not provided.
        :param result_bucket_name: Name for the S3 Bucket in case it should be created. Default: - Name will be provided.
        :param results_encryption_key: Encryption key used to encrypt query results. Has to be provided if Result bucket is provided. User needs to grant access to it for AthenaWorkGroup's executionRole (if Spark engine) or for principals that were granted to run queries using AthenaWorkGroup's grantRunQueries. Default: - The key is created if Result Bucket is not provided.
        :param results_retention_period: Indicates the number of days after creation when objects are deleted from the Result bucket.
        :param state: The state of the Workgroup. Default: - ENABLED.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15339157ee2b24d990c2efefafd65bf35e69eee9f4bca1f6e95210a8c521bd46)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AthenaWorkgroupProps(
            name=name,
            result_location_prefix=result_location_prefix,
            bytes_scanned_cutoff_per_query=bytes_scanned_cutoff_per_query,
            enforce_work_group_configuration=enforce_work_group_configuration,
            engine_version=engine_version,
            execution_role=execution_role,
            publish_cloud_watch_metrics_enabled=publish_cloud_watch_metrics_enabled,
            recursive_delete_option=recursive_delete_option,
            removal_policy=removal_policy,
            requester_pays_enabled=requester_pays_enabled,
            result_bucket=result_bucket,
            result_bucket_name=result_bucket_name,
            results_encryption_key=results_encryption_key,
            results_retention_period=results_retention_period,
            state=state,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="grantRunQueries")
    def grant_run_queries(
        self,
        principal: _aws_cdk_aws_iam_ceddda9d.IPrincipal,
    ) -> None:
        '''Grants running queries access to Principal.

        :param principal: Principal to attach query access to Athena Workgroup.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dae31e93a53a124faa0e753ab90b50aadc8ec8c3fe3110c4f935b3d20012ef0)
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
        return typing.cast(None, jsii.invoke(self, "grantRunQueries", [principal]))

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
    @jsii.member(jsii_name="resultBucket")
    def result_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''S3 Bucket used for query results.'''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "resultBucket"))

    @builtins.property
    @jsii.member(jsii_name="resultsEncryptionKey")
    def results_encryption_key(self) -> _aws_cdk_aws_kms_ceddda9d.IKey:
        '''KMS Key to encrypt the query results.'''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.IKey, jsii.get(self, "resultsEncryptionKey"))

    @builtins.property
    @jsii.member(jsii_name="workGroup")
    def work_group(self) -> _aws_cdk_aws_athena_ceddda9d.CfnWorkGroup:
        '''Athena Workgroup that is created.'''
        return typing.cast(_aws_cdk_aws_athena_ceddda9d.CfnWorkGroup, jsii.get(self, "workGroup"))

    @builtins.property
    @jsii.member(jsii_name="workGroupName")
    def work_group_name(self) -> builtins.str:
        '''WorkGroup name with the randomized suffix.'''
        return typing.cast(builtins.str, jsii.get(self, "workGroupName"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Role used to access user resources in an Athena for Apache Spark session.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "executionRole"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.AthenaWorkgroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "result_location_prefix": "resultLocationPrefix",
        "bytes_scanned_cutoff_per_query": "bytesScannedCutoffPerQuery",
        "enforce_work_group_configuration": "enforceWorkGroupConfiguration",
        "engine_version": "engineVersion",
        "execution_role": "executionRole",
        "publish_cloud_watch_metrics_enabled": "publishCloudWatchMetricsEnabled",
        "recursive_delete_option": "recursiveDeleteOption",
        "removal_policy": "removalPolicy",
        "requester_pays_enabled": "requesterPaysEnabled",
        "result_bucket": "resultBucket",
        "result_bucket_name": "resultBucketName",
        "results_encryption_key": "resultsEncryptionKey",
        "results_retention_period": "resultsRetentionPeriod",
        "state": "state",
    },
)
class AthenaWorkgroupProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        result_location_prefix: builtins.str,
        bytes_scanned_cutoff_per_query: typing.Optional[jsii.Number] = None,
        enforce_work_group_configuration: typing.Optional[builtins.bool] = None,
        engine_version: typing.Optional["EngineVersion"] = None,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        publish_cloud_watch_metrics_enabled: typing.Optional[builtins.bool] = None,
        recursive_delete_option: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        requester_pays_enabled: typing.Optional[builtins.bool] = None,
        result_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        result_bucket_name: typing.Optional[builtins.str] = None,
        results_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        results_retention_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        state: typing.Optional["State"] = None,
    ) -> None:
        '''Properties for the AthenaWorkgroup Construct.

        :param name: Name of the Workgroup.
        :param result_location_prefix: Specifies the location in Amazon S3 where query results are stored.
        :param bytes_scanned_cutoff_per_query: Indicates the number of days after creation when objects are deleted from the Result bucket.
        :param enforce_work_group_configuration: If set to "true", the settings for the workgroup override client-side settings. Default: - True.
        :param engine_version: The engine version on which the query runs. Default: - AUTO.
        :param execution_role: Role used to access user resources in an Athena for Apache Spark session. Default: - The role is created if PySpark engine version is selected and no role is provided.
        :param publish_cloud_watch_metrics_enabled: Indicates that the Amazon CloudWatch metrics are enabled for the workgroup. Default: - True.
        :param recursive_delete_option: The option to delete a workgroup and its contents even if the workgroup contains any named queries. Default: - Workgroup is retained.
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param requester_pays_enabled: Allows members assigned to a workgroup to reference Amazon S3 Requester Pays buckets in queries. Default: - False.
        :param result_bucket: Amazon S3 Bucket where query results are stored. Default: - Create a new bucket with SSE encryption using AnalyticsBucket if not provided.
        :param result_bucket_name: Name for the S3 Bucket in case it should be created. Default: - Name will be provided.
        :param results_encryption_key: Encryption key used to encrypt query results. Has to be provided if Result bucket is provided. User needs to grant access to it for AthenaWorkGroup's executionRole (if Spark engine) or for principals that were granted to run queries using AthenaWorkGroup's grantRunQueries. Default: - The key is created if Result Bucket is not provided.
        :param results_retention_period: Indicates the number of days after creation when objects are deleted from the Result bucket.
        :param state: The state of the Workgroup. Default: - ENABLED.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cb515883861e94cb0356ff0dbaafe8172250732d8c494d9aefa4ebe8ce1bf67)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument result_location_prefix", value=result_location_prefix, expected_type=type_hints["result_location_prefix"])
            check_type(argname="argument bytes_scanned_cutoff_per_query", value=bytes_scanned_cutoff_per_query, expected_type=type_hints["bytes_scanned_cutoff_per_query"])
            check_type(argname="argument enforce_work_group_configuration", value=enforce_work_group_configuration, expected_type=type_hints["enforce_work_group_configuration"])
            check_type(argname="argument engine_version", value=engine_version, expected_type=type_hints["engine_version"])
            check_type(argname="argument execution_role", value=execution_role, expected_type=type_hints["execution_role"])
            check_type(argname="argument publish_cloud_watch_metrics_enabled", value=publish_cloud_watch_metrics_enabled, expected_type=type_hints["publish_cloud_watch_metrics_enabled"])
            check_type(argname="argument recursive_delete_option", value=recursive_delete_option, expected_type=type_hints["recursive_delete_option"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument requester_pays_enabled", value=requester_pays_enabled, expected_type=type_hints["requester_pays_enabled"])
            check_type(argname="argument result_bucket", value=result_bucket, expected_type=type_hints["result_bucket"])
            check_type(argname="argument result_bucket_name", value=result_bucket_name, expected_type=type_hints["result_bucket_name"])
            check_type(argname="argument results_encryption_key", value=results_encryption_key, expected_type=type_hints["results_encryption_key"])
            check_type(argname="argument results_retention_period", value=results_retention_period, expected_type=type_hints["results_retention_period"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "result_location_prefix": result_location_prefix,
        }
        if bytes_scanned_cutoff_per_query is not None:
            self._values["bytes_scanned_cutoff_per_query"] = bytes_scanned_cutoff_per_query
        if enforce_work_group_configuration is not None:
            self._values["enforce_work_group_configuration"] = enforce_work_group_configuration
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if execution_role is not None:
            self._values["execution_role"] = execution_role
        if publish_cloud_watch_metrics_enabled is not None:
            self._values["publish_cloud_watch_metrics_enabled"] = publish_cloud_watch_metrics_enabled
        if recursive_delete_option is not None:
            self._values["recursive_delete_option"] = recursive_delete_option
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if requester_pays_enabled is not None:
            self._values["requester_pays_enabled"] = requester_pays_enabled
        if result_bucket is not None:
            self._values["result_bucket"] = result_bucket
        if result_bucket_name is not None:
            self._values["result_bucket_name"] = result_bucket_name
        if results_encryption_key is not None:
            self._values["results_encryption_key"] = results_encryption_key
        if results_retention_period is not None:
            self._values["results_retention_period"] = results_retention_period
        if state is not None:
            self._values["state"] = state

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the Workgroup.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def result_location_prefix(self) -> builtins.str:
        '''Specifies the location in Amazon S3 where query results are stored.'''
        result = self._values.get("result_location_prefix")
        assert result is not None, "Required property 'result_location_prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bytes_scanned_cutoff_per_query(self) -> typing.Optional[jsii.Number]:
        '''Indicates the number of days after creation when objects are deleted from the Result bucket.'''
        result = self._values.get("bytes_scanned_cutoff_per_query")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def enforce_work_group_configuration(self) -> typing.Optional[builtins.bool]:
        '''If set to "true", the settings for the workgroup override client-side settings.

        :default: - True.
        '''
        result = self._values.get("enforce_work_group_configuration")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def engine_version(self) -> typing.Optional["EngineVersion"]:
        '''The engine version on which the query runs.

        :default: - AUTO.
        '''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional["EngineVersion"], result)

    @builtins.property
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Role used to access user resources in an Athena for Apache Spark session.

        :default: - The role is created if PySpark engine version is selected and no role is provided.
        '''
        result = self._values.get("execution_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def publish_cloud_watch_metrics_enabled(self) -> typing.Optional[builtins.bool]:
        '''Indicates that the Amazon CloudWatch metrics are enabled for the workgroup.

        :default: - True.
        '''
        result = self._values.get("publish_cloud_watch_metrics_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def recursive_delete_option(self) -> typing.Optional[builtins.bool]:
        '''The option to delete a workgroup and its contents even if the workgroup contains any named queries.

        :default: - Workgroup is retained.
        '''
        result = self._values.get("recursive_delete_option")
        return typing.cast(typing.Optional[builtins.bool], result)

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
    def requester_pays_enabled(self) -> typing.Optional[builtins.bool]:
        '''Allows members assigned to a workgroup to reference Amazon S3 Requester Pays buckets in queries.

        :default: - False.
        '''
        result = self._values.get("requester_pays_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def result_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''Amazon S3 Bucket where query results are stored.

        :default: - Create a new bucket with SSE encryption using AnalyticsBucket if not provided.
        '''
        result = self._values.get("result_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def result_bucket_name(self) -> typing.Optional[builtins.str]:
        '''Name for the S3 Bucket in case it should be created.

        :default: - Name will be provided.
        '''
        result = self._values.get("result_bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def results_encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''Encryption key used to encrypt query results.

        Has to be provided if Result bucket is provided.
        User needs to grant access to it for AthenaWorkGroup's executionRole (if Spark engine) or for
        principals that were granted to run queries using AthenaWorkGroup's grantRunQueries.

        :default: - The key is created if Result Bucket is not provided.
        '''
        result = self._values.get("results_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def results_retention_period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''Indicates the number of days after creation when objects are deleted from the Result bucket.'''
        result = self._values.get("results_retention_period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def state(self) -> typing.Optional["State"]:
        '''The state of the Workgroup.

        :default: - ENABLED.
        '''
        result = self._values.get("state")
        return typing.cast(typing.Optional["State"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaWorkgroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BaseRedshiftDataAccess(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.BaseRedshiftDataAccess",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: typing.Union["RedshiftDataProps", typing.Dict[builtins.str, typing.Any]],
        tracked_construct_props: typing.Any,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        :param tracked_construct_props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9985f4049aa72dd939b7a61db338637dec44417183751017e2218bc9be83c02c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
            check_type(argname="argument tracked_construct_props", value=tracked_construct_props, expected_type=type_hints["tracked_construct_props"])
        jsii.create(self.__class__, self, [scope, id, props, tracked_construct_props])

    @jsii.member(jsii_name="createProviderExecutionRole")
    def _create_provider_execution_role(
        self,
        id: builtins.str,
        data_access_target: typing.Union["RedshiftDataAccessTargetProps", typing.Dict[builtins.str, typing.Any]],
        *,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        cluster_id: typing.Optional[builtins.str] = None,
        create_interface_vpc_endpoint: typing.Optional[builtins.bool] = None,
        execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        existing_interface_vpc_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        workgroup_id: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''
        :param id: -
        :param data_access_target: -
        :param secret: The Secrets Manager Secret containing the admin credentials for the Redshift cluster / namespace.
        :param cluster_id: The name of the Redshift provisioned to query. It must be configured if the ``workgroupId`` is not. Default: - The ``workgroupId`` is used
        :param create_interface_vpc_endpoint: If set to true, create the Redshift Data Interface VPC Endpoint in the configured VPC/Subnets. Default: - false
        :param execution_timeout: The timeout for the query execution. Default: - 5mins
        :param existing_interface_vpc_endpoint: If this parameter is provided, the data access execution security group would be granted inbound to the interface VPC endpoint's security group. This is assuming that the ``createInterfaceVpcEndpoint`` parameter is ``false``. Default: - No security group ingress rule would be created.
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param secret_key: The KMS Key used to encrypt the admin credentials for the Redshift cluster / namespace. Default: - no secret key is used
        :param subnets: The subnets where the Custom Resource Lambda Function would be created in. A Redshift Data API Interface VPC Endpoint is created in the subnets. Default: - No subnets are used. The Custom Resource runs in the Redshift service team subnets.
        :param vpc: The VPC where the Custom Resource Lambda Function would be created in. A Redshift Data API Interface VPC Endpoint is created in the VPC. Default: - No VPC is used. The Custom Resource runs in the Redshift service team VPC
        :param workgroup_id: The ``workgroupId`` for the Redshift Serverless Workgroup to query. It must be configured if the ``clusterId`` is not. Default: - The ``clusterId`` is used
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d0c35b695ab38577c2fecab94b554b10d8b4aafafd90ce100ced23a87e472a0)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument data_access_target", value=data_access_target, expected_type=type_hints["data_access_target"])
        props = RedshiftDataProps(
            secret=secret,
            cluster_id=cluster_id,
            create_interface_vpc_endpoint=create_interface_vpc_endpoint,
            execution_timeout=execution_timeout,
            existing_interface_vpc_endpoint=existing_interface_vpc_endpoint,
            removal_policy=removal_policy,
            secret_key=secret_key,
            subnets=subnets,
            vpc=vpc,
            workgroup_id=workgroup_id,
        )

        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.invoke(self, "createProviderExecutionRole", [id, data_access_target, props]))

    @jsii.member(jsii_name="getDataAccessTarget")
    def _get_data_access_target(
        self,
        *,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        cluster_id: typing.Optional[builtins.str] = None,
        create_interface_vpc_endpoint: typing.Optional[builtins.bool] = None,
        execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        existing_interface_vpc_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        workgroup_id: typing.Optional[builtins.str] = None,
    ) -> "RedshiftDataAccessTargetProps":
        '''
        :param secret: The Secrets Manager Secret containing the admin credentials for the Redshift cluster / namespace.
        :param cluster_id: The name of the Redshift provisioned to query. It must be configured if the ``workgroupId`` is not. Default: - The ``workgroupId`` is used
        :param create_interface_vpc_endpoint: If set to true, create the Redshift Data Interface VPC Endpoint in the configured VPC/Subnets. Default: - false
        :param execution_timeout: The timeout for the query execution. Default: - 5mins
        :param existing_interface_vpc_endpoint: If this parameter is provided, the data access execution security group would be granted inbound to the interface VPC endpoint's security group. This is assuming that the ``createInterfaceVpcEndpoint`` parameter is ``false``. Default: - No security group ingress rule would be created.
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param secret_key: The KMS Key used to encrypt the admin credentials for the Redshift cluster / namespace. Default: - no secret key is used
        :param subnets: The subnets where the Custom Resource Lambda Function would be created in. A Redshift Data API Interface VPC Endpoint is created in the subnets. Default: - No subnets are used. The Custom Resource runs in the Redshift service team subnets.
        :param vpc: The VPC where the Custom Resource Lambda Function would be created in. A Redshift Data API Interface VPC Endpoint is created in the VPC. Default: - No VPC is used. The Custom Resource runs in the Redshift service team VPC
        :param workgroup_id: The ``workgroupId`` for the Redshift Serverless Workgroup to query. It must be configured if the ``clusterId`` is not. Default: - The ``clusterId`` is used
        '''
        props = RedshiftDataProps(
            secret=secret,
            cluster_id=cluster_id,
            create_interface_vpc_endpoint=create_interface_vpc_endpoint,
            execution_timeout=execution_timeout,
            existing_interface_vpc_endpoint=existing_interface_vpc_endpoint,
            removal_policy=removal_policy,
            secret_key=secret_key,
            subnets=subnets,
            vpc=vpc,
            workgroup_id=workgroup_id,
        )

        return typing.cast("RedshiftDataAccessTargetProps", jsii.invoke(self, "getDataAccessTarget", [props]))

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
    @jsii.member(jsii_name="removalPolicy")
    def _removal_policy(self) -> _aws_cdk_ceddda9d.RemovalPolicy:
        return typing.cast(_aws_cdk_ceddda9d.RemovalPolicy, jsii.get(self, "removalPolicy"))

    @builtins.property
    @jsii.member(jsii_name="customResourceSecurityGroup")
    def custom_resource_security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The Security Group used by the Custom Resource when deployed in a VPC.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "customResourceSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="vpcEndpoint")
    def vpc_endpoint(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint]:
        '''The created Redshift Data API interface vpc endpoint when deployed in a VPC.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint], jsii.get(self, "vpcEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="vpcEndpointSecurityGroup")
    def vpc_endpoint_security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The Security Group used by the VPC Endpoint when deployed in a VPC.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "vpcEndpointSecurityGroup"))


class _BaseRedshiftDataAccessProxy(BaseRedshiftDataAccess):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseRedshiftDataAccess).__jsii_proxy_class__ = lambda : _BaseRedshiftDataAccessProxy


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.BaseRedshiftDataSharingAccessProps",
    jsii_struct_bases=[],
    name_mapping={
        "database_name": "databaseName",
        "data_share_name": "dataShareName",
        "account_id": "accountId",
        "data_share_arn": "dataShareArn",
        "namespace_id": "namespaceId",
    },
)
class BaseRedshiftDataSharingAccessProps:
    def __init__(
        self,
        *,
        database_name: builtins.str,
        data_share_name: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        data_share_arn: typing.Optional[builtins.str] = None,
        namespace_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''The base interface for the different data sharing lifecycle properties.

        :param database_name: The name of the Redshift database used in the data sharing.
        :param data_share_name: The name of the data share.
        :param account_id: For cross-account grants, this is the consumer account ID. For cross-account consumers, this is the producer account ID. Default: - No account ID is used.
        :param data_share_arn: The ARN of the datashare. This is required for any action that is cross account. Default: - No data share ARN is used.
        :param namespace_id: For single account grants, this is the consumer namespace ID. For cross-account grants, ``namespaceId`` is ignored. For consumers, this is the producer namespace ID. It is required for both single and cross account data sharing. Default: - No namespace ID is used.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a28e18f6974415cc94fcaebffd87efa6925735276e0230c357d938a182f6d2bb)
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument data_share_name", value=data_share_name, expected_type=type_hints["data_share_name"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument data_share_arn", value=data_share_arn, expected_type=type_hints["data_share_arn"])
            check_type(argname="argument namespace_id", value=namespace_id, expected_type=type_hints["namespace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_name": database_name,
            "data_share_name": data_share_name,
        }
        if account_id is not None:
            self._values["account_id"] = account_id
        if data_share_arn is not None:
            self._values["data_share_arn"] = data_share_arn
        if namespace_id is not None:
            self._values["namespace_id"] = namespace_id

    @builtins.property
    def database_name(self) -> builtins.str:
        '''The name of the Redshift database used in the data sharing.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data_share_name(self) -> builtins.str:
        '''The name of the data share.'''
        result = self._values.get("data_share_name")
        assert result is not None, "Required property 'data_share_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''For cross-account grants, this is the consumer account ID.

        For cross-account consumers, this is the producer account ID.

        :default: - No account ID is used.
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_share_arn(self) -> typing.Optional[builtins.str]:
        '''The ARN of the datashare.

        This is required for any action that is cross account.

        :default: - No data share ARN is used.
        '''
        result = self._values.get("data_share_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace_id(self) -> typing.Optional[builtins.str]:
        '''For single account grants, this is the consumer namespace ID. For cross-account grants, ``namespaceId`` is ignored.

        For consumers, this is the producer namespace ID. It is required for both single and cross account data sharing.

        :default: - No namespace ID is used.
        '''
        result = self._values.get("namespace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseRedshiftDataSharingAccessProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/aws-data-solutions-framework.consumption.EngineVersion")
class EngineVersion(enum.Enum):
    AUTO = "AUTO"
    ATHENA_V3 = "ATHENA_V3"
    PYSPARK_V3 = "PYSPARK_V3"


class OpenSearchApi(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.OpenSearchApi",
):
    '''A construct to create an OpenSearch API client.

    Example::

        from aws_cdk.aws_iam import Role
        
        domain_endpoint = "search-XXXXXX.XXXXXX.es.amazonaws.com"
        api_role = Role.from_role_name(self, "ApiRole", "<IAMRoleWithOpenSearchPermissions>")
        os_api = dsf.consumption.OpenSearchApi(self, "MyOpenSearchApi",
            iam_handler_role=api_role,
            open_search_endpoint=domain_endpoint,
            open_search_cluster_type=dsf.consumption.OpenSearchClusterType.PROVISIONED,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )
        
        role_map = os_api.add_role_mapping("DashBoardUser", "dashboards_user", "<IAMIdentityCenterDashboardUsersGroupId>")
        add1_cr = os_api.call_open_search_api("AddData1", "movies-01/_doc/1111", {"title": "Rush", "year": 2013}, "PUT")
        add1_cr.node.add_dependency(role_map)
        add2_cr = os_api.call_open_search_api("AddData3", "movies-01/_doc/2222", {"title": "Toy Story", "year": 2014}, "PUT")
        add2_cr.node.add_dependency(role_map)
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        iam_handler_role: _aws_cdk_aws_iam_ceddda9d.IRole,
        open_search_cluster_type: "OpenSearchClusterType",
        open_search_endpoint: builtins.str,
        open_search_endpoint_region: typing.Optional[builtins.str] = None,
        query_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        query_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''Constructs a new instance of the OpenSearch API construct.

        :param scope: Construct.
        :param id: unique ID for the construct.
        :param iam_handler_role: The IAM role to pass to IAM authentication lambda handler This role must be able to be assumed with ``lambda.amazonaws.com`` service principal and have the necessary permissions to call OpenSearch API.
        :param open_search_cluster_type: Type of OpenSearch cluster.
        :param open_search_endpoint: The OpenSearch Cluster or Serverless collection endpoint to connect to. if you provisoned your cluster using CDK use domainEndpoint property of OpenSearch provisioned cluster or attrCollectionEndpoint property of OpenSearch Serverless collection.
        :param open_search_endpoint_region: AWS Region openSearchEndpoint is provisioned in. Default: - same region as stack.
        :param query_interval: Time between calls to the ``isComplete`` handler which determines if the resource has been stabilized. Default: Duration.seconds(5)
        :param query_timeout: Total timeout for the entire custom resource operation. The maximum timeout is 1 hour. Default: Duration.minutes(30)
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param security_groups: The list of security groups to attach to the lambda functions. The security groups MUST be exclusively used by the custom resource. Default: - If ``vpc`` is not supplied, no security groups are attached. Otherwise, a dedicated security group is created for each function.
        :param subnets: The subnets where the Custom Resource Lambda Function would be created in. Required if vpc parameter is provided. Default: - One private subnet with egress is used per AZ.
        :param vpc: Defines the virtual networking environment for this construct. Typically should use same VPC as OpenSearch cluster or serverless collection. Must have at least 2 subnets in two different AZs. Default: - no VPC is used.

        :see: OpenSearchApiProps
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8efac875434c2ff3bedcef40f1dbae7e47123a4751d234bd1bac60d2a468e1ef)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OpenSearchApiProps(
            iam_handler_role=iam_handler_role,
            open_search_cluster_type=open_search_cluster_type,
            open_search_endpoint=open_search_endpoint,
            open_search_endpoint_region=open_search_endpoint_region,
            query_interval=query_interval,
            query_timeout=query_timeout,
            removal_policy=removal_policy,
            security_groups=security_groups,
            subnets=subnets,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addRoleMapping")
    def add_role_mapping(
        self,
        id: builtins.str,
        name: builtins.str,
        role: builtins.str,
        persist: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''
        :param id: The CDK resource ID.
        :param name: OpenSearch role name.
        :param role: list of IAM roles. For IAM Identity center provide SAML group Id as a role
        :param persist: Set to true if you want to prevent the roles to be ovewritten by subsequent PUT API calls. Default false.

        :return: CustomResource object.

        :see: https://opensearch.org/docs/2.9/security/access-control/users-roles/#predefined-roles
        :public:

        Add a new role mapping to the cluster.
        This method is used to add a role mapping to the Amazon OpenSearch cluster
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7aeb5e0efc38b4f92132936725a6dff4aa74533cb2028da7462b93cb303afbc)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument persist", value=persist, expected_type=type_hints["persist"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "addRoleMapping", [id, name, role, persist]))

    @jsii.member(jsii_name="callOpenSearchApi")
    def call_open_search_api(
        self,
        id: builtins.str,
        api_path: builtins.str,
        body: typing.Any,
        method: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Calls OpenSearch API using custom resource.

        :param id: The CDK resource ID.
        :param api_path: OpenSearch API path.
        :param body: OpenSearch API request body.
        :param method: Opensearch API method,.

        :default: PUT

        :return: CustomResource object.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ecd8383a967da8ab7ee7f183e887c27ae441daff51214512d7b26ea78e8f41f)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument api_path", value=api_path, expected_type=type_hints["api_path"])
            check_type(argname="argument body", value=body, expected_type=type_hints["body"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "callOpenSearchApi", [id, api_path, body, method]))

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
    @jsii.member(jsii_name="apiFunction")
    def api_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda Function used for the onEventHandler.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "apiFunction"))

    @api_function.setter
    def api_function(self, value: _aws_cdk_aws_lambda_ceddda9d.IFunction) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43a6edd19c0d6911251eed3a9f9c4cfaec5badcf5e6ccef4fc4dabe4188fa83c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiFunction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="apiLogGroup")
    def api_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Log Group for the  onEventHandler Lambda Function.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "apiLogGroup"))

    @api_log_group.setter
    def api_log_group(self, value: _aws_cdk_aws_logs_ceddda9d.ILogGroup) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__260162222abba8d8fb264695411f01927754e8e344d84aff9e285f78d362c2f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiLogGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="apiRole")
    def api_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM Role for the onEventHandler Lambba Function.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "apiRole"))

    @api_role.setter
    def api_role(self, value: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dda92ecf9e44229c03338082bd125f0e0a0f4b2a3734416f9abd87c0b866f3d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiRole", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="apiSecurityGroups")
    def api_security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The list of EC2 Security Groups used by the Lambda Functions.'''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], jsii.get(self, "apiSecurityGroups"))

    @api_security_groups.setter
    def api_security_groups(
        self,
        value: typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c0f4e512135e6844fda97751b0c5dcfad23f99713dd467a913d652a2a16f882)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiSecurityGroups", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.OpenSearchApiProps",
    jsii_struct_bases=[],
    name_mapping={
        "iam_handler_role": "iamHandlerRole",
        "open_search_cluster_type": "openSearchClusterType",
        "open_search_endpoint": "openSearchEndpoint",
        "open_search_endpoint_region": "openSearchEndpointRegion",
        "query_interval": "queryInterval",
        "query_timeout": "queryTimeout",
        "removal_policy": "removalPolicy",
        "security_groups": "securityGroups",
        "subnets": "subnets",
        "vpc": "vpc",
    },
)
class OpenSearchApiProps:
    def __init__(
        self,
        *,
        iam_handler_role: _aws_cdk_aws_iam_ceddda9d.IRole,
        open_search_cluster_type: "OpenSearchClusterType",
        open_search_endpoint: builtins.str,
        open_search_endpoint_region: typing.Optional[builtins.str] = None,
        query_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        query_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''Configuration for the OpenSearch API.

        :param iam_handler_role: The IAM role to pass to IAM authentication lambda handler This role must be able to be assumed with ``lambda.amazonaws.com`` service principal and have the necessary permissions to call OpenSearch API.
        :param open_search_cluster_type: Type of OpenSearch cluster.
        :param open_search_endpoint: The OpenSearch Cluster or Serverless collection endpoint to connect to. if you provisoned your cluster using CDK use domainEndpoint property of OpenSearch provisioned cluster or attrCollectionEndpoint property of OpenSearch Serverless collection.
        :param open_search_endpoint_region: AWS Region openSearchEndpoint is provisioned in. Default: - same region as stack.
        :param query_interval: Time between calls to the ``isComplete`` handler which determines if the resource has been stabilized. Default: Duration.seconds(5)
        :param query_timeout: Total timeout for the entire custom resource operation. The maximum timeout is 1 hour. Default: Duration.minutes(30)
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param security_groups: The list of security groups to attach to the lambda functions. The security groups MUST be exclusively used by the custom resource. Default: - If ``vpc`` is not supplied, no security groups are attached. Otherwise, a dedicated security group is created for each function.
        :param subnets: The subnets where the Custom Resource Lambda Function would be created in. Required if vpc parameter is provided. Default: - One private subnet with egress is used per AZ.
        :param vpc: Defines the virtual networking environment for this construct. Typically should use same VPC as OpenSearch cluster or serverless collection. Must have at least 2 subnets in two different AZs. Default: - no VPC is used.
        '''
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__142210441c72f24f3d7c5b491edc882440257e40fae05d89f8037093e705237d)
            check_type(argname="argument iam_handler_role", value=iam_handler_role, expected_type=type_hints["iam_handler_role"])
            check_type(argname="argument open_search_cluster_type", value=open_search_cluster_type, expected_type=type_hints["open_search_cluster_type"])
            check_type(argname="argument open_search_endpoint", value=open_search_endpoint, expected_type=type_hints["open_search_endpoint"])
            check_type(argname="argument open_search_endpoint_region", value=open_search_endpoint_region, expected_type=type_hints["open_search_endpoint_region"])
            check_type(argname="argument query_interval", value=query_interval, expected_type=type_hints["query_interval"])
            check_type(argname="argument query_timeout", value=query_timeout, expected_type=type_hints["query_timeout"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "iam_handler_role": iam_handler_role,
            "open_search_cluster_type": open_search_cluster_type,
            "open_search_endpoint": open_search_endpoint,
        }
        if open_search_endpoint_region is not None:
            self._values["open_search_endpoint_region"] = open_search_endpoint_region
        if query_interval is not None:
            self._values["query_interval"] = query_interval
        if query_timeout is not None:
            self._values["query_timeout"] = query_timeout
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if subnets is not None:
            self._values["subnets"] = subnets
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def iam_handler_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM role to pass to IAM authentication lambda handler This role must be able to be assumed with ``lambda.amazonaws.com`` service principal and have the necessary permissions to call OpenSearch API.'''
        result = self._values.get("iam_handler_role")
        assert result is not None, "Required property 'iam_handler_role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, result)

    @builtins.property
    def open_search_cluster_type(self) -> "OpenSearchClusterType":
        '''Type of OpenSearch cluster.'''
        result = self._values.get("open_search_cluster_type")
        assert result is not None, "Required property 'open_search_cluster_type' is missing"
        return typing.cast("OpenSearchClusterType", result)

    @builtins.property
    def open_search_endpoint(self) -> builtins.str:
        '''The OpenSearch Cluster or Serverless collection endpoint to connect to.

        if you provisoned your cluster using CDK
        use domainEndpoint property of OpenSearch provisioned cluster or
        attrCollectionEndpoint property of OpenSearch Serverless collection.
        '''
        result = self._values.get("open_search_endpoint")
        assert result is not None, "Required property 'open_search_endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def open_search_endpoint_region(self) -> typing.Optional[builtins.str]:
        '''AWS Region openSearchEndpoint is provisioned in.

        :default: - same region as stack.
        '''
        result = self._values.get("open_search_endpoint_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def query_interval(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''Time between calls to the ``isComplete`` handler which determines if the resource has been stabilized.

        :default: Duration.seconds(5)

        :see: dsf.utils.DsfProviderProps *
        '''
        result = self._values.get("query_interval")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def query_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''Total timeout for the entire custom resource operation.

        The maximum timeout is 1 hour.

        :default: Duration.minutes(30)

        :see: dsf.utils.DsfProviderProps *
        '''
        result = self._values.get("query_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

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
        '''The list of security groups to attach to the lambda functions.

        The security groups MUST be exclusively used by the custom resource.

        :default:

        - If ``vpc`` is not supplied, no security groups are attached. Otherwise, a dedicated security
        group is created for each function.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The subnets where the Custom Resource Lambda Function would be created in.

        Required if vpc parameter is provided.

        :default: - One private subnet with egress is used per AZ.
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''Defines the virtual networking environment for this construct.

        Typically should use same VPC as OpenSearch cluster or serverless collection.
        Must have at least 2 subnets in two different AZs.

        :default: - no VPC is used.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenSearchApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpenSearchCluster(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.OpenSearchCluster",
):
    '''A construct to provision Amazon OpenSearch Cluster and OpenSearch Dashboards.

    Uses IAM Identity Center SAML authentication.
    If OpenSearch cluster is deployed in vpc created using DataVpc construct,
    ClientVPNEndpoint will be provisioned automatically for secure access to OpenSearch Dashboards.

    Example::

        os_cluster = dsf.consumption.OpenSearchCluster(self, "MyOpenSearchCluster",
            domain_name="mycluster1",
            saml_entity_id="<IdpIdentityId>",
            saml_metadata_content="<IdpMetadataXml>",
            saml_master_backend_role="<IAMIdentityCenterAdminGroupId>",
            deploy_in_vpc=True,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )
        
        os_cluster.add_role_mapping("DashBoardUser", "dashboards_user", "<IAMIdentityCenterDashboardUsersGroupId>")
        os_cluster.add_role_mapping("ReadAllRole", "readall", "<IAMIdentityCenterDashboardUsersGroupId>")
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        deploy_in_vpc: builtins.bool,
        domain_name: builtins.str,
        saml_entity_id: builtins.str,
        saml_master_backend_role: builtins.str,
        saml_metadata_content: builtins.str,
        availability_zone_count: typing.Optional[jsii.Number] = None,
        data_node_instance_count: typing.Optional[jsii.Number] = None,
        data_node_instance_type: typing.Optional[builtins.str] = None,
        ebs_size: typing.Optional[jsii.Number] = None,
        ebs_volume_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.EbsDeviceVolumeType] = None,
        enable_auto_software_update: typing.Optional[builtins.bool] = None,
        enable_version_upgrade: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        master_node_instance_count: typing.Optional[jsii.Number] = None,
        master_node_instance_type: typing.Optional[builtins.str] = None,
        multi_az_with_standby_enabled: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        saml_roles_key: typing.Optional[builtins.str] = None,
        saml_session_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        saml_subject_key: typing.Optional[builtins.str] = None,
        version: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        warm_instance_count: typing.Optional[jsii.Number] = None,
        warm_instance_type: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Constructs a new instance of the OpenSearchCluster class.

        :param scope: the Scope of the AWS CDK Construct.
        :param id: the ID of the AWS CDK Construct.
        :param deploy_in_vpc: If the OpenSearch Domain is created in a default VPC when there is no VPC configured.
        :param domain_name: The OpenSearch Domain name.
        :param saml_entity_id: The SAML entity ID used for SAML based authentication.
        :param saml_master_backend_role: The SAML Idp Admin GroupId as returned by {user:groups} in Idp.
        :param saml_metadata_content: The SAML Idp XML Metadata Content, needs to be downloaded from IAM Identity Center.
        :param availability_zone_count: The number of availability zones to use. Be sure to configure the number of data nodes to a multiple of the number of AZ. Default: - For private Domains, use the number of configured ``vpcSubnets`` or the number of AZ in the VPC if not configured. For public Domains, 1 AZ is used.
        :param data_node_instance_count: The number of OpenSearch data nodes to provision. Be sure to configure the number of data nodes to a multiple of the number of AZ. Default: - For public Domains, 1 data node is created. For private Domains, 1 data node per AZ.
        :param data_node_instance_type: The EC2 Instance Type used for OpenSearch data nodes. Default: -
        :param ebs_size: The size of EBS Volumes to use. Default: - 10
        :param ebs_volume_type: The type of EBS Volumes to use. Default: - EbsDeviceVolumeType.GENERAL_PURPOSE_SSD_GP3 is used
        :param enable_auto_software_update: Enable OpenSearch Auto Software Update. Default: - false
        :param enable_version_upgrade: Enable OpenSearch Version Upgrade. Default: - false
        :param encryption_key: The KMS Key for encryption in OpenSearch (data and logs). Default: - A new key is created
        :param master_node_instance_count: The number of OpenSearch master nodes to provision. Default: - No master nodes are created
        :param master_node_instance_type: The EC2 Instance Type for OpenSearch master nodes. Default: -
        :param multi_az_with_standby_enabled: If multi AZ with standby mode is enabled. Default: - false
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param saml_roles_key: The SAML Roles Key. Default: - "Role" is used
        :param saml_session_timeout: The timeout of the SAML session. Max allowed value is 24 hours. Default: - 480 minutes
        :param saml_subject_key: The SAML Subject Key. Default: - No subject key is used
        :param version: The OpenSearch version. Default: -
        :param vpc: The VPC to deploy the OpenSearch Domain. Default: - A new VPC is created if ``deployInVpc`` is ``true``,
        :param vpc_subnets: The VPC private Subnets to deploy the OpenSearch cluster nodes. Only used for VPC deployments. You must configure a VPC if you configure this parameter. Provide only one Subnet per AZ. Default: - Single private subnet per each AZ.
        :param warm_instance_count: The number of Ultra Warn nodes to provision. Default: - No Ultra Warn nodes are created
        :param warm_instance_type: The type of nodes for Ultra Warn nodes. Default: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60f575b30a96a58830f495b53ff60cfcbd6167aef0ea4f794adc5678f7b24a0e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OpenSearchClusterProps(
            deploy_in_vpc=deploy_in_vpc,
            domain_name=domain_name,
            saml_entity_id=saml_entity_id,
            saml_master_backend_role=saml_master_backend_role,
            saml_metadata_content=saml_metadata_content,
            availability_zone_count=availability_zone_count,
            data_node_instance_count=data_node_instance_count,
            data_node_instance_type=data_node_instance_type,
            ebs_size=ebs_size,
            ebs_volume_type=ebs_volume_type,
            enable_auto_software_update=enable_auto_software_update,
            enable_version_upgrade=enable_version_upgrade,
            encryption_key=encryption_key,
            master_node_instance_count=master_node_instance_count,
            master_node_instance_type=master_node_instance_type,
            multi_az_with_standby_enabled=multi_az_with_standby_enabled,
            removal_policy=removal_policy,
            saml_roles_key=saml_roles_key,
            saml_session_timeout=saml_session_timeout,
            saml_subject_key=saml_subject_key,
            version=version,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            warm_instance_count=warm_instance_count,
            warm_instance_type=warm_instance_type,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addRoleMapping")
    def add_role_mapping(
        self,
        id: builtins.str,
        name: builtins.str,
        role: builtins.str,
        persist: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''
        :param id: The CDK resource ID.
        :param name: OpenSearch role name.
        :param role: list of IAM roles. For IAM Identity center provide SAML group Id as a role
        :param persist: Set to true if you want to prevent the roles to be ovewritten by subsequent PUT API calls. Default false.

        :return: CustomResource object.

        :see: https://opensearch.org/docs/2.9/security/access-control/users-roles/#predefined-roles
        :public:

        Add a new role mapping to the cluster.
        This method is used to add a role mapping to the Amazon OpenSearch cluster
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a2802fc2c9fb60dc104a1f00436fda25dcfa3e7b38fe466059411c265fabb80)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument persist", value=persist, expected_type=type_hints["persist"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "addRoleMapping", [id, name, role, persist]))

    @jsii.member(jsii_name="callOpenSearchApi")
    def call_open_search_api(
        self,
        id: builtins.str,
        api_path: builtins.str,
        body: typing.Any,
        method: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Calls OpenSearch API using custom resource.

        :param id: The CDK resource ID.
        :param api_path: OpenSearch API path.
        :param body: OpenSearch API request body.
        :param method: Opensearch API method,.

        :default: PUT

        :return: CustomResource object.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab2f032aaae68164347e789baa2a730951e9dba8c79c67088effadcdebe23be4)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument api_path", value=api_path, expected_type=type_hints["api_path"])
            check_type(argname="argument body", value=body, expected_type=type_hints["body"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "callOpenSearchApi", [id, api_path, body, method]))

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
    @jsii.member(jsii_name="domain")
    def domain(self) -> _aws_cdk_aws_opensearchservice_ceddda9d.IDomain:
        '''OpenSearchCluster domain.'''
        return typing.cast(_aws_cdk_aws_opensearchservice_ceddda9d.IDomain, jsii.get(self, "domain"))

    @builtins.property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> _aws_cdk_aws_kms_ceddda9d.IKey:
        '''The KMS Key used to encrypt data and logs.'''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.IKey, jsii.get(self, "encryptionKey"))

    @builtins.property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''CloudWatch Logs Log Group to store OpenSearch cluster logs.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "logGroup"))

    @builtins.property
    @jsii.member(jsii_name="masterRole")
    def master_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''IAM Role used to provision and configure OpenSearch domain.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "masterRole"))

    @builtins.property
    @jsii.member(jsii_name="openSearchApiFunction")
    def open_search_api_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''Lambda Function used for OpenSearch API.

        :see: OpenSearchApi
        '''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "openSearchApiFunction"))

    @builtins.property
    @jsii.member(jsii_name="openSearchApiLogGroup")
    def open_search_api_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''CloudWatch Logs Log Group to store OpenSearch API logs.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "openSearchApiLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="apiSecurityGroups")
    def api_security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''Security Group for OpenSearch API Lambda Function.

        :see: OpenSearchApi
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], jsii.get(self, "apiSecurityGroups"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''VPC OpenSearch cluster is provisioned in.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.OpenSearchClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "deploy_in_vpc": "deployInVpc",
        "domain_name": "domainName",
        "saml_entity_id": "samlEntityId",
        "saml_master_backend_role": "samlMasterBackendRole",
        "saml_metadata_content": "samlMetadataContent",
        "availability_zone_count": "availabilityZoneCount",
        "data_node_instance_count": "dataNodeInstanceCount",
        "data_node_instance_type": "dataNodeInstanceType",
        "ebs_size": "ebsSize",
        "ebs_volume_type": "ebsVolumeType",
        "enable_auto_software_update": "enableAutoSoftwareUpdate",
        "enable_version_upgrade": "enableVersionUpgrade",
        "encryption_key": "encryptionKey",
        "master_node_instance_count": "masterNodeInstanceCount",
        "master_node_instance_type": "masterNodeInstanceType",
        "multi_az_with_standby_enabled": "multiAzWithStandbyEnabled",
        "removal_policy": "removalPolicy",
        "saml_roles_key": "samlRolesKey",
        "saml_session_timeout": "samlSessionTimeout",
        "saml_subject_key": "samlSubjectKey",
        "version": "version",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "warm_instance_count": "warmInstanceCount",
        "warm_instance_type": "warmInstanceType",
    },
)
class OpenSearchClusterProps:
    def __init__(
        self,
        *,
        deploy_in_vpc: builtins.bool,
        domain_name: builtins.str,
        saml_entity_id: builtins.str,
        saml_master_backend_role: builtins.str,
        saml_metadata_content: builtins.str,
        availability_zone_count: typing.Optional[jsii.Number] = None,
        data_node_instance_count: typing.Optional[jsii.Number] = None,
        data_node_instance_type: typing.Optional[builtins.str] = None,
        ebs_size: typing.Optional[jsii.Number] = None,
        ebs_volume_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.EbsDeviceVolumeType] = None,
        enable_auto_software_update: typing.Optional[builtins.bool] = None,
        enable_version_upgrade: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        master_node_instance_count: typing.Optional[jsii.Number] = None,
        master_node_instance_type: typing.Optional[builtins.str] = None,
        multi_az_with_standby_enabled: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        saml_roles_key: typing.Optional[builtins.str] = None,
        saml_session_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        saml_subject_key: typing.Optional[builtins.str] = None,
        version: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        warm_instance_count: typing.Optional[jsii.Number] = None,
        warm_instance_type: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Simplified configuration for the OpenSearch Cluster.

        :param deploy_in_vpc: If the OpenSearch Domain is created in a default VPC when there is no VPC configured.
        :param domain_name: The OpenSearch Domain name.
        :param saml_entity_id: The SAML entity ID used for SAML based authentication.
        :param saml_master_backend_role: The SAML Idp Admin GroupId as returned by {user:groups} in Idp.
        :param saml_metadata_content: The SAML Idp XML Metadata Content, needs to be downloaded from IAM Identity Center.
        :param availability_zone_count: The number of availability zones to use. Be sure to configure the number of data nodes to a multiple of the number of AZ. Default: - For private Domains, use the number of configured ``vpcSubnets`` or the number of AZ in the VPC if not configured. For public Domains, 1 AZ is used.
        :param data_node_instance_count: The number of OpenSearch data nodes to provision. Be sure to configure the number of data nodes to a multiple of the number of AZ. Default: - For public Domains, 1 data node is created. For private Domains, 1 data node per AZ.
        :param data_node_instance_type: The EC2 Instance Type used for OpenSearch data nodes. Default: -
        :param ebs_size: The size of EBS Volumes to use. Default: - 10
        :param ebs_volume_type: The type of EBS Volumes to use. Default: - EbsDeviceVolumeType.GENERAL_PURPOSE_SSD_GP3 is used
        :param enable_auto_software_update: Enable OpenSearch Auto Software Update. Default: - false
        :param enable_version_upgrade: Enable OpenSearch Version Upgrade. Default: - false
        :param encryption_key: The KMS Key for encryption in OpenSearch (data and logs). Default: - A new key is created
        :param master_node_instance_count: The number of OpenSearch master nodes to provision. Default: - No master nodes are created
        :param master_node_instance_type: The EC2 Instance Type for OpenSearch master nodes. Default: -
        :param multi_az_with_standby_enabled: If multi AZ with standby mode is enabled. Default: - false
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param saml_roles_key: The SAML Roles Key. Default: - "Role" is used
        :param saml_session_timeout: The timeout of the SAML session. Max allowed value is 24 hours. Default: - 480 minutes
        :param saml_subject_key: The SAML Subject Key. Default: - No subject key is used
        :param version: The OpenSearch version. Default: -
        :param vpc: The VPC to deploy the OpenSearch Domain. Default: - A new VPC is created if ``deployInVpc`` is ``true``,
        :param vpc_subnets: The VPC private Subnets to deploy the OpenSearch cluster nodes. Only used for VPC deployments. You must configure a VPC if you configure this parameter. Provide only one Subnet per AZ. Default: - Single private subnet per each AZ.
        :param warm_instance_count: The number of Ultra Warn nodes to provision. Default: - No Ultra Warn nodes are created
        :param warm_instance_type: The type of nodes for Ultra Warn nodes. Default: -
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ab254d0fd8b8275467b9080f08ede4baf63fc2639bc444965e3c87af35c6995)
            check_type(argname="argument deploy_in_vpc", value=deploy_in_vpc, expected_type=type_hints["deploy_in_vpc"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument saml_entity_id", value=saml_entity_id, expected_type=type_hints["saml_entity_id"])
            check_type(argname="argument saml_master_backend_role", value=saml_master_backend_role, expected_type=type_hints["saml_master_backend_role"])
            check_type(argname="argument saml_metadata_content", value=saml_metadata_content, expected_type=type_hints["saml_metadata_content"])
            check_type(argname="argument availability_zone_count", value=availability_zone_count, expected_type=type_hints["availability_zone_count"])
            check_type(argname="argument data_node_instance_count", value=data_node_instance_count, expected_type=type_hints["data_node_instance_count"])
            check_type(argname="argument data_node_instance_type", value=data_node_instance_type, expected_type=type_hints["data_node_instance_type"])
            check_type(argname="argument ebs_size", value=ebs_size, expected_type=type_hints["ebs_size"])
            check_type(argname="argument ebs_volume_type", value=ebs_volume_type, expected_type=type_hints["ebs_volume_type"])
            check_type(argname="argument enable_auto_software_update", value=enable_auto_software_update, expected_type=type_hints["enable_auto_software_update"])
            check_type(argname="argument enable_version_upgrade", value=enable_version_upgrade, expected_type=type_hints["enable_version_upgrade"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument master_node_instance_count", value=master_node_instance_count, expected_type=type_hints["master_node_instance_count"])
            check_type(argname="argument master_node_instance_type", value=master_node_instance_type, expected_type=type_hints["master_node_instance_type"])
            check_type(argname="argument multi_az_with_standby_enabled", value=multi_az_with_standby_enabled, expected_type=type_hints["multi_az_with_standby_enabled"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument saml_roles_key", value=saml_roles_key, expected_type=type_hints["saml_roles_key"])
            check_type(argname="argument saml_session_timeout", value=saml_session_timeout, expected_type=type_hints["saml_session_timeout"])
            check_type(argname="argument saml_subject_key", value=saml_subject_key, expected_type=type_hints["saml_subject_key"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument warm_instance_count", value=warm_instance_count, expected_type=type_hints["warm_instance_count"])
            check_type(argname="argument warm_instance_type", value=warm_instance_type, expected_type=type_hints["warm_instance_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "deploy_in_vpc": deploy_in_vpc,
            "domain_name": domain_name,
            "saml_entity_id": saml_entity_id,
            "saml_master_backend_role": saml_master_backend_role,
            "saml_metadata_content": saml_metadata_content,
        }
        if availability_zone_count is not None:
            self._values["availability_zone_count"] = availability_zone_count
        if data_node_instance_count is not None:
            self._values["data_node_instance_count"] = data_node_instance_count
        if data_node_instance_type is not None:
            self._values["data_node_instance_type"] = data_node_instance_type
        if ebs_size is not None:
            self._values["ebs_size"] = ebs_size
        if ebs_volume_type is not None:
            self._values["ebs_volume_type"] = ebs_volume_type
        if enable_auto_software_update is not None:
            self._values["enable_auto_software_update"] = enable_auto_software_update
        if enable_version_upgrade is not None:
            self._values["enable_version_upgrade"] = enable_version_upgrade
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if master_node_instance_count is not None:
            self._values["master_node_instance_count"] = master_node_instance_count
        if master_node_instance_type is not None:
            self._values["master_node_instance_type"] = master_node_instance_type
        if multi_az_with_standby_enabled is not None:
            self._values["multi_az_with_standby_enabled"] = multi_az_with_standby_enabled
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if saml_roles_key is not None:
            self._values["saml_roles_key"] = saml_roles_key
        if saml_session_timeout is not None:
            self._values["saml_session_timeout"] = saml_session_timeout
        if saml_subject_key is not None:
            self._values["saml_subject_key"] = saml_subject_key
        if version is not None:
            self._values["version"] = version
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if warm_instance_count is not None:
            self._values["warm_instance_count"] = warm_instance_count
        if warm_instance_type is not None:
            self._values["warm_instance_type"] = warm_instance_type

    @builtins.property
    def deploy_in_vpc(self) -> builtins.bool:
        '''If the OpenSearch Domain is created in a default VPC when there is no VPC configured.'''
        result = self._values.get("deploy_in_vpc")
        assert result is not None, "Required property 'deploy_in_vpc' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''The OpenSearch Domain name.'''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def saml_entity_id(self) -> builtins.str:
        '''The SAML entity ID used for SAML based authentication.'''
        result = self._values.get("saml_entity_id")
        assert result is not None, "Required property 'saml_entity_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def saml_master_backend_role(self) -> builtins.str:
        '''The SAML Idp Admin GroupId as returned by {user:groups} in Idp.'''
        result = self._values.get("saml_master_backend_role")
        assert result is not None, "Required property 'saml_master_backend_role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def saml_metadata_content(self) -> builtins.str:
        '''The SAML Idp XML Metadata Content, needs to be downloaded from IAM Identity Center.'''
        result = self._values.get("saml_metadata_content")
        assert result is not None, "Required property 'saml_metadata_content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def availability_zone_count(self) -> typing.Optional[jsii.Number]:
        '''The number of availability zones to use.

        Be sure to configure the number of data nodes to a multiple of the number of AZ.

        :default:

        - For private Domains, use the number of configured ``vpcSubnets`` or the number of AZ in the VPC if not configured.
        For public Domains, 1 AZ is used.
        '''
        result = self._values.get("availability_zone_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def data_node_instance_count(self) -> typing.Optional[jsii.Number]:
        '''The number of OpenSearch data nodes to provision.

        Be sure to configure the number of data nodes to a multiple of the number of AZ.

        :default: - For public Domains, 1 data node is created. For private Domains, 1 data node per AZ.
        '''
        result = self._values.get("data_node_instance_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def data_node_instance_type(self) -> typing.Optional[builtins.str]:
        '''The EC2 Instance Type used for OpenSearch data nodes.

        :default: -

        :see: OpenSearchNodes.DATA_NODE_INSTANCE_DEFAULT
        '''
        result = self._values.get("data_node_instance_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs_size(self) -> typing.Optional[jsii.Number]:
        '''The size of EBS Volumes to use.

        :default: - 10
        '''
        result = self._values.get("ebs_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_volume_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.EbsDeviceVolumeType]:
        '''The type of EBS Volumes to use.

        :default: - EbsDeviceVolumeType.GENERAL_PURPOSE_SSD_GP3 is used
        '''
        result = self._values.get("ebs_volume_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.EbsDeviceVolumeType], result)

    @builtins.property
    def enable_auto_software_update(self) -> typing.Optional[builtins.bool]:
        '''Enable OpenSearch Auto Software Update.

        :default: - false
        '''
        result = self._values.get("enable_auto_software_update")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_version_upgrade(self) -> typing.Optional[builtins.bool]:
        '''Enable OpenSearch Version Upgrade.

        :default: - false
        '''
        result = self._values.get("enable_version_upgrade")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS Key for encryption in OpenSearch (data and logs).

        :default: - A new key is created
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def master_node_instance_count(self) -> typing.Optional[jsii.Number]:
        '''The number of OpenSearch master nodes to provision.

        :default: - No master nodes are created
        '''
        result = self._values.get("master_node_instance_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def master_node_instance_type(self) -> typing.Optional[builtins.str]:
        '''The EC2 Instance Type for OpenSearch master nodes.

        :default: -

        :see: OpenSearchNodes.MASTER_NODE_INSTANCE_DEFAULT
        '''
        result = self._values.get("master_node_instance_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def multi_az_with_standby_enabled(self) -> typing.Optional[builtins.bool]:
        '''If multi AZ with standby mode is enabled.

        :default: - false
        '''
        result = self._values.get("multi_az_with_standby_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

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
    def saml_roles_key(self) -> typing.Optional[builtins.str]:
        '''The SAML Roles Key.

        :default: - "Role" is used
        '''
        result = self._values.get("saml_roles_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def saml_session_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The timeout of the SAML session.

        Max allowed value is 24 hours.

        :default: - 480 minutes
        '''
        result = self._values.get("saml_session_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def saml_subject_key(self) -> typing.Optional[builtins.str]:
        '''The SAML Subject Key.

        :default: - No subject key is used
        '''
        result = self._values.get("saml_subject_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion]:
        '''The OpenSearch version.

        :default: -

        :see: OPENSEARCH_DEFAULT_VERSION
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC to deploy the OpenSearch Domain.

        :default: - A new VPC is created if ``deployInVpc`` is ``true``,

        :see: DataVpc
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The VPC private Subnets to deploy the OpenSearch cluster nodes.

        Only used for VPC deployments.
        You must configure a VPC if you configure this parameter. Provide only one Subnet per AZ.

        :default: - Single private subnet per each AZ.

        :see: DataVpc
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def warm_instance_count(self) -> typing.Optional[jsii.Number]:
        '''The number of Ultra Warn nodes to provision.

        :default: - No Ultra Warn nodes are created
        '''
        result = self._values.get("warm_instance_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def warm_instance_type(self) -> typing.Optional[jsii.Number]:
        '''The type of nodes for Ultra Warn nodes.

        :default: -

        :see: OpenSearchNodes.WARM_NODE_INSTANCE_DEFAULT
        '''
        result = self._values.get("warm_instance_type")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenSearchClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.OpenSearchClusterType"
)
class OpenSearchClusterType(enum.Enum):
    PROVISIONED = "PROVISIONED"
    SERVERLESS = "SERVERLESS"


@jsii.enum(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.OpenSearchNodes"
)
class OpenSearchNodes(enum.Enum):
    '''Default Node Instances for OpenSearch cluster.'''

    DATA_NODE_INSTANCE_DEFAULT = "DATA_NODE_INSTANCE_DEFAULT"
    MASTER_NODE_INSTANCE_DEFAULT = "MASTER_NODE_INSTANCE_DEFAULT"
    WARM_NODE_INSTANCE_DEFAULT = "WARM_NODE_INSTANCE_DEFAULT"


class RedshiftData(
    BaseRedshiftDataAccess,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.RedshiftData",
):
    '''Creates an asynchronous custom resource that handles the execution of SQL using Redshift's Data API.

    If ``vpc`` and ``vpcSubnets`` are passed, this construct would also create the Redshift Data Interface VPC endpoint and configure the custom resource in the same VPC subnet.

    Example::

        namespace = dsf.consumption.RedshiftServerlessNamespace(self, "RedshiftNamespace",
            name="default",
            db_name="defaultdb"
        )
        
        workgroup = dsf.consumption.RedshiftServerlessWorkgroup(self, "RedshiftWorkgroup",
            name="redshift-workgroup",
            namespace=namespace
        )
        
        rs_data = workgroup.access_data("DataApi")
        rs_data.create_db_role("EngineeringRole", "defaultdb", "engineering")
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        cluster_id: typing.Optional[builtins.str] = None,
        create_interface_vpc_endpoint: typing.Optional[builtins.bool] = None,
        execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        existing_interface_vpc_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        workgroup_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param secret: The Secrets Manager Secret containing the admin credentials for the Redshift cluster / namespace.
        :param cluster_id: The name of the Redshift provisioned to query. It must be configured if the ``workgroupId`` is not. Default: - The ``workgroupId`` is used
        :param create_interface_vpc_endpoint: If set to true, create the Redshift Data Interface VPC Endpoint in the configured VPC/Subnets. Default: - false
        :param execution_timeout: The timeout for the query execution. Default: - 5mins
        :param existing_interface_vpc_endpoint: If this parameter is provided, the data access execution security group would be granted inbound to the interface VPC endpoint's security group. This is assuming that the ``createInterfaceVpcEndpoint`` parameter is ``false``. Default: - No security group ingress rule would be created.
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param secret_key: The KMS Key used to encrypt the admin credentials for the Redshift cluster / namespace. Default: - no secret key is used
        :param subnets: The subnets where the Custom Resource Lambda Function would be created in. A Redshift Data API Interface VPC Endpoint is created in the subnets. Default: - No subnets are used. The Custom Resource runs in the Redshift service team subnets.
        :param vpc: The VPC where the Custom Resource Lambda Function would be created in. A Redshift Data API Interface VPC Endpoint is created in the VPC. Default: - No VPC is used. The Custom Resource runs in the Redshift service team VPC
        :param workgroup_id: The ``workgroupId`` for the Redshift Serverless Workgroup to query. It must be configured if the ``clusterId`` is not. Default: - The ``clusterId`` is used
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9a2d248d6fbf659d115f24968cc59aac0104e5a923ac52cee2a23bce808688e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RedshiftDataProps(
            secret=secret,
            cluster_id=cluster_id,
            create_interface_vpc_endpoint=create_interface_vpc_endpoint,
            execution_timeout=execution_timeout,
            existing_interface_vpc_endpoint=existing_interface_vpc_endpoint,
            removal_policy=removal_policy,
            secret_key=secret_key,
            subnets=subnets,
            vpc=vpc,
            workgroup_id=workgroup_id,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="assignDbRolesToIAMRole")
    def assign_db_roles_to_iam_role(
        self,
        db_roles: typing.Sequence[builtins.str],
        target_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    ) -> None:
        '''Assigns Redshift DB roles to IAM role vs the ``RedshiftDbRoles`` tag.

        :param db_roles: List of Redshift DB roles to assign to IAM role.
        :param target_role: The IAM role to assign the Redshift DB roles to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d69eede88c497092e8f7fd603a0542f6c9554b439f3bf93346b28c818678472c)
            check_type(argname="argument db_roles", value=db_roles, expected_type=type_hints["db_roles"])
            check_type(argname="argument target_role", value=target_role, expected_type=type_hints["target_role"])
        return typing.cast(None, jsii.invoke(self, "assignDbRolesToIAMRole", [db_roles, target_role]))

    @jsii.member(jsii_name="createDbRole")
    def create_db_role(
        self,
        id: builtins.str,
        database_name: builtins.str,
        role_name: builtins.str,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Creates a new DB role.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param role_name: The name of the role to create.

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f14371ad2ad05c07137e411b1d1d513561fc32a19c5e32873b7434c9bd6ce958)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "createDbRole", [id, database_name, role_name]))

    @jsii.member(jsii_name="grantDbAllPrivilegesToRole")
    def grant_db_all_privileges_to_role(
        self,
        id: builtins.str,
        database_name: builtins.str,
        schema: builtins.str,
        role_name: builtins.str,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Grants both read and write permissions on all the tables in the ``schema`` to the DB role.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param schema: The schema where the tables are located in.
        :param role_name: The DB role to grant the permissions to.

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3a8c6a93b4f6656c5b5465925552b1d9bcf808d0960799d84a434e67eb29cd6)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "grantDbAllPrivilegesToRole", [id, database_name, schema, role_name]))

    @jsii.member(jsii_name="grantDbSchemaToRole")
    def grant_db_schema_to_role(
        self,
        id: builtins.str,
        database_name: builtins.str,
        schema: builtins.str,
        role_name: builtins.str,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Grants access to the schema to the DB role.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param schema: The schema where the tables are located in.
        :param role_name: The DB role to grant the permissions to.

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e10fab791ae834d9c06b689c13987c2ee10638ec886903128e17f47014fe0e6)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "grantDbSchemaToRole", [id, database_name, schema, role_name]))

    @jsii.member(jsii_name="grantSchemaReadToRole")
    def grant_schema_read_to_role(
        self,
        id: builtins.str,
        database_name: builtins.str,
        schema: builtins.str,
        role_name: builtins.str,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Grants read permission on all the tables in the ``schema`` to the DB role.

        :param id: -
        :param database_name: The name of the database to run this command.
        :param schema: The schema where the tables are located in.
        :param role_name: The DB role to grant the permissions to.

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4dfcf9706dcab4280387aae8ed45d13e997c2395e953d93135c70de8cc6884b)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "grantSchemaReadToRole", [id, database_name, schema, role_name]))

    @jsii.member(jsii_name="ingestData")
    def ingest_data(
        self,
        id: builtins.str,
        database_name: builtins.str,
        target_table: builtins.str,
        source_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        source_prefix: builtins.str,
        ingest_additional_options: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Ingest data from S3 into a Redshift table.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param target_table: The target table to load the data into.
        :param source_bucket: The bucket where the source data would be coming from.
        :param source_prefix: The location inside the bucket where the data would be ingested from.
        :param ingest_additional_options: Optional. Additional options to pass to the ``COPY`` command. For example, ``delimiter '|'`` or ``ignoreheader 1``
        :param role: Optional. The IAM Role to use to access the data in S3. If not provided, it would use the default IAM role configured in the Redshift Namespace
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e780d5708468f127fb8b94065194842b051792812507b57493d738900b10e2bc)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument target_table", value=target_table, expected_type=type_hints["target_table"])
            check_type(argname="argument source_bucket", value=source_bucket, expected_type=type_hints["source_bucket"])
            check_type(argname="argument source_prefix", value=source_prefix, expected_type=type_hints["source_prefix"])
            check_type(argname="argument ingest_additional_options", value=ingest_additional_options, expected_type=type_hints["ingest_additional_options"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "ingestData", [id, database_name, target_table, source_bucket, source_prefix, ingest_additional_options, role]))

    @jsii.member(jsii_name="mergeToTargetTable")
    def merge_to_target_table(
        self,
        id: builtins.str,
        database_name: builtins.str,
        source_table: builtins.str,
        target_table: builtins.str,
        source_column_id: typing.Optional[builtins.str] = None,
        target_column_id: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Run the ``MERGE`` query using simplified mode.

        This command would do an upsert into the target table.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param source_table: The source table name. Schema can also be included using the following format: ``schemaName.tableName``
        :param target_table: The target table name. Schema can also be included using the following format: ``schemaName.tableName``
        :param source_column_id: The column in the source table that's used to determine whether the rows in the ``sourceTable`` can be matched with rows in the ``targetTable``. Default is ``id``
        :param target_column_id: The column in the target table that's used to determine whether the rows in the ``sourceTable`` can be matched with rows in the ``targetTable``. Default is ``id``

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34612948d8c76fa94cac7ac063e59ccb539459f9fa991d1d0c5c3925a10b4181)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument source_table", value=source_table, expected_type=type_hints["source_table"])
            check_type(argname="argument target_table", value=target_table, expected_type=type_hints["target_table"])
            check_type(argname="argument source_column_id", value=source_column_id, expected_type=type_hints["source_column_id"])
            check_type(argname="argument target_column_id", value=target_column_id, expected_type=type_hints["target_column_id"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "mergeToTargetTable", [id, database_name, source_table, target_table, source_column_id, target_column_id]))

    @jsii.member(jsii_name="runCustomSQL")
    def run_custom_sql(
        self,
        id: builtins.str,
        database_name: builtins.str,
        sql: builtins.str,
        delete_sql: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Runs a custom SQL.

        Once the custom resource finishes execution, the attribute ``Data`` contains an attribute ``execId`` which contains the Redshift Data API execution ID. You can then use this to retrieve execution results via the ``GetStatementResult`` API.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param sql: The sql to run.
        :param delete_sql: Optional. The sql to run when this resource gets deleted

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79343924d71f835a06e1f24ed7dbe20b8c9fb32df7c1089747cc9cfe30bd9e03)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument sql", value=sql, expected_type=type_hints["sql"])
            check_type(argname="argument delete_sql", value=delete_sql, expected_type=type_hints["delete_sql"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "runCustomSQL", [id, database_name, sql, delete_sql]))

    @builtins.property
    @jsii.member(jsii_name="dataAccessTargetProps")
    def data_access_target_props(self) -> "RedshiftDataAccessTargetProps":
        '''Contains normalized details of the target Redshift cluster/workgroup for data access.'''
        return typing.cast("RedshiftDataAccessTargetProps", jsii.get(self, "dataAccessTargetProps"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM Role for the Redshift Data API execution.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "executionRole"))

    @builtins.property
    @jsii.member(jsii_name="statusFunction")
    def status_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda Function for the Redshift Data API status checks.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "statusFunction"))

    @builtins.property
    @jsii.member(jsii_name="statusLogGroup")
    def status_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Log Group for the Redshift Data API status checks.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "statusLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="submitFunction")
    def submit_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda Function for the Redshift Data submission.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "submitFunction"))

    @builtins.property
    @jsii.member(jsii_name="submitLogGroup")
    def submit_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Log Group for the Redshift Data API submission.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "submitLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="taggingManagedPolicy")
    def tagging_managed_policy(self) -> _aws_cdk_aws_iam_ceddda9d.IManagedPolicy:
        '''The managed IAM policy allowing IAM Role to retrieve tag information.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IManagedPolicy, jsii.get(self, "taggingManagedPolicy"))

    @builtins.property
    @jsii.member(jsii_name="cleanUpFunction")
    def clean_up_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        '''The Lambda function for the S3 data copy cleaning up lambda.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], jsii.get(self, "cleanUpFunction"))

    @builtins.property
    @jsii.member(jsii_name="cleanUpLogGroup")
    def clean_up_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The CloudWatch Log Group for the Redshift Data cleaning up lambda.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "cleanUpLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="cleanUpRole")
    def clean_up_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role for the the S3 data copy cleaning up lambda.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "cleanUpRole"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.RedshiftDataAccessTargetProps",
    jsii_struct_bases=[],
    name_mapping={
        "target_arn": "targetArn",
        "target_id": "targetId",
        "target_type": "targetType",
    },
)
class RedshiftDataAccessTargetProps:
    def __init__(
        self,
        *,
        target_arn: builtins.str,
        target_id: builtins.str,
        target_type: builtins.str,
    ) -> None:
        '''
        :param target_arn: 
        :param target_id: 
        :param target_type: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__861d9de737cf60e979f1fb120ea5724ba7b2873aeb4538ad5841df9f93570307)
            check_type(argname="argument target_arn", value=target_arn, expected_type=type_hints["target_arn"])
            check_type(argname="argument target_id", value=target_id, expected_type=type_hints["target_id"])
            check_type(argname="argument target_type", value=target_type, expected_type=type_hints["target_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "target_arn": target_arn,
            "target_id": target_id,
            "target_type": target_type,
        }

    @builtins.property
    def target_arn(self) -> builtins.str:
        result = self._values.get("target_arn")
        assert result is not None, "Required property 'target_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_id(self) -> builtins.str:
        result = self._values.get("target_id")
        assert result is not None, "Required property 'target_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_type(self) -> builtins.str:
        result = self._values.get("target_type")
        assert result is not None, "Required property 'target_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftDataAccessTargetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.RedshiftDataProps",
    jsii_struct_bases=[],
    name_mapping={
        "secret": "secret",
        "cluster_id": "clusterId",
        "create_interface_vpc_endpoint": "createInterfaceVpcEndpoint",
        "execution_timeout": "executionTimeout",
        "existing_interface_vpc_endpoint": "existingInterfaceVPCEndpoint",
        "removal_policy": "removalPolicy",
        "secret_key": "secretKey",
        "subnets": "subnets",
        "vpc": "vpc",
        "workgroup_id": "workgroupId",
    },
)
class RedshiftDataProps:
    def __init__(
        self,
        *,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        cluster_id: typing.Optional[builtins.str] = None,
        create_interface_vpc_endpoint: typing.Optional[builtins.bool] = None,
        execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        existing_interface_vpc_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        workgroup_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''The properties for the ``RedshiftData`` construct.

        :param secret: The Secrets Manager Secret containing the admin credentials for the Redshift cluster / namespace.
        :param cluster_id: The name of the Redshift provisioned to query. It must be configured if the ``workgroupId`` is not. Default: - The ``workgroupId`` is used
        :param create_interface_vpc_endpoint: If set to true, create the Redshift Data Interface VPC Endpoint in the configured VPC/Subnets. Default: - false
        :param execution_timeout: The timeout for the query execution. Default: - 5mins
        :param existing_interface_vpc_endpoint: If this parameter is provided, the data access execution security group would be granted inbound to the interface VPC endpoint's security group. This is assuming that the ``createInterfaceVpcEndpoint`` parameter is ``false``. Default: - No security group ingress rule would be created.
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param secret_key: The KMS Key used to encrypt the admin credentials for the Redshift cluster / namespace. Default: - no secret key is used
        :param subnets: The subnets where the Custom Resource Lambda Function would be created in. A Redshift Data API Interface VPC Endpoint is created in the subnets. Default: - No subnets are used. The Custom Resource runs in the Redshift service team subnets.
        :param vpc: The VPC where the Custom Resource Lambda Function would be created in. A Redshift Data API Interface VPC Endpoint is created in the VPC. Default: - No VPC is used. The Custom Resource runs in the Redshift service team VPC
        :param workgroup_id: The ``workgroupId`` for the Redshift Serverless Workgroup to query. It must be configured if the ``clusterId`` is not. Default: - The ``clusterId`` is used
        '''
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SelectedSubnets(**subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d480592ed79dd1af33b7179862f6641c88e07337cf7c2b6ead428ed68bc84cdd)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument create_interface_vpc_endpoint", value=create_interface_vpc_endpoint, expected_type=type_hints["create_interface_vpc_endpoint"])
            check_type(argname="argument execution_timeout", value=execution_timeout, expected_type=type_hints["execution_timeout"])
            check_type(argname="argument existing_interface_vpc_endpoint", value=existing_interface_vpc_endpoint, expected_type=type_hints["existing_interface_vpc_endpoint"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument secret_key", value=secret_key, expected_type=type_hints["secret_key"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument workgroup_id", value=workgroup_id, expected_type=type_hints["workgroup_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "secret": secret,
        }
        if cluster_id is not None:
            self._values["cluster_id"] = cluster_id
        if create_interface_vpc_endpoint is not None:
            self._values["create_interface_vpc_endpoint"] = create_interface_vpc_endpoint
        if execution_timeout is not None:
            self._values["execution_timeout"] = execution_timeout
        if existing_interface_vpc_endpoint is not None:
            self._values["existing_interface_vpc_endpoint"] = existing_interface_vpc_endpoint
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if secret_key is not None:
            self._values["secret_key"] = secret_key
        if subnets is not None:
            self._values["subnets"] = subnets
        if vpc is not None:
            self._values["vpc"] = vpc
        if workgroup_id is not None:
            self._values["workgroup_id"] = workgroup_id

    @builtins.property
    def secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''The Secrets Manager Secret containing the admin credentials for the Redshift cluster / namespace.'''
        result = self._values.get("secret")
        assert result is not None, "Required property 'secret' is missing"
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, result)

    @builtins.property
    def cluster_id(self) -> typing.Optional[builtins.str]:
        '''The name of the Redshift provisioned to query.

        It must be configured if the ``workgroupId`` is not.

        :default: - The ``workgroupId`` is used
        '''
        result = self._values.get("cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def create_interface_vpc_endpoint(self) -> typing.Optional[builtins.bool]:
        '''If set to true, create the Redshift Data Interface VPC Endpoint in the configured VPC/Subnets.

        :default: - false
        '''
        result = self._values.get("create_interface_vpc_endpoint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def execution_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The timeout for the query execution.

        :default: - 5mins
        '''
        result = self._values.get("execution_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def existing_interface_vpc_endpoint(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint]:
        '''If this parameter is provided, the data access execution security group would be granted inbound to the interface VPC endpoint's security group.

        This is assuming that the ``createInterfaceVpcEndpoint`` parameter is ``false``.

        :default: - No security group ingress rule would be created.
        '''
        result = self._values.get("existing_interface_vpc_endpoint")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise, the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def secret_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS Key used to encrypt the admin credentials for the Redshift cluster / namespace.

        :default: - no secret key is used
        '''
        result = self._values.get("secret_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets]:
        '''The subnets where the Custom Resource Lambda Function would be created in.

        A Redshift Data API Interface VPC Endpoint is created in the subnets.

        :default: - No subnets are used. The Custom Resource runs in the Redshift service team subnets.
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC where the Custom Resource Lambda Function would be created in.

        A Redshift Data API Interface VPC Endpoint is created in the VPC.

        :default: - No VPC is used. The Custom Resource runs in the Redshift service team VPC
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def workgroup_id(self) -> typing.Optional[builtins.str]:
        '''The ``workgroupId`` for the Redshift Serverless Workgroup to query.

        It must be configured if the ``clusterId`` is not.

        :default: - The ``clusterId`` is used
        '''
        result = self._values.get("workgroup_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftDataProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftDataSharing(
    BaseRedshiftDataAccess,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.RedshiftDataSharing",
):
    '''Creates an asynchronous custom resource to manage the data sharing lifecycle for both data producers and data consumers.

    This also covers both same account and cross account access.

    :exampleMetadata: fixture=vpc-secret

    Example::

        redshift_admin_secret = Secret.from_secret_partial_arn(self, "RedshiftAdminCredentials", "arn:aws:secretsmanager:us-east-1:XXXXXXXX:secret:YYYYYYYY")
        
        redshift_vpc = Vpc.from_lookup(self, "RedshiftVpc",
            vpc_id="XXXXXXXX"
        )
        
        data_access = dsf.consumption.RedshiftData(self, "RedshiftDataAccess",
            workgroup_id="XXXXXXXXXXXXXXX",
            secret=redshift_admin_secret,
            vpc=redshift_vpc,
            subnets=redshift_vpc.select_subnets(
                subnet_group_name="YYYYYYYY"
            ),
            create_interface_vpc_endpoint=True,
            execution_timeout=Duration.minutes(10)
        )
        
        data_share = dsf.consumption.RedshiftDataSharing(self, "RedshiftDataShare",
            redshift_data=data_access,
            workgroup_id="XXXXXXXXXXXXXXX",
            secret=redshift_admin_secret,
            vpc=redshift_vpc,
            subnets=redshift_vpc.select_subnets(
                subnet_group_name="YYYYYYYY"
            ),
            create_interface_vpc_endpoint=True,
            execution_timeout=Duration.minutes(10)
        )
        
        share = data_share.create_share("ProducerShare", "default", "example_share", "public", ["public.customers"])
        
        grant_to_consumer = data_share.grant("GrantToConsumer",
            data_share_name="example_share",
            database_name="default",
            auto_authorized=True,
            account_id="<CONSUMER_ACCOUNT_ID>",
            data_share_arn="<DATASHARE_ARN>"
        )
        
        data_share.create_database_from_share("ProducerShare",
            consumer_namespace_arn="",
            new_database_name="db_from_share",
            database_name="default",
            data_share_name="example_share",
            data_share_arn="<DATASHARE_ARN>",
            account_id="<PRODUCER_ACCOUNT_ID>"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        redshift_data: RedshiftData,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        cluster_id: typing.Optional[builtins.str] = None,
        create_interface_vpc_endpoint: typing.Optional[builtins.bool] = None,
        execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        existing_interface_vpc_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        workgroup_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param redshift_data: Instance of ``RedshiftData`` construct.
        :param secret: The Secrets Manager Secret containing the admin credentials for the Redshift cluster / namespace.
        :param cluster_id: The name of the Redshift provisioned to query. It must be configured if the ``workgroupId`` is not. Default: - The ``workgroupId`` is used
        :param create_interface_vpc_endpoint: If set to true, create the Redshift Data Interface VPC Endpoint in the configured VPC/Subnets. Default: - false
        :param execution_timeout: The timeout for the query execution. Default: - 5mins
        :param existing_interface_vpc_endpoint: If this parameter is provided, the data access execution security group would be granted inbound to the interface VPC endpoint's security group. This is assuming that the ``createInterfaceVpcEndpoint`` parameter is ``false``. Default: - No security group ingress rule would be created.
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param secret_key: The KMS Key used to encrypt the admin credentials for the Redshift cluster / namespace. Default: - no secret key is used
        :param subnets: The subnets where the Custom Resource Lambda Function would be created in. A Redshift Data API Interface VPC Endpoint is created in the subnets. Default: - No subnets are used. The Custom Resource runs in the Redshift service team subnets.
        :param vpc: The VPC where the Custom Resource Lambda Function would be created in. A Redshift Data API Interface VPC Endpoint is created in the VPC. Default: - No VPC is used. The Custom Resource runs in the Redshift service team VPC
        :param workgroup_id: The ``workgroupId`` for the Redshift Serverless Workgroup to query. It must be configured if the ``clusterId`` is not. Default: - The ``clusterId`` is used
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1a39f7fe2374e40e1f26a21341c7716f3c4f3b3e11bd11ab56403e4097056c3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RedshiftDataSharingProps(
            redshift_data=redshift_data,
            secret=secret,
            cluster_id=cluster_id,
            create_interface_vpc_endpoint=create_interface_vpc_endpoint,
            execution_timeout=execution_timeout,
            existing_interface_vpc_endpoint=existing_interface_vpc_endpoint,
            removal_policy=removal_policy,
            secret_key=secret_key,
            subnets=subnets,
            vpc=vpc,
            workgroup_id=workgroup_id,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createDatabaseFromShare")
    def create_database_from_share(
        self,
        id: builtins.str,
        *,
        new_database_name: builtins.str,
        consumer_namespace_arn: typing.Optional[builtins.str] = None,
        database_name: builtins.str,
        data_share_name: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        data_share_arn: typing.Optional[builtins.str] = None,
        namespace_id: typing.Optional[builtins.str] = None,
    ) -> "RedshiftDataSharingCreateDbFromShareProps":
        '''Consume datashare by creating a new database pointing to the share.

        If datashare is coming from a different account, setting ``autoAssociate`` to true
        automatically associates the datashare to the cluster before the new database is created.

        :param id: the CDK ID of the resource.
        :param new_database_name: For consumers, the data share would be located in this database that would be created.
        :param consumer_namespace_arn: The namespace of the consumer, necessary for cross-account data shares.
        :param database_name: The name of the Redshift database used in the data sharing.
        :param data_share_name: The name of the data share.
        :param account_id: For cross-account grants, this is the consumer account ID. For cross-account consumers, this is the producer account ID. Default: - No account ID is used.
        :param data_share_arn: The ARN of the datashare. This is required for any action that is cross account. Default: - No data share ARN is used.
        :param namespace_id: For single account grants, this is the consumer namespace ID. For cross-account grants, ``namespaceId`` is ignored. For consumers, this is the producer namespace ID. It is required for both single and cross account data sharing. Default: - No namespace ID is used.

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fc88db2a86b7ba500cafae04f1c330c70bd663b454f63ba85997d7f7058ec7f)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RedshiftDataSharingCreateDbProps(
            new_database_name=new_database_name,
            consumer_namespace_arn=consumer_namespace_arn,
            database_name=database_name,
            data_share_name=data_share_name,
            account_id=account_id,
            data_share_arn=data_share_arn,
            namespace_id=namespace_id,
        )

        return typing.cast("RedshiftDataSharingCreateDbFromShareProps", jsii.invoke(self, "createDatabaseFromShare", [id, props]))

    @jsii.member(jsii_name="createShare")
    def create_share(
        self,
        id: builtins.str,
        database_name: builtins.str,
        data_share_name: builtins.str,
        schema: builtins.str,
        tables: typing.Sequence[builtins.str],
    ) -> "RedshiftNewShareProps":
        '''Create a new datashare.

        :param id: the CDK ID of the resource.
        :param database_name: The name of the database to connect to.
        :param data_share_name: The name of the datashare.
        :param schema: The schema to add in the datashare.
        :param tables: The list of tables that would be included in the datashare. This must follow the format: ``<schema>.<tableName>``

        :return: ``RedshiftNewShareProps``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b31f4e36ef22e73a5897a8eb4beac7096331fea9862ce0b1cc8d1afd8aca77a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument data_share_name", value=data_share_name, expected_type=type_hints["data_share_name"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument tables", value=tables, expected_type=type_hints["tables"])
        return typing.cast("RedshiftNewShareProps", jsii.invoke(self, "createShare", [id, database_name, data_share_name, schema, tables]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        id: builtins.str,
        *,
        auto_authorized: typing.Optional[builtins.bool] = None,
        database_name: builtins.str,
        data_share_name: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        data_share_arn: typing.Optional[builtins.str] = None,
        namespace_id: typing.Optional[builtins.str] = None,
    ) -> "RedshiftDataSharingGrantedProps":
        '''Create a datashare grant to a namespace if it's in the same account, or to another account.

        :param id: the CDK ID of the resource.
        :param auto_authorized: If set to ``true``, cross-account grants would automatically be authorized. See https://docs.aws.amazon.com/redshift/latest/dg/consumer-account-admin.html Default: - cross-account grants should be authorized manually
        :param database_name: The name of the Redshift database used in the data sharing.
        :param data_share_name: The name of the data share.
        :param account_id: For cross-account grants, this is the consumer account ID. For cross-account consumers, this is the producer account ID. Default: - No account ID is used.
        :param data_share_arn: The ARN of the datashare. This is required for any action that is cross account. Default: - No data share ARN is used.
        :param namespace_id: For single account grants, this is the consumer namespace ID. For cross-account grants, ``namespaceId`` is ignored. For consumers, this is the producer namespace ID. It is required for both single and cross account data sharing. Default: - No namespace ID is used.

        :return: ``RedshiftDataSharingGrantedProps``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9201574db2958d2cf5ed51c6378268cad17e0a20e9959178d578de9292e7c1fc)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RedshiftDataSharingGrantProps(
            auto_authorized=auto_authorized,
            database_name=database_name,
            data_share_name=data_share_name,
            account_id=account_id,
            data_share_arn=data_share_arn,
            namespace_id=namespace_id,
        )

        return typing.cast("RedshiftDataSharingGrantedProps", jsii.invoke(self, "grant", [id, props]))

    @builtins.property
    @jsii.member(jsii_name="dataAccessTargetProps")
    def data_access_target_props(self) -> RedshiftDataAccessTargetProps:
        '''Contains normalized details of the target Redshift cluster/workgroup for data access.'''
        return typing.cast(RedshiftDataAccessTargetProps, jsii.get(self, "dataAccessTargetProps"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM Role for the Redshift Data API execution.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "executionRole"))

    @builtins.property
    @jsii.member(jsii_name="statusFunction")
    def status_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda Function for the Redshift Data Sharing status checks.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "statusFunction"))

    @builtins.property
    @jsii.member(jsii_name="statusLogGroup")
    def status_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Log Group for the Redshift Data Sharing status checks.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "statusLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="submitFunction")
    def submit_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda Function for the Redshift Data Sharing submission.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "submitFunction"))

    @builtins.property
    @jsii.member(jsii_name="submitLogGroup")
    def submit_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Log Group for the Redshift Data Sharing submission.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "submitLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="cleanUpFunction")
    def clean_up_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        '''The Lambda function for the cleaning up lambda.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], jsii.get(self, "cleanUpFunction"))

    @builtins.property
    @jsii.member(jsii_name="cleanUpLogGroup")
    def clean_up_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The CloudWatch Log Group for the Redshift Data Sharing cleaning up lambda.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "cleanUpLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="cleanUpRole")
    def clean_up_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role for the the cleaning up lambda.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "cleanUpRole"))


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.RedshiftDataSharingCreateDbFromShareProps",
    jsii_struct_bases=[],
    name_mapping={
        "resource": "resource",
        "associate_data_share_resource": "associateDataShareResource",
    },
)
class RedshiftDataSharingCreateDbFromShareProps:
    def __init__(
        self,
        *,
        resource: _aws_cdk_ceddda9d.CustomResource,
        associate_data_share_resource: typing.Optional[_aws_cdk_custom_resources_ceddda9d.AwsCustomResource] = None,
    ) -> None:
        '''Return interface after creating a new database from data share.

        :param resource: The resource associated with the create database command.
        :param associate_data_share_resource: If auto-association is turned on, this is the resource associated with the action.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ceb8aa411cca34c81cde3126681ca9a5e6865f9187185acd4868c42cc50f350d)
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
            check_type(argname="argument associate_data_share_resource", value=associate_data_share_resource, expected_type=type_hints["associate_data_share_resource"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "resource": resource,
        }
        if associate_data_share_resource is not None:
            self._values["associate_data_share_resource"] = associate_data_share_resource

    @builtins.property
    def resource(self) -> _aws_cdk_ceddda9d.CustomResource:
        '''The resource associated with the create database command.'''
        result = self._values.get("resource")
        assert result is not None, "Required property 'resource' is missing"
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, result)

    @builtins.property
    def associate_data_share_resource(
        self,
    ) -> typing.Optional[_aws_cdk_custom_resources_ceddda9d.AwsCustomResource]:
        '''If auto-association is turned on, this is the resource associated with the action.'''
        result = self._values.get("associate_data_share_resource")
        return typing.cast(typing.Optional[_aws_cdk_custom_resources_ceddda9d.AwsCustomResource], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftDataSharingCreateDbFromShareProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.RedshiftDataSharingCreateDbProps",
    jsii_struct_bases=[BaseRedshiftDataSharingAccessProps],
    name_mapping={
        "database_name": "databaseName",
        "data_share_name": "dataShareName",
        "account_id": "accountId",
        "data_share_arn": "dataShareArn",
        "namespace_id": "namespaceId",
        "new_database_name": "newDatabaseName",
        "consumer_namespace_arn": "consumerNamespaceArn",
    },
)
class RedshiftDataSharingCreateDbProps(BaseRedshiftDataSharingAccessProps):
    def __init__(
        self,
        *,
        database_name: builtins.str,
        data_share_name: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        data_share_arn: typing.Optional[builtins.str] = None,
        namespace_id: typing.Optional[builtins.str] = None,
        new_database_name: builtins.str,
        consumer_namespace_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for data sharing consumer.

        :param database_name: The name of the Redshift database used in the data sharing.
        :param data_share_name: The name of the data share.
        :param account_id: For cross-account grants, this is the consumer account ID. For cross-account consumers, this is the producer account ID. Default: - No account ID is used.
        :param data_share_arn: The ARN of the datashare. This is required for any action that is cross account. Default: - No data share ARN is used.
        :param namespace_id: For single account grants, this is the consumer namespace ID. For cross-account grants, ``namespaceId`` is ignored. For consumers, this is the producer namespace ID. It is required for both single and cross account data sharing. Default: - No namespace ID is used.
        :param new_database_name: For consumers, the data share would be located in this database that would be created.
        :param consumer_namespace_arn: The namespace of the consumer, necessary for cross-account data shares.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cadfd7328c9e91872b4f5f98d320822f101f2ca3d1c390fd8b98132df55a6cf)
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument data_share_name", value=data_share_name, expected_type=type_hints["data_share_name"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument data_share_arn", value=data_share_arn, expected_type=type_hints["data_share_arn"])
            check_type(argname="argument namespace_id", value=namespace_id, expected_type=type_hints["namespace_id"])
            check_type(argname="argument new_database_name", value=new_database_name, expected_type=type_hints["new_database_name"])
            check_type(argname="argument consumer_namespace_arn", value=consumer_namespace_arn, expected_type=type_hints["consumer_namespace_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_name": database_name,
            "data_share_name": data_share_name,
            "new_database_name": new_database_name,
        }
        if account_id is not None:
            self._values["account_id"] = account_id
        if data_share_arn is not None:
            self._values["data_share_arn"] = data_share_arn
        if namespace_id is not None:
            self._values["namespace_id"] = namespace_id
        if consumer_namespace_arn is not None:
            self._values["consumer_namespace_arn"] = consumer_namespace_arn

    @builtins.property
    def database_name(self) -> builtins.str:
        '''The name of the Redshift database used in the data sharing.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data_share_name(self) -> builtins.str:
        '''The name of the data share.'''
        result = self._values.get("data_share_name")
        assert result is not None, "Required property 'data_share_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''For cross-account grants, this is the consumer account ID.

        For cross-account consumers, this is the producer account ID.

        :default: - No account ID is used.
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_share_arn(self) -> typing.Optional[builtins.str]:
        '''The ARN of the datashare.

        This is required for any action that is cross account.

        :default: - No data share ARN is used.
        '''
        result = self._values.get("data_share_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace_id(self) -> typing.Optional[builtins.str]:
        '''For single account grants, this is the consumer namespace ID. For cross-account grants, ``namespaceId`` is ignored.

        For consumers, this is the producer namespace ID. It is required for both single and cross account data sharing.

        :default: - No namespace ID is used.
        '''
        result = self._values.get("namespace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def new_database_name(self) -> builtins.str:
        '''For consumers, the data share would be located in this database that would be created.'''
        result = self._values.get("new_database_name")
        assert result is not None, "Required property 'new_database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def consumer_namespace_arn(self) -> typing.Optional[builtins.str]:
        '''The namespace of the consumer, necessary for cross-account data shares.'''
        result = self._values.get("consumer_namespace_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftDataSharingCreateDbProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.RedshiftDataSharingGrantProps",
    jsii_struct_bases=[BaseRedshiftDataSharingAccessProps],
    name_mapping={
        "database_name": "databaseName",
        "data_share_name": "dataShareName",
        "account_id": "accountId",
        "data_share_arn": "dataShareArn",
        "namespace_id": "namespaceId",
        "auto_authorized": "autoAuthorized",
    },
)
class RedshiftDataSharingGrantProps(BaseRedshiftDataSharingAccessProps):
    def __init__(
        self,
        *,
        database_name: builtins.str,
        data_share_name: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        data_share_arn: typing.Optional[builtins.str] = None,
        namespace_id: typing.Optional[builtins.str] = None,
        auto_authorized: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Properties for data sharing grants.

        :param database_name: The name of the Redshift database used in the data sharing.
        :param data_share_name: The name of the data share.
        :param account_id: For cross-account grants, this is the consumer account ID. For cross-account consumers, this is the producer account ID. Default: - No account ID is used.
        :param data_share_arn: The ARN of the datashare. This is required for any action that is cross account. Default: - No data share ARN is used.
        :param namespace_id: For single account grants, this is the consumer namespace ID. For cross-account grants, ``namespaceId`` is ignored. For consumers, this is the producer namespace ID. It is required for both single and cross account data sharing. Default: - No namespace ID is used.
        :param auto_authorized: If set to ``true``, cross-account grants would automatically be authorized. See https://docs.aws.amazon.com/redshift/latest/dg/consumer-account-admin.html Default: - cross-account grants should be authorized manually
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08e47e7834f522ee1825b8a15ab18c8d4a9e926997d5a3a7949617851df7fe21)
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument data_share_name", value=data_share_name, expected_type=type_hints["data_share_name"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument data_share_arn", value=data_share_arn, expected_type=type_hints["data_share_arn"])
            check_type(argname="argument namespace_id", value=namespace_id, expected_type=type_hints["namespace_id"])
            check_type(argname="argument auto_authorized", value=auto_authorized, expected_type=type_hints["auto_authorized"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_name": database_name,
            "data_share_name": data_share_name,
        }
        if account_id is not None:
            self._values["account_id"] = account_id
        if data_share_arn is not None:
            self._values["data_share_arn"] = data_share_arn
        if namespace_id is not None:
            self._values["namespace_id"] = namespace_id
        if auto_authorized is not None:
            self._values["auto_authorized"] = auto_authorized

    @builtins.property
    def database_name(self) -> builtins.str:
        '''The name of the Redshift database used in the data sharing.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data_share_name(self) -> builtins.str:
        '''The name of the data share.'''
        result = self._values.get("data_share_name")
        assert result is not None, "Required property 'data_share_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''For cross-account grants, this is the consumer account ID.

        For cross-account consumers, this is the producer account ID.

        :default: - No account ID is used.
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_share_arn(self) -> typing.Optional[builtins.str]:
        '''The ARN of the datashare.

        This is required for any action that is cross account.

        :default: - No data share ARN is used.
        '''
        result = self._values.get("data_share_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace_id(self) -> typing.Optional[builtins.str]:
        '''For single account grants, this is the consumer namespace ID. For cross-account grants, ``namespaceId`` is ignored.

        For consumers, this is the producer namespace ID. It is required for both single and cross account data sharing.

        :default: - No namespace ID is used.
        '''
        result = self._values.get("namespace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_authorized(self) -> typing.Optional[builtins.bool]:
        '''If set to ``true``, cross-account grants would automatically be authorized.

        See https://docs.aws.amazon.com/redshift/latest/dg/consumer-account-admin.html

        :default: - cross-account grants should be authorized manually
        '''
        result = self._values.get("auto_authorized")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftDataSharingGrantProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.RedshiftDataSharingGrantedProps",
    jsii_struct_bases=[],
    name_mapping={
        "resource": "resource",
        "share_authorization_resource": "shareAuthorizationResource",
    },
)
class RedshiftDataSharingGrantedProps:
    def __init__(
        self,
        *,
        resource: _aws_cdk_ceddda9d.CustomResource,
        share_authorization_resource: typing.Optional[_aws_cdk_custom_resources_ceddda9d.AwsCustomResource] = None,
    ) -> None:
        '''Return interface after granting access to consumer.

        :param resource: The resource associated with the grant command.
        :param share_authorization_resource: If auto-authorization is turned on, this is the resource associated with the action.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e38b2bf6fd9554265c2a2a36ca3368c9ac87852c2ab34cb1ee51d8486214527)
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
            check_type(argname="argument share_authorization_resource", value=share_authorization_resource, expected_type=type_hints["share_authorization_resource"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "resource": resource,
        }
        if share_authorization_resource is not None:
            self._values["share_authorization_resource"] = share_authorization_resource

    @builtins.property
    def resource(self) -> _aws_cdk_ceddda9d.CustomResource:
        '''The resource associated with the grant command.'''
        result = self._values.get("resource")
        assert result is not None, "Required property 'resource' is missing"
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, result)

    @builtins.property
    def share_authorization_resource(
        self,
    ) -> typing.Optional[_aws_cdk_custom_resources_ceddda9d.AwsCustomResource]:
        '''If auto-authorization is turned on, this is the resource associated with the action.'''
        result = self._values.get("share_authorization_resource")
        return typing.cast(typing.Optional[_aws_cdk_custom_resources_ceddda9d.AwsCustomResource], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftDataSharingGrantedProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.RedshiftDataSharingProps",
    jsii_struct_bases=[RedshiftDataProps],
    name_mapping={
        "secret": "secret",
        "cluster_id": "clusterId",
        "create_interface_vpc_endpoint": "createInterfaceVpcEndpoint",
        "execution_timeout": "executionTimeout",
        "existing_interface_vpc_endpoint": "existingInterfaceVPCEndpoint",
        "removal_policy": "removalPolicy",
        "secret_key": "secretKey",
        "subnets": "subnets",
        "vpc": "vpc",
        "workgroup_id": "workgroupId",
        "redshift_data": "redshiftData",
    },
)
class RedshiftDataSharingProps(RedshiftDataProps):
    def __init__(
        self,
        *,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        cluster_id: typing.Optional[builtins.str] = None,
        create_interface_vpc_endpoint: typing.Optional[builtins.bool] = None,
        execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        existing_interface_vpc_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        workgroup_id: typing.Optional[builtins.str] = None,
        redshift_data: RedshiftData,
    ) -> None:
        '''Properties for the ``RedshiftDataSharing`` construct.

        :param secret: The Secrets Manager Secret containing the admin credentials for the Redshift cluster / namespace.
        :param cluster_id: The name of the Redshift provisioned to query. It must be configured if the ``workgroupId`` is not. Default: - The ``workgroupId`` is used
        :param create_interface_vpc_endpoint: If set to true, create the Redshift Data Interface VPC Endpoint in the configured VPC/Subnets. Default: - false
        :param execution_timeout: The timeout for the query execution. Default: - 5mins
        :param existing_interface_vpc_endpoint: If this parameter is provided, the data access execution security group would be granted inbound to the interface VPC endpoint's security group. This is assuming that the ``createInterfaceVpcEndpoint`` parameter is ``false``. Default: - No security group ingress rule would be created.
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param secret_key: The KMS Key used to encrypt the admin credentials for the Redshift cluster / namespace. Default: - no secret key is used
        :param subnets: The subnets where the Custom Resource Lambda Function would be created in. A Redshift Data API Interface VPC Endpoint is created in the subnets. Default: - No subnets are used. The Custom Resource runs in the Redshift service team subnets.
        :param vpc: The VPC where the Custom Resource Lambda Function would be created in. A Redshift Data API Interface VPC Endpoint is created in the VPC. Default: - No VPC is used. The Custom Resource runs in the Redshift service team VPC
        :param workgroup_id: The ``workgroupId`` for the Redshift Serverless Workgroup to query. It must be configured if the ``clusterId`` is not. Default: - The ``clusterId`` is used
        :param redshift_data: Instance of ``RedshiftData`` construct.
        '''
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SelectedSubnets(**subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea9e32f91290772227d25742eab949586a52606a31e5d50c08552be8f5094492)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument create_interface_vpc_endpoint", value=create_interface_vpc_endpoint, expected_type=type_hints["create_interface_vpc_endpoint"])
            check_type(argname="argument execution_timeout", value=execution_timeout, expected_type=type_hints["execution_timeout"])
            check_type(argname="argument existing_interface_vpc_endpoint", value=existing_interface_vpc_endpoint, expected_type=type_hints["existing_interface_vpc_endpoint"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument secret_key", value=secret_key, expected_type=type_hints["secret_key"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument workgroup_id", value=workgroup_id, expected_type=type_hints["workgroup_id"])
            check_type(argname="argument redshift_data", value=redshift_data, expected_type=type_hints["redshift_data"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "secret": secret,
            "redshift_data": redshift_data,
        }
        if cluster_id is not None:
            self._values["cluster_id"] = cluster_id
        if create_interface_vpc_endpoint is not None:
            self._values["create_interface_vpc_endpoint"] = create_interface_vpc_endpoint
        if execution_timeout is not None:
            self._values["execution_timeout"] = execution_timeout
        if existing_interface_vpc_endpoint is not None:
            self._values["existing_interface_vpc_endpoint"] = existing_interface_vpc_endpoint
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if secret_key is not None:
            self._values["secret_key"] = secret_key
        if subnets is not None:
            self._values["subnets"] = subnets
        if vpc is not None:
            self._values["vpc"] = vpc
        if workgroup_id is not None:
            self._values["workgroup_id"] = workgroup_id

    @builtins.property
    def secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''The Secrets Manager Secret containing the admin credentials for the Redshift cluster / namespace.'''
        result = self._values.get("secret")
        assert result is not None, "Required property 'secret' is missing"
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, result)

    @builtins.property
    def cluster_id(self) -> typing.Optional[builtins.str]:
        '''The name of the Redshift provisioned to query.

        It must be configured if the ``workgroupId`` is not.

        :default: - The ``workgroupId`` is used
        '''
        result = self._values.get("cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def create_interface_vpc_endpoint(self) -> typing.Optional[builtins.bool]:
        '''If set to true, create the Redshift Data Interface VPC Endpoint in the configured VPC/Subnets.

        :default: - false
        '''
        result = self._values.get("create_interface_vpc_endpoint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def execution_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The timeout for the query execution.

        :default: - 5mins
        '''
        result = self._values.get("execution_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def existing_interface_vpc_endpoint(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint]:
        '''If this parameter is provided, the data access execution security group would be granted inbound to the interface VPC endpoint's security group.

        This is assuming that the ``createInterfaceVpcEndpoint`` parameter is ``false``.

        :default: - No security group ingress rule would be created.
        '''
        result = self._values.get("existing_interface_vpc_endpoint")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise, the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def secret_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS Key used to encrypt the admin credentials for the Redshift cluster / namespace.

        :default: - no secret key is used
        '''
        result = self._values.get("secret_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets]:
        '''The subnets where the Custom Resource Lambda Function would be created in.

        A Redshift Data API Interface VPC Endpoint is created in the subnets.

        :default: - No subnets are used. The Custom Resource runs in the Redshift service team subnets.
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC where the Custom Resource Lambda Function would be created in.

        A Redshift Data API Interface VPC Endpoint is created in the VPC.

        :default: - No VPC is used. The Custom Resource runs in the Redshift service team VPC
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def workgroup_id(self) -> typing.Optional[builtins.str]:
        '''The ``workgroupId`` for the Redshift Serverless Workgroup to query.

        It must be configured if the ``clusterId`` is not.

        :default: - The ``clusterId`` is used
        '''
        result = self._values.get("workgroup_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redshift_data(self) -> RedshiftData:
        '''Instance of ``RedshiftData`` construct.'''
        result = self._values.get("redshift_data")
        assert result is not None, "Required property 'redshift_data' is missing"
        return typing.cast(RedshiftData, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftDataSharingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.RedshiftNewShareProps",
    jsii_struct_bases=[],
    name_mapping={
        "database_name": "databaseName",
        "data_share_arn": "dataShareArn",
        "data_share_name": "dataShareName",
        "new_share_custom_resource": "newShareCustomResource",
        "producer_arn": "producerArn",
        "producer_namespace": "producerNamespace",
    },
)
class RedshiftNewShareProps:
    def __init__(
        self,
        *,
        database_name: builtins.str,
        data_share_arn: builtins.str,
        data_share_name: builtins.str,
        new_share_custom_resource: _aws_cdk_ceddda9d.CustomResource,
        producer_arn: builtins.str,
        producer_namespace: builtins.str,
    ) -> None:
        '''Redshift new data share details.

        :param database_name: The database name where the share belongs to.
        :param data_share_arn: The ARN of the data share.
        :param data_share_name: The name of the data share.
        :param new_share_custom_resource: The custom resource related to the management of the data share.
        :param producer_arn: The ARN of the producer.
        :param producer_namespace: The namespace ID of the producer.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__100f15df37a3044d0c5511b2ce12a309acffd87db4e2a40893f10c064c35d64e)
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument data_share_arn", value=data_share_arn, expected_type=type_hints["data_share_arn"])
            check_type(argname="argument data_share_name", value=data_share_name, expected_type=type_hints["data_share_name"])
            check_type(argname="argument new_share_custom_resource", value=new_share_custom_resource, expected_type=type_hints["new_share_custom_resource"])
            check_type(argname="argument producer_arn", value=producer_arn, expected_type=type_hints["producer_arn"])
            check_type(argname="argument producer_namespace", value=producer_namespace, expected_type=type_hints["producer_namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_name": database_name,
            "data_share_arn": data_share_arn,
            "data_share_name": data_share_name,
            "new_share_custom_resource": new_share_custom_resource,
            "producer_arn": producer_arn,
            "producer_namespace": producer_namespace,
        }

    @builtins.property
    def database_name(self) -> builtins.str:
        '''The database name where the share belongs to.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data_share_arn(self) -> builtins.str:
        '''The ARN of the data share.'''
        result = self._values.get("data_share_arn")
        assert result is not None, "Required property 'data_share_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data_share_name(self) -> builtins.str:
        '''The name of the data share.'''
        result = self._values.get("data_share_name")
        assert result is not None, "Required property 'data_share_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def new_share_custom_resource(self) -> _aws_cdk_ceddda9d.CustomResource:
        '''The custom resource related to the management of the data share.'''
        result = self._values.get("new_share_custom_resource")
        assert result is not None, "Required property 'new_share_custom_resource' is missing"
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, result)

    @builtins.property
    def producer_arn(self) -> builtins.str:
        '''The ARN of the producer.'''
        result = self._values.get("producer_arn")
        assert result is not None, "Required property 'producer_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def producer_namespace(self) -> builtins.str:
        '''The namespace ID of the producer.'''
        result = self._values.get("producer_namespace")
        assert result is not None, "Required property 'producer_namespace' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftNewShareProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftServerlessNamespace(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.RedshiftServerlessNamespace",
):
    '''Create a Redshift Serverless Namespace with the admin credentials stored in Secrets Manager.

    Example::

        namespace = dsf.consumption.RedshiftServerlessNamespace(self, "DefaultServerlessNamespace",
            db_name="defaultdb",
            name="default"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        db_name: builtins.str,
        name: builtins.str,
        admin_secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        admin_username: typing.Optional[builtins.str] = None,
        data_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        default_iam_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        final_snapshot_name: typing.Optional[builtins.str] = None,
        final_snapshot_retention_period: typing.Optional[jsii.Number] = None,
        iam_roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
        log_exports: typing.Optional[typing.Sequence["RedshiftServerlessNamespaceLogExport"]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        service_linked_role_factory: typing.Optional[_CreateServiceLinkedRole_fba94500] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param db_name: The name of the primary database that would be created in the Redshift Serverless Namespace.
        :param name: The name of the Redshift Serverless Namespace.
        :param admin_secret_key: The KMS Key used by the managed Secrets Manager Secret storing admin credentials. Default: - A new KMS Key is created
        :param admin_username: The admin username to be used. Default: - The default username is "admin"
        :param data_key: The KMS Key used to encrypt the data. Default: - A new KMS Key is created
        :param default_iam_role: Default IAM Role associated to the Redshift Serverless Namespace. Default: - No default IAM Role is associated with the Redshift Serverless Namespace
        :param final_snapshot_name: If provided, final snapshot would be taken with the name provided. Default: No final snapshot would be taken
        :param final_snapshot_retention_period: The number of days the final snapshot would be retained. Must be between 1-3653 days. Default: Indefinite final snapshot retention
        :param iam_roles: List of IAM Roles attached to the Redshift Serverless Namespace. This list of Roles must also contain the ``defaultIamRole``. Default: - No IAM roles are associated with the Redshift Serverless Namespace
        :param log_exports: The type of logs to be exported. Default: - No logs are exported
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param service_linked_role_factory: The Factory for creating Redshift service linked role. Default: - A factory is created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9507a166b2460e33a5a01511fed95cd5cead50cc1f27c934665aee7800656cee)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RedshiftServerlessNamespaceProps(
            db_name=db_name,
            name=name,
            admin_secret_key=admin_secret_key,
            admin_username=admin_username,
            data_key=data_key,
            default_iam_role=default_iam_role,
            final_snapshot_name=final_snapshot_name,
            final_snapshot_retention_period=final_snapshot_retention_period,
            iam_roles=iam_roles,
            log_exports=log_exports,
            removal_policy=removal_policy,
            service_linked_role_factory=service_linked_role_factory,
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
    @jsii.member(jsii_name="adminSecret")
    def admin_secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''The created Secrets Manager secret containing the admin credentials.'''
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, jsii.get(self, "adminSecret"))

    @builtins.property
    @jsii.member(jsii_name="adminSecretKey")
    def admin_secret_key(self) -> _aws_cdk_aws_kms_ceddda9d.IKey:
        '''The KMS Key used to encrypt the admin credentials secret.'''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.IKey, jsii.get(self, "adminSecretKey"))

    @builtins.property
    @jsii.member(jsii_name="createFunction")
    def create_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda Function for the Redshift Serverless creation.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "createFunction"))

    @builtins.property
    @jsii.member(jsii_name="createLogGroup")
    def create_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Logs Log Group for the Redshift Serverless creation.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "createLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="createRole")
    def create_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM Role for the Redshift Serverless creation.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "createRole"))

    @builtins.property
    @jsii.member(jsii_name="customResource")
    def custom_resource(self) -> _aws_cdk_ceddda9d.CustomResource:
        '''The custom resource that creates the Namespace.'''
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.get(self, "customResource"))

    @builtins.property
    @jsii.member(jsii_name="dataKey")
    def data_key(self) -> _aws_cdk_aws_kms_ceddda9d.Key:
        '''KMS key used by the namespace to encrypt the data.'''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.Key, jsii.get(self, "dataKey"))

    @builtins.property
    @jsii.member(jsii_name="dbName")
    def db_name(self) -> builtins.str:
        '''The name of the database.'''
        return typing.cast(builtins.str, jsii.get(self, "dbName"))

    @builtins.property
    @jsii.member(jsii_name="namespaceArn")
    def namespace_arn(self) -> builtins.str:
        '''The ARN of the created namespace.'''
        return typing.cast(builtins.str, jsii.get(self, "namespaceArn"))

    @builtins.property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        '''The ID of the created namespace.'''
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @builtins.property
    @jsii.member(jsii_name="namespaceName")
    def namespace_name(self) -> builtins.str:
        '''The name of the created namespace.'''
        return typing.cast(builtins.str, jsii.get(self, "namespaceName"))

    @builtins.property
    @jsii.member(jsii_name="roles")
    def roles(self) -> typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The roles attached to the namespace in the form of ``{RoleArn: IRole}``.

        These roles are used to access other AWS services for ingestion, federated query, and data catalog access.

        :see: https://docs.aws.amazon.com/redshift/latest/mgmt/redshift-iam-authentication-access-control.html
        '''
        return typing.cast(typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "roles"))

    @builtins.property
    @jsii.member(jsii_name="statusFunction")
    def status_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda Function for the creation status check.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "statusFunction"))

    @builtins.property
    @jsii.member(jsii_name="statusLogGroup")
    def status_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Logs Log Group for the creation status check.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "statusLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="statusRole")
    def status_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM Role for the creation status check.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "statusRole"))


@jsii.enum(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.RedshiftServerlessNamespaceLogExport"
)
class RedshiftServerlessNamespaceLogExport(enum.Enum):
    '''Namespace log export types.'''

    USER_LOG = "USER_LOG"
    CONNECTION_LOG = "CONNECTION_LOG"
    USER_ACTIVITY_LOG = "USER_ACTIVITY_LOG"


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.RedshiftServerlessNamespaceProps",
    jsii_struct_bases=[],
    name_mapping={
        "db_name": "dbName",
        "name": "name",
        "admin_secret_key": "adminSecretKey",
        "admin_username": "adminUsername",
        "data_key": "dataKey",
        "default_iam_role": "defaultIAMRole",
        "final_snapshot_name": "finalSnapshotName",
        "final_snapshot_retention_period": "finalSnapshotRetentionPeriod",
        "iam_roles": "iamRoles",
        "log_exports": "logExports",
        "removal_policy": "removalPolicy",
        "service_linked_role_factory": "serviceLinkedRoleFactory",
    },
)
class RedshiftServerlessNamespaceProps:
    def __init__(
        self,
        *,
        db_name: builtins.str,
        name: builtins.str,
        admin_secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        admin_username: typing.Optional[builtins.str] = None,
        data_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        default_iam_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        final_snapshot_name: typing.Optional[builtins.str] = None,
        final_snapshot_retention_period: typing.Optional[jsii.Number] = None,
        iam_roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
        log_exports: typing.Optional[typing.Sequence[RedshiftServerlessNamespaceLogExport]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        service_linked_role_factory: typing.Optional[_CreateServiceLinkedRole_fba94500] = None,
    ) -> None:
        '''RedshiftServerlessNamespace properties.

        :param db_name: The name of the primary database that would be created in the Redshift Serverless Namespace.
        :param name: The name of the Redshift Serverless Namespace.
        :param admin_secret_key: The KMS Key used by the managed Secrets Manager Secret storing admin credentials. Default: - A new KMS Key is created
        :param admin_username: The admin username to be used. Default: - The default username is "admin"
        :param data_key: The KMS Key used to encrypt the data. Default: - A new KMS Key is created
        :param default_iam_role: Default IAM Role associated to the Redshift Serverless Namespace. Default: - No default IAM Role is associated with the Redshift Serverless Namespace
        :param final_snapshot_name: If provided, final snapshot would be taken with the name provided. Default: No final snapshot would be taken
        :param final_snapshot_retention_period: The number of days the final snapshot would be retained. Must be between 1-3653 days. Default: Indefinite final snapshot retention
        :param iam_roles: List of IAM Roles attached to the Redshift Serverless Namespace. This list of Roles must also contain the ``defaultIamRole``. Default: - No IAM roles are associated with the Redshift Serverless Namespace
        :param log_exports: The type of logs to be exported. Default: - No logs are exported
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param service_linked_role_factory: The Factory for creating Redshift service linked role. Default: - A factory is created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8549fe13f562662bc17af1b381de6c8045964b12fea2e988c063b8045eb0bdb)
            check_type(argname="argument db_name", value=db_name, expected_type=type_hints["db_name"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument admin_secret_key", value=admin_secret_key, expected_type=type_hints["admin_secret_key"])
            check_type(argname="argument admin_username", value=admin_username, expected_type=type_hints["admin_username"])
            check_type(argname="argument data_key", value=data_key, expected_type=type_hints["data_key"])
            check_type(argname="argument default_iam_role", value=default_iam_role, expected_type=type_hints["default_iam_role"])
            check_type(argname="argument final_snapshot_name", value=final_snapshot_name, expected_type=type_hints["final_snapshot_name"])
            check_type(argname="argument final_snapshot_retention_period", value=final_snapshot_retention_period, expected_type=type_hints["final_snapshot_retention_period"])
            check_type(argname="argument iam_roles", value=iam_roles, expected_type=type_hints["iam_roles"])
            check_type(argname="argument log_exports", value=log_exports, expected_type=type_hints["log_exports"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument service_linked_role_factory", value=service_linked_role_factory, expected_type=type_hints["service_linked_role_factory"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "db_name": db_name,
            "name": name,
        }
        if admin_secret_key is not None:
            self._values["admin_secret_key"] = admin_secret_key
        if admin_username is not None:
            self._values["admin_username"] = admin_username
        if data_key is not None:
            self._values["data_key"] = data_key
        if default_iam_role is not None:
            self._values["default_iam_role"] = default_iam_role
        if final_snapshot_name is not None:
            self._values["final_snapshot_name"] = final_snapshot_name
        if final_snapshot_retention_period is not None:
            self._values["final_snapshot_retention_period"] = final_snapshot_retention_period
        if iam_roles is not None:
            self._values["iam_roles"] = iam_roles
        if log_exports is not None:
            self._values["log_exports"] = log_exports
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if service_linked_role_factory is not None:
            self._values["service_linked_role_factory"] = service_linked_role_factory

    @builtins.property
    def db_name(self) -> builtins.str:
        '''The name of the primary database that would be created in the Redshift Serverless Namespace.'''
        result = self._values.get("db_name")
        assert result is not None, "Required property 'db_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Redshift Serverless Namespace.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def admin_secret_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''The KMS Key used by the managed Secrets Manager Secret storing admin credentials.

        :default: - A new KMS Key is created
        '''
        result = self._values.get("admin_secret_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def admin_username(self) -> typing.Optional[builtins.str]:
        '''The admin username to be used.

        :default: - The default username is "admin"
        '''
        result = self._values.get("admin_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''The KMS Key used to encrypt the data.

        :default: - A new KMS Key is created
        '''
        result = self._values.get("data_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def default_iam_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Default IAM Role associated to the Redshift Serverless Namespace.

        :default: - No default IAM Role is associated with the Redshift Serverless Namespace
        '''
        result = self._values.get("default_iam_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def final_snapshot_name(self) -> typing.Optional[builtins.str]:
        '''If provided, final snapshot would be taken with the name provided.

        :default: No final snapshot would be taken
        '''
        result = self._values.get("final_snapshot_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def final_snapshot_retention_period(self) -> typing.Optional[jsii.Number]:
        '''The number of days the final snapshot would be retained.

        Must be between 1-3653 days.

        :default: Indefinite final snapshot retention
        '''
        result = self._values.get("final_snapshot_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def iam_roles(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IRole]]:
        '''List of IAM Roles attached to the Redshift Serverless Namespace.

        This list of Roles must also contain the ``defaultIamRole``.

        :default: - No IAM roles are associated with the Redshift Serverless Namespace
        '''
        result = self._values.get("iam_roles")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IRole]], result)

    @builtins.property
    def log_exports(
        self,
    ) -> typing.Optional[typing.List[RedshiftServerlessNamespaceLogExport]]:
        '''The type of logs to be exported.

        :default: - No logs are exported
        '''
        result = self._values.get("log_exports")
        return typing.cast(typing.Optional[typing.List[RedshiftServerlessNamespaceLogExport]], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise, the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def service_linked_role_factory(
        self,
    ) -> typing.Optional[_CreateServiceLinkedRole_fba94500]:
        '''The Factory for creating Redshift service linked role.

        :default: - A factory is created
        '''
        result = self._values.get("service_linked_role_factory")
        return typing.cast(typing.Optional[_CreateServiceLinkedRole_fba94500], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftServerlessNamespaceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_aws_ec2_ceddda9d.IConnectable)
class RedshiftServerlessWorkgroup(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.RedshiftServerlessWorkgroup",
):
    '''Create a Redshift Serverless Workgroup.

    A default namespace would be created if none is provided.

    Example::

        workgroup = dsf.consumption.RedshiftServerlessWorkgroup(self, "RedshiftWorkgroup",
            name="example-workgroup",
            namespace=dsf.consumption.RedshiftServerlessNamespace(self, "RedshiftNamespace",
                name="example-namespace",
                db_name="defaultdb"
            )
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        namespace: RedshiftServerlessNamespace,
        base_capacity: typing.Optional[jsii.Number] = None,
        config_parameters: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_redshiftserverless_ceddda9d.CfnWorkgroup.ConfigParameterProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        extra_security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]] = None,
        port: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name: The name of the Redshift Serverless Workgroup.
        :param namespace: The Redshift Serverless Namespace associated with the Workgroup.
        :param base_capacity: The base capacity of the Redshift Serverless Workgroup in RPU. Default: - 128 RPU
        :param config_parameters: Additional parameters to set for advanced control over the Redshift Workgroup. See {@link https://docs.aws.amazon.com/redshift-serverless/latest/APIReference/API_CreateWorkgroup.html#redshiftserverless-CreateWorkgroup-request-configParameters} for more information on what parameters can be set. Default: - ``require_ssl`` parameter is set to true.
        :param extra_security_groups: The extra EC2 Security Groups to associate with the Redshift Serverless Workgroup (in addition to the primary Security Group). Default: - No extra security groups are used
        :param port: The custom port to use when connecting to workgroup. Valid port ranges are 5431-5455 and 8191-8215. Default: - 5439
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param subnets: The subnets where the Redshift Serverless Workgroup is deployed. Default: - Use the private subnets of the VPC
        :param vpc: The VPC where the Redshift Serverless Workgroup is deployed. Default: - A default VPC is created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0beb9838d3eaaf6da4bf6eff2c139e8c6bef6e7f3a51a3a74cb0001d4b76cc5a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RedshiftServerlessWorkgroupProps(
            name=name,
            namespace=namespace,
            base_capacity=base_capacity,
            config_parameters=config_parameters,
            extra_security_groups=extra_security_groups,
            port=port,
            removal_policy=removal_policy,
            subnets=subnets,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="accessData")
    def access_data(
        self,
        id: builtins.str,
        create_vpc_endpoint: typing.Optional[builtins.bool] = None,
        existing_interface_vpc_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
    ) -> RedshiftData:
        '''(deprecated) Creates an instance of ``RedshiftData`` to send custom SQLs to the workgroup.

        :param id: The CDK ID of the resource.
        :param create_vpc_endpoint: if set to true, create interface VPC endpoint for Redshift Data API.
        :param existing_interface_vpc_endpoint: if ``createVpcEndpoint`` is false, and if this is populated, then the Lambda function's security group would be added in the existing VPC endpoint's security group.

        :return: ``RedshiftData``

        :deprecated: Use the convenience methods directly from the ``RedshiftServerlessWorkgroup`` construct.

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__656d5ccac3be5498f4c9424d9535dc359e8d9f55ffcaf649ad7cfc1b2de647d4)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument create_vpc_endpoint", value=create_vpc_endpoint, expected_type=type_hints["create_vpc_endpoint"])
            check_type(argname="argument existing_interface_vpc_endpoint", value=existing_interface_vpc_endpoint, expected_type=type_hints["existing_interface_vpc_endpoint"])
        return typing.cast(RedshiftData, jsii.invoke(self, "accessData", [id, create_vpc_endpoint, existing_interface_vpc_endpoint]))

    @jsii.member(jsii_name="assignDbRolesToIAMRole")
    def assign_db_roles_to_iam_role(
        self,
        db_roles: typing.Sequence[builtins.str],
        target_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    ) -> None:
        '''Assigns Redshift DB roles to IAM role vs the ``RedshiftDbRoles`` tag.

        :param db_roles: List of Redshift DB roles to assign to IAM role.
        :param target_role: The IAM role to assign the Redshift DB roles to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__274a1c47474a72a173b6aa1ea8f194624cfca935b741372a44d5145e2c0268e2)
            check_type(argname="argument db_roles", value=db_roles, expected_type=type_hints["db_roles"])
            check_type(argname="argument target_role", value=target_role, expected_type=type_hints["target_role"])
        return typing.cast(None, jsii.invoke(self, "assignDbRolesToIAMRole", [db_roles, target_role]))

    @jsii.member(jsii_name="catalogTables")
    def catalog_tables(
        self,
        id: builtins.str,
        catalog_db_name: builtins.str,
        path_to_crawl: typing.Optional[builtins.str] = None,
    ) -> _DataCatalogDatabase_925dcbbb:
        '''Creates a new Glue data catalog database with a crawler using JDBC target type to connect to the Redshift Workgroup.

        :param id: The CDK ID of the resource.
        :param catalog_db_name: The name of the Glue Database to create.
        :param path_to_crawl: The path of Redshift tables to crawl.

        :default: `/public/%``

        :return: The DataCatalogDatabase created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1732f80b1debc82beaf28365ccb5311f0a9de55e9b841b2a6932b124a8b0b979)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument catalog_db_name", value=catalog_db_name, expected_type=type_hints["catalog_db_name"])
            check_type(argname="argument path_to_crawl", value=path_to_crawl, expected_type=type_hints["path_to_crawl"])
        return typing.cast(_DataCatalogDatabase_925dcbbb, jsii.invoke(self, "catalogTables", [id, catalog_db_name, path_to_crawl]))

    @jsii.member(jsii_name="createDatabaseFromShare")
    def create_database_from_share(
        self,
        id: builtins.str,
        new_database_name: builtins.str,
        producer_data_share_name: builtins.str,
        producer_namespace_id: typing.Optional[builtins.str] = None,
        producer_account_id: typing.Optional[builtins.str] = None,
    ) -> RedshiftDataSharingCreateDbFromShareProps:
        '''Consume datashare by creating a new database pointing to the share.

        If datashare is coming from a different account, setting ``autoAssociate`` to true
        automatically associates the datashare to the cluster before the new database is created.

        :param id: The CDK ID of the resource.
        :param new_database_name: The name of the database that would be created from the data share.
        :param producer_data_share_name: The name of the data share from producer.
        :param producer_namespace_id: The producer cluster namespace.
        :param producer_account_id: The producer account ID. Required for cross account shares.

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10c3d7e1746f0d16676b6d37da1e17d6ff455720d41ecdbe5e051b8a32f6c65f)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument new_database_name", value=new_database_name, expected_type=type_hints["new_database_name"])
            check_type(argname="argument producer_data_share_name", value=producer_data_share_name, expected_type=type_hints["producer_data_share_name"])
            check_type(argname="argument producer_namespace_id", value=producer_namespace_id, expected_type=type_hints["producer_namespace_id"])
            check_type(argname="argument producer_account_id", value=producer_account_id, expected_type=type_hints["producer_account_id"])
        return typing.cast(RedshiftDataSharingCreateDbFromShareProps, jsii.invoke(self, "createDatabaseFromShare", [id, new_database_name, producer_data_share_name, producer_namespace_id, producer_account_id]))

    @jsii.member(jsii_name="createDbRole")
    def create_db_role(
        self,
        id: builtins.str,
        database_name: builtins.str,
        role_name: builtins.str,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Creates a new DB role.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param role_name: The name of the role to create.

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffd90f090e5decf054755d4d34db25c9506e74ac2990171d30d286da23fbde0a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "createDbRole", [id, database_name, role_name]))

    @jsii.member(jsii_name="createShare")
    def create_share(
        self,
        id: builtins.str,
        database_name: builtins.str,
        data_share_name: builtins.str,
        schema: builtins.str,
        tables: typing.Sequence[builtins.str],
    ) -> RedshiftNewShareProps:
        '''Create a new datashare.

        :param id: The CDK ID of the resource.
        :param database_name: The name of the database to connect to.
        :param data_share_name: The name of the datashare.
        :param schema: The schema to add in the datashare.
        :param tables: The list of tables that would be included in the datashare. This must follow the format: ``<schema>.<tableName>``

        :return: ``RedshiftNewShareProps``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb7d745f44f06dc1511932c5b2a7566dc46ab9fe97deaf5bdb0768eef6f679ef)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument data_share_name", value=data_share_name, expected_type=type_hints["data_share_name"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument tables", value=tables, expected_type=type_hints["tables"])
        return typing.cast(RedshiftNewShareProps, jsii.invoke(self, "createShare", [id, database_name, data_share_name, schema, tables]))

    @jsii.member(jsii_name="grantAccessToShare")
    def grant_access_to_share(
        self,
        id: builtins.str,
        data_share_details: typing.Union[RedshiftNewShareProps, typing.Dict[builtins.str, typing.Any]],
        consumer_namespace_id: typing.Optional[builtins.str] = None,
        consumer_account_id: typing.Optional[builtins.str] = None,
        auto_authorized: typing.Optional[builtins.bool] = None,
    ) -> RedshiftDataSharingGrantedProps:
        '''Create a datashare grant to a namespace if it's in the same account, or to another account.

        :param id: The CDK ID of the resource.
        :param data_share_details: The details of the datashare.
        :param consumer_namespace_id: The namespace of the consumer that you're sharing to. Either namespace or account Id must be provided.
        :param consumer_account_id: The account ID of the consumer that you're sharing to. Either namespace or account Id must be provided.
        :param auto_authorized: -

        :default: false, when this is set to true, cross-account shares would automatically be authorized

        :return: ``RedshiftDataSharingGrantedProps``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5522ed7209bb1ef22b91cc7862372a04f8c622832963bf2043b367a469b92075)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument data_share_details", value=data_share_details, expected_type=type_hints["data_share_details"])
            check_type(argname="argument consumer_namespace_id", value=consumer_namespace_id, expected_type=type_hints["consumer_namespace_id"])
            check_type(argname="argument consumer_account_id", value=consumer_account_id, expected_type=type_hints["consumer_account_id"])
            check_type(argname="argument auto_authorized", value=auto_authorized, expected_type=type_hints["auto_authorized"])
        return typing.cast(RedshiftDataSharingGrantedProps, jsii.invoke(self, "grantAccessToShare", [id, data_share_details, consumer_namespace_id, consumer_account_id, auto_authorized]))

    @jsii.member(jsii_name="grantDbAllPrivilegesToRole")
    def grant_db_all_privileges_to_role(
        self,
        id: builtins.str,
        database_name: builtins.str,
        schema: builtins.str,
        role_name: builtins.str,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Grants both read and write permissions on all the tables in the ``schema`` to the DB role.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param schema: The schema where the tables are located in.
        :param role_name: The DB role to grant the permissions to.

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44c0a0a30c1e3e0f45aac36fa07c8a0b1426550b5f557e03fe782092f459620f)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "grantDbAllPrivilegesToRole", [id, database_name, schema, role_name]))

    @jsii.member(jsii_name="grantDbSchemaToRole")
    def grant_db_schema_to_role(
        self,
        id: builtins.str,
        database_name: builtins.str,
        schema: builtins.str,
        role_name: builtins.str,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Grants access to the schema to the DB role.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param schema: The schema where the tables are located in.
        :param role_name: The DB role to grant the permissions to.

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f71eb71eb7f7dd7216af3dc20d9b6906e806742b531d956dd6bd1bd9949e625)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "grantDbSchemaToRole", [id, database_name, schema, role_name]))

    @jsii.member(jsii_name="grantSchemaReadToRole")
    def grant_schema_read_to_role(
        self,
        id: builtins.str,
        database_name: builtins.str,
        schema: builtins.str,
        role_name: builtins.str,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Grants read permission on all the tables in the ``schema`` to the DB role.

        :param id: -
        :param database_name: The name of the database to run this command.
        :param schema: The schema where the tables are located in.
        :param role_name: The DB role to grant the permissions to.

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b6639981684a4360e50ba57963d7af9f370fc6b052cec18de467dfc77599d8d)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "grantSchemaReadToRole", [id, database_name, schema, role_name]))

    @jsii.member(jsii_name="ingestData")
    def ingest_data(
        self,
        id: builtins.str,
        database_name: builtins.str,
        target_table: builtins.str,
        source_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        source_prefix: builtins.str,
        ingest_additional_options: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Ingest data from S3 into a Redshift table.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param target_table: The target table to load the data into.
        :param source_bucket: The bucket where the source data would be coming from.
        :param source_prefix: The location inside the bucket where the data would be ingested from.
        :param ingest_additional_options: Optional. Additional options to pass to the ``COPY`` command. For example, ``delimiter '|'`` or ``ignoreheader 1``
        :param role: Optional. The IAM Role to use to access the data in S3. If not provided, it would use the default IAM role configured in the Redshift Namespace
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c51af318125fc00003c4631af5211b0ca4110e65b4dd14747f1bb0cd6497a0a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument target_table", value=target_table, expected_type=type_hints["target_table"])
            check_type(argname="argument source_bucket", value=source_bucket, expected_type=type_hints["source_bucket"])
            check_type(argname="argument source_prefix", value=source_prefix, expected_type=type_hints["source_prefix"])
            check_type(argname="argument ingest_additional_options", value=ingest_additional_options, expected_type=type_hints["ingest_additional_options"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "ingestData", [id, database_name, target_table, source_bucket, source_prefix, ingest_additional_options, role]))

    @jsii.member(jsii_name="mergeToTargetTable")
    def merge_to_target_table(
        self,
        id: builtins.str,
        database_name: builtins.str,
        source_table: builtins.str,
        target_table: builtins.str,
        source_column_id: typing.Optional[builtins.str] = None,
        target_column_id: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Run the ``MERGE`` query using simplified mode.

        This command would do an upsert into the target table.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param source_table: The source table name. Schema can also be included using the following format: ``schemaName.tableName``
        :param target_table: The target table name. Schema can also be included using the following format: ``schemaName.tableName``
        :param source_column_id: The column in the source table that's used to determine whether the rows in the ``sourceTable`` can be matched with rows in the ``targetTable``. Default is ``id``
        :param target_column_id: The column in the target table that's used to determine whether the rows in the ``sourceTable`` can be matched with rows in the ``targetTable``. Default is ``id``

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa028c96754f9f984481434a31ccaaec5289a009cc31f17849f3eac21feb9704)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument source_table", value=source_table, expected_type=type_hints["source_table"])
            check_type(argname="argument target_table", value=target_table, expected_type=type_hints["target_table"])
            check_type(argname="argument source_column_id", value=source_column_id, expected_type=type_hints["source_column_id"])
            check_type(argname="argument target_column_id", value=target_column_id, expected_type=type_hints["target_column_id"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "mergeToTargetTable", [id, database_name, source_table, target_table, source_column_id, target_column_id]))

    @jsii.member(jsii_name="retrieveVersion")
    def retrieve_version(self) -> typing.Any:
        '''Retrieve DSF package.json version.'''
        return typing.cast(typing.Any, jsii.invoke(self, "retrieveVersion", []))

    @jsii.member(jsii_name="runCustomSQL")
    def run_custom_sql(
        self,
        id: builtins.str,
        database_name: builtins.str,
        sql: builtins.str,
        delete_sql: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Runs a custom SQL.

        Once the custom resource finishes execution, the attribute ``Data`` contains an attribute ``execId`` which contains the Redshift Data API execution ID. You can then use this to retrieve execution results via the ``GetStatementResult`` API.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param sql: The sql to run.
        :param delete_sql: Optional. The sql to run when this resource gets deleted

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7039acbf64106fcfc7e263695ba5592494b32eeef7b9afbda78e216ec8bf630)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument sql", value=sql, expected_type=type_hints["sql"])
            check_type(argname="argument delete_sql", value=delete_sql, expected_type=type_hints["delete_sql"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "runCustomSQL", [id, database_name, sql, delete_sql]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_OWNED_TAG")
    def DSF_OWNED_TAG(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_OWNED_TAG"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_TRACKING_CODE")
    def DSF_TRACKING_CODE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_TRACKING_CODE"))

    @builtins.property
    @jsii.member(jsii_name="cfnResource")
    def cfn_resource(self) -> _aws_cdk_aws_redshiftserverless_ceddda9d.CfnWorkgroup:
        '''The created Redshift Serverless Workgroup.'''
        return typing.cast(_aws_cdk_aws_redshiftserverless_ceddda9d.CfnWorkgroup, jsii.get(self, "cfnResource"))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''Connections used by Workgroup security group.

        Used this to enable access from clients connecting to the workgroup
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="existingShares")
    def existing_shares(self) -> typing.Mapping[builtins.str, RedshiftNewShareProps]:
        '''Index of existing shares.'''
        return typing.cast(typing.Mapping[builtins.str, RedshiftNewShareProps], jsii.get(self, "existingShares"))

    @builtins.property
    @jsii.member(jsii_name="glueConnection")
    def glue_connection(self) -> _aws_cdk_aws_glue_ceddda9d.CfnConnection:
        '''The Glue Connection associated with the workgroup.

        This can be used by Glue ETL Jobs to read/write data from/to Redshift workgroup
        '''
        return typing.cast(_aws_cdk_aws_glue_ceddda9d.CfnConnection, jsii.get(self, "glueConnection"))

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> RedshiftServerlessNamespace:
        '''The associated Redshift Serverless Namespace.'''
        return typing.cast(RedshiftServerlessNamespace, jsii.get(self, "namespace"))

    @builtins.property
    @jsii.member(jsii_name="primarySecurityGroup")
    def primary_security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        '''The primary EC2 Security Group associated with the Redshift Serverless Workgroup.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, jsii.get(self, "primarySecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="selectedSubnets")
    def selected_subnets(self) -> _aws_cdk_aws_ec2_ceddda9d.SelectedSubnets:
        '''The subnets where the Redshift Serverless Workgroup is deployed.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, jsii.get(self, "selectedSubnets"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC where the Redshift Serverless Workgroup is deployed.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))


@jsii.enum(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.RedshiftServerlessWorkgroupConfigParamKey"
)
class RedshiftServerlessWorkgroupConfigParamKey(enum.Enum):
    AUTO_MV = "AUTO_MV"
    DATESTYLE = "DATESTYLE"
    ENABLE_USER_ACTIVITY_LOGGING = "ENABLE_USER_ACTIVITY_LOGGING"
    QUERY_GROUP = "QUERY_GROUP"
    SEARCH_PATH = "SEARCH_PATH"
    MAX_QUERY_EXECUTION_TIME = "MAX_QUERY_EXECUTION_TIME"
    REQUIRE_SSL = "REQUIRE_SSL"
    USE_FIPS_SSL = "USE_FIPS_SSL"


@jsii.data_type(
    jsii_type="@cdklabs/aws-data-solutions-framework.consumption.RedshiftServerlessWorkgroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "namespace": "namespace",
        "base_capacity": "baseCapacity",
        "config_parameters": "configParameters",
        "extra_security_groups": "extraSecurityGroups",
        "port": "port",
        "removal_policy": "removalPolicy",
        "subnets": "subnets",
        "vpc": "vpc",
    },
)
class RedshiftServerlessWorkgroupProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        namespace: RedshiftServerlessNamespace,
        base_capacity: typing.Optional[jsii.Number] = None,
        config_parameters: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_redshiftserverless_ceddda9d.CfnWorkgroup.ConfigParameterProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        extra_security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]] = None,
        port: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc] = None,
    ) -> None:
        '''RedshiftServerlessWorkgroup properties.

        :param name: The name of the Redshift Serverless Workgroup.
        :param namespace: The Redshift Serverless Namespace associated with the Workgroup.
        :param base_capacity: The base capacity of the Redshift Serverless Workgroup in RPU. Default: - 128 RPU
        :param config_parameters: Additional parameters to set for advanced control over the Redshift Workgroup. See {@link https://docs.aws.amazon.com/redshift-serverless/latest/APIReference/API_CreateWorkgroup.html#redshiftserverless-CreateWorkgroup-request-configParameters} for more information on what parameters can be set. Default: - ``require_ssl`` parameter is set to true.
        :param extra_security_groups: The extra EC2 Security Groups to associate with the Redshift Serverless Workgroup (in addition to the primary Security Group). Default: - No extra security groups are used
        :param port: The custom port to use when connecting to workgroup. Valid port ranges are 5431-5455 and 8191-8215. Default: - 5439
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param subnets: The subnets where the Redshift Serverless Workgroup is deployed. Default: - Use the private subnets of the VPC
        :param vpc: The VPC where the Redshift Serverless Workgroup is deployed. Default: - A default VPC is created
        '''
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83581aad2a8ffe9885f335ae9f8efd43c1cb14783aad8eb61311a8a99788bd1f)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument base_capacity", value=base_capacity, expected_type=type_hints["base_capacity"])
            check_type(argname="argument config_parameters", value=config_parameters, expected_type=type_hints["config_parameters"])
            check_type(argname="argument extra_security_groups", value=extra_security_groups, expected_type=type_hints["extra_security_groups"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "namespace": namespace,
        }
        if base_capacity is not None:
            self._values["base_capacity"] = base_capacity
        if config_parameters is not None:
            self._values["config_parameters"] = config_parameters
        if extra_security_groups is not None:
            self._values["extra_security_groups"] = extra_security_groups
        if port is not None:
            self._values["port"] = port
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if subnets is not None:
            self._values["subnets"] = subnets
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Redshift Serverless Workgroup.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace(self) -> RedshiftServerlessNamespace:
        '''The Redshift Serverless Namespace associated with the Workgroup.'''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(RedshiftServerlessNamespace, result)

    @builtins.property
    def base_capacity(self) -> typing.Optional[jsii.Number]:
        '''The base capacity of the Redshift Serverless Workgroup in RPU.

        :default: - 128 RPU
        '''
        result = self._values.get("base_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def config_parameters(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_redshiftserverless_ceddda9d.CfnWorkgroup.ConfigParameterProperty]]:
        '''Additional parameters to set for advanced control over the Redshift Workgroup.

        See {@link https://docs.aws.amazon.com/redshift-serverless/latest/APIReference/API_CreateWorkgroup.html#redshiftserverless-CreateWorkgroup-request-configParameters}
        for more information on what parameters can be set.

        :default: - ``require_ssl`` parameter is set to true.
        '''
        result = self._values.get("config_parameters")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_redshiftserverless_ceddda9d.CfnWorkgroup.ConfigParameterProperty]], result)

    @builtins.property
    def extra_security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]]:
        '''The extra EC2 Security Groups to associate with the Redshift Serverless Workgroup (in addition to the primary Security Group).

        :default: - No extra security groups are used
        '''
        result = self._values.get("extra_security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''The custom port to use when connecting to workgroup.

        Valid port ranges are 5431-5455 and 8191-8215.

        :default: - 5439
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise, the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The subnets where the Redshift Serverless Workgroup is deployed.

        :default: - Use the private subnets of the VPC
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc]:
        '''The VPC where the Redshift Serverless Workgroup is deployed.

        :default: - A default VPC is created
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftServerlessWorkgroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/aws-data-solutions-framework.consumption.State")
class State(enum.Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


__all__ = [
    "AthenaWorkGroup",
    "AthenaWorkgroupProps",
    "BaseRedshiftDataAccess",
    "BaseRedshiftDataSharingAccessProps",
    "EngineVersion",
    "OpenSearchApi",
    "OpenSearchApiProps",
    "OpenSearchCluster",
    "OpenSearchClusterProps",
    "OpenSearchClusterType",
    "OpenSearchNodes",
    "RedshiftData",
    "RedshiftDataAccessTargetProps",
    "RedshiftDataProps",
    "RedshiftDataSharing",
    "RedshiftDataSharingCreateDbFromShareProps",
    "RedshiftDataSharingCreateDbProps",
    "RedshiftDataSharingGrantProps",
    "RedshiftDataSharingGrantedProps",
    "RedshiftDataSharingProps",
    "RedshiftNewShareProps",
    "RedshiftServerlessNamespace",
    "RedshiftServerlessNamespaceLogExport",
    "RedshiftServerlessNamespaceProps",
    "RedshiftServerlessWorkgroup",
    "RedshiftServerlessWorkgroupConfigParamKey",
    "RedshiftServerlessWorkgroupProps",
    "State",
]

publication.publish()

def _typecheckingstub__15339157ee2b24d990c2efefafd65bf35e69eee9f4bca1f6e95210a8c521bd46(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    result_location_prefix: builtins.str,
    bytes_scanned_cutoff_per_query: typing.Optional[jsii.Number] = None,
    enforce_work_group_configuration: typing.Optional[builtins.bool] = None,
    engine_version: typing.Optional[EngineVersion] = None,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    publish_cloud_watch_metrics_enabled: typing.Optional[builtins.bool] = None,
    recursive_delete_option: typing.Optional[builtins.bool] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    requester_pays_enabled: typing.Optional[builtins.bool] = None,
    result_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    result_bucket_name: typing.Optional[builtins.str] = None,
    results_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    results_retention_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    state: typing.Optional[State] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dae31e93a53a124faa0e753ab90b50aadc8ec8c3fe3110c4f935b3d20012ef0(
    principal: _aws_cdk_aws_iam_ceddda9d.IPrincipal,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cb515883861e94cb0356ff0dbaafe8172250732d8c494d9aefa4ebe8ce1bf67(
    *,
    name: builtins.str,
    result_location_prefix: builtins.str,
    bytes_scanned_cutoff_per_query: typing.Optional[jsii.Number] = None,
    enforce_work_group_configuration: typing.Optional[builtins.bool] = None,
    engine_version: typing.Optional[EngineVersion] = None,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    publish_cloud_watch_metrics_enabled: typing.Optional[builtins.bool] = None,
    recursive_delete_option: typing.Optional[builtins.bool] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    requester_pays_enabled: typing.Optional[builtins.bool] = None,
    result_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    result_bucket_name: typing.Optional[builtins.str] = None,
    results_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    results_retention_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    state: typing.Optional[State] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9985f4049aa72dd939b7a61db338637dec44417183751017e2218bc9be83c02c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: typing.Union[RedshiftDataProps, typing.Dict[builtins.str, typing.Any]],
    tracked_construct_props: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d0c35b695ab38577c2fecab94b554b10d8b4aafafd90ce100ced23a87e472a0(
    id: builtins.str,
    data_access_target: typing.Union[RedshiftDataAccessTargetProps, typing.Dict[builtins.str, typing.Any]],
    *,
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    cluster_id: typing.Optional[builtins.str] = None,
    create_interface_vpc_endpoint: typing.Optional[builtins.bool] = None,
    execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    existing_interface_vpc_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    workgroup_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a28e18f6974415cc94fcaebffd87efa6925735276e0230c357d938a182f6d2bb(
    *,
    database_name: builtins.str,
    data_share_name: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
    data_share_arn: typing.Optional[builtins.str] = None,
    namespace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8efac875434c2ff3bedcef40f1dbae7e47123a4751d234bd1bac60d2a468e1ef(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    iam_handler_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    open_search_cluster_type: OpenSearchClusterType,
    open_search_endpoint: builtins.str,
    open_search_endpoint_region: typing.Optional[builtins.str] = None,
    query_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    query_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7aeb5e0efc38b4f92132936725a6dff4aa74533cb2028da7462b93cb303afbc(
    id: builtins.str,
    name: builtins.str,
    role: builtins.str,
    persist: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ecd8383a967da8ab7ee7f183e887c27ae441daff51214512d7b26ea78e8f41f(
    id: builtins.str,
    api_path: builtins.str,
    body: typing.Any,
    method: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43a6edd19c0d6911251eed3a9f9c4cfaec5badcf5e6ccef4fc4dabe4188fa83c(
    value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__260162222abba8d8fb264695411f01927754e8e344d84aff9e285f78d362c2f6(
    value: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dda92ecf9e44229c03338082bd125f0e0a0f4b2a3734416f9abd87c0b866f3d0(
    value: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c0f4e512135e6844fda97751b0c5dcfad23f99713dd467a913d652a2a16f882(
    value: typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__142210441c72f24f3d7c5b491edc882440257e40fae05d89f8037093e705237d(
    *,
    iam_handler_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    open_search_cluster_type: OpenSearchClusterType,
    open_search_endpoint: builtins.str,
    open_search_endpoint_region: typing.Optional[builtins.str] = None,
    query_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    query_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60f575b30a96a58830f495b53ff60cfcbd6167aef0ea4f794adc5678f7b24a0e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    deploy_in_vpc: builtins.bool,
    domain_name: builtins.str,
    saml_entity_id: builtins.str,
    saml_master_backend_role: builtins.str,
    saml_metadata_content: builtins.str,
    availability_zone_count: typing.Optional[jsii.Number] = None,
    data_node_instance_count: typing.Optional[jsii.Number] = None,
    data_node_instance_type: typing.Optional[builtins.str] = None,
    ebs_size: typing.Optional[jsii.Number] = None,
    ebs_volume_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.EbsDeviceVolumeType] = None,
    enable_auto_software_update: typing.Optional[builtins.bool] = None,
    enable_version_upgrade: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    master_node_instance_count: typing.Optional[jsii.Number] = None,
    master_node_instance_type: typing.Optional[builtins.str] = None,
    multi_az_with_standby_enabled: typing.Optional[builtins.bool] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    saml_roles_key: typing.Optional[builtins.str] = None,
    saml_session_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    saml_subject_key: typing.Optional[builtins.str] = None,
    version: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    warm_instance_count: typing.Optional[jsii.Number] = None,
    warm_instance_type: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a2802fc2c9fb60dc104a1f00436fda25dcfa3e7b38fe466059411c265fabb80(
    id: builtins.str,
    name: builtins.str,
    role: builtins.str,
    persist: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab2f032aaae68164347e789baa2a730951e9dba8c79c67088effadcdebe23be4(
    id: builtins.str,
    api_path: builtins.str,
    body: typing.Any,
    method: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ab254d0fd8b8275467b9080f08ede4baf63fc2639bc444965e3c87af35c6995(
    *,
    deploy_in_vpc: builtins.bool,
    domain_name: builtins.str,
    saml_entity_id: builtins.str,
    saml_master_backend_role: builtins.str,
    saml_metadata_content: builtins.str,
    availability_zone_count: typing.Optional[jsii.Number] = None,
    data_node_instance_count: typing.Optional[jsii.Number] = None,
    data_node_instance_type: typing.Optional[builtins.str] = None,
    ebs_size: typing.Optional[jsii.Number] = None,
    ebs_volume_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.EbsDeviceVolumeType] = None,
    enable_auto_software_update: typing.Optional[builtins.bool] = None,
    enable_version_upgrade: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    master_node_instance_count: typing.Optional[jsii.Number] = None,
    master_node_instance_type: typing.Optional[builtins.str] = None,
    multi_az_with_standby_enabled: typing.Optional[builtins.bool] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    saml_roles_key: typing.Optional[builtins.str] = None,
    saml_session_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    saml_subject_key: typing.Optional[builtins.str] = None,
    version: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    warm_instance_count: typing.Optional[jsii.Number] = None,
    warm_instance_type: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9a2d248d6fbf659d115f24968cc59aac0104e5a923ac52cee2a23bce808688e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    cluster_id: typing.Optional[builtins.str] = None,
    create_interface_vpc_endpoint: typing.Optional[builtins.bool] = None,
    execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    existing_interface_vpc_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    workgroup_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d69eede88c497092e8f7fd603a0542f6c9554b439f3bf93346b28c818678472c(
    db_roles: typing.Sequence[builtins.str],
    target_role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f14371ad2ad05c07137e411b1d1d513561fc32a19c5e32873b7434c9bd6ce958(
    id: builtins.str,
    database_name: builtins.str,
    role_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3a8c6a93b4f6656c5b5465925552b1d9bcf808d0960799d84a434e67eb29cd6(
    id: builtins.str,
    database_name: builtins.str,
    schema: builtins.str,
    role_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e10fab791ae834d9c06b689c13987c2ee10638ec886903128e17f47014fe0e6(
    id: builtins.str,
    database_name: builtins.str,
    schema: builtins.str,
    role_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4dfcf9706dcab4280387aae8ed45d13e997c2395e953d93135c70de8cc6884b(
    id: builtins.str,
    database_name: builtins.str,
    schema: builtins.str,
    role_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e780d5708468f127fb8b94065194842b051792812507b57493d738900b10e2bc(
    id: builtins.str,
    database_name: builtins.str,
    target_table: builtins.str,
    source_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    source_prefix: builtins.str,
    ingest_additional_options: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34612948d8c76fa94cac7ac063e59ccb539459f9fa991d1d0c5c3925a10b4181(
    id: builtins.str,
    database_name: builtins.str,
    source_table: builtins.str,
    target_table: builtins.str,
    source_column_id: typing.Optional[builtins.str] = None,
    target_column_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79343924d71f835a06e1f24ed7dbe20b8c9fb32df7c1089747cc9cfe30bd9e03(
    id: builtins.str,
    database_name: builtins.str,
    sql: builtins.str,
    delete_sql: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__861d9de737cf60e979f1fb120ea5724ba7b2873aeb4538ad5841df9f93570307(
    *,
    target_arn: builtins.str,
    target_id: builtins.str,
    target_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d480592ed79dd1af33b7179862f6641c88e07337cf7c2b6ead428ed68bc84cdd(
    *,
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    cluster_id: typing.Optional[builtins.str] = None,
    create_interface_vpc_endpoint: typing.Optional[builtins.bool] = None,
    execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    existing_interface_vpc_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    workgroup_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1a39f7fe2374e40e1f26a21341c7716f3c4f3b3e11bd11ab56403e4097056c3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    redshift_data: RedshiftData,
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    cluster_id: typing.Optional[builtins.str] = None,
    create_interface_vpc_endpoint: typing.Optional[builtins.bool] = None,
    execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    existing_interface_vpc_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    workgroup_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fc88db2a86b7ba500cafae04f1c330c70bd663b454f63ba85997d7f7058ec7f(
    id: builtins.str,
    *,
    new_database_name: builtins.str,
    consumer_namespace_arn: typing.Optional[builtins.str] = None,
    database_name: builtins.str,
    data_share_name: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
    data_share_arn: typing.Optional[builtins.str] = None,
    namespace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b31f4e36ef22e73a5897a8eb4beac7096331fea9862ce0b1cc8d1afd8aca77a(
    id: builtins.str,
    database_name: builtins.str,
    data_share_name: builtins.str,
    schema: builtins.str,
    tables: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9201574db2958d2cf5ed51c6378268cad17e0a20e9959178d578de9292e7c1fc(
    id: builtins.str,
    *,
    auto_authorized: typing.Optional[builtins.bool] = None,
    database_name: builtins.str,
    data_share_name: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
    data_share_arn: typing.Optional[builtins.str] = None,
    namespace_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ceb8aa411cca34c81cde3126681ca9a5e6865f9187185acd4868c42cc50f350d(
    *,
    resource: _aws_cdk_ceddda9d.CustomResource,
    associate_data_share_resource: typing.Optional[_aws_cdk_custom_resources_ceddda9d.AwsCustomResource] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cadfd7328c9e91872b4f5f98d320822f101f2ca3d1c390fd8b98132df55a6cf(
    *,
    database_name: builtins.str,
    data_share_name: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
    data_share_arn: typing.Optional[builtins.str] = None,
    namespace_id: typing.Optional[builtins.str] = None,
    new_database_name: builtins.str,
    consumer_namespace_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08e47e7834f522ee1825b8a15ab18c8d4a9e926997d5a3a7949617851df7fe21(
    *,
    database_name: builtins.str,
    data_share_name: builtins.str,
    account_id: typing.Optional[builtins.str] = None,
    data_share_arn: typing.Optional[builtins.str] = None,
    namespace_id: typing.Optional[builtins.str] = None,
    auto_authorized: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e38b2bf6fd9554265c2a2a36ca3368c9ac87852c2ab34cb1ee51d8486214527(
    *,
    resource: _aws_cdk_ceddda9d.CustomResource,
    share_authorization_resource: typing.Optional[_aws_cdk_custom_resources_ceddda9d.AwsCustomResource] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea9e32f91290772227d25742eab949586a52606a31e5d50c08552be8f5094492(
    *,
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    cluster_id: typing.Optional[builtins.str] = None,
    create_interface_vpc_endpoint: typing.Optional[builtins.bool] = None,
    execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    existing_interface_vpc_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    workgroup_id: typing.Optional[builtins.str] = None,
    redshift_data: RedshiftData,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__100f15df37a3044d0c5511b2ce12a309acffd87db4e2a40893f10c064c35d64e(
    *,
    database_name: builtins.str,
    data_share_arn: builtins.str,
    data_share_name: builtins.str,
    new_share_custom_resource: _aws_cdk_ceddda9d.CustomResource,
    producer_arn: builtins.str,
    producer_namespace: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9507a166b2460e33a5a01511fed95cd5cead50cc1f27c934665aee7800656cee(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    db_name: builtins.str,
    name: builtins.str,
    admin_secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    admin_username: typing.Optional[builtins.str] = None,
    data_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    default_iam_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    final_snapshot_name: typing.Optional[builtins.str] = None,
    final_snapshot_retention_period: typing.Optional[jsii.Number] = None,
    iam_roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
    log_exports: typing.Optional[typing.Sequence[RedshiftServerlessNamespaceLogExport]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    service_linked_role_factory: typing.Optional[_CreateServiceLinkedRole_fba94500] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8549fe13f562662bc17af1b381de6c8045964b12fea2e988c063b8045eb0bdb(
    *,
    db_name: builtins.str,
    name: builtins.str,
    admin_secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    admin_username: typing.Optional[builtins.str] = None,
    data_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    default_iam_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    final_snapshot_name: typing.Optional[builtins.str] = None,
    final_snapshot_retention_period: typing.Optional[jsii.Number] = None,
    iam_roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
    log_exports: typing.Optional[typing.Sequence[RedshiftServerlessNamespaceLogExport]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    service_linked_role_factory: typing.Optional[_CreateServiceLinkedRole_fba94500] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0beb9838d3eaaf6da4bf6eff2c139e8c6bef6e7f3a51a3a74cb0001d4b76cc5a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    namespace: RedshiftServerlessNamespace,
    base_capacity: typing.Optional[jsii.Number] = None,
    config_parameters: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_redshiftserverless_ceddda9d.CfnWorkgroup.ConfigParameterProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    extra_security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]] = None,
    port: typing.Optional[jsii.Number] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__656d5ccac3be5498f4c9424d9535dc359e8d9f55ffcaf649ad7cfc1b2de647d4(
    id: builtins.str,
    create_vpc_endpoint: typing.Optional[builtins.bool] = None,
    existing_interface_vpc_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__274a1c47474a72a173b6aa1ea8f194624cfca935b741372a44d5145e2c0268e2(
    db_roles: typing.Sequence[builtins.str],
    target_role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1732f80b1debc82beaf28365ccb5311f0a9de55e9b841b2a6932b124a8b0b979(
    id: builtins.str,
    catalog_db_name: builtins.str,
    path_to_crawl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10c3d7e1746f0d16676b6d37da1e17d6ff455720d41ecdbe5e051b8a32f6c65f(
    id: builtins.str,
    new_database_name: builtins.str,
    producer_data_share_name: builtins.str,
    producer_namespace_id: typing.Optional[builtins.str] = None,
    producer_account_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffd90f090e5decf054755d4d34db25c9506e74ac2990171d30d286da23fbde0a(
    id: builtins.str,
    database_name: builtins.str,
    role_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb7d745f44f06dc1511932c5b2a7566dc46ab9fe97deaf5bdb0768eef6f679ef(
    id: builtins.str,
    database_name: builtins.str,
    data_share_name: builtins.str,
    schema: builtins.str,
    tables: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5522ed7209bb1ef22b91cc7862372a04f8c622832963bf2043b367a469b92075(
    id: builtins.str,
    data_share_details: typing.Union[RedshiftNewShareProps, typing.Dict[builtins.str, typing.Any]],
    consumer_namespace_id: typing.Optional[builtins.str] = None,
    consumer_account_id: typing.Optional[builtins.str] = None,
    auto_authorized: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44c0a0a30c1e3e0f45aac36fa07c8a0b1426550b5f557e03fe782092f459620f(
    id: builtins.str,
    database_name: builtins.str,
    schema: builtins.str,
    role_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f71eb71eb7f7dd7216af3dc20d9b6906e806742b531d956dd6bd1bd9949e625(
    id: builtins.str,
    database_name: builtins.str,
    schema: builtins.str,
    role_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b6639981684a4360e50ba57963d7af9f370fc6b052cec18de467dfc77599d8d(
    id: builtins.str,
    database_name: builtins.str,
    schema: builtins.str,
    role_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c51af318125fc00003c4631af5211b0ca4110e65b4dd14747f1bb0cd6497a0a(
    id: builtins.str,
    database_name: builtins.str,
    target_table: builtins.str,
    source_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    source_prefix: builtins.str,
    ingest_additional_options: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa028c96754f9f984481434a31ccaaec5289a009cc31f17849f3eac21feb9704(
    id: builtins.str,
    database_name: builtins.str,
    source_table: builtins.str,
    target_table: builtins.str,
    source_column_id: typing.Optional[builtins.str] = None,
    target_column_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7039acbf64106fcfc7e263695ba5592494b32eeef7b9afbda78e216ec8bf630(
    id: builtins.str,
    database_name: builtins.str,
    sql: builtins.str,
    delete_sql: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83581aad2a8ffe9885f335ae9f8efd43c1cb14783aad8eb61311a8a99788bd1f(
    *,
    name: builtins.str,
    namespace: RedshiftServerlessNamespace,
    base_capacity: typing.Optional[jsii.Number] = None,
    config_parameters: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_redshiftserverless_ceddda9d.CfnWorkgroup.ConfigParameterProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    extra_security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]] = None,
    port: typing.Optional[jsii.Number] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc] = None,
) -> None:
    """Type checking stubs"""
    pass
