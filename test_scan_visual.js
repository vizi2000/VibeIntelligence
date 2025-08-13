const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ 
    headless: false, // Show browser
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    defaultViewport: { width: 1280, height: 800 }
  });
  
  try {
    const page = await browser.newPage();
    
    console.log('🧪 Visual Test: Project Scanning Functionality\n');
    
    // Navigate to projects page
    console.log('1️⃣ Navigating to Projects page...');
    await page.goto('http://localhost:3101/projects', {
      waitUntil: 'networkidle2',
      timeout: 15000
    });
    
    // Wait for projects to load
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Take initial screenshot
    await page.screenshot({ path: 'scan_test_1_initial.png', fullPage: true });
    console.log('📸 Initial screenshot saved');
    
    // Check if projects are loaded
    const projectCount = await page.evaluate(() => {
      const cards = document.querySelectorAll('[class*="Card"]');
      console.log('Cards found:', cards.length);
      return cards.length;
    });
    
    console.log(`✅ Found ${projectCount} project cards`);
    
    if (projectCount > 0) {
      // Find and click the first scan button
      console.log('\n2️⃣ Looking for scan button...');
      
      const scanButtonClicked = await page.evaluate(() => {
        // Find all buttons
        const buttons = Array.from(document.querySelectorAll('button'));
        console.log('Total buttons found:', buttons.length);
        
        // Find scan button
        const scanButton = buttons.find(btn => 
          btn.textContent.includes('Scan') || 
          btn.innerHTML.includes('Activity')
        );
        
        if (scanButton) {
          console.log('Scan button found:', scanButton.textContent);
          scanButton.click();
          return true;
        }
        return false;
      });
      
      if (scanButtonClicked) {
        console.log('✅ Clicked scan button');
        
        // Wait for scan to start
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Take screenshot during scan
        await page.screenshot({ path: 'scan_test_2_scanning.png', fullPage: true });
        console.log('📸 Scanning screenshot saved');
        
        // Check for toast notifications
        const toastMessages = await page.evaluate(() => {
          const toasts = document.querySelectorAll('[role="status"], [class*="toast"], [class*="Toast"]');
          return Array.from(toasts).map(t => t.textContent);
        });
        
        if (toastMessages.length > 0) {
          console.log('\n📢 Toast messages:', toastMessages);
        }
        
        // Wait for scan to complete
        console.log('\n3️⃣ Waiting for scan to complete...');
        await new Promise(resolve => setTimeout(resolve, 10000));
        
        // Take final screenshot
        await page.screenshot({ path: 'scan_test_3_completed.png', fullPage: true });
        console.log('📸 Final screenshot saved');
        
        // Check final toast messages
        const finalToasts = await page.evaluate(() => {
          const toasts = document.querySelectorAll('[role="status"], [class*="toast"], [class*="Toast"]');
          return Array.from(toasts).map(t => t.textContent);
        });
        
        if (finalToasts.length > 0) {
          console.log('\n📢 Final toast messages:', finalToasts);
        }
        
        // Check if any UI changed
        const uiChanges = await page.evaluate(() => {
          // Check for any loading indicators
          const loadingElements = document.querySelectorAll('[class*="loading"], [class*="Loading"], [class*="spin"], [class*="Spin"]');
          
          // Check for any error messages
          const errorElements = document.querySelectorAll('[class*="error"], [class*="Error"]');
          
          return {
            hasLoading: loadingElements.length > 0,
            hasErrors: errorElements.length > 0,
            errorMessages: Array.from(errorElements).map(e => e.textContent)
          };
        });
        
        console.log('\n4️⃣ UI State Check:');
        console.log('   Has loading indicators:', uiChanges.hasLoading);
        console.log('   Has errors:', uiChanges.hasErrors);
        if (uiChanges.errorMessages.length > 0) {
          console.log('   Error messages:', uiChanges.errorMessages);
        }
        
      } else {
        console.log('❌ No scan button found');
        
        // Debug: List all button texts
        const buttonTexts = await page.evaluate(() => {
          return Array.from(document.querySelectorAll('button')).map(b => b.textContent.trim());
        });
        console.log('\nAll button texts found:', buttonTexts);
      }
    } else {
      console.log('❌ No projects found on page');
    }
    
    // Test direct API scan
    console.log('\n5️⃣ Testing direct API scan...');
    const apiScanResult = await page.evaluate(async () => {
      try {
        // Get first project
        const projectsResponse = await fetch('/api/v1/projects/');
        const projects = await projectsResponse.json();
        
        if (projects.length > 0) {
          const firstProject = projects[0];
          console.log('Scanning project:', firstProject.name);
          
          // Start scan
          const scanResponse = await fetch('/api/v1/scanner/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              path: firstProject.path,
              full_scan: false
            })
          });
          
          return await scanResponse.json();
        }
        return { error: 'No projects found' };
      } catch (error) {
        return { error: error.message };
      }
    });
    
    console.log('API Scan Result:', apiScanResult);
    
    // Keep browser open for manual inspection
    console.log('\n🔍 Browser will stay open for 30 seconds for manual inspection...');
    await new Promise(resolve => setTimeout(resolve, 30000));
    
  } catch (error) {
    console.error('Test error:', error);
    await page.screenshot({ path: 'scan_test_error.png', fullPage: true });
  } finally {
    await browser.close();
  }
})();