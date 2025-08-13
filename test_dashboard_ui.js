const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ 
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    defaultViewport: { width: 1280, height: 800 }
  });
  
  try {
    const page = await browser.newPage();
    
    console.log('🧪 Testing Dashboard UI Components\n');
    
    // Navigate to dashboard
    console.log('1️⃣ Navigating to Dashboard...');
    await page.goto('http://localhost:3101/dashboard', {
      waitUntil: 'networkidle2',
      timeout: 15000
    });
    
    // Wait for content to load
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Check what's rendered
    const dashboardInfo = await page.evaluate(() => {
      // Get all cards
      const cards = document.querySelectorAll('[class*="Card"], .card-hover');
      
      // Look for specific text
      const aiAssistantText = document.body.textContent.includes('AI Assistant');
      const agentActivityText = document.body.textContent.includes('Agent Activity');
      const chatBubbles = document.querySelectorAll('.chat-bubble');
      
      // Get grid structure
      const grids = document.querySelectorAll('.grid');
      const cols = document.querySelectorAll('[class*="col-span"]');
      
      // Get actual card titles
      const cardTitles = Array.from(cards).map(card => {
        const title = card.querySelector('[class*="CardTitle"], h2, h3');
        return title ? title.textContent : 'No title';
      });
      
      return {
        cardCount: cards.length,
        hasAIAssistantText: aiAssistantText,
        hasAgentActivityText: agentActivityText,
        chatBubbleCount: chatBubbles.length,
        gridCount: grids.length,
        colCount: cols.length,
        cardTitles: cardTitles,
        // Get the HTML structure to debug
        bodyClasses: document.body.className,
        mainContent: document.querySelector('main')?.className || 'No main element'
      };
    });
    
    console.log('\n📊 Dashboard Analysis:');
    console.log('Cards found:', dashboardInfo.cardCount);
    console.log('Card titles:', dashboardInfo.cardTitles);
    console.log('Has AI Assistant text:', dashboardInfo.hasAIAssistantText);
    console.log('Has Agent Activity text:', dashboardInfo.hasAgentActivityText);
    console.log('Chat bubbles:', dashboardInfo.chatBubbleCount);
    console.log('Grid elements:', dashboardInfo.gridCount);
    console.log('Column elements:', dashboardInfo.colCount);
    
    // Take screenshot
    await page.screenshot({ path: 'dashboard_ui_test.png', fullPage: true });
    console.log('\n📸 Screenshot saved as dashboard_ui_test.png');
    
    // Check the grid structure
    const gridStructure = await page.evaluate(() => {
      const mainGrid = document.querySelector('.grid.grid-cols-12');
      if (!mainGrid) return 'No main grid found';
      
      const children = mainGrid.children;
      return {
        childCount: children.length,
        childClasses: Array.from(children).map(child => ({
          className: child.className,
          hasCards: child.querySelectorAll('[class*="Card"]').length
        }))
      };
    });
    
    console.log('\n🏗️ Grid Structure:');
    console.log('Main grid children:', gridStructure.childCount);
    if (gridStructure.childClasses) {
      gridStructure.childClasses.forEach((child, i) => {
        console.log(`  Child ${i}: ${child.className} (${child.hasCards} cards)`);
      });
    }
    
    // Keep browser open
    console.log('\n🔍 Browser will stay open for manual inspection...');
    await new Promise(resolve => setTimeout(resolve, 30000));
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
})();