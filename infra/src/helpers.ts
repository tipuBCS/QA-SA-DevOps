import { config } from 'dotenv';
import { join } from 'path';
import { Environment } from 'aws-cdk-lib/core';

config({ path: join(__dirname, '..', '.env') });

export type Stage = 'dev' | 'prod';

export function getStage(): Stage {
  const stage = process.env.STAGE;
  if (stage !== 'dev' && stage !== 'prod') {
    throw new Error(`Invalid STAGE "${stage}" in .env. Must be "dev" or "prod".`);
  }
  return stage;
}

export function getEnv(): Environment {
  const account = process.env.AWS_ACCOUNT_ID;
  const region = process.env.AWS_REGION;
  if (!account || !region) {
    throw new Error('AWS_ACCOUNT_ID and AWS_REGION must both be set in .env.');
  }
  return { account, region };
}
