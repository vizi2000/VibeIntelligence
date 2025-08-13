const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ 
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    defaultViewport: { width: 1280, height: 800 }
  });
  
  try {
    const page = await browser.newPage();
    
    console.log('🧪 Testing Full Scan Flow\n');
    
    // Enable request interception to monitor API calls
    await page.setRequestInterception(true);
    
    const apiCalls = [];
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        apiCalls.push({
          method: request.method(),
          url: request.url(),
          timestamp: new Date().toISOString()
        });
      }
      request.continue();
    });
    
    // Navigate to projects page
    console.log('1️⃣ Navigating to Projects page...');
    await page.goto('http://localhost:3101/projects', {
      waitUntil: 'networkidle2'
    });
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Clear API calls from initial load
    apiCalls.length = 0;
    
    // Click scan button
    console.log('\n2️⃣ Clicking scan button...');
    const scanStarted = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const scanButton = buttons.find(btn => btn.textContent.includes('Scan'));
      if (scanButton) {
        scanButton.click();
        return true;
      }
      return false;
    });
    
    if (!scanStarted) {
      console.log('❌ Could not find scan button');
      return;
    }
    
    // Monitor for 20 seconds
    console.log('\n3️⃣ Monitoring scan progress...');
    
    for (let i = 0; i < 20; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Check for API calls
      const recentCalls = apiCalls.filter(call => 
        new Date() - new Date(call.timestamp) < 1100
      );
      
      if (recentCalls.length > 0) {
        recentCalls.forEach(call => {
          console.log(`   API: ${call.method} ${call.url.replace('http://localhost:3101', '')}`);
        });
      }
      
      // Check for UI changes
      const uiState = await page.evaluate(() => {
        const toasts = document.querySelectorAll('[role="status"]');
        const spinners = document.querySelectorAll('[class*="animate-spin"]');
        const buttons = Array.from(document.querySelectorAll('button'));
        const scanningButtons = buttons.filter(btn => btn.textContent.includes('Scanning'));
        
        return {
          toasts: Array.from(toasts).map(t => t.textContent),
          hasSpinners: spinners.length > 0,
          scanningButtonCount: scanningButtons.length
        };
      });
      
      if (uiState.toasts.length > 0) {
        uiState.toasts.forEach(toast => {
          console.log(`   📢 Toast: ${toast}`);
        });
      }
      
      if (uiState.scanningButtonCount > 0) {
        console.log(`   ⏳ ${uiState.scanningButtonCount} buttons showing "Scanning..."`);
      }
    }
    
    // Final check
    console.log('\n4️⃣ Final state check...');
    
    // Get project data
    const projectData = await page.evaluate(() => {
      const projectElements = document.querySelectorAll('.space-y-2 > div');
      const firstProject = projectElements[0];
      
      if (firstProject) {
        const healthScore = firstProject.querySelector('span')?.textContent || '';
        return {
          found: true,
          healthScore
        };
      }
      return { found: false };
    });
    
    console.log('Project data:', projectData);
    
    // Check if projects were refreshed
    const finalApiCalls = apiCalls.filter(call => call.url.includes('/projects'));
    console.log(`\n📊 Total API calls to /projects: ${finalApiCalls.length}`);
    
    await page.screenshot({ path: 'full_scan_flow.png', fullPage: true });
    console.log('\n📸 Screenshot saved');
    
    console.log('\n🔍 Keeping browser open for inspection...');
    await new Promise(resolve => setTimeout(resolve, 30000));
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
})();