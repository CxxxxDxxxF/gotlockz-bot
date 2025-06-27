#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import Ajv from 'ajv';
import addFormats from 'ajv-formats';

// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Initialize AJV with formats support
const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

// Sample messages for validation
const sampleMessages = {
  'vip-play': {
    type: 'VIP Play',
    number: 1,
    sport: 'MLB',
    teams: 'Yankees vs Red Sox',
    pick: 'Yankees ML',
    odds: '-110',
    units: 2.5,
    reasoning: 'Strong pitching matchup favors the Yankees. Recent form shows they perform well in this stadium.',
    weather: {
      temperature: 72,
      conditions: 'Clear',
      windSpeed: 8,
      humidity: 65
    },
    timestamp: new Date().toISOString()
  },
  'free-play': {
    type: 'Free Play',
    sport: 'NBA',
    teams: 'Lakers vs Warriors',
    pick: 'Over 220.5',
    odds: '-105',
    reasoning: 'Both teams are averaging over 110 points per game. High-scoring matchup expected.',
    weather: {
      temperature: 68,
      conditions: 'Indoor',
      windSpeed: 0,
      humidity: 45
    },
    notes: 'Indoor game, weather not a factor',
    timestamp: new Date().toISOString()
  },
  'lotto-ticket': {
    type: 'Lotto Ticket',
    sport: 'NFL',
    teams: 'Chiefs vs Bills',
    pick: 'Mahomes 300+ passing yards',
    odds: '+180',
    reasoning: 'Mahomes has thrown for 300+ yards in 4 of last 5 games against Bills. High-stakes playoff atmosphere.',
    weather: {
      temperature: 45,
      conditions: 'Partly Cloudy',
      windSpeed: 12,
      humidity: 70
    },
    notes: 'Cold weather but Mahomes performs well in these conditions',
    timestamp: new Date().toISOString()
  }
};

// Load and validate schemas
function validateSchemas() {
  const schemasDir = path.join(__dirname, '..', 'schemas');
  const schemaFiles = fs.readdirSync(schemasDir).filter(file => file.endsWith('.json'));
  
  console.log('🔍 Validating JSON schemas...\n');
  
  let allValid = true;
  
  for (const schemaFile of schemaFiles) {
    const schemaPath = path.join(schemasDir, schemaFile);
    const schemaName = path.basename(schemaFile, '.json');
    
    try {
      // Load schema
      const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
      
      // Compile schema
      const validate = ajv.compile(schema);
      
      console.log(`📋 Testing schema: ${schemaName}`);
      
      // Test with sample message
      const sampleMessage = sampleMessages[schemaName.replace('-', '-')];
      if (sampleMessage) {
        const isValid = validate(sampleMessage);
        
        if (isValid) {
          console.log(`  ✅ Sample message validates successfully`);
        } else {
          console.log(`  ❌ Sample message validation failed:`);
          console.log(`     ${JSON.stringify(validate.errors, null, 2)}`);
          allValid = false;
        }
      } else {
        console.log(`  ⚠️  No sample message found for ${schemaName}`);
      }
      
      // Test schema itself is valid JSON Schema
      const metaValidate = ajv.compile({
        $schema: "http://json-schema.org/draft-07/schema#",
        type: "object"
      });
      
      if (metaValidate(schema)) {
        console.log(`  ✅ Schema structure is valid`);
      } else {
        console.log(`  ❌ Schema structure is invalid`);
        allValid = false;
      }
      
    } catch (error) {
      console.log(`  ❌ Error loading schema ${schemaName}: ${error.message}`);
      allValid = false;
    }
    
    console.log('');
  }
  
  if (allValid) {
    console.log('🎉 All schemas validated successfully!');
    process.exit(0);
  } else {
    console.log('❌ Some schemas failed validation');
    process.exit(1);
  }
}

// Run validation
validateSchemas(); 