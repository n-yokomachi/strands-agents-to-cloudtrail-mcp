# Architecture Guidelines

## System Architecture

```
User → ALB → ECS Fargate (Streamlit) → Strands Agent → Bedrock Claude 3.5 Sonnet v2
                                    ↓
                                MCP Client → Lambda MCP Server → CloudTrail API
```

## Technology Stack

### Frontend & UI
- **Streamlit**: Web interface framework
- **Python 3.12**: Runtime environment
- **Detective-themed UI**: Japanese conversational interface

### AI & Agent Layer
- **Strands Agents**: AI agent framework
- **Amazon Bedrock**: Claude 3.5 Sonnet v2 model hosting
- **MCP (Model Context Protocol)**: Tool integration protocol

### Backend Services
- **AWS Lambda**: MCP server hosting (ARM64 architecture)
- **FastMCP**: MCP server implementation framework
- **CloudTrail API**: AWS event data source

### Infrastructure
- **AWS CDK (TypeScript)**: Infrastructure as Code
- **Docker**: Containerization
- **AWS ECS Fargate**: Container orchestration
- **AWS ECR**: Container registry
- **Application Load Balancer**: Traffic distribution
- **VPC**: Network isolation

## Key Design Patterns

### MCP Integration
- Lambda-hosted MCP server for CloudTrail access
- HTTP-based MCP client in Streamlit app
- Stateless MCP server design for Lambda compatibility

### Container Strategy
- Multi-stage Docker builds for optimization
- ARM64 architecture for cost efficiency
- Separate containers for app and MCP server

### Security Model
- IAM roles with least privilege access
- VPC isolation with public/private subnets
- Security groups for network access control