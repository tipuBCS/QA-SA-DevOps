#!/usr/bin/env node
import { App } from 'aws-cdk-lib/core';
import { ApiStack } from './stacks/api-stack';
import { FrontendStack } from './stacks/frontend-stack';
import { getStage, getEnv } from './helpers';

const app = new App();
const stage = getStage();
const env = getEnv();

new ApiStack(app, `ApiStack-${stage}`, { env });
new FrontendStack(app, `FrontendStack-${stage}`, { env });
