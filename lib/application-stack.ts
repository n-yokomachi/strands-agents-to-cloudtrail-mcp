import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export interface ApplicationStackProps extends cdk.StackProps {
  vpc: ec2.IVpc;
  cloudtrailMcpRole: iam.Role;
  fargateExecutionRole: iam.Role;
  fargateTaskRole: iam.Role;
}

export class ApplicationStack extends cdk.Stack {
  public readonly cloudtrailMcpFunction: lambda.Function;
  public readonly functionUrl: lambda.FunctionUrl;
  public readonly ecsService: any;

  constructor(scope: Construct, id: string, props: ApplicationStackProps) {
    super(scope, id, props);

    // CloudTrail MCP Server Lambda
    this.cloudtrailMcpFunction = new lambda.Function(this, 'CloudTrailMCPServer', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'index.handler',
      code: lambda.Code.fromInline(`
import json

def handler(event, context):
    # CloudTrail MCP Server placeholder
    # 実装予定: FastAPI + MCP SDK + Lambda Web Adapter
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': 'CloudTrail MCP Server placeholder',
            'protocol': 'MCP over Lambda Function URL',
            'event_type': event.get('requestContext', {}).get('http', {}).get('method', 'UNKNOWN')
        })
    }
      `),
      role: props.cloudtrailMcpRole,
      description: 'CloudTrail MCP Server with Function URL',
      timeout: cdk.Duration.minutes(15),
      memorySize: 256
    });

    // Function URL with RESPONSE_STREAM mode for MCP streaming
    this.functionUrl = this.cloudtrailMcpFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      invokeMode: lambda.InvokeMode.RESPONSE_STREAM,
      cors: {
        allowCredentials: true,
        allowedHeaders: ['*'],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedOrigins: ['*']
      }
    });

    // Outputs
    new cdk.CfnOutput(this, 'CloudTrailMCPServerUrl', {
      value: this.functionUrl.url,
      description: 'CloudTrail MCP Server Function URL'
    });

    new cdk.CfnOutput(this, 'CloudTrailMCPFunctionArn', {
      value: this.cloudtrailMcpFunction.functionArn,
      description: 'CloudTrail MCP Server Function ARN'
    });

    // TODO: Strands Agents Fargate implementation
    this.ecsService = null; // placeholder
  }
} 