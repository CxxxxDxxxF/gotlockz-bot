/**
 * Standalone OCR Debug Script
 * Run this to test OCR on a known-good bet slip image
 */

import fs from 'fs';
import path from 'path';
import { parseImage } from './src/services/ocrParser.js';

async function debugOCR() {
  try {
    console.log('🔍 Starting OCR Debug Test...\n');
    
    // Check if test image exists
    const testImagePath = 'tests/fixtures/clean-slip.png';
    if (!fs.existsSync(testImagePath)) {
      console.log('❌ Test image not found. Please place a bet slip image at: tests/fixtures/clean-slip.png');
      console.log('   Or update the path in this script to point to your test image.\n');
      return;
    }
    
    // Read the test image
    console.log(`📸 Loading test image: ${testImagePath}`);
    const imageBuffer = fs.readFileSync(testImagePath);
    console.log(`📏 Image size: ${imageBuffer.length} bytes\n`);
    
    // Run OCR with debug mode enabled
    console.log('🚀 Running OCR with debug mode...');
    const result = await parseImage(imageBuffer, true);
    
    // Display results
    console.log('\n📊 OCR Results:');
    console.log(`✅ Confidence: ${result.confidence.toFixed(1)}%`);
    console.log(`📝 Lines found: ${result.lines.length}`);
    console.log(`🔧 Used fallback: ${result.usedFallback ? 'Yes' : 'No'}`);
    
    if (result.debug) {
      console.log('\n📁 Debug files saved:');
      console.log(`   Raw image: ${result.debug.rawImagePath}`);
      console.log(`   Preprocessed: ${result.debug.preprocessedImagePath}`);
      console.log(`   Tesseract output: ${result.debug.tesseractOutputPath}`);
      if (result.debug.cropRegion) {
        console.log(`   Crop region: ${result.debug.cropRegion.x},${result.debug.cropRegion.y} ${result.debug.cropRegion.w}x${result.debug.cropRegion.h}`);
      }
    }
    
    console.log('\n📝 Extracted text:');
    if (result.lines.length > 0) {
      result.lines.forEach((line, index) => {
        console.log(`   ${index + 1}. ${line}`);
      });
    } else {
      console.log('   ❌ No text extracted');
    }
    
    console.log('\n📄 Raw Tesseract text:');
    console.log(result.rawText || '   ❌ No raw text');
    
    console.log('\n✅ Debug test completed!');
    console.log('📁 Check the debug/ directory for saved images and data.');
    
  } catch (error) {
    console.error('❌ Debug test failed:', error);
  }
}

// Run the debug test
debugOCR().catch(console.error); 