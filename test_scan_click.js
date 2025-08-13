const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ 
    headless: false, // Show browser
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    defaultViewport: { width: 1280, height: 800 }
  });
  
  try {
    const page = await browser.newPage();
    
    console.log('🧪 Testing Scan Button Click\n');
    
    // Navigate to projects page
    console.log('1️⃣ Navigating to Projects page...');
    await page.goto('http://localhost:3101/projects', {
      waitUntil: 'networkidle2',
      timeout: 15000
    });
    
    // Wait for page to load
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Get all scan buttons
    const scanButtons = await page.$$eval('button', buttons => 
      buttons.filter(btn => btn.textContent.includes('Scan')).length
    );
    
    console.log(`✅ Found ${scanButtons} scan buttons`);
    
    // Click the first project's scan button
    console.log('\n2️⃣ Clicking first scan button...');
    
    // Find and click first scan button
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const firstScanButton = buttons.find(btn => btn.textContent.includes('Scan'));
      if (firstScanButton) {
        console.log('Clicking button:', firstScanButton);
        firstScanButton.click();
      }
    });
    
    // Wait a moment
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Monitor for toast messages
    console.log('\n3️⃣ Monitoring for toast messages...');
    
    let toastCount = 0;
    const checkToasts = async () => {
      const toasts = await page.evaluate(() => {
        const toastElements = document.querySelectorAll('[role="status"]');
        return Array.from(toastElements).map(t => ({
          text: t.textContent,
          className: t.className
        }));
      });
      
      if (toasts.length > toastCount) {
        console.log(`📢 New toast: ${toasts[toasts.length - 1].text}`);
        toastCount = toasts.length;
      }
      
      return toasts;
    };
    
    // Check for toasts every second for 15 seconds
    for (let i = 0; i < 15; i++) {
      await checkToasts();
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // Take final screenshot
    await page.screenshot({ path: 'scan_button_test.png', fullPage: true });
    console.log('\n📸 Screenshot saved as scan_button_test.png');
    
    // Check final state
    const finalState = await page.evaluate(() => {
      // Check for any visible changes
      const loadingIndicators = document.querySelectorAll('[class*="animate-spin"]');
      const toasts = document.querySelectorAll('[role="status"]');
      const buttons = Array.from(document.querySelectorAll('button'));
      const scanningButtons = buttons.filter(btn => btn.textContent.includes('Scanning'));
      
      return {
        hasLoadingIndicators: loadingIndicators.length > 0,
        toastCount: toasts.length,
        scanningButtonCount: scanningButtons.length,
        allToasts: Array.from(toasts).map(t => t.textContent)
      };
    });
    
    console.log('\n4️⃣ Final State:');
    console.log('   Loading indicators:', finalState.hasLoadingIndicators);
    console.log('   Toast count:', finalState.toastCount);
    console.log('   Scanning buttons:', finalState.scanningButtonCount);
    console.log('   All toasts:', finalState.allToasts);
    
    // Keep browser open
    console.log('\n🔍 Browser will stay open for manual inspection...');
    await new Promise(resolve => setTimeout(resolve, 30000));
    
  } catch (error) {
    console.error('Test error:', error);
  } finally {
    await browser.close();
  }
})();