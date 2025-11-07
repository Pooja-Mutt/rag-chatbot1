# AWS Deployment Guide

## Option 1: AWS Elastic Beanstalk (Recommended - Easiest)

### Prerequisites
- AWS Account
- AWS CLI installed and configured
- EB CLI installed: `pip install awsebcli`

### Steps

1. **Initialize Elastic Beanstalk:**
   ```bash
   eb init -p python-3.13 workingagent --region us-east-1
   ```

2. **Create application:**
   ```bash
   eb create workingagent-env
   ```

3. **Set environment variables:**
   ```bash
   eb setenv OPENAI_API_KEY=your_key_here OPENAI_MODEL=gpt-4o-mini
   ```

4. **Deploy:**
   ```bash
   eb deploy
   ```

5. **Open application:**
   ```bash
   eb open
   ```

### Configuration Files

Create `.ebextensions/python.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: backend.main:app
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: static
```

---

## Option 2: AWS EC2 (More Control)

### Steps

1. **Launch EC2 Instance:**
   - Choose Ubuntu 22.04 LTS
   - t2.micro (free tier) or t3.small
   - Configure security group: Allow ports 22, 8000, 8080

2. **SSH into instance:**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install -y python3.13 python3.13-venv git
   ```

4. **Clone and setup:**
   ```bash
   git clone https://github.com/your-username/workingagent.git
   cd workingagent
   python3.13 -m venv venv
   source venv/bin/activate
   pip install -e ".[dev]"
   ```

5. **Set environment variables:**
   ```bash
   echo "OPENAI_API_KEY=your_key" > .env
   echo "OPENAI_MODEL=gpt-4o-mini" >> .env
   ```

6. **Run with systemd (create `/etc/systemd/system/workingagent.service`):**
   ```ini
   [Unit]
   Description=workingAgent RAG Chatbot
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/workingagent
   Environment="PATH=/home/ubuntu/workingagent/venv/bin"
   ExecStart=/home/ubuntu/workingagent/venv/bin/python run.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

7. **Start service:**
   ```bash
   sudo systemctl enable workingagent
   sudo systemctl start workingagent
   ```

8. **Setup Nginx reverse proxy (optional):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

---

## Option 3: AWS Lambda + API Gateway (Serverless)

### Setup

1. **Install Mangum:**
   ```bash
   pip install mangum
   ```

2. **Modify `backend/main.py`:**
   ```python
   from mangum import Mangum
   
   # ... existing code ...
   
   handler = Mangum(app)
   ```

3. **Package and deploy using AWS SAM or Serverless Framework**

---

## Option 4: AWS ECS/Fargate (Containerized)

### Steps

1. **Build and push Docker image:**
   ```bash
   docker build -t workingagent .
   docker tag workingagent:latest your-account.dkr.ecr.us-east-1.amazonaws.com/workingagent:latest
   docker push your-account.dkr.ecr.us-east-1.amazonaws.com/workingagent:latest
   ```

2. **Create ECS task definition and service**

3. **Configure Application Load Balancer**

---

## Environment Variables

Set these in your AWS environment:
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Model to use (default: gpt-4o-mini)

## Security Best Practices

1. **Never commit `.env` file**
2. **Use AWS Secrets Manager for API keys:**
   ```python
   import boto3
   client = boto3.client('secretsmanager')
   secret = client.get_secret_value(SecretId='openai-api-key')
   ```

3. **Enable HTTPS with AWS Certificate Manager**
4. **Use IAM roles instead of access keys**
5. **Enable CloudWatch logging**

## Monitoring

- **CloudWatch Logs:** Application logs
- **CloudWatch Metrics:** CPU, memory, request count
- **CloudWatch Alarms:** Set up alerts for errors

## Cost Estimation

- **EC2 t3.small:** ~$15/month
- **Elastic Beanstalk:** ~$0 (only pay for EC2)
- **Lambda:** Pay per request (very cheap for low traffic)
- **ECS Fargate:** ~$30-50/month

## Recommended: Elastic Beanstalk

Easiest to set up, automatic scaling, built-in monitoring, and free (only pay for EC2).

