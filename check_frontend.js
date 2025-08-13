const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ 
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    
    // Set viewport
    await page.setViewport({ width: 1280, height: 800 });
    
    // Navigate to dashboard
    console.log('Navigating to http://localhost:3101/dashboard...');
    await page.goto('http://localhost:3101/dashboard', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    // Wait for content to load
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Take screenshot
    await page.screenshot({ path: 'dashboard.png', fullPage: true });
    console.log('Screenshot saved as dashboard.png');
    
    // Get page title
    const title = await page.title();
    console.log('Page title:', title);
    
    // Check for project cards
    const projectCards = await page.evaluate(() => {
      const cards = document.querySelectorAll('.card-hover');
      return Array.from(cards).map(card => {
        const nameEl = card.querySelector('h3');
        const healthEl = card.querySelector('[class*="Health"]');
        return {
          name: nameEl ? nameEl.textContent : 'No name',
          health: healthEl ? healthEl.textContent : 'No health'
        };
      });
    });
    
    console.log('\nProjects found:', projectCards.length);
    projectCards.forEach(project => {
      console.log(`- ${project.name} (${project.health})`);
    });
    
    // Check for error messages
    const errors = await page.evaluate(() => {
      const errorElements = document.querySelectorAll('[class*="error"], [class*="Error"]');
      return Array.from(errorElements).map(el => el.textContent);
    });
    
    if (errors.length > 0) {
      console.log('\nErrors found:');
      errors.forEach(error => console.log(`- ${error}`));
    }
    
    // Check console logs
    const consoleLogs = [];
    page.on('console', msg => consoleLogs.push(msg.text()));
    
    // Navigate to projects page
    console.log('\nNavigating to projects page...');
    await page.goto('http://localhost:3101/projects', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    await new Promise(resolve => setTimeout(resolve, 3000));
    await page.screenshot({ path: 'projects.png', fullPage: true });
    console.log('Projects page screenshot saved as projects.png');
    
    // Check for project list
    const projectsList = await page.evaluate(() => {
      const cards = document.querySelectorAll('[class*="Card"]');
      return Array.from(cards).map(card => {
        const nameEl = card.querySelector('[class*="CardTitle"], h3');
        return nameEl ? nameEl.textContent : null;
      }).filter(Boolean);
    });
    
    console.log('\nProjects on projects page:', projectsList.length);
    projectsList.forEach(name => console.log(`- ${name}`));
    
    // Print console logs
    if (consoleLogs.length > 0) {
      console.log('\nConsole logs:');
      consoleLogs.forEach(log => console.log(log));
    }
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
})();