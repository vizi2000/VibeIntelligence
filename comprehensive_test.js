const puppeteer = require('puppeteer');
const fs = require('fs');

// Test results storage
const testResults = {
  timestamp: new Date().toISOString(),
  tests: []
};

// Helper function to add test result
function addTestResult(name, status, details = '') {
  testResults.tests.push({
    name,
    status,
    details,
    timestamp: new Date().toISOString()
  });
  console.log(`${status === 'PASS' ? '✅' : '❌'} ${name} - ${details}`);
}

// Main test function
(async () => {
  const browser = await puppeteer.launch({ 
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    
    // Enable console logging
    const consoleLogs = [];
    page.on('console', msg => consoleLogs.push(msg.text()));
    page.on('pageerror', error => consoleLogs.push('PAGE ERROR: ' + error.message));
    
    console.log('🧪 Starting Comprehensive Test Suite for Zenith Coder\n');
    
    // Test 1: Frontend accessibility
    console.log('1️⃣ Testing Frontend Accessibility...');
    try {
      const response = await page.goto('http://localhost:3101', {
        waitUntil: 'domcontentloaded',
        timeout: 10000
      });
      
      if (response && response.status() === 200) {
        addTestResult('Frontend Accessibility', 'PASS', 'Frontend is accessible on port 3101');
      } else {
        addTestResult('Frontend Accessibility', 'FAIL', `Status code: ${response?.status()}`);
      }
    } catch (error) {
      addTestResult('Frontend Accessibility', 'FAIL', error.message);
    }
    
    // Test 2: Dashboard Page
    console.log('\n2️⃣ Testing Dashboard Page...');
    try {
      await page.goto('http://localhost:3101/dashboard', {
        waitUntil: 'networkidle2',
        timeout: 10000
      });
      
      // Wait for React to render
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Check for dashboard elements
      const dashboardElements = await page.evaluate(() => {
        return {
          title: document.querySelector('h1')?.textContent || '',
          projectCards: document.querySelectorAll('[class*="card"], .card-hover').length,
          aiAssistantCard: !!document.querySelector('[class*="AI Assistant"]'),
          agentActivityCard: !!document.querySelector('[class*="Agent Activity"]')
        };
      });
      
      if (dashboardElements.title.includes('Dashboard')) {
        addTestResult('Dashboard Page Load', 'PASS', `Found ${dashboardElements.projectCards} project cards`);
      } else {
        addTestResult('Dashboard Page Load', 'FAIL', 'Dashboard title not found');
      }
      
      if (dashboardElements.aiAssistantCard) {
        addTestResult('AI Assistant Card', 'PASS', 'AI Assistant card present on dashboard');
      } else {
        addTestResult('AI Assistant Card', 'FAIL', 'AI Assistant card not found');
      }
      
      if (dashboardElements.agentActivityCard) {
        addTestResult('Agent Activity Card', 'PASS', 'Agent Activity card present on dashboard');
      } else {
        addTestResult('Agent Activity Card', 'FAIL', 'Agent Activity card not found');
      }
      
      await page.screenshot({ path: 'test_dashboard.png' });
      
    } catch (error) {
      addTestResult('Dashboard Page', 'FAIL', error.message);
    }
    
    // Test 3: Projects Page
    console.log('\n3️⃣ Testing Projects Page...');
    try {
      await page.goto('http://localhost:3101/projects', {
        waitUntil: 'networkidle2',
        timeout: 10000
      });
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const projectsData = await page.evaluate(() => {
        const cards = document.querySelectorAll('[class*="card"], .card-hover');
        const scanButtons = document.querySelectorAll('button:has-text("Scan"), button:has([class*="Activity"])');
        
        return {
          projectCount: cards.length,
          scanButtonCount: Array.from(document.querySelectorAll('button')).filter(b => b.textContent.includes('Scan')).length,
          projectNames: Array.from(cards).slice(0, 5).map(card => 
            card.querySelector('h3, [class*="CardTitle"]')?.textContent || 'Unknown'
          )
        };
      });
      
      if (projectsData.projectCount > 0) {
        addTestResult('Projects Page Load', 'PASS', `Found ${projectsData.projectCount} projects`);
        console.log('   Project names:', projectsData.projectNames.join(', '));
      } else {
        addTestResult('Projects Page Load', 'FAIL', 'No projects found');
      }
      
      if (projectsData.scanButtonCount > 0) {
        addTestResult('Scan Buttons', 'PASS', `Found ${projectsData.scanButtonCount} scan buttons`);
      } else {
        addTestResult('Scan Buttons', 'FAIL', 'No scan buttons found');
      }
      
      await page.screenshot({ path: 'test_projects.png' });
      
    } catch (error) {
      addTestResult('Projects Page', 'FAIL', error.message);
    }
    
    // Test 4: AI Assistant Page
    console.log('\n4️⃣ Testing AI Assistant Page...');
    try {
      await page.goto('http://localhost:3101/ai-assistant', {
        waitUntil: 'networkidle2',
        timeout: 10000
      });
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const aiAssistantData = await page.evaluate(() => {
        const chatInput = document.querySelector('input[type="text"], textarea');
        const sendButton = Array.from(document.querySelectorAll('button')).find(b => 
          b.textContent.includes('Send') || b.querySelector('[class*="Send"]')
        );
        const messages = document.querySelectorAll('[class*="message"], [class*="chat"]');
        
        return {
          hasChatInput: !!chatInput,
          hasSendButton: !!sendButton,
          messageCount: messages.length
        };
      });
      
      if (aiAssistantData.hasChatInput && aiAssistantData.hasSendButton) {
        addTestResult('AI Assistant UI', 'PASS', 'Chat interface found');
      } else {
        addTestResult('AI Assistant UI', 'FAIL', 'Chat interface incomplete');
      }
      
      await page.screenshot({ path: 'test_ai_assistant.png' });
      
    } catch (error) {
      addTestResult('AI Assistant Page', 'FAIL', error.message);
    }
    
    // Test 5: API Endpoints
    console.log('\n5️⃣ Testing API Endpoints...');
    
    // Test projects API
    try {
      const projectsResponse = await page.evaluate(async () => {
        const response = await fetch('http://localhost:3101/api/v1/projects/');
        return {
          status: response.status,
          data: await response.json()
        };
      });
      
      if (projectsResponse.status === 200 && Array.isArray(projectsResponse.data)) {
        addTestResult('Projects API', 'PASS', `Returned ${projectsResponse.data.length} projects`);
      } else {
        addTestResult('Projects API', 'FAIL', `Status: ${projectsResponse.status}`);
      }
    } catch (error) {
      addTestResult('Projects API', 'FAIL', error.message);
    }
    
    // Test health API
    try {
      const healthResponse = await page.evaluate(async () => {
        const response = await fetch('http://localhost:3101/api/v1/health');
        return {
          status: response.status,
          data: await response.text()
        };
      });
      
      if (healthResponse.status === 200) {
        addTestResult('Health API', 'PASS', 'Health endpoint responding');
      } else {
        addTestResult('Health API', 'FAIL', `Status: ${healthResponse.status}`);
      }
    } catch (error) {
      addTestResult('Health API', 'FAIL', error.message);
    }
    
    // Test 6: Project Scanning Functionality
    console.log('\n6️⃣ Testing Project Scanning...');
    try {
      // Get projects first
      const projects = await page.evaluate(async () => {
        const response = await fetch('http://localhost:3101/api/v1/projects/');
        return await response.json();
      });
      
      if (projects.length > 0) {
        const firstProject = projects[0];
        
        // Start a scan
        const scanResponse = await page.evaluate(async (project) => {
          const response = await fetch('http://localhost:3101/api/v1/scanner/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              path: project.path,
              full_scan: false
            })
          });
          return await response.json();
        }, firstProject);
        
        if (scanResponse.scan_id) {
          addTestResult('Project Scan Start', 'PASS', `Scan ID: ${scanResponse.scan_id}`);
          
          // Wait and check status
          await new Promise(resolve => setTimeout(resolve, 3000));
          
          const scanStatus = await page.evaluate(async (scanId) => {
            const response = await fetch(`http://localhost:3101/api/v1/scanner/scan/${scanId}`);
            return await response.json();
          }, scanResponse.scan_id);
          
          if (scanStatus.status === 'completed' || scanStatus.status === 'running') {
            addTestResult('Project Scan Status', 'PASS', `Status: ${scanStatus.status}`);
          } else {
            addTestResult('Project Scan Status', 'FAIL', `Status: ${scanStatus.status}, Message: ${scanStatus.message}`);
          }
        } else {
          addTestResult('Project Scan Start', 'FAIL', 'No scan ID returned');
        }
      } else {
        addTestResult('Project Scan', 'SKIP', 'No projects available to scan');
      }
    } catch (error) {
      addTestResult('Project Scanning', 'FAIL', error.message);
    }
    
    // Test 7: AI Chat Functionality
    console.log('\n7️⃣ Testing AI Chat...');
    try {
      const chatResponse = await page.evaluate(async () => {
        const response = await fetch('http://localhost:3101/api/v1/ai/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: 'Hello, can you help me?'
          })
        });
        return {
          status: response.status,
          data: await response.json()
        };
      });
      
      if (chatResponse.status === 200 && chatResponse.data.response) {
        addTestResult('AI Chat API', 'PASS', 'AI responded successfully');
      } else {
        addTestResult('AI Chat API', 'FAIL', `Status: ${chatResponse.status}`);
      }
    } catch (error) {
      addTestResult('AI Chat API', 'FAIL', error.message);
    }
    
    // Test 8: Agent System
    console.log('\n8️⃣ Testing Agent System...');
    try {
      const agentStats = await page.evaluate(async () => {
        const response = await fetch('http://localhost:3101/api/v1/agents/stats');
        return {
          status: response.status,
          data: response.status === 200 ? await response.json() : null
        };
      });
      
      if (agentStats.status === 200) {
        addTestResult('Agent Stats API', 'PASS', 'Agent system accessible');
      } else {
        addTestResult('Agent Stats API', 'FAIL', `Status: ${agentStats.status}`);
      }
      
      const agentTasks = await page.evaluate(async () => {
        const response = await fetch('http://localhost:3101/api/v1/agents/tasks');
        return {
          status: response.status,
          data: response.status === 200 ? await response.json() : null
        };
      });
      
      if (agentTasks.status === 200) {
        addTestResult('Agent Tasks API', 'PASS', `Found ${agentTasks.data?.length || 0} tasks`);
      } else {
        addTestResult('Agent Tasks API', 'FAIL', `Status: ${agentTasks.status}`);
      }
    } catch (error) {
      addTestResult('Agent System', 'FAIL', error.message);
    }
    
    // Summary
    console.log('\n📊 Test Summary:');
    const passCount = testResults.tests.filter(t => t.status === 'PASS').length;
    const failCount = testResults.tests.filter(t => t.status === 'FAIL').length;
    const skipCount = testResults.tests.filter(t => t.status === 'SKIP').length;
    
    console.log(`✅ Passed: ${passCount}`);
    console.log(`❌ Failed: ${failCount}`);
    console.log(`⏭️  Skipped: ${skipCount}`);
    console.log(`📋 Total: ${testResults.tests.length}`);
    
    // Save results
    fs.writeFileSync('test_results.json', JSON.stringify(testResults, null, 2));
    console.log('\n📄 Test results saved to test_results.json');
    
    // Save console logs
    if (consoleLogs.length > 0) {
      console.log('\n⚠️  Console logs from frontend:');
      consoleLogs.forEach(log => console.log('   ', log));
    }
    
  } catch (error) {
    console.error('Test suite error:', error);
  } finally {
    await browser.close();
  }
})();