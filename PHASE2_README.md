# JanMitra AI - Phase 2: Voice Transcription

## ✅ Phase 2 Complete

Voice-first eligibility checking is now implemented!

## What's New in Phase 2

### Voice Input Flow
```
User speaks → Audio recorded → Uploaded to backend → 
S3 storage → Amazon Transcribe → Text transcript → 
Parser extracts data → Eligibility evaluation → Results
```

### New Endpoints

**1. POST /upload-audio**
- Upload audio file (.wav, .mp3, .m4a, .webm)
- Transcribe speech to text
- Parse into structured profile
- Evaluate eligibility
- Return complete results

**2. POST /transcribe-only**
- Upload audio file
- Transcribe speech to text only
- Useful for testing transcription accuracy

## Quick Start

### 1. AWS Setup

```bash
# Create S3 bucket
aws s3 mb s3://janmitra-audio-files --region ap-south-1

# Apply IAM policy (see docs/iam-policy-phase2.json)
aws iam put-role-policy \
  --role-name JanMitraEC2Role \
  --policy-name Phase2Policy \
  --policy-document file://docs/iam-policy-phase2.json
```

### 2. Update Environment

```bash
# Add to .env
S3_AUDIO_BUCKET=janmitra-audio-files
```

### 3. Test Locally

```bash
# Start backend
python main.py

# Test with curl
curl -X POST http://localhost:8000/upload-audio \
  -F "audio=@test-audio.wav"
```

## New Files Added

### Backend Services
- `services/transcribe_service.py` - Amazon Transcribe integration
- `services/audio_parser.py` - Speech-to-structured-data parser
- `routes/voice.py` - Voice API endpoints

### Documentation
- `docs/PHASE2_VOICE_SETUP.md` - Complete setup guide
- `docs/PHASE2_TESTING.md` - Testing guide with examples
- `docs/iam-policy-phase2.json` - IAM permissions

### Configuration
- Updated `models/config.py` - Added S3 bucket config
- Updated `.env.example` - Added S3_AUDIO_BUCKET
- Updated `main.py` - Registered voice routes

## How It Works

### 1. Audio Upload
```python
# User uploads audio file
POST /upload-audio
Content-Type: multipart/form-data
Body: audio file
```

### 2. Transcription
```python
# Backend process:
1. Validate file (type, size)
2. Upload to S3
3. Start Transcribe job
4. Poll until complete (max 5 min)
5. Fetch transcript from S3
```

### 3. Parsing
```python
# Extract structured data from transcript
Input: "I am a 52 year old farmer from Tamil Nadu. My income is 3 lakh."

Output: {
  "age": 52,
  "occupation": "farmer",
  "state": "Tamil Nadu",
  "income": 300000
}
```

### 4. Evaluation
```python
# Run eligibility rules
# Return ranked results
```

## Supported Keywords

### States
- All 28 Indian states
- Common abbreviations (TN, UP, MP, etc.)
- Variations (Tamil Nadu, Tamilnadu)

### Occupations
- farmer, farming, agriculture
- student, studying
- business, businessman
- teacher, doctor, engineer
- worker, labour
- self-employed, unemployed

### Categories
- General, Gen
- OBC, Other Backward Class
- SC, Scheduled Caste
- ST, Scheduled Tribe
- EWS, Economically Weaker Section

### Numbers
- Age: "52 years old", "age is 52"
- Income: "3 lakh", "300000", "3 lakhs"
- Land: "2 hectares", "2 acres"

## Example Requests

### Complete Profile

**Audio**: "I am Rajesh Kumar, a 52 year old farmer from Tamil Nadu. My income is 3 lakh rupees."

**Response**:
```json
{
  "success": true,
  "transcript": "I am Rajesh Kumar, a 52 year old farmer from Tamil Nadu. My income is 3 lakh rupees.",
  "extracted_data": {
    "name": "Rajesh Kumar",
    "age": 52,
    "occupation": "farmer",
    "state": "Tamil Nadu",
    "income": 300000,
    "category": null,
    "land_size": 0
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

### Partial Profile

**Audio**: "I am a student from Kerala."

**Response**:
```json
{
  "success": true,
  "transcript": "I am a student from Kerala.",
  "extracted_data": {
    "occupation": "student",
    "state": "Kerala",
    "age": 0,
    "income": 0,
    "land_size": 0
  },
  "eligibility_results": [...],
  "message": "Audio processed successfully"
}
```

## Audio Requirements

- **Formats**: .wav, .mp3, .m4a, .webm
- **Max size**: 10MB
- **Max duration**: ~5 minutes
- **Language**: English (Indian accent)
- **Quality**: Clear speech, minimal background noise

## Performance

- **Upload**: ~1 second
- **Transcription**: 10-30 seconds (depends on audio length)
- **Parsing**: <1 second
- **Evaluation**: <1 second
- **Total**: 15-35 seconds typical

## Error Handling

### Unsupported File Type
```json
{
  "detail": "Unsupported file type. Allowed: .wav, .mp3, .m4a, .webm"
}
```

### File Too Large
```json
{
  "detail": "File too large. Maximum size: 10MB"
}
```

### Transcription Failed
```json
{
  "detail": "Audio processing failed: Transcription failed: [reason]"
}
```

### Timeout
```json
{
  "detail": "Audio processing failed: Transcription timeout after 300 seconds"
}
```

## Testing

### Test with Sample Audio

```bash
# Record test audio or use text-to-speech
# Test transcription only
curl -X POST http://localhost:8000/transcribe-only \
  -F "audio=@sample.wav"

# Test full flow
curl -X POST http://localhost:8000/upload-audio \
  -F "audio=@sample.wav"
```

### Test with Postman

1. Create POST request to `/upload-audio`
2. Body → form-data
3. Key: `audio`, Type: File
4. Select audio file
5. Send

See `docs/PHASE2_TESTING.md` for comprehensive testing guide.

## Cost Estimation

### Per Request
- Transcribe: $0.024 per minute
- S3 storage: ~$0.0002 (with 7-day lifecycle)
- Data transfer: ~$0.001
- **Total**: ~$0.025 per request (1-minute audio)

### Monthly (1000 users/day)
- Transcribe: ~$720
- S3: ~$6
- Data transfer: ~$30
- **Total**: ~$756/month

## Security

- ✅ IAM role-based authentication
- ✅ No hardcoded credentials
- ✅ Audio files deleted after transcription
- ✅ S3 bucket with restricted access
- ✅ Lifecycle policies for cleanup
- ✅ Structured logging for audit

## Monitoring

### CloudWatch Metrics
- Transcribe job success rate
- Transcribe job duration
- S3 upload errors
- API response times

### Application Logs
- Transcription start/complete
- Parsing results
- Evaluation results
- Error details

## Troubleshooting

### Transcription Inaccurate
- Use better quality audio
- Reduce background noise
- Speak clearly and slowly
- Use supported keywords

### Parser Misses Fields
- Check transcript text
- Use exact phrases
- Add more keywords to parser
- Improve audio quality

### Slow Performance
- Use shorter audio
- Use .wav format
- Check AWS region
- Optimize polling interval

See `docs/PHASE2_VOICE_SETUP.md` for detailed troubleshooting.

## Frontend Integration

The frontend already has VoiceInput component that:
1. Records audio using MediaRecorder API
2. Uploads to `/upload-audio` endpoint
3. Receives transcript and extracted data
4. Auto-fills form fields
5. Shows success/error messages

No frontend changes needed - it's ready to use!

## Next Steps

### Phase 3 (Future)
- Add regional language support (Hindi, Tamil, etc.)
- Improve parser with ML models
- Add caching for repeated queries
- Implement streaming transcription
- Add voice feedback (text-to-speech)

### Optimization
- Reduce transcription time
- Improve parsing accuracy
- Add more keywords
- Better error messages
- Performance monitoring

## Documentation

- **Setup**: `docs/PHASE2_VOICE_SETUP.md`
- **Testing**: `docs/PHASE2_TESTING.md`
- **IAM Policy**: `docs/iam-policy-phase2.json`
- **API Docs**: FastAPI auto-docs at `/docs`

## Support

For issues:
1. Check logs: `sudo journalctl -u janmitra-backend -f`
2. Verify S3 bucket: `aws s3 ls s3://janmitra-audio-files`
3. Check IAM permissions
4. Review documentation
5. Test with sample audio

## Summary

Phase 2 adds complete voice transcription capability:
- ✅ Audio upload endpoint
- ✅ Amazon Transcribe integration
- ✅ Speech-to-structured-data parser
- ✅ Eligibility evaluation
- ✅ Error handling
- ✅ Documentation
- ✅ Testing guide
- ✅ IAM policies
- ✅ Frontend ready

**Status**: Production-ready for hackathon demo! 🚀
