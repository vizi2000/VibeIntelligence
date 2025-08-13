const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ 
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    
    // Listen for console logs
    page.on('console', msg => console.log('Browser console:', msg.text()));
    
    // Navigate to projects page
    console.log('Navigating to projects page...');
    await page.goto('http://localhost:3101/projects', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    // Wait for projects to load
    await page.waitForSelector('.card-hover', { timeout: 10000 });
    
    // Click the first project's scan button
    console.log('Clicking scan button on first project...');
    const scanButton = await page.$('.card-hover:first-child button');
    if (scanButton) {
      await scanButton.click();
      
      // Wait for scan to start
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Take screenshot
      await page.screenshot({ path: 'scan_in_progress.png', fullPage: true });
      console.log('Screenshot saved as scan_in_progress.png');
      
      // Wait for scan to complete (max 30 seconds)
      console.log('Waiting for scan to complete...');
      let scanCompleted = false;
      const startTime = Date.now();
      
      while (!scanCompleted && Date.now() - startTime < 30000) {
        // Check for success toast
        const toastText = await page.evaluate(() => {
          const toasts = document.querySelectorAll('[role="status"]');
          return Array.from(toasts).map(t => t.textContent).join(' ');
        });
        
        if (toastText.includes('completed') || toastText.includes('failed')) {
          scanCompleted = true;
          console.log('Scan result:', toastText);
        }
        
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      // Final screenshot
      await page.screenshot({ path: 'scan_completed.png', fullPage: true });
      console.log('Final screenshot saved as scan_completed.png');
      
    } else {
      console.log('No scan button found!');
    }
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
})();