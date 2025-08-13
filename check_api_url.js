const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ 
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    
    // Intercept requests to see what URLs are being called
    page.on('request', request => {
      if (request.url().includes('api')) {
        console.log('API Request:', request.method(), request.url());
      }
    });
    
    // Navigate to dashboard
    console.log('Navigating to http://localhost:3101/dashboard...');
    await page.goto('http://localhost:3101/dashboard', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    // Wait a bit
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Check what the API_BASE_URL is in the frontend
    const apiConfig = await page.evaluate(() => {
      // Try to find the API configuration
      const scripts = Array.from(document.querySelectorAll('script'));
      let config = {};
      
      // Check localStorage
      config.localStorage = {
        auth_token: localStorage.getItem('auth_token')
      };
      
      // Check if there's a global config
      if (window.VITE_API_URL) {
        config.VITE_API_URL = window.VITE_API_URL;
      }
      
      // Check meta tags
      const metaTags = Array.from(document.querySelectorAll('meta'));
      metaTags.forEach(tag => {
        if (tag.name && tag.name.includes('api')) {
          config[tag.name] = tag.content;
        }
      });
      
      return config;
    });
    
    console.log('\nFrontend API Configuration:', apiConfig);
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
})();