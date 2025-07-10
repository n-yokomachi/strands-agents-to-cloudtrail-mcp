import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as assets from 'aws-cdk-lib/aws-ecr-assets';
import { Construct } from 'constructs';
import { AppConfig, APP_CONFIG } from './config';

export interface UnifiedStackProps extends cdk.StackProps {
  config: AppConfig;
}

export class UnifiedStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: UnifiedStackProps) {
    super(scope, id, props);

    // VPC
    const vpc = new ec2.Vpc(this, 'StrandsVPC', {
      vpcName: 'strands-vpc',
      maxAzs: 2,
      natGateways: 1,
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
        {
          cidrMask: 24,
          name: 'Private',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        }
      ]
    });

    // Security Groups
    const albSecurityGroup = new ec2.SecurityGroup(this, 'ALBSecurityGroup', {
      vpc,
      description: 'Security group for Application Load Balancer',
      allowAllOutbound: true
    });

    albSecurityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(80),
      'Allow HTTP traffic'
    );

    const fargateSecurityGroup = new ec2.SecurityGroup(this, 'FargateSecurityGroup', {
      vpc,
      description: 'Security group for Fargate tasks',
      allowAllOutbound: true
    });

    fargateSecurityGroup.addIngressRule(
      albSecurityGroup,
      ec2.Port.tcp(8501),
      'Allow traffic from ALB'
    );

    // IAM Roles
    const cloudtrailMcpRole = new iam.Role(this, 'CloudTrailMCPLambdaRole', {
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
              actions: [
                'cloudtrail:LookupEvents',
                'cloudtrail:GetTrailStatus',
                'cloudtrail:DescribeTrails'
              ],
              resources: ['*']
            })
          ]
        })
      }
    });

    const fargateExecutionRole = new iam.Role(this, 'FargateExecutionRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
      description: 'Fargate task execution role',
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonECSTaskExecutionRolePolicy')
      ]
    });

    const fargateTaskRole = new iam.Role(this, 'FargateTaskRole', {
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

    // CloudTrail MCP Server Lambda (Container Image)
    const cloudtrailMcpFunction = new lambda.DockerImageFunction(this, 'CloudTrailMCPServer', {
      code: lambda.DockerImageCode.fromImageAsset('./lambda'),
      memorySize: 256,
      timeout: cdk.Duration.minutes(15),
      architecture: lambda.Architecture.ARM_64,
      environment: {
        UV_CACHE_DIR: '/tmp/uv-cache',
        UV_NO_SYNC: '1',
        AWS_LAMBDA_ADAPTER_BUFFER_OFF: '1',
        AWS_LAMBDA_ADAPTER_CALLBACK_PATH: '/callback',
        AWS_LAMBDA_ADAPTER_HTTP_PROXY_BUFFERING: 'off',
        PYTHONPATH: '/app',
        PATH: '/app/.venv/bin:$PATH'
      },
      role: cloudtrailMcpRole,
      description: 'CloudTrail MCP Server with FastMCP and Lambda Web Adapter'
    });

    // Function URL
    const functionUrl = cloudtrailMcpFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      invokeMode: lambda.InvokeMode.BUFFERED,
      cors: {
        allowCredentials: true,
        allowedHeaders: ['*'],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedOrigins: ['*']
      }
    });

    // ECS Cluster
    const ecsCluster = new ecs.Cluster(this, 'StrandsCluster', {
      clusterName: APP_CONFIG.ecsClusterName,
      vpc: vpc,
      containerInsights: true
    });

    // Task Definition
    const taskDefinition = new ecs.FargateTaskDefinition(this, 'StrandsTaskDef', {
      memoryLimitMiB: 512,
      cpu: 256,
      executionRole: fargateExecutionRole,
      taskRole: fargateTaskRole
    });

    // Docker Image Asset
    const dockerImageAsset = new assets.DockerImageAsset(this, 'StrandsAppImage', {
      directory: './app'
    });

    // Container Definition
    const container = taskDefinition.addContainer('StrandsContainer', {
      image: ecs.ContainerImage.fromDockerImageAsset(dockerImageAsset),
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'strands-app'
      })
    });

    container.addPortMappings({
      containerPort: 8501,
      protocol: ecs.Protocol.TCP
    });

    // Application Load Balancer
    const loadBalancer = new elbv2.ApplicationLoadBalancer(this, 'StrandsALB', {
      loadBalancerName: APP_CONFIG.albName,
      vpc: vpc,
      internetFacing: true,
      securityGroup: albSecurityGroup
    });

    // Target Group
    const targetGroup = new elbv2.ApplicationTargetGroup(this, 'StrandsTargetGroup', {
      port: 8501,
      protocol: elbv2.ApplicationProtocol.HTTP,
      vpc: vpc,
      targetType: elbv2.TargetType.IP,
      healthCheck: {
        enabled: true,
        path: '/_stcore/health',
        protocol: elbv2.Protocol.HTTP,
        port: '8501'
      }
    });

    // Listener
    loadBalancer.addListener('StrandsListener', {
      port: 80,
      protocol: elbv2.ApplicationProtocol.HTTP,
      defaultTargetGroups: [targetGroup]
    });

    // ECS Service
    const ecsService = new ecs.FargateService(this, 'StrandsService', {
      serviceName: APP_CONFIG.ecsServiceName,
      cluster: ecsCluster,
      taskDefinition: taskDefinition,
      desiredCount: 1,
      securityGroups: [fargateSecurityGroup],
      assignPublicIp: true
    });

    // Attach service to target group
    ecsService.attachToApplicationTargetGroup(targetGroup);

    // Outputs
    new cdk.CfnOutput(this, 'LoadBalancerURL', {
      value: `http://${loadBalancer.loadBalancerDnsName}`,
      description: 'Strands Agents Streamlit App URL'
    });

    new cdk.CfnOutput(this, 'CloudTrailMCPFunctionURL', {
      value: functionUrl.url,
      description: 'CloudTrail MCP Server Function URL'
    });
  }
} 