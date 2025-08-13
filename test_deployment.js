const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--ignore-certificate-errors', '--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    
    console.log('Accessing VibeIntelligence at https://borgtools.ddns.net:8102...');
    await page.goto('https://borgtools.ddns.net:8102', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    // Wait for app to load
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Take screenshot
    await page.screenshot({ path: 'vi_deployment_test.png', fullPage: true });
    console.log('Screenshot saved as vi_deployment_test.png');
    
    // Check for title
    const title = await page.title();
    console.log(`Page title: ${title}`);
    
    // Check if API is accessible
    const apiResponse = await page.evaluate(async () => {
      try {
        const response = await fetch('/api/v1/health');
        const data = await response.json();
        return { status: response.status, data };
      } catch (error) {
        return { error: error.message };
      }
    });
    
    console.log('API Health check:', apiResponse);
    
    // Check for main elements
    const hasApp = await page.$('#root') !== null;
    console.log(`React app root found: ${hasApp}`);
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
})();