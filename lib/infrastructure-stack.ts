import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

export class InfrastructureStack extends cdk.Stack {
  public readonly vpc: ec2.IVpc;
  public readonly securityGroups: {
    alb: ec2.SecurityGroup;
    fargate: ec2.SecurityGroup;
  };

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // デフォルトVPCを使用（検証環境のため）
    this.vpc = ec2.Vpc.fromLookup(this, 'DefaultVpc', {
      isDefault: true
    });

    // ALB用セキュリティグループ（自宅IP限定）
    this.securityGroups = {
      alb: new ec2.SecurityGroup(this, 'ALBSecurityGroup', {
        vpc: this.vpc,
        description: 'Security group for ALB (Home IP only)',
        allowAllOutbound: true
      }),
      
      fargate: new ec2.SecurityGroup(this, 'FargateSecurityGroup', {
        vpc: this.vpc,
        description: 'Security group for Fargate tasks',
        allowAllOutbound: true
      })
    };

    // TODO: 実際の自宅IPアドレスは環境変数から取得
    // 現在はプレースホルダー
    const homeIpAddress = '203.0.113.100/32'; // 後で環境変数から取得

    // ALBへのHTTPアクセス（自宅IPのみ）
    this.securityGroups.alb.addIngressRule(
      ec2.Peer.ipv4(homeIpAddress),
      ec2.Port.tcp(80),
      'Allow HTTP from home IP'
    );

    // FargateへのALBからのアクセス
    this.securityGroups.fargate.addIngressRule(
      this.securityGroups.alb,
      ec2.Port.tcp(8501),
      'Allow traffic from ALB to Streamlit'
    );

    // ヘルスチェック用ポート
    this.securityGroups.fargate.addIngressRule(
      this.securityGroups.alb,
      ec2.Port.tcp(8080),
      'Allow health check from ALB'
    );

    // Outputs
    new cdk.CfnOutput(this, 'VpcId', {
      value: this.vpc.vpcId,
      description: 'VPC ID'
    });

    new cdk.CfnOutput(this, 'ALBSecurityGroupId', {
      value: this.securityGroups.alb.securityGroupId,
      description: 'ALB Security Group ID'
    });

    new cdk.CfnOutput(this, 'FargateSecurityGroupId', {
      value: this.securityGroups.fargate.securityGroupId,
      description: 'Fargate Security Group ID'
    });
  }
} 