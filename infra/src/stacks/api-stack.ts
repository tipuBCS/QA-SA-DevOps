import { Stack, StackProps, Duration, CfnOutput, RemovalPolicy } from 'aws-cdk-lib/core';
import { Function, Runtime, Code, LayerVersion, Architecture } from 'aws-cdk-lib/aws-lambda';
import { RestApi, Cors, LambdaIntegration } from 'aws-cdk-lib/aws-apigateway';
import { Table, BillingMode, AttributeType, ProjectionType } from 'aws-cdk-lib/aws-dynamodb';
import { join } from 'path';
import { Construct } from 'constructs';
import { getStage } from '../helpers';

export class ApiStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const stage = getStage();

    // DynamoDB table (single-table design)
    const table = new Table(this, `RoomBookerTable-${stage}`, {
      tableName: `room-booker-${stage}`,
      partitionKey: { name: 'PK', type: AttributeType.STRING },
      sortKey: { name: 'SK', type: AttributeType.STRING },
      billingMode: BillingMode.PAY_PER_REQUEST,
      removalPolicy: stage === 'dev' ? RemovalPolicy.DESTROY : RemovalPolicy.RETAIN,
    });

    // GSI for email lookups (and other access patterns later)
    table.addGlobalSecondaryIndex({
      indexName: 'GSI1',
      partitionKey: { name: 'GSI1PK', type: AttributeType.STRING },
      sortKey: { name: 'GSI1SK', type: AttributeType.STRING },
      projectionType: ProjectionType.ALL,
    });

    // AWS Lambda Powertools layer
    const powertoolsLayer = LayerVersion.fromLayerVersionArn(
      this, `PowertoolsLayer-${stage}`,
      `arn:aws:lambda:${this.region}:017000801446:layer:AWSLambdaPowertoolsPythonV3-python312-x86_64:7`
    );

    // Dependencies layer (pre-built by deploy script into api/.deps/python)
    const depsLayer = new LayerVersion(this, `DepsLayer-${stage}`, {
      code: Code.fromAsset(join(__dirname, '../../../api/.deps')),
      compatibleRuntimes: [Runtime.PYTHON_3_12],
      description: 'API Python dependencies',
      compatibleArchitectures: [Architecture.X86_64]
    });

    // Lambda function with the API code
    const apiFunction = new Function(this, `ApiFunction-${stage}`, {
      functionName: `room-booker-api-${stage}`,
      runtime: Runtime.PYTHON_3_12,
      handler: 'main.lambda_handler',
      code: Code.fromAsset(join(__dirname, '../../../api'), {
        exclude: ['.venv', '.deps', 'tests', '__pycache__', '.pytest_cache', '.env', 'uv.lock'],
      }),
      layers: [powertoolsLayer, depsLayer],
      timeout: Duration.seconds(30),
      memorySize: 256,
      environment: {
        POWERTOOLS_SERVICE_NAME: `room-booker-api-${stage}`,
        LOG_LEVEL: 'INFO',
        DB_TABLE_NAME: table.tableName,
      },
    });

    // Grant the Lambda read/write access to the table
    table.grantReadWriteData(apiFunction);

    // API Gateway with Lambda proxy integration
    const api = new RestApi(this, `Api-${stage}`, {
      restApiName: `RoomBookerApi-${stage}`,
      description: 'Room Booker API',
      deployOptions: {
        stageName: stage,
      },
      defaultCorsPreflightOptions: {
        allowOrigins: Cors.ALL_ORIGINS,
        allowMethods: Cors.ALL_METHODS,
      },
    });

    // Add a proxy resource to forward all requests to the Lambda
    api.root.addProxy({
      defaultIntegration: new LambdaIntegration(apiFunction),
      anyMethod: true,
    });

    // Outputs
    new CfnOutput(this, 'ApiUrl', {
      value: api.url,
      description: 'API Gateway URL',
    });

    new CfnOutput(this, 'TableName', {
      value: table.tableName,
      description: 'DynamoDB Table Name',
    });
  }
}
