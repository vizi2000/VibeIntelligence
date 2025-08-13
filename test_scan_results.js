const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ 
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    defaultViewport: { width: 1280, height: 800 }
  });
  
  try {
    const page = await browser.newPage();
    
    console.log('🧪 Testing Scan Results Display\n');
    
    // Navigate to projects page
    console.log('1️⃣ Navigating to Projects page...');
    await page.goto('http://localhost:3101/projects', {
      waitUntil: 'networkidle2'
    });
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Take initial screenshot
    await page.screenshot({ path: 'scan_results_1_before.png' });
    
    // Click scan button
    console.log('\n2️⃣ Starting scan...');
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
    
    // Wait for scan to complete
    console.log('\n3️⃣ Waiting for scan to complete...');
    let scanCompleted = false;
    let attempts = 0;
    
    while (!scanCompleted && attempts < 30) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      attempts++;
      
      // Check for completion toast
      const toasts = await page.evaluate(() => {
        const toastElements = document.querySelectorAll('[role="status"]');
        return Array.from(toastElements).map(t => t.textContent);
      });
      
      const completedToast = toasts.find(t => t.includes('Scan completed!'));
      if (completedToast) {
        scanCompleted = true;
        console.log('✅ Scan completed!');
        console.log('   Toast message:', completedToast);
      }
    }
    
    // Wait a bit more for UI to update
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Take screenshot after scan
    await page.screenshot({ path: 'scan_results_2_after.png' });
    
    // Check for scan results display
    console.log('\n4️⃣ Checking for scan results display...');
    const scanResultsInfo = await page.evaluate(() => {
      // Look for scan results card
      const resultsCard = Array.from(document.querySelectorAll('[class*="Card"]'))
        .find(card => card.textContent.includes('Last Scan Results'));
      
      if (resultsCard) {
        return {
          found: true,
          text: resultsCard.textContent
        };
      }
      
      return { found: false };
    });
    
    if (scanResultsInfo.found) {
      console.log('✅ Scan results displayed!');
      console.log('   Content:', scanResultsInfo.text);
    } else {
      console.log('❌ No scan results display found');
    }
    
    // Check project updates
    console.log('\n5️⃣ Checking if projects were updated...');
    const projectInfo = await page.evaluate(() => {
      const projectCards = document.querySelectorAll('[class*="hover:shadow-lg"]');
      const firstProject = projectCards[0];
      
      if (firstProject) {
        const healthScore = firstProject.textContent.match(/Health: (\d+)%/);
        return {
          found: true,
          healthScore: healthScore ? healthScore[1] : 'Not found'
        };
      }
      
      return { found: false };
    });
    
    console.log('Project info:', projectInfo);
    
    // Keep browser open
    console.log('\n🔍 Browser will stay open for inspection...');
    await new Promise(resolve => setTimeout(resolve, 30000));
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
})();