#!/usr/bin/env node

import axios from 'axios';

const HEALTH_URL = process.env.HEALTH_URL || 'http://localhost:3000/health';

async function checkHealth() {
  try {
    console.log('🏥 Checking bot health...');
    console.log(`URL: ${HEALTH_URL}`);
    
    const response = await axios.get(HEALTH_URL, {
      timeout: 5000
    });
    
    if (response.status === 200) {
      const data = response.data;
      console.log('✅ Bot is healthy!');
      console.log(`Status: ${data.status}`);
      console.log(`Uptime: ${data.uptime}s`);
      console.log(`Memory: ${Math.round(data.memory.heapUsed / 1024 / 1024)}MB`);
      console.log(`Version: ${data.version}`);
      return true;
    } else {
      console.log(`❌ Health check failed: ${response.status}`);
      return false;
    }
    
  } catch (error) {
    console.log('❌ Health check failed:', error.message);
    return false;
  }
}

// Run health check
checkHealth().then(success => {
  process.exit(success ? 0 : 1);
}); 