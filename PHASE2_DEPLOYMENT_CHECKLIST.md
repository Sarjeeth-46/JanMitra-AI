# Phase 2 Deployment Checklist

Complete checklist for deploying voice transcription feature.

## Pre-Deployment

### AWS Setup
- [ ] S3 bucket created: `janmitra-audio-files`
- [ ] S3 bucket in correct region: `ap-south-1`
- [ ] S3 lifecycle policy configured (7-day deletion)
- [ ] IAM policy created with Transcribe permissions
- [ ] IAM policy attached to EC2 role
- [ ] Transcribe service available in region
- [ ] CloudWatch logging enabled

### Code Deployment
- [ ] New files added to repository:
  - [ ] `services/transcribe_service.py`
  - [ ] `services/audio_parser.py`
  - [ ] `routes/voice.py`
- [ ] Configuration updated:
  - [ ] `models/config.py` (S3_AUDIO_BUCKET)
  - [ ] `.env.example` (S3_AUDIO_BUCKET)
  - [ ] `main.py` (voice routes registered)
- [ ] Documentation added:
  - [ ] `docs/PHASE2_VOICE_SETUP.md`
  - [ ] `docs/PHASE2_TESTING.md`
  - [ ] `docs/iam-policy-phase2.json`
  - [ ] `PHASE2_README.md`

## Deployment Steps

### 1. Update EC2 Instance

```bash
# SSH to EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# Navigate to project
cd /home/ec2-user/janmitra-backend

# Pull latest code
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install dependencies (boto3 already in requirements.txt)
pip install -r requirements.txt

# Update .env file
nano .env
# Add: S3_AUDIO_BUCKET=janmitra-audio-files

# Restart service
sudo systemctl restart janmitra-backend

# Check status
sudo systemctl status janmitra-backend
```

- [ ] Code pulled from repository
- [ ] Dependencies installed
- [ ] Environment variables updated
- [ ] Service restarted successfully
- [ ] No errors in logs

### 2. Verify AWS Permissions

```bash
# Test S3 access
aws s3 ls s3://janmitra-audio-files

# Test Transcribe access
aws transcribe list-transcription-jobs --max-results 1

# Check IAM role
aws sts get-caller-identity
```

- [ ] S3 bucket accessible
- [ ] Transcribe service accessible
- [ ] IAM role attached to EC2
- [ ] Permissions verified

### 3. Test Endpoints

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test transcribe-only with sample audio
curl -X POST http://localhost:8000/transcribe-only \
  -F "audio=@sample.wav"

# Test full upload-audio flow
curl -X POST http://localhost:8000/upload-audio \
  -F "audio=@sample.wav"
```

- [ ] Health endpoint responds
- [ ] Transcribe-only works
- [ ] Upload-audio works
- [ ] Response format correct
- [ ] Parsing extracts data
- [ ] Eligibility evaluation runs

## Post-Deployment Testing

### Functional Tests
- [ ] Upload .wav file - works
- [ ] Upload .mp3 file - works
- [ ] Upload .m4a file - works
- [ ] Upload .webm file - works
- [ ] Upload invalid file type - returns 400 error
- [ ] Upload file >10MB - returns 400 error
- [ ] Transcription completes successfully
- [ ] Parser extracts age correctly
- [ ] Parser extracts income correctly
- [ ] Parser extracts state correctly
- [ ] Parser extracts occupation correctly
- [ ] Eligibility evaluation runs
- [ ] Results returned in correct format

### Performance Tests
- [ ] Transcription completes in <35 seconds
- [ ] No timeout errors
- [ ] S3 upload is fast (<2 seconds)
- [ ] Parsing is fast (<1 second)

### Error Handling Tests
- [ ] Invalid file type handled
- [ ] File too large handled
- [ ] Transcription failure handled
- [ ] Timeout handled gracefully
- [ ] Error messages are clear

### Integration Tests
- [ ] Frontend voice input works
- [ ] Audio uploads from frontend
- [ ] Form auto-fills with extracted data
- [ ] Error messages display in frontend
- [ ] Loading states work correctly

## Monitoring Setup

### CloudWatch
- [ ] Log group created: `/aws/janmitra/transcribe`
- [ ] Metrics dashboard created
- [ ] Alarms configured:
  - [ ] High error rate
  - [ ] Slow transcription
  - [ ] S3 upload failures

### Application Logs
- [ ] Structured logging working
- [ ] Transcription events logged
- [ ] Parsing results logged
- [ ] Errors logged with details

## Security Verification

- [ ] No AWS credentials in code
- [ ] IAM role used (not access keys)
- [ ] S3 bucket not publicly accessible
- [ ] Audio files deleted after transcription
- [ ] Lifecycle policy active
- [ ] HTTPS enabled (production)
- [ ] CORS configured correctly

## Documentation

- [ ] README updated with Phase 2 info
- [ ] API documentation updated
- [ ] Setup guide available
- [ ] Testing guide available
- [ ] Troubleshooting guide available
- [ ] Team trained on new feature

## Rollback Plan

If issues occur:

```bash
# Revert to Phase 1
git checkout <previous-commit>
pip install -r requirements.txt
sudo systemctl restart janmitra-backend

# Or disable voice routes
# Comment out in main.py:
# app.include_router(voice.router)
```

- [ ] Rollback procedure documented
- [ ] Previous version tagged in git
- [ ] Rollback tested

## Production Checklist

### Before Going Live
- [ ] All tests passing
- [ ] Performance acceptable
- [ ] Error handling robust
- [ ] Monitoring in place
- [ ] Documentation complete
- [ ] Team trained
- [ ] Rollback plan ready

### Launch
- [ ] Deploy to production
- [ ] Verify all endpoints
- [ ] Monitor for errors
- [ ] Check performance metrics
- [ ] Verify S3 cleanup working

### Post-Launch
- [ ] Monitor for 24 hours
- [ ] Check error rates
- [ ] Review user feedback
- [ ] Optimize if needed
- [ ] Document lessons learned

## Cost Monitoring

- [ ] CloudWatch billing alarm set
- [ ] S3 storage monitored
- [ ] Transcribe usage tracked
- [ ] Cost within budget

## Success Criteria

Phase 2 deployment is successful when:

- [ ] All endpoints responding
- [ ] Transcription accuracy >80%
- [ ] Response time <35 seconds
- [ ] Error rate <5%
- [ ] No security issues
- [ ] Monitoring working
- [ ] Documentation complete
- [ ] Team can support feature

## Sign-Off

- [ ] Development team: _______________
- [ ] QA team: _______________
- [ ] DevOps team: _______________
- [ ] Product owner: _______________

Date: _______________

## Notes

Additional notes or issues encountered:

---

## Quick Commands Reference

### Check Service Status
```bash
sudo systemctl status janmitra-backend
sudo journalctl -u janmitra-backend -f
```

### Test Endpoints
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/upload-audio -F "audio=@test.wav"
```

### Check S3
```bash
aws s3 ls s3://janmitra-audio-files/audio/
aws s3 ls s3://janmitra-audio-files/transcripts/
```

### Check Transcribe Jobs
```bash
aws transcribe list-transcription-jobs --max-results 10
```

### View Logs
```bash
tail -f /var/log/janmitra-backend.log
sudo journalctl -u janmitra-backend --since "10 minutes ago"
```
