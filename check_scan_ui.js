const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ 
    headless: false, // Show browser
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    
    // Set viewport
    await page.setViewport({ width: 1280, height: 800 });
    
    // Enable console logging
    page.on('console', msg => console.log('Console:', msg.text()));
    page.on('pageerror', error => console.log('Page error:', error.message));
    
    // Navigate to projects page
    console.log('Navigating to http://localhost:3101/projects...');
    await page.goto('http://localhost:3101/projects', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    console.log('Page loaded. Waiting 5 seconds for React to render...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Take screenshot
    await page.screenshot({ path: 'projects_page.png', fullPage: true });
    console.log('Screenshot saved as projects_page.png');
    
    // Check what's on the page
    const pageContent = await page.evaluate(() => {
      const projectCards = document.querySelectorAll('.card-hover, [class*="Card"]');
      const buttons = document.querySelectorAll('button');
      const errors = document.querySelectorAll('[class*="error"], [class*="Error"]');
      
      return {
        projectCardsCount: projectCards.length,
        buttonsCount: buttons.length,
        buttonTexts: Array.from(buttons).map(b => b.textContent),
        errors: Array.from(errors).map(e => e.textContent),
        bodyText: document.body.innerText.substring(0, 500)
      };
    });
    
    console.log('\nPage analysis:');
    console.log('Project cards found:', pageContent.projectCardsCount);
    console.log('Buttons found:', pageContent.buttonsCount);
    console.log('Button texts:', pageContent.buttonTexts);
    if (pageContent.errors.length > 0) {
      console.log('Errors:', pageContent.errors);
    }
    console.log('\nPage text preview:', pageContent.bodyText);
    
    // Wait for user to interact
    console.log('\nBrowser will stay open for 30 seconds. You can interact with it...');
    await new Promise(resolve => setTimeout(resolve, 30000));
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
})();