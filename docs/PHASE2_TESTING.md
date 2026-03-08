# Phase 2: Voice Testing Guide

Complete testing guide for voice transcription feature.

## Quick Test Commands

### 1. Test Transcription Only

```bash
curl -X POST http://localhost:8000/transcribe-only \
  -F "audio=@sample-audio.wav"
```

### 2. Test Full Voice Flow

```bash
curl -X POST http://localhost:8000/upload-audio \
  -F "audio=@sample-audio.wav"
```

## Sample Audio Scripts

Create test audio files by recording these scripts:

### Script 1: Complete Profile

```
"I am Rajesh Kumar, a 52 year old farmer from Tamil Nadu. 
My annual income is 3 lakh rupees. I belong to the OBC category."
```

**Expected extraction**:
- name: "Rajesh Kumar"
- age: 52
- occupation: "farmer"
- state: "Tamil Nadu"
- income: 300000
- category: "OBC"

### Script 2: Minimal Profile

```
"I am a student from Kerala."
```

**Expected extraction**:
- occupation: "student"
- state: "Kerala"

### Script 3: With Land Size

```
"I am a 45 year old farmer from Punjab with 2 hectares of land. 
My income is 5 lakh per year."
```

**Expected extraction**:
- age: 45
- occupation: "farmer"
- state: "Punjab"
- land_size: 2.0
- income: 500000

### Script 4: Business Owner

```
"My name is Priya Sharma. I am 38 years old and run a small business 
in Maharashtra. My annual income is 8 lakh rupees."
```

**Expected extraction**:
- name: "Priya Sharma"
- age: 38
- occupation: "business"
- state: "Maharashtra"
- income: 800000

## Testing with Postman

### Setup

1. Open Postman
2. Create new collection: "JanMitra Phase 2"
3. Add environment variables:
   - `base_url`: `http://localhost:8000` or `http://your-ec2-ip:8000`

### Test 1: Transcribe Only

**Request**:
- Method: POST
- URL: `{{base_url}}/transcribe-only`
- Body: form-data
  - Key: `audio`
  - Type: File
  - Value: Select audio file

**Expected Response** (200 OK):
```json
{
  "success": true,
  "transcript": "I am a 52 year old farmer from Tamil Nadu..."
}
```

### Test 2: Upload Audio (Full Flow)

**Request**:
- Method: POST
- URL: `{{base_url}}/upload-audio`
- Body: form-data
  - Key: `audio`
  - Type: File
  - Value: Select audio file

**Expected Response** (200 OK):
```json
{
  "success": true,
  "transcript": "I am a 52 year old farmer from Tamil Nadu. My income is 3 lakh.",
  "extracted_data": {
    "name": null,
    "age": 52,
    "income": 300000,
    "state": "Tamil Nadu",
    "occupation": "farmer",
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

### Test 3: Invalid File Type

**Request**:
- Method: POST
- URL: `{{base_url}}/upload-audio`
- Body: form-data
  - Key: `audio`
  - Type: File
  - Value: Select .txt or .pdf file

**Expected Response** (400 Bad Request):
```json
{
  "detail": "Unsupported file type. Allowed: .wav, .mp3, .m4a, .webm"
}
```

### Test 4: File Too Large

**Request**:
- Method: POST
- URL: `{{base_url}}/upload-audio`
- Body: form-data
  - Key: `audio`
  - Type: File
  - Value: Select file >10MB

**Expected Response** (400 Bad Request):
```json
{
  "detail": "File too large. Maximum size: 10MB"
}
```

## Testing with Python

### Test Script

```python
import requests

# Configuration
BASE_URL = "http://localhost:8000"
AUDIO_FILE = "sample-audio.wav"

def test_transcribe_only():
    """Test transcription without parsing"""
    with open(AUDIO_FILE, 'rb') as f:
        files = {'audio': f}
        response = requests.post(
            f"{BASE_URL}/transcribe-only",
            files=files
        )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert 'transcript' in response.json()
    print("✓ Transcribe only test passed")

def test_upload_audio():
    """Test full voice flow"""
    with open(AUDIO_FILE, 'rb') as f:
        files = {'audio': f}
        response = requests.post(
            f"{BASE_URL}/upload-audio",
            files=files
        )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")
    
    assert response.status_code == 200
    assert data['success'] == True
    assert 'transcript' in data
    assert 'extracted_data' in data
    print("✓ Upload audio test passed")

def test_invalid_file():
    """Test with invalid file type"""
    # Create a dummy text file
    with open('test.txt', 'w') as f:
        f.write('test')
    
    with open('test.txt', 'rb') as f:
        files = {'audio': f}
        response = requests.post(
            f"{BASE_URL}/upload-audio",
            files=files
        )
    
    print(f"Status: {response.status_code}")
    assert response.status_code == 400
    print("✓ Invalid file test passed")

if __name__ == "__main__":
    test_transcribe_only()
    test_upload_audio()
    test_invalid_file()
    print("\n✓ All tests passed!")
```

Run tests:
```bash
python test_voice.py
```

## Frontend Integration Testing

### 1. Test Voice Recording

1. Open frontend: `http://localhost:3000/eligibility`
2. Click microphone button
3. Allow microphone access
4. Speak test script
5. Click stop button
6. Verify form auto-fills

### 2. Test Error Handling

1. Record very short audio (<1 second)
2. Verify error message displayed
3. Record with background noise
4. Check transcription accuracy

### 3. Test Different Browsers

Test on:
- Chrome (recommended)
- Firefox
- Safari
- Edge

## Performance Testing

### Test Transcription Speed

```bash
# Time the request
time curl -X POST http://localhost:8000/upload-audio \
  -F "audio=@sample-audio.wav"

# Expected: 15-35 seconds for typical audio
```

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test with 10 concurrent requests
ab -n 10 -c 2 -p audio-data.txt -T multipart/form-data \
  http://localhost:8000/upload-audio
```

## Parsing Accuracy Testing

### Test Different Accents

Record same script with different accents:
1. North Indian accent
2. South Indian accent
3. East Indian accent
4. West Indian accent

Compare transcription accuracy.

### Test Different Speaking Speeds

1. Slow and clear
2. Normal speed
3. Fast speaking

Verify parser handles all speeds.

### Test Background Noise

1. Quiet environment (best)
2. Moderate background noise
3. Noisy environment

Check transcription quality.

## Edge Cases

### Test 1: No Speech

Upload audio with silence only.

**Expected**: Empty transcript or error

### Test 2: Multiple Languages

Mix English with Hindi/Tamil/etc.

**Expected**: Partial transcription

### Test 3: Numbers in Different Formats

- "Three lakh" vs "3 lakh" vs "300000"
- "Two hectares" vs "2 hectares"

**Expected**: All parsed correctly

### Test 4: State Name Variations

- "Tamil Nadu" vs "Tamilnadu" vs "TN"
- "Uttar Pradesh" vs "UP"

**Expected**: All recognized

## Debugging

### Enable Debug Logging

```python
# In transcribe_service.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check S3 Bucket

```bash
# List uploaded files
aws s3 ls s3://janmitra-audio-files/audio/

# List transcripts
aws s3 ls s3://janmitra-audio-files/transcripts/

# Download transcript for inspection
aws s3 cp s3://janmitra-audio-files/transcripts/transcribe-xxx.json .
```

### Check Transcribe Jobs

```bash
# List recent jobs
aws transcribe list-transcription-jobs --max-results 10

# Get job details
aws transcribe get-transcription-job \
  --transcription-job-name transcribe-xxx
```

## Common Issues

### Issue: Transcription is Inaccurate

**Solutions**:
1. Use better quality audio
2. Reduce background noise
3. Speak clearly and slowly
4. Use supported keywords

### Issue: Parser Misses Fields

**Solutions**:
1. Check transcript text
2. Add more keywords to parser
3. Use exact phrases from parser
4. Improve audio quality

### Issue: Slow Transcription

**Solutions**:
1. Use shorter audio
2. Use .wav format
3. Check AWS region latency
4. Optimize polling interval

## Test Checklist

Before deploying to production:

- [ ] Transcription works with .wav files
- [ ] Transcription works with .mp3 files
- [ ] Transcription works with .m4a files
- [ ] Transcription works with .webm files
- [ ] Parser extracts age correctly
- [ ] Parser extracts income correctly
- [ ] Parser extracts state correctly
- [ ] Parser extracts occupation correctly
- [ ] Parser extracts category correctly
- [ ] Parser extracts land size correctly
- [ ] Eligibility evaluation works
- [ ] Error handling works
- [ ] File size validation works
- [ ] File type validation works
- [ ] Frontend integration works
- [ ] Performance is acceptable (<35s)
- [ ] S3 cleanup works
- [ ] IAM permissions are correct
- [ ] Logs are structured
- [ ] Monitoring is set up

## Success Criteria

Phase 2 is successful when:

1. **Accuracy**: >80% transcription accuracy
2. **Speed**: <35 seconds end-to-end
3. **Reliability**: >95% success rate
4. **Usability**: Users can complete profile via voice
5. **Cost**: <$1 per 1000 requests

## Next Steps

After testing:
1. Deploy to staging
2. User acceptance testing
3. Collect feedback
4. Optimize parser
5. Deploy to production
