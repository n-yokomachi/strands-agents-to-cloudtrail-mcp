import * as dotenv from 'dotenv';

// .envファイルを読み込み（存在する場合のみ）
dotenv.config();

export interface AppConfig {
  // AWS基本設定
  awsRegion: string;
  awsAccountId: string;
  homeIpAddress: string;
}

// シンプルな設定（最小限の環境変数のみ）
export const getConfig = (): AppConfig => {
  if (!process.env.AWS_ACCOUNT_ID || !process.env.HOME_IP_ADDRESS) {
    throw new Error('AWS_ACCOUNT_ID and HOME_IP_ADDRESS are required');
  }
  
  return {
    awsRegion: 'ap-northeast-1',
    awsAccountId: process.env.AWS_ACCOUNT_ID!,
    homeIpAddress: process.env.HOME_IP_ADDRESS!
  };
};

// 固定値の設定
export const APP_CONFIG = {
  bedrockModelId: 'apac.anthropic.claude-3-5-sonnet-20241022-v2:0',
  projectName: 'strands-agents-app',
  ecsClusterName: 'strands-cluster',
  ecsServiceName: 'strands-service',
  albName: 'strands-alb'
};

 