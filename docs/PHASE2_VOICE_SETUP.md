# Phase 2: Voice Transcription Setup Guide

Complete guide for setting up voice transcription with Amazon Transcribe.

## Overview

Phase 2 adds voice input capability:
1. User records audio in frontend
2. Audio uploaded to backend
3. Backend uploads to S3
4. Amazon Transcribe converts speech → text
5. Parser extracts structured data
6. Eligibility engine evaluates
7. Results returned to frontend

## Prerequisites

- Phase 1 backend deployed and working
- AWS account with appropriate permissions
- IAM role or credentials configured

## AWS Setup

### 1. Create S3 Bucket

```bash
# Create bucket for audio files
aws s3 mb s3://janmitra-audio-files --region ap-south-1

# Enable versioning (optional)
aws s3api put-bucket-versioning \
  --bucket janmitra-audio-files \
  --versioning-configuration Status=Enabled

# Set lifecycle policy to delete old files (optional)
cat > lifecycle-policy.json <<EOF
{
  "Rules": [
    {
      "Id": "DeleteOldAudioFiles",
      "Status": "Enabled",
      "Prefix": "audio/",
      "Expiration": {
        "Days": 7
      }
    },
    {
      "Id": "DeleteOldTranscripts",
      "Status": "Enabled",
      "Prefix": "transcripts/",
      "Expiration": {
        "Days": 30
      }
    }
  ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
  --bucket janmitra-audio-files \
  --lifecycle-configuration file://lifecycle-policy.json
```

### 2. Configure IAM Permissions

Create IAM policy for EC2 instance:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3AudioAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::janmitra-audio-files/*"
    },
    {
      "Sid": "S3BucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::janmitra-audio-files"
    },
    {
      "Sid": "TranscribeAccess",
      "Effect": "Allow",
      "Action": [
        "transcribe:StartTranscriptionJob",
        "transcribe:GetTranscriptionJob",
        "transcribe:DeleteTranscriptionJob"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DynamoDBAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Scan",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:ap-south-1:*:table/government_schemes"
    }
  ]
}
```

Apply policy to EC2 IAM role:

```bash
# Create policy
aws iam create-policy \
  --policy-name JanMitraPhase2Policy \
  --policy-document file://iam-policy.json

# Attach to existing role
aws iam attach-role-policy \
  --role-name JanMitraEC2Role \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/JanMitraPhase2Policy
```

### 3. Configure Environment Variables

Update `.env` file on EC2:

```bash
# AWS Configuration
AWS_REGION=ap-south-1

# S3 Configuration
S3_AUDIO_BUCKET=janmitra-audio-files

# DynamoDB Configuration
DYNAMODB_TABLE_NAME=government_schemes

# API Configuration
API_PORT=8000
```

## Backend Deployment

### 1. Update Code on EC2

```bash
# SSH to EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# Navigate to project
cd /home/ec2-user/janmitra-backend

# Pull latest code
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install dependencies (if any new ones)
pip install -r requirements.txt

# Restart service
sudo systemctl restart janmitra-backend
```

### 2. Verify Services

```bash
# Check service status
sudo systemctl status janmitra-backend

# Check logs
sudo journalctl -u janmitra-backend -f

# Test health endpoint
curl http://localhost:8000/health
```

## Testing

### 1. Test Transcription Only

```bash
# Record a test audio file or use existing one
# Test with curl
curl -X POST http://your-ec2-ip:8000/transcribe-only \
  -F "audio=@test-audio.wav" \
  -H "Content-Type: multipart/form-data"

# Expected response:
{
  "success": true,
  "transcript": "I am a 52 year old farmer from Tamil Nadu..."
}
```

### 2. Test Full Voice Flow

```bash
# Test complete flow with audio upload
curl -X POST http://your-ec2-ip:8000/upload-audio \
  -F "audio=@test-audio.wav" \
  -H "Content-Type: multipart/form-data"

# Expected response:
{
  "success": true,
  "transcript": "I am a 52 year old farmer from Tamil Nadu. My income is 3 lakh.",
  "extracted_data": {
    "age": 52,
    "occupation": "farmer",
    "state": "Tamil Nadu",
    "income": 300000
  },
  "eligibility_results": [
    {
      "scheme_name": "PM-KISAN",
      "eligible": true,
      "missing_fields": [],
      "failed_conditions": []
    }
  ],
  "message": "Audio processed successfully"
}
```

### 3. Test with Postman

1. Open Postman
2. Create new POST request to `http://your-ec2-ip:8000/upload-audio`
3. Go to Body → form-data
4. Add key: `audio`, type: File
5. Select audio file (.wav, .mp3, .m4a, or .webm)
6. Send request
7. Verify response

## Supported Audio Formats

- `.wav` - Recommended for best quality
- `.mp3` - Compressed, good for mobile
- `.m4a` - Apple devices
- `.webm` - Web browsers

## Audio Requirements

- **Max file size**: 10MB
- **Max duration**: ~5 minutes (for 10MB limit)
- **Sample rate**: 8kHz - 48kHz
- **Channels**: Mono or Stereo
- **Language**: English (Indian accent) - `en-IN`

## Transcription Process

1. **Upload** (~1 second)
   - File validated
   - Uploaded to S3

2. **Transcribe** (~10-30 seconds)
   - Job started
   - Polling every 5 seconds
   - Max wait: 5 minutes

3. **Parse** (~1 second)
   - Extract structured data
   - Validate fields

4. **Evaluate** (~1 second)
   - Run eligibility rules
   - Rank results

**Total time**: ~15-35 seconds for typical audio

## Parsing Examples

### Example 1: Complete Profile

**Input**: "I am Rajesh Kumar, 52 years old farmer from Tamil Nadu. My income is 3 lakh per year."

**Parsed**:
```json
{
  "name": "Rajesh Kumar",
  "age": 52,
  "occupation": "farmer",
  "state": "Tamil Nadu",
  "income": 300000
}
```

### Example 2: Partial Profile

**Input**: "I am a student from Kerala."

**Parsed**:
```json
{
  "occupation": "student",
  "state": "Kerala",
  "age": 0,
  "income": 0
}
```

**Note**: Missing fields get default values (0 for numbers, null for strings)

### Example 3: With Land Size

**Input**: "I am a farmer with 2 hectares of land in Punjab. My age is 45."

**Parsed**:
```json
{
  "age": 45,
  "occupation": "farmer",
  "state": "Punjab",
  "land_size": 2.0
}
```

## Troubleshooting

### Issue: Transcription Timeout

**Symptoms**: Request takes >5 minutes, returns timeout error

**Solutions**:
1. Check audio file size (should be <10MB)
2. Check audio format (use .wav for best results)
3. Check AWS Transcribe service status
4. Increase timeout in `transcribe_service.py` if needed

### Issue: S3 Upload Failed

**Symptoms**: "S3 upload failed" error

**Solutions**:
1. Verify S3 bucket exists: `aws s3 ls s3://janmitra-audio-files`
2. Check IAM permissions
3. Verify AWS region matches
4. Check EC2 instance has IAM role attached

### Issue: Transcription Job Failed

**Symptoms**: "Transcription failed" error

**Solutions**:
1. Check audio file format (must be .wav, .mp3, .m4a, or .webm)
2. Check audio file is not corrupted
3. Verify Transcribe has permissions to access S3
4. Check CloudWatch logs for Transcribe errors

### Issue: Parsing Returns Empty Data

**Symptoms**: `extracted_data` is mostly empty

**Solutions**:
1. Check transcript text - may not contain expected keywords
2. Improve audio quality (reduce background noise)
3. Speak clearly and include key information
4. Use supported keywords (see audio_parser.py)

### Issue: No Eligibility Results

**Symptoms**: `eligibility_results` is null

**Solutions**:
1. Ensure `state` and `occupation` are extracted
2. These are minimum required fields
3. Check warning message in response
4. Manually fill missing fields in frontend

## Cost Estimation

### AWS Transcribe
- **Price**: $0.024 per minute (first 250 million minutes)
- **Example**: 1-minute audio = $0.024
- **1000 users/day**: ~$24/day = $720/month

### S3 Storage
- **Price**: $0.023 per GB/month
- **Example**: 10MB audio = $0.00023/month
- **With 7-day lifecycle**: Minimal cost

### Data Transfer
- **Price**: $0.09 per GB (out to internet)
- **Example**: 10MB response = $0.0009
- **1000 users/day**: ~$27/month

**Total estimated cost**: ~$750/month for 1000 users/day

## Optimization Tips

1. **Delete audio after transcription** (already implemented)
2. **Use lifecycle policies** to auto-delete old files
3. **Compress audio** before upload (frontend)
4. **Cache transcripts** if same audio uploaded multiple times
5. **Use shorter audio** (30-60 seconds is enough)

## Security Best Practices

1. **Use IAM roles** (no hardcoded credentials)
2. **Encrypt S3 bucket** (enable default encryption)
3. **Restrict S3 access** (bucket policy)
4. **Enable CloudTrail** (audit logging)
5. **Use VPC endpoints** (avoid internet traffic)
6. **Implement rate limiting** (prevent abuse)

## Monitoring

### CloudWatch Metrics

Monitor these metrics:
- Transcribe job success rate
- Transcribe job duration
- S3 upload errors
- API response times

### Logs

Check these logs:
- Application logs: `/var/log/janmitra-backend.log`
- System logs: `sudo journalctl -u janmitra-backend`
- CloudWatch Logs: Transcribe job logs

## Next Steps

After Phase 2 is working:
1. Test with real users
2. Collect feedback on transcription accuracy
3. Improve parser with more keywords
4. Add support for regional languages
5. Implement caching for better performance
6. Add analytics and monitoring

## Support

For issues:
1. Check application logs
2. Check AWS CloudWatch logs
3. Verify IAM permissions
4. Test with sample audio files
5. Review this documentation
