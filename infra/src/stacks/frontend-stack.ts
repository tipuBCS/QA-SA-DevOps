import { Stack, StackProps, CfnOutput, RemovalPolicy } from 'aws-cdk-lib/core';
import { Bucket } from 'aws-cdk-lib/aws-s3';
import { Distribution, ViewerProtocolPolicy, OriginAccessIdentity } from 'aws-cdk-lib/aws-cloudfront';
import { S3Origin } from 'aws-cdk-lib/aws-cloudfront-origins';
import { BucketDeployment, Source } from 'aws-cdk-lib/aws-s3-deployment';
import { join } from 'path';
import { Construct } from 'constructs';
import { getStage } from '../helpers';

export class FrontendStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const stage = getStage();

    // S3 bucket for hosting the frontend assets
    const bucket = new Bucket(this, `FrontendBucket-${stage}`, {
      bucketName: `room-booker-frontend-${stage}`,
      removalPolicy: stage === 'dev' ? RemovalPolicy.DESTROY : RemovalPolicy.RETAIN,
      autoDeleteObjects: stage === 'dev',
    });

    // Origin Access Identity for CloudFront to access S3
    const originAccessIdentity = new OriginAccessIdentity(this, `OAI-${stage}`, {
      comment: `OAI for room-booker-frontend-${stage}`,
    });

    bucket.grantRead(originAccessIdentity);

    // CloudFront distribution
    const distribution = new Distribution(this, `Distribution-${stage}`, {
      defaultBehavior: {
        origin: new S3Origin(bucket, { originAccessIdentity }),
        viewerProtocolPolicy: ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
      },
      defaultRootObject: 'index.html',
      errorResponses: [
        {
          httpStatus: 403,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
        },
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
        },
      ],
    });

    // Deploy the UI dist folder to S3
    new BucketDeployment(this, `DeployUI-${stage}`, {
      sources: [Source.asset(join(__dirname, '../../../ui/dist'))],
      destinationBucket: bucket,
      distribution,
      distributionPaths: ['/*'],
    });

    // Outputs
    new CfnOutput(this, 'BucketName', {
      value: bucket.bucketName,
      description: 'Frontend S3 Bucket Name',
    });

    new CfnOutput(this, 'DistributionDomainName', {
      value: distribution.distributionDomainName,
      description: 'CloudFront Distribution Domain Name',
    });

    new CfnOutput(this, 'DistributionId', {
      value: distribution.distributionId,
      description: 'CloudFront Distribution ID',
    });
  }
}
