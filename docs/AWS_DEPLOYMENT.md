# AWS Deployment Guide

This guide provides detailed instructions for deploying the JanMitra AI Phase 1 Backend on AWS infrastructure using EC2 and DynamoDB.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    AWS Cloud                             │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         EC2 Instance (t3.micro)                │    │
│  │                                                 │    │
│  │  ┌──────────────────────────────────────────┐  │    │
│  │  │   FastAPI Application (Port 8000)        │  │    │
│  │  │   - Uvicorn ASGI Server                  │  │    │
│  │  │   - Python 3.9+                          │  │    │
│  │  └──────────────────────────────────────────┘  │    │
│  │                                                 │    │
│  │  IAM Role: janmitra-ec2-role                   │    │
│  │  - DynamoDB read/write permissions             │    │
│  │                                                 │    │
│  │  Security Group: janmitra-sg                   │    │
│  │  - Inbound: Port 8000 (HTTP)                   │    │
│  │  - Inbound: Port 22 (SSH)                      │    │
│  └────────────────┬───────────────────────────────┘    │
│                   │                                     │
│                   │ boto3 SDK                           │
│                   ▼                                     │
│  ┌────────────────────────────────────────────────┐    │
│  │         DynamoDB                               │    │
│  │         Table: government_schemes              │    │
│  │         - Partition Key: scheme_id (String)    │    │
│  │         - Billing: On-Demand                   │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

- AWS account with appropriate permissions
- AWS CLI installed and configured
- SSH key pair for EC2 access
- Basic knowledge of AWS services (EC2, DynamoDB, IAM)

## Step 1: Create IAM Role for EC2

The EC2 instance needs an IAM role to access DynamoDB without hardcoded credentials.

### 1.1 Create IAM Policy

Create a file named `dynamodb-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Scan",
        "dynamodb:Query",
        "dynamodb:BatchGetItem",
        "dynamodb:BatchWriteItem"
      ],
      "Resource": "arn:aws:dynamodb:ap-south-1:*:table/government_schemes"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:ListTables"
      ],
      "Resource": "*"
    }
  ]
}
```

Create the policy:

```bash
aws iam create-policy \
  --policy-name JanMitraDynamoDBPolicy \
  --policy-document file://dynamodb-policy.json \
  --description "Policy for JanMitra backend to access DynamoDB"
```

**Note the Policy ARN** from the output (e.g., `arn:aws:iam::123456789012:policy/JanMitraDynamoDBPolicy`)

### 1.2 Create IAM Role

Create a trust policy file named `ec2-trust-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Create the role:

```bash
aws iam create-role \
  --role-name janmitra-ec2-role \
  --assume-role-policy-document file://ec2-trust-policy.json \
  --description "IAM role for JanMitra EC2 instance"
```

### 1.3 Attach Policy to Role

```bash
aws iam attach-role-policy \
  --role-name janmitra-ec2-role \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/JanMitraDynamoDBPolicy
```

Replace `YOUR_ACCOUNT_ID` with your AWS account ID.

### 1.4 Create Instance Profile

```bash
aws iam create-instance-profile \
  --instance-profile-name janmitra-ec2-profile

aws iam add-role-to-instance-profile \
  --instance-profile-name janmitra-ec2-profile \
  --role-name janmitra-ec2-role
```

## Step 2: Create DynamoDB Table

Create the `government_schemes` table with on-demand billing:

```bash
aws dynamodb create-table \
  --table-name government_schemes \
  --attribute-definitions AttributeName=scheme_id,AttributeType=S \
  --key-schema AttributeName=scheme_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ap-south-1 \
  --tags Key=Project,Value=JanMitra Key=Environment,Value=Production
```

### Verify Table Creation

```bash
aws dynamodb describe-table \
  --table-name government_schemes \
  --region ap-south-1
```

Wait until the table status is `ACTIVE`.

## Step 3: Create Security Group

Create a security group that allows HTTP traffic on port 8000 and SSH access:

```bash
# Create security group
aws ec2 create-security-group \
  --group-name janmitra-sg \
  --description "Security group for JanMitra backend" \
  --vpc-id vpc-xxxxxxxx

# Note the security group ID from output (sg-xxxxxxxxx)

# Allow SSH access (port 22)
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

# Allow HTTP access on port 8000
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0
```

**Security Note**: For production, restrict SSH access to your IP address instead of `0.0.0.0/0`:

```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 22 \
  --cidr YOUR_IP_ADDRESS/32
```

## Step 4: Launch EC2 Instance

### 4.1 Choose AMI

For Amazon Linux 2023:
- AMI ID: `ami-0c55b159cbfafe1f0` (ap-south-1 region)
- Or find the latest: `aws ec2 describe-images --owners amazon --filters "Name=name,Values=al2023-ami-*" --query 'Images[0].ImageId'`

### 4.2 Launch Instance

```bash
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.micro \
  --key-name your-key-pair-name \
  --security-group-ids sg-xxxxxxxxx \
  --iam-instance-profile Name=janmitra-ec2-profile \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=JanMitra-Backend},{Key=Project,Value=JanMitra}]' \
  --region ap-south-1
```

Replace:
- `your-key-pair-name` with your SSH key pair name
- `sg-xxxxxxxxx` with your security group ID

**Note the Instance ID** from the output (e.g., `i-0123456789abcdef0`)

### 4.3 Get Instance Public IP

```bash
aws ec2 describe-instances \
  --instance-ids i-0123456789abcdef0 \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text
```

Wait a few minutes for the instance to start.

## Step 5: Configure EC2 Instance

### 5.1 Connect via SSH

```bash
ssh -i /path/to/your-key.pem ec2-user@<instance-public-ip>
```

### 5.2 Update System Packages

```bash
sudo yum update -y
```

### 5.3 Install Python 3.9+

```bash
# Amazon Linux 2023 comes with Python 3.9+
python3 --version

# Install pip and development tools
sudo yum install python3-pip python3-devel git -y
```

### 5.4 Install Application

```bash
# Clone repository
cd /home/ec2-user
git clone <your-repository-url> janmitra-ai-phase1-backend
cd janmitra-ai-phase1-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 6: Configure Environment Variables

Create the `.env` file on the EC2 instance:

```bash
cd /home/ec2-user/janmitra-ai-phase1-backend
nano .env
```

Add the following configuration:

```env
# AWS Configuration
AWS_REGION=ap-south-1
# Note: No need for AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY
# The IAM role provides credentials automatically

# DynamoDB Configuration
DYNAMODB_TABLE_NAME=government_schemes

# API Configuration
API_PORT=8000

# Environment
ENVIRONMENT=production
```

**Important**: Do NOT include `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY`. The IAM role attached to the EC2 instance provides credentials automatically.

Save and exit (Ctrl+X, then Y, then Enter).

## Step 7: Seed the Database

Populate DynamoDB with the 5 government schemes:

```bash
cd /home/ec2-user/janmitra-ai-phase1-backend
source venv/bin/activate
python -m database.seed_schemes
```

Expected output:
```
Seeding government schemes to DynamoDB...
✓ Seeded scheme: PM-KISAN
✓ Seeded scheme: Ayushman Bharat
✓ Seeded scheme: Sukanya Samriddhi Yojana
✓ Seeded scheme: MGNREGA
✓ Seeded scheme: Stand Up India
Successfully seeded 5 schemes to DynamoDB
```

### Verify Data

```bash
aws dynamodb scan \
  --table-name government_schemes \
  --region ap-south-1 \
  --query 'Items[*].name.S'
```

## Step 8: Set Up Systemd Service for Auto-Start

Create a systemd service file to run the application automatically on boot and restart on failure.

### 8.1 Create Service File

```bash
sudo nano /etc/systemd/system/janmitra.service
```

Add the following content:

```ini
[Unit]
Description=JanMitra AI Phase 1 Backend
After=network.target

[Service]
Type=simple
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/janmitra-ai-phase1-backend
Environment="PATH=/home/ec2-user/janmitra-ai-phase1-backend/venv/bin"
ExecStart=/home/ec2-user/janmitra-ai-phase1-backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=janmitra

[Install]
WantedBy=multi-user.target
```

Save and exit.

### 8.2 Enable and Start Service

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable janmitra

# Start the service
sudo systemctl start janmitra

# Check status
sudo systemctl status janmitra
```

Expected output:
```
● janmitra.service - JanMitra AI Phase 1 Backend
   Loaded: loaded (/etc/systemd/system/janmitra.service; enabled)
   Active: active (running) since ...
```

### 8.3 Service Management Commands

```bash
# Start service
sudo systemctl start janmitra

# Stop service
sudo systemctl stop janmitra

# Restart service
sudo systemctl restart janmitra

# View logs
sudo journalctl -u janmitra -f

# View last 100 lines
sudo journalctl -u janmitra -n 100
```

## Step 9: Verify Deployment

### 9.1 Test Health Endpoint

From your local machine:

```bash
curl http://<instance-public-ip>:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 9.2 Test Evaluation Endpoint

```bash
curl -X POST http://<instance-public-ip>:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rajesh Kumar",
    "age": 35,
    "income": 250000,
    "state": "Bihar",
    "occupation": "farmer",
    "category": "OBC",
    "land_size": 1.5
  }'
```

### 9.3 Test Schemes Endpoint

```bash
curl http://<instance-public-ip>:8000/schemes
```

### 9.4 Access API Documentation

Open in browser:
- Swagger UI: `http://<instance-public-ip>:8000/docs`
- ReDoc: `http://<instance-public-ip>:8000/redoc`

## Step 10: Monitoring and Maintenance

### View Application Logs

```bash
# Real-time logs
sudo journalctl -u janmitra -f

# Logs from last hour
sudo journalctl -u janmitra --since "1 hour ago"

# Logs with specific priority (error and above)
sudo journalctl -u janmitra -p err
```

### Check System Resources

```bash
# CPU and memory usage
top

# Disk usage
df -h

# Check if service is running
sudo systemctl is-active janmitra
```

### Update Application

```bash
# Stop service
sudo systemctl stop janmitra

# Pull latest code
cd /home/ec2-user/janmitra-ai-phase1-backend
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl start janmitra
```

## Troubleshooting

### Service Won't Start

**Check logs**:
```bash
sudo journalctl -u janmitra -n 50
```

**Common issues**:
1. Port 8000 already in use
2. Missing dependencies
3. Environment variables not set
4. DynamoDB connection issues

### DynamoDB Connection Errors

**Verify IAM role**:
```bash
# Check if instance has IAM role attached
aws ec2 describe-instances \
  --instance-ids i-xxxxxxxxx \
  --query 'Reservations[0].Instances[0].IamInstanceProfile'
```

**Test DynamoDB access from EC2**:
```bash
aws dynamodb list-tables --region ap-south-1
```

### Port 8000 Not Accessible

**Check security group**:
```bash
aws ec2 describe-security-groups \
  --group-ids sg-xxxxxxxxx \
  --query 'SecurityGroups[0].IpPermissions'
```

**Verify service is listening**:
```bash
sudo netstat -tlnp | grep 8000
```

### High Memory Usage

t3.micro has 1GB RAM. If memory is insufficient:

1. **Upgrade to t3.small** (2GB RAM):
   ```bash
   aws ec2 modify-instance-attribute \
     --instance-id i-xxxxxxxxx \
     --instance-type t3.small
   ```

2. **Add swap space**:
   ```bash
   sudo dd if=/dev/zero of=/swapfile bs=1M count=1024
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

## Cost Optimization

### EC2 Costs
- **t3.micro**: ~$7.50/month (on-demand, ap-south-1)
- Consider Reserved Instances for 1-year commitment: ~40% savings
- Use Spot Instances for non-production: ~70% savings

### DynamoDB Costs
- **On-Demand**: Pay per request
  - Read: $0.25 per million requests
  - Write: $1.25 per million requests
  - Storage: $0.25 per GB-month
- For predictable workloads, consider Provisioned Capacity

### Monitoring Costs

```bash
# Check DynamoDB usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=government_schemes \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T23:59:59Z \
  --period 86400 \
  --statistics Sum
```

## Security Best Practices

1. **Never hardcode credentials**: Use IAM roles
2. **Restrict security group**: Limit SSH to your IP
3. **Keep system updated**: Regular `yum update`
4. **Use HTTPS**: Add SSL/TLS certificate (use AWS Certificate Manager + Application Load Balancer)
5. **Enable CloudWatch logs**: Monitor application behavior
6. **Regular backups**: Enable DynamoDB point-in-time recovery
7. **Use VPC**: Deploy in private subnet with NAT gateway

## Production Enhancements

### Add Application Load Balancer

For HTTPS and better availability:

```bash
# Create target group
aws elbv2 create-target-group \
  --name janmitra-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxxxxxxx \
  --health-check-path /health

# Create load balancer
aws elbv2 create-load-balancer \
  --name janmitra-alb \
  --subnets subnet-xxxxxxxx subnet-yyyyyyyy \
  --security-groups sg-xxxxxxxxx
```

### Enable DynamoDB Backups

```bash
aws dynamodb update-continuous-backups \
  --table-name government_schemes \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true
```

### Set Up CloudWatch Alarms

```bash
# CPU utilization alarm
aws cloudwatch put-metric-alarm \
  --alarm-name janmitra-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=InstanceId,Value=i-xxxxxxxxx \
  --evaluation-periods 2
```

## Summary

You now have a production-ready deployment of JanMitra AI Phase 1 Backend on AWS with:

✓ EC2 t3.micro instance running the FastAPI application
✓ IAM role-based authentication (no hardcoded credentials)
✓ DynamoDB table storing 5 government schemes
✓ Security group allowing HTTP traffic on port 8000
✓ Systemd service for automatic startup and restart
✓ Structured logging via journald

**Next Steps**:
- Set up monitoring and alerting
- Configure HTTPS with SSL/TLS
- Implement CI/CD pipeline
- Add rate limiting and API authentication
- Scale horizontally with Auto Scaling Groups

For support, refer to the main README.md or contact the development team.
