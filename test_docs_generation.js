const puppeteer = require('puppeteer');

(async () => {
  console.log('🧪 Testing documentation generation functionality...\n');
  
  const browser = await puppeteer.launch({ 
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    
    // Set viewport
    await page.setViewport({ width: 1366, height: 768 });
    
    // Navigate to the projects page
    console.log('📱 Navigating to Projects page...');
    await page.goto('http://localhost:3101/projects', { 
      waitUntil: 'networkidle0',
      timeout: 30000 
    });
    
    // Wait for projects to load
    console.log('⏳ Waiting for projects to load...');
    await page.waitForSelector('.grid', { timeout: 10000 });
    
    // Check if there are any projects
    const projects = await page.$$('.grid > div');
    console.log(`📦 Found ${projects.length} projects`);
    
    if (projects.length === 0) {
      console.log('❌ No projects found. Running a scan first...');
      
      // Click scan button if available
      const buttons = await page.$$('button');
      let scanButton = null;
      for (const button of buttons) {
        const text = await button.evaluate(el => el.textContent);
        if (text && text.includes('Start Project Scan')) {
          scanButton = button;
          break;
        }
      }
      
      if (scanButton) {
        console.log('🔍 Starting project scan...');
        await scanButton.click();
        
        // Wait for scan to complete
        await page.waitForFunction(
          () => !document.querySelector('.animate-spin'),
          { timeout: 60000 }
        );
        
        console.log('✅ Scan completed');
        
        // Refresh to see new projects
        await page.reload({ waitUntil: 'networkidle0' });
        await page.waitForSelector('.grid', { timeout: 10000 });
      }
    }
    
    // Get first project card
    const firstProject = await page.$('.grid > div:first-child');
    if (!firstProject) {
      throw new Error('No project cards found');
    }
    
    // Get project info
    const projectName = await firstProject.$eval('.text-lg', el => el.textContent);
    console.log(`\n📋 Testing documentation generation for: ${projectName}`);
    
    // Find and click the Docs button
    const docsButtons = await firstProject.$$('button');
    let docsButton = null;
    for (const button of docsButtons) {
      const text = await button.evaluate(el => el.textContent);
      if (text && text.includes('Docs')) {
        docsButton = button;
        break;
      }
    }
    
    if (!docsButton) {
      throw new Error('Docs button not found');
    }
    
    console.log('📝 Clicking Docs button...');
    await docsButton.click();
    
    // Wait for toast notification
    await page.waitForFunction(
      () => {
        const toasts = Array.from(document.querySelectorAll('[role="status"]'));
        return toasts.some(toast => 
          toast.textContent.includes('Documentation generation started') ||
          toast.textContent.includes('Documentation generated successfully')
        );
      },
      { timeout: 10000 }
    );
    
    console.log('✅ Documentation generation started');
    
    // Wait for completion (max 30 seconds)
    console.log('⏳ Waiting for documentation to be generated...');
    const startTime = Date.now();
    
    await page.waitForFunction(
      () => {
        const toasts = Array.from(document.querySelectorAll('[role="status"]'));
        return toasts.some(toast => 
          toast.textContent.includes('Documentation generated successfully') ||
          toast.textContent.includes('Documentation generation failed')
        );
      },
      { timeout: 30000 }
    ).catch(() => {
      console.log('⚠️ Documentation generation timed out after 30 seconds');
    });
    
    const endTime = Date.now();
    const duration = (endTime - startTime) / 1000;
    
    // Check final status
    const toastText = await page.evaluate(() => {
      const toasts = Array.from(document.querySelectorAll('[role="status"]'));
      const statusToast = toasts.find(toast => 
        toast.textContent.includes('Documentation') && 
        !toast.textContent.includes('started')
      );
      return statusToast ? statusToast.textContent : '';
    });
    
    if (toastText.includes('successfully')) {
      console.log(`\n✅ SUCCESS: Documentation generated in ${duration}s`);
      console.log(`📄 ${toastText}`);
      
      // Check API for the generated documentation
      console.log('\n🔍 Checking API for generated documentation...');
      const response = await page.evaluate(async (projectName) => {
        // Get project ID from the API
        const projectsResponse = await fetch('/api/v1/projects/');
        const projects = await projectsResponse.json();
        const project = projects.find(p => p.name === projectName);
        
        if (project) {
          const docsResponse = await fetch(`/api/v1/documentation/project/${project.id}`);
          return await docsResponse.json();
        }
        return null;
      }, projectName);
      
      if (response && response.documents && response.documents.length > 0) {
        console.log(`📚 Found ${response.documents.length} generated documents`);
        response.documents.forEach(doc => {
          console.log(`   - ${doc.type}: ${doc.file_path} (${new Date(doc.created_at).toLocaleString()})`);
        });
      }
    } else if (toastText.includes('failed')) {
      console.log(`\n❌ FAILED: Documentation generation failed`);
      console.log(`📄 ${toastText}`);
    } else {
      console.log(`\n⚠️ TIMEOUT: Documentation generation status unknown after ${duration}s`);
    }
    
    // Take a screenshot
    await page.screenshot({ 
      path: 'test_docs_result.png',
      fullPage: true 
    });
    console.log('\n📸 Screenshot saved as test_docs_result.png');
    
  } catch (error) {
    console.error('\n❌ Test failed:', error);
    
    // Take error screenshot
    const page = (await browser.pages())[0];
    if (page) {
      await page.screenshot({ 
        path: 'test_docs_error.png',
        fullPage: true 
      });
      console.log('📸 Error screenshot saved as test_docs_error.png');
    }
  } finally {
    // Keep browser open for manual inspection
    console.log('\n🔍 Browser will remain open for inspection. Press Ctrl+C to exit.');
  }
})();