# Welcome to your CDK TypeScript project

This is a blank project for CDK development with TypeScript.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `npx cdk deploy`  deploy this stack to your default AWS account/region
* `npx cdk diff`    compare deployed stack with current state
* `npx cdk synth`   emits the synthesized CloudFormation template

## Manual deployment section:

### S3 Bucket
1. Create an s3 bucket
2. Add it to the .env e.g. S3_BUCKET_NAME=my-bucket-name

### Cloudfront distribution
1. Create a cloudfront distribution
2. Set the origin to the s3 bucket
3. Set the root object to index.html Distribution -> General -> Default Root Object
4. Give the cloudfront distribution access to the s3 bucket (Can occur automatically through creation)
5. Add the distribution to .env e.g. CLOUDFRONT_DISTRIBUTION_ID=12345abcdef

### Deploying website:
1. Add the following to .env:
AWS_ACCOUNT_ID=1234-5678-9123
AWS_ROLE=role_name
AWS_PROVIDER=provider
AWS_PROFILE=profile-name
2. Run the deploy-ui.sh script 