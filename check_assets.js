const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--ignore-certificate-errors', '--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    
    // Track network requests
    const failedRequests = [];
    const successfulRequests = [];
    
    page.on('response', response => {
      const url = response.url();
      const status = response.status();
      
      if (url.includes('.css') || url.includes('.js')) {
        if (status >= 400) {
          failedRequests.push({ url, status });
          console.log(`❌ Failed: ${url} - Status: ${status}`);
        } else {
          successfulRequests.push({ url, status });
          console.log(`✅ Success: ${url} - Status: ${status}`);
        }
      }
    });
    
    page.on('requestfailed', request => {
      const url = request.url();
      if (url.includes('.css') || url.includes('.js')) {
        console.log(`❌ Request failed: ${url} - ${request.failure().errorText}`);
        failedRequests.push({ url, error: request.failure().errorText });
      }
    });
    
    console.log('Loading VibeIntelligence...');
    await page.goto('https://borgtools.ddns.net:8102', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    // Check for CSS application
    const hasStyles = await page.evaluate(() => {
      const root = document.getElementById('root');
      if (!root) return false;
      const computed = window.getComputedStyle(root);
      return computed.backgroundColor !== 'rgba(0, 0, 0, 0)' || 
             computed.color !== 'rgb(0, 0, 0)';
    });
    
    console.log(`\nStyles applied: ${hasStyles}`);
    
    // Get all stylesheets
    const stylesheets = await page.evaluate(() => {
      return Array.from(document.styleSheets).map(sheet => ({
        href: sheet.href,
        rules: sheet.cssRules ? sheet.cssRules.length : 0
      }));
    });
    
    console.log('\nStylesheets loaded:');
    stylesheets.forEach(sheet => {
      console.log(`  ${sheet.href || 'inline'} - ${sheet.rules} rules`);
    });
    
    // Check body styles
    const bodyStyles = await page.evaluate(() => {
      const body = document.body;
      const computed = window.getComputedStyle(body);
      return {
        backgroundColor: computed.backgroundColor,
        fontFamily: computed.fontFamily,
        margin: computed.margin
      };
    });
    
    console.log('\nBody styles:', bodyStyles);
    
    await page.screenshot({ path: 'asset_check.png', fullPage: true });
    console.log('\nScreenshot saved as asset_check.png');
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
})();