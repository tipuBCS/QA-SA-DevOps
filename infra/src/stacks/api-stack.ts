import { Stack, StackProps, Duration, CfnOutput } from 'aws-cdk-lib/core';
import { Function, Runtime, Code } from 'aws-cdk-lib/aws-lambda';
import { RestApi, Cors, LambdaIntegration } from 'aws-cdk-lib/aws-apigateway';
import { join } from 'path';
import { Construct } from 'constructs';
import { getStage } from '../helpers';

export class ApiStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const stage = getStage();

    // Lambda function with the API code
    const apiFunction = new Function(this, `ApiFunction-${stage}`, {
      functionName: `room-booker-api-${stage}`,
      runtime: Runtime.PYTHON_3_12,
      handler: 'main.lambda_handler',
      code: Code.fromAsset(join(__dirname, '../../../api')),
      timeout: Duration.seconds(30),
      memorySize: 256,
      environment: {
        POWERTOOLS_SERVICE_NAME: `room-booker-api-${stage}`,
        LOG_LEVEL: 'INFO',
      },
    });

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

    // Output the API URL
    new CfnOutput(this, 'ApiUrl', {
      value: api.url,
      description: 'API Gateway URL',
    });
  }
}
