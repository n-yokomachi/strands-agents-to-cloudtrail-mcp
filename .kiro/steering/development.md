# Development Guidelines

## Code Standards

### Python Code Style
- Follow PEP 8 conventions
- Use type hints for function parameters and return values
- Implement proper error handling with try/catch blocks
- Use async/await patterns for I/O operations where applicable

### TypeScript/CDK Standards
- Use strict TypeScript configuration
- Follow AWS CDK best practices for resource naming
- Implement proper resource tagging and descriptions
- Use environment-specific configurations

## Project Structure

```
aws-detective-agent/
├── app/                    # Streamlit Application
│   ├── main.py            # Main app with Strands Agent integration
│   ├── components.py      # UI components and helpers
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Container configuration
├── lambda/                # MCP Server
│   ├── mcpserver/
│   │   └── main.py       # FastMCP server implementation
│   ├── Dockerfile        # Lambda container config
│   └── pyproject.toml    # Python project configuration
├── lib/                  # CDK Infrastructure
│   ├── config.ts         # Configuration management
│   └── stack.ts          # Unified CDK stack definition
└── bin/
    └── app.ts            # CDK application entry point
```

## Development Workflow

### Local Development
- Use `.env` file for local configuration
- Test MCP server locally before Lambda deployment
- Use CDK diff to preview infrastructure changes

### Deployment Process
1. Configure environment variables in `.env`
2. Run `./app/deploy.sh` for full deployment
3. Use `npm run destroy` for cleanup

### Key Environment Variables
- `AWS_ACCOUNT_ID`: Target AWS account
- `HOME_IP_ADDRESS`: IP address for security group access
- `MCP_URL`: Lambda function URL for MCP server

## Testing Guidelines

### MCP Server Testing
- Test CloudTrail API integration with various time ranges
- Validate error handling for invalid parameters
- Ensure proper IAM permissions for CloudTrail access

### Streamlit App Testing
- Test agent streaming functionality
- Validate MCP client integration
- Test UI responsiveness and error states

## Security Considerations

### IAM Permissions
- Use least privilege principle for all roles
- Separate execution and task roles for ECS
- Limit CloudTrail access to necessary operations only

### Network Security
- Use VPC with proper subnet isolation
- Configure security groups with minimal required access
- Enable container insights for monitoring