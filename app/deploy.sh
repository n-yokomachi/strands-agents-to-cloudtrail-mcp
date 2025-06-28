#!/bin/bash
set -e

echo "🚀 Deploying Strands Agents app..."
npx cdk deploy --all --require-approval never
echo "✅ Deployment completed!" 