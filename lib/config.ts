import * as dotenv from 'dotenv';

// .envファイルを読み込み（存在する場合のみ）
dotenv.config();

export interface AppConfig {
  // AWS基本設定
  awsRegion: string;
  awsAccountId: string;
  
  // Bedrock設定
  bedrockModelId: string;
  
  // セキュリティ設定
  homeIpAddress: string;
  
  // プロジェクト設定
  projectName: string;
  environment: string;
  
  // リソース名設定
  ecrRepositoryName: string;
  ecsClusterName: string;
      ecsServiceName: string;
    cloudtrailMcpFunctionName: string;
    albName: string;
}

// 環境変数から設定を取得（デフォルト値付き）
export const getConfig = (): AppConfig => {
  const requiredEnvVars = [
    'AWS_REGION',
    'AWS_ACCOUNT_ID',
    'HOME_IP_ADDRESS'
  ];
  
  // 必須環境変数のチェック
  for (const envVar of requiredEnvVars) {
    if (!process.env[envVar]) {
      throw new Error(`Required environment variable ${envVar} is not set. Please check your .env file.`);
    }
  }
  
  return {
    // AWS基本設定
    awsRegion: process.env.AWS_REGION!,
    awsAccountId: process.env.AWS_ACCOUNT_ID!,
    
    // Bedrock設定
    bedrockModelId: process.env.BEDROCK_MODEL_ID || 'anthropic.claude-3-5-sonnet-20241022-v2:0',
    
    // セキュリティ設定
    homeIpAddress: process.env.HOME_IP_ADDRESS!,
    
    // プロジェクト設定
    projectName: process.env.PROJECT_NAME || 'cloudtrail-behavior-prediction',
    environment: process.env.ENVIRONMENT || 'dev',
    
    // リソース名設定
    ecrRepositoryName: process.env.ECR_REPOSITORY_NAME || 'strands-app',
    ecsClusterName: process.env.ECS_CLUSTER_NAME || 'strands-cluster',
          ecsServiceName: process.env.ECS_SERVICE_NAME || 'strands-service',
      cloudtrailMcpFunctionName: process.env.CLOUDTRAIL_MCP_FUNCTION_NAME || 'cloudtrail-mcp-server',
      albName: process.env.ALB_NAME || 'strands-alb'
  };
};

// 設定値の検証
export const validateConfig = (config: AppConfig): void => {
  // IPアドレス形式の検証
  const ipRegex = /^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$/;
  if (!ipRegex.test(config.homeIpAddress)) {
    throw new Error(`Invalid IP address format: ${config.homeIpAddress}. Expected format: x.x.x.x/xx`);
  }
  
  // AWSアカウントIDの検証（12桁の数字）
  const accountIdRegex = /^\d{12}$/;
  if (!accountIdRegex.test(config.awsAccountId)) {
    throw new Error(`Invalid AWS Account ID: ${config.awsAccountId}. Must be 12 digits.`);
  }
  
  // リージョン形式の検証
  const regionRegex = /^[a-z]{2}-[a-z]+-\d{1}$/;
  if (!regionRegex.test(config.awsRegion)) {
    throw new Error(`Invalid AWS region format: ${config.awsRegion}`);
  }
  
  console.log('✅ Configuration validation passed');
}; 