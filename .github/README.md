# Setting up deployment pipeline workflow

## Prerequisites
We need to give Github access to our AWS account so that it can perform actions like creating buckets, lambda functions etc for the production environment
### 1. Create an identity provider 
We must go to our AWS account -> IAM -> Identity provider
Create an [identity provider for Github](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)

### 2. Create a role for Github to use in your AWS Account
Use this [guide](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws#configuring-the-role-and-trust-policy)

### 3. Create a secret in Github for AWS Account and Role
Go to your repo on GitHub
Settings → Secrets and variables → Actions
Click "New repository secret"
Add these:
Name: AWS_ROLE_ARN → Value: your-role-arn
Name: AWS_REGION → Value: region