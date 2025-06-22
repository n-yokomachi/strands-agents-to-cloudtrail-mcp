#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { InfrastructureStack } from '../lib/infrastructure-stack';
import { IAMStack } from '../lib/iam-stack';
import { ApplicationStack } from '../lib/application-stack';

const app = new cdk.App();

// 環境設定（後で.envから読み込み予定）
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

// Stack間の依存関係を考慮してデプロイ
const infrastructureStack = new InfrastructureStack(app, 'InfrastructureStack', { env });

const iamStack = new IAMStack(app, 'IAMStack', { 
  env
});

const applicationStack = new ApplicationStack(app, 'ApplicationStack', {
  env,
  vpc: infrastructureStack.vpc,
  cloudtrailMcpRole: iamStack.cloudtrailMcpRole,
  fargateExecutionRole: iamStack.fargateExecutionRole,
  fargateTaskRole: iamStack.fargateTaskRole
});

// タグ付け
cdk.Tags.of(app).add('Project', 'CloudTrail-Behavior-Prediction');
cdk.Tags.of(app).add('Environment', 'Development');
cdk.Tags.of(app).add('ManagedBy', 'CDK'); 