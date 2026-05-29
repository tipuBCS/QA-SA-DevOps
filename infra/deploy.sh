#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/.env"

STACK="${1:-all}"

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
