import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export class IAMStack extends cdk.Stack {
  public readonly cloudtrailMcpRole: iam.Role;
  public readonly fargateExecutionRole: iam.Role;
  public readonly fargateTaskRole: iam.Role;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // CloudTrail MCP Lambda実行ロール
    this.cloudtrailMcpRole = new iam.Role(this, 'CloudTrailMCPLambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      description: 'CloudTrail MCP Server Lambda execution role',
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole')
      ],
      inlinePolicies: {
        CloudTrailAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: ['cloudtrail:*'],
              resources: ['*']
            }),
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: ['logs:*'],
              resources: ['*']
            })
          ]
        })
      }
    });

    // Fargate実行ロール
    this.fargateExecutionRole = new iam.Role(this, 'FargateExecutionRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
      description: 'Fargate task execution role',
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonECSTaskExecutionRolePolicy')
      ]
    });

    // Fargateタスクロール
    this.fargateTaskRole = new iam.Role(this, 'FargateTaskRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
      description: 'Fargate task role for Strands Agents',
      inlinePolicies: {
        StrandsAgentsAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: ['bedrock:*'],
              resources: ['*']
            }),
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: ['logs:*'],
              resources: ['*']
            })
          ]
        })
      }
    });

    // Outputs
    new cdk.CfnOutput(this, 'CloudTrailMCPRoleArn', {
      value: this.cloudtrailMcpRole.roleArn,
      description: 'CloudTrail MCP Lambda Role ARN'
    });

    new cdk.CfnOutput(this, 'FargateExecutionRoleArn', {
      value: this.fargateExecutionRole.roleArn,
      description: 'Fargate Execution Role ARN'
    });

    new cdk.CfnOutput(this, 'FargateTaskRoleArn', {
      value: this.fargateTaskRole.roleArn,
      description: 'Fargate Task Role ARN'
    });
  }
} 