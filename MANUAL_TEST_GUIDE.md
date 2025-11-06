# Manual Test Guide - Upload & Download Flow

## Test the Live Space

🌐 **Space URL**: https://huggingface.co/spaces/zxc1232/koreantoenglish

## Test Steps

### 1. Navigate to Space
- Open the Space URL in your browser
- Wait for the interface to load

### 2. Upload Test Video
- **Option A**: Use the test video at `testsprite_tests/assets/sample.mp4` (3.6 KB)
- **Option B**: Upload any Korean video/audio file
- Click "Choose File" or drag & drop the file
- Wait for upload to complete (you should see "✅ Upload complete" message)

### 3. Verify Auto-Processing
- After upload completes, processing should **auto-start** (no need to click "Process")
- You should see progress updates in the progress bar

### 4. Check SRT Download (Early Return)
- **SRT file should appear FIRST** (before video is ready)
- Look for: "📄 SRT Subtitle File (for CapCut) ✅ Ready"
- Click the download button to download the SRT file
- Verify the file:
  - Opens in a text editor
  - Contains Korean and English subtitles
  - Has proper timestamps (HH:MM:SS,mmm format)
  - Uses UTF-8 encoding (no BOM)

### 5. Check Video Download (After Processing)
- Wait for video processing to complete
- Look for: "🎬 Video with Burned-in Subtitles (Korean + English) ✅"
- Click the download button to download the video
- Verify the video:
  - Plays correctly
  - Has Korean subtitles on top (light blue/white)
  - Has English subtitles below (white)
  - Both subtitles are readable and properly positioned

### 6. Check Text Outputs
- **Korean Transcription** tab: Should show Korean text
- **English Translation** tab: Should show English translation

## Expected Behavior

✅ **SRT appears immediately** after translation completes (don't wait for video)  
✅ **Video appears later** after burn-in completes  
✅ **Processing continues** even if you close the tab (server-side queue)  
✅ **No connection timeout** on mobile when switching apps  

## Troubleshooting

### SRT doesn't appear
- Check browser console for errors
- Verify Papago API credentials are set in Space Secrets
- Check Space logs for errors

### Video doesn't appear
- Check if input was actually a video file (not audio)
- Verify FFmpeg is working (check Space logs)
- Check video file size (very large files may timeout)

### Connection timeout
- Ensure queue is enabled (should be automatic)
- Try refreshing the page - job may have completed server-side
- Check Space logs to see if processing completed

## Test Checklist

- [ ] Space loads successfully
- [ ] File upload works
- [ ] Upload completion message appears
- [ ] Processing auto-starts after upload
- [ ] SRT file appears and is downloadable
- [ ] SRT file opens correctly in text editor
- [ ] SRT file has proper format (timestamps, Korean + English)
- [ ] Video appears after processing
- [ ] Video downloads successfully
- [ ] Video plays with subtitles burned in
- [ ] Korean subtitles are on top
- [ ] English subtitles are below
- [ ] Both subtitles are readable
- [ ] Korean transcription text appears
- [ ] English translation text appears

## Quick Test Command

If you have `curl` and a test video:

```bash
# Check Space is accessible
curl -I https://huggingface.co/spaces/zxc1232/koreantoenglish

# Should return HTTP 200
```

