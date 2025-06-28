#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { UnifiedStack } from '../lib/stack';
import { getConfig, APP_CONFIG } from '../lib/config';

const app = new cdk.App();

// 設定を取得
const config = getConfig();

// CDK環境設定
const env = {
  account: config.awsAccountId,
  region: config.awsRegion,
};

// 統合スタック
const unifiedStack = new UnifiedStack(app, 'StrandsUnifiedStack', {
  env,
  config
});

// タグ付け
cdk.Tags.of(app).add('Project', APP_CONFIG.projectName);
cdk.Tags.of(app).add('ManagedBy', 'CDK'); 