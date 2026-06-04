#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/.env"

STACK="${1:-all}"

# Pre-deploy: generate requirements.txt and install deps for Lambda layer
echo "Generating requirements.txt for API dependencies..."
cd "$SCRIPT_DIR/../api"
uv export --no-dev --no-editable --no-hashes > requirements.txt

echo "Installing dependencies into .deps/python..."
rm -rf .deps
uv pip install -r requirements.txt --target .deps/python --quiet
cd "$SCRIPT_DIR"

case "$STACK" in
  api)
    STACK_NAME="ApiStack-${STAGE}"
    ;;
  frontend)
    STACK_NAME="FrontendStack-${STAGE}"
    ;;
  all)
    STACK_NAME="--all"
    ;;
  *)
    echo "Usage: ./deploy.sh [api|frontend|all]"
    echo "  api       - Deploy the API stack"
    echo "  frontend  - Deploy the Frontend stack"
    echo "  all       - Deploy all stacks (default)"
    exit 1
    ;;
esac

echo "Deploying: $STACK_NAME"
npx cdk deploy $STACK_NAME --profile "$AWS_PROFILE" --require-approval never
