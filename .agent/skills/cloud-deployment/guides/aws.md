# AWS Deployment Guide

> Deploy containerized applications to AWS

## Quick Start (ECS Fargate)

```bash
# Install AWS CLI
pip install awscli

# Configure
aws configure

# Deploy with ECS CLI
ecs-cli up --keypair mykey --capability-iam --size 2 --instance-type t3.medium
```

## Architecture Options

### Option 1: ECS Fargate (Containers)

Best for: Long-running services, full-stack apps

### Option 2: Lambda (Serverless)

Best for: APIs, event processing, low traffic

### Option 3: Elastic Beanstalk

Best for: Quick deployment, simple apps

## ECS Fargate Deployment

### 1. Create ECR Repository

```bash
aws ecr create-repository --repository-name myapp

# Login
aws ecr get-login-password | docker login --username AWS --password-stdin [account].dkr.ecr.[region].amazonaws.com
```

### 2. Build and Push

```bash
# Build
docker build -t myapp .

# Tag
docker tag myapp:latest [account].dkr.ecr.[region].amazonaws.com/myapp:latest

# Push
docker push [account].dkr.ecr.[region].amazonaws.com/myapp:latest
```

### 3. Create Task Definition

```json
{
  "family": "myapp",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "myapp",
      "image": "[account].dkr.ecr.[region].amazonaws.com/myapp:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://..."
        }
      ]
    }
  ]
}
```

### 4. Create Service

```bash
aws ecs create-service \
  --cluster mycluster \
  --service-name myservice \
  --task-definition myapp:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

## Lambda Deployment

### 1. Create Function

```bash
aws lambda create-function \
  --function-name myapi \
  --runtime python3.11 \
  --handler main.handler \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::[account]:role/lambda-role
```

### 2. API Gateway

```bash
aws apigateway create-rest-api --name myapi

# Create resource and method...
```

### 3. Serverless Framework

```yaml
# serverless.yml
service: myapi

provider:
  name: aws
  runtime: python3.11

functions:
  api:
    handler: main.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
```

```bash
serverless deploy
```

## Database (RDS)

### Create PostgreSQL Instance

```bash
aws rds create-db-instance \
  --db-instance-identifier mydb \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password mypassword \
  --allocated-storage 20
```

## S3 Static Hosting

### 1. Create Bucket

```bash
aws s3 mb s3://myapp-frontend
```

### 2. Configure for Static Hosting

```bash
aws s3 website s3://myapp-frontend --index-document index.html --error-document index.html
```

### 3. Upload

```bash
aws s3 sync ./dist s3://myapp-frontend
```

## CloudFront CDN

```bash
aws cloudfront create-distribution \
  --origin-domain-name myapp-frontend.s3.amazonaws.com \
  --default-root-object index.html
```

## Custom Domain (Route 53)

### 1. Register Domain

```bash
aws route53domains register-domain --domain-name example.com --duration-in-years 1
```

### 2. Create Hosted Zone

```bash
aws route53 create-hosted-zone --name example.com --caller-reference $(date +%s)
```

### 3. Add Records

```bash
aws route53 change-resource-record-sets \
  --hosted-zone-id ZONEID \
  --change-batch file://records.json
```

## SSL Certificate (ACM)

```bash
aws acm request-certificate \
  --domain-name example.com \
  --validation-method DNS

# Add validation records to Route 53...
```

## Environment Variables

### Parameter Store

```bash
aws ssm put-parameter \
  --name /myapp/prod/database_url \
  --value "postgresql://..." \
  --type SecureString
```

### Secrets Manager

```bash
aws secretsmanager create-secret \
  --name myapp/prod/secrets \
  --secret-string '{"api_key":"xxx"}'
```

## Monitoring (CloudWatch)

```bash
# View logs
aws logs tail /ecs/myapp --follow

# Create alarm
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu \
  --metric-name CPUUtilization \
  --threshold 80
```

## Cost Optimization

1. **Use Spot instances**: For background jobs
2. **Right-size**: Match resources to usage
3. **Reserved capacity**: For steady workloads
4. **Cleanup**: Remove unused resources
5. **Billing alerts**: Set budget notifications

## Pricing

| Service | Cost | Notes |
|---------|------|-------|
| ECS Fargate | $0.04/vCPU/hr | Per usage |
| Lambda | $0.20/million | First 1M free |
| RDS | $13/mo | db.t3.micro |
| S3 | $0.023/GB | Storage |
| CloudFront | $0.085/GB | Data transfer |

## Best Practices

1. **Infrastructure as Code**: Use CloudFormation/Terraform
2. **Security Groups**: Minimal access
3. **IAM Roles**: Least privilege
4. **Logging**: Centralize with CloudWatch
5. **Backups**: Automated RDS backups

## Troubleshooting

### Check Service Status

```bash
aws ecs describe-services --cluster mycluster --services myservice
```

### View Logs

```bash
aws logs tail /ecs/myapp --follow
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Task pending | Check VPC/subnet config |
| Out of memory | Increase task memory |
| Health check fail | Check security groups |
