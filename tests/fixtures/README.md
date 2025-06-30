# OCR Debug Fixtures

This directory contains test images and data for debugging the OCR pipeline.

## Usage

### 1. Place Test Images
Add bet slip images here for testing:
- `clean-slip.png` - A known-good bet slip image for testing
- `problematic-slip.png` - A bet slip that's causing OCR issues
- `low-quality-slip.png` - A low-quality image to test fallback behavior

### 2. Run Debug Script
```bash
node debug-ocr.js
```

This will:
- Load the test image from `tests/fixtures/clean-slip.png`
- Run OCR with debug mode enabled
- Save debug artifacts to the `debug/` directory
- Display detailed results in the console

### 3. Check Debug Output
After running the debug script, check the `debug/` directory for:
- `raw.png` - The original uploaded image
- `preprocessed.png` - The image after preprocessing
- `tesseract.json` - Full Tesseract output with confidence scores

### 4. Analyze Results
Compare the images to see where text is being lost:
- If `raw.png` shows text but `preprocessed.png` doesn't → preprocessing issue
- If `preprocessed.png` shows text but `tesseract.json` is empty → Tesseract issue
- If `tesseract.json` has low confidence → image quality or parameter issue

## Debug Commands

### Discord Command with Debug
Use the `/pick` command with debug mode enabled:
```
/pick channel_type:vip_plays image:[your_image] debug:true
```

### Local Testing
```bash
# Test with a specific image
node debug-ocr.js

# Or run the full test suite
npm test
```

## Expected Results

A successful OCR should show:
- Confidence > 70%
- Extracted lines containing team names and odds
- No fallback to Google Vision needed
- Clear text in preprocessed image

## Troubleshooting

### Low Confidence Issues
1. Check if the crop region is correct
2. Adjust preprocessing parameters
3. Try different threshold values
4. Verify image quality

### No Text Extracted
1. Check if the image contains text
2. Verify the crop region includes the bet area
3. Try without cropping
4. Check Tesseract parameters

### Fallback Triggered
1. Check Google Vision credentials
2. Verify image format is supported
3. Check API quotas and limits 