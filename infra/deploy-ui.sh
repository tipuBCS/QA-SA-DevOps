#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$SCRIPT_DIR/.env"

# Load .env file
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: .env file not found at $ENV_FILE"
  exit 1
fi

source "$ENV_FILE"

if [ -z "$S3_BUCKET_NAME" ]; then
  echo "Error: S3_BUCKET_NAME not set in .env"
  exit 1
fi

# Check if we can access the S3 bucket, refresh credentials if not
echo "Checking S3 access..."
if ! aws s3 ls "s3://$S3_BUCKET_NAME" --profile "$AWS_PROFILE" > /dev/null 2>&1; then
  echo "Cannot access S3 bucket. Refreshing credentials..."
  ada credentials update --account "$AWS_ACCOUNT_ID" --role "$AWS_ROLE" --provider "$AWS_PROVIDER" --profile "$AWS_PROFILE"
fi

echo "Building UI..."
cd "$ROOT_DIR/ui"
npm run build

echo "Uploading dist/ to s3://$S3_BUCKET_NAME..."
aws s3 sync dist/ "s3://$S3_BUCKET_NAME" --delete --profile "$AWS_PROFILE"

echo "Invalidating CloudFront cache..."
aws cloudfront create-invalidation --distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" --paths "/*" --profile "$AWS_PROFILE"

echo "Deploy complete!"
