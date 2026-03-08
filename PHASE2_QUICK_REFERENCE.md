# Phase 2: Quick Reference Card

## 🚀 Quick Deploy

```bash
# 1. Create S3 bucket
aws s3 mb s3://janmitra-audio-files --region ap-south-1

# 2. Apply IAM policy
aws iam put-role-policy --role-name JanMitraEC2Role \
  --policy-name Phase2Policy \
  --policy-document file://docs/iam-policy-phase2.json

# 3. Update .env
echo "S3_AUDIO_BUCKET=janmitra-audio-files" >> .env

# 4. Restart
sudo systemctl restart janmitra-backend
```

## 📡 API Endpoints

### Upload Audio (Full Flow)
```bash
POST /upload-audio
Content-Type: multipart/form-data
Body: audio file (.wav, .mp3, .m4a, .webm)
Max Size: 10MB
```

### Transcribe Only
```bash
POST /transcribe-only
Content-Type: multipart/form-data
Body: audio file
```

## 🧪 Quick Test

```bash
curl -X POST http://localhost:8000/upload-audio \
  -F "audio=@test.wav"
```

## 📝 Sample Audio Script

```
"I am Rajesh Kumar, a 52 year old farmer from Tamil Nadu. 
My annual income is 3 lakh rupees."
```

## 🎯 Supported Keywords

**States**: Tamil Nadu, Kerala, Punjab, UP, Maharashtra, etc.
**Occupations**: farmer, student, business, teacher, doctor
**Categories**: General, OBC, SC, ST, EWS
**Numbers**: "3 lakh", "52 years old", "2 hectares"

## ⚡ Performance

- Upload: ~1s
- Transcribe: 10-30s
- Parse: <1s
- Total: 15-35s

## 💰 Cost

~$0.025 per request (1-min audio)
~$756/month (1000 users/day)

## 🔧 Troubleshooting

```bash
# Check service
sudo systemctl status janmitra-backend

# View logs
sudo journalctl -u janmitra-backend -f

# Check S3
aws s3 ls s3://janmitra-audio-files/

# Check Transcribe
aws transcribe list-transcription-jobs
```

## 📚 Documentation

- Setup: `docs/PHASE2_VOICE_SETUP.md`
- Testing: `docs/PHASE2_TESTING.md`
- Overview: `PHASE2_README.md`
- Checklist: `PHASE2_DEPLOYMENT_CHECKLIST.md`

## ✅ Success Checklist

- [ ] S3 bucket created
- [ ] IAM policy applied
- [ ] .env updated
- [ ] Service restarted
- [ ] Test endpoint works
- [ ] Frontend integrated

## 🆘 Quick Fixes

**Transcription fails**: Check IAM permissions
**S3 error**: Verify bucket exists and region
**Timeout**: Use shorter audio or increase timeout
**Parser empty**: Check transcript, use keywords

## 📞 Support

1. Check logs
2. Review docs
3. Test with sample audio
4. Verify AWS setup
