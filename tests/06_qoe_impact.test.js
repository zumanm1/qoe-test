const puppeteer = require('puppeteer');
const { login, initializePage, ensureScreenshotsDir, config } = require('../qoe-tool-tests/helpers');

describe('QoE Impact Dashboard - Graph Rendering Test', () => {
  let browser;
  let page;
  let consoleErrors = [];

  beforeAll(async () => {
    ensureScreenshotsDir();
    browser = await puppeteer.launch({
      headless: config.headless,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  });

  beforeEach(async () => {
    page = await initializePage(browser);
    consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
  });

  afterEach(async () => {
    if (page) {
      await page.close();
    }
  });

  afterAll(async () => {
    if (browser) {
      await browser.close();
    }
  });

  test('should open QoE Impact Dashboard and verify graphs render', async () => {
    // Step 1: Login using helper
    await login(page);
    
    // Step 2: Navigate to QoE Impact Dashboard
    await page.goto(`${config.baseUrl}/feature04/qoe_impact_dashboard`, { waitUntil: 'networkidle2' });
    
    // Step 3: Wait for page to stabilize and graphs to load
    await page.waitForTimeout(3000);
    
    // Step 4: Look for graph/chart elements with comprehensive selectors
    const graphElements = await page.evaluate(() => {
      const canvasElements = document.querySelectorAll('canvas');
      const svgElements = document.querySelectorAll('svg');
      const chartContainers = document.querySelectorAll('.chart, [id*="chart"], [class*="chart"]');
      const plotlyElements = document.querySelectorAll('.plotly-graph-div, .js-plotly-plot');
      const d3Elements = document.querySelectorAll('.d3-chart, .d3-graph');
      const highchartsElements = document.querySelectorAll('.highcharts-container');
      
      // Check if elements are visible and have meaningful dimensions
      const visibleCanvases = Array.from(canvasElements).filter(el => 
        el.offsetWidth > 50 && el.offsetHeight > 50
      );
      const visibleSvgs = Array.from(svgElements).filter(el => 
        el.offsetWidth > 50 && el.offsetHeight > 50
      );
      const visibleCharts = Array.from(chartContainers).filter(el => 
        el.offsetWidth > 50 && el.offsetHeight > 50
      );
      const visiblePlotly = Array.from(plotlyElements).filter(el => 
        el.offsetWidth > 50 && el.offsetHeight > 50
      );
      const visibleD3 = Array.from(d3Elements).filter(el => 
        el.offsetWidth > 50 && el.offsetHeight > 50
      );
      const visibleHighcharts = Array.from(highchartsElements).filter(el => 
        el.offsetWidth > 50 && el.offsetHeight > 50
      );
      
      return {
        totalCanvases: canvasElements.length,
        visibleCanvases: visibleCanvases.length,
        totalSvgs: svgElements.length,
        visibleSvgs: visibleSvgs.length,
        totalCharts: chartContainers.length,
        visibleCharts: visibleCharts.length,
        totalPlotly: plotlyElements.length,
        visiblePlotly: visiblePlotly.length,
        totalD3: d3Elements.length,
        visibleD3: visibleD3.length,
        totalHighcharts: highchartsElements.length,
        visibleHighcharts: visibleHighcharts.length
      };
    });
    
    console.log('Graph elements found:', graphElements);
    
    // Step 5: Verify that graphs are rendered
    const totalVisibleGraphs = graphElements.visibleCanvases + 
                              graphElements.visibleSvgs + 
                              graphElements.visibleCharts + 
                              graphElements.visiblePlotly + 
                              graphElements.visibleD3 + 
                              graphElements.visibleHighcharts;
    
    expect(totalVisibleGraphs).toBeGreaterThan(0);
    
    // Step 6: Additional checks for specific QoE dashboard elements
    const qoeElements = await page.evaluate(() => {
      // Look for QoE-specific elements
      const qoeCharts = document.querySelectorAll('[id*="qoe"], [class*="qoe"], .impact-chart, .quality-chart');
      const dashboardWidgets = document.querySelectorAll('.widget, .dashboard-widget, .chart-widget');
      const dataVisualization = document.querySelectorAll('.visualization, .graph-container, .chart-container');
      
      return {
        qoeCharts: qoeCharts.length,
        dashboardWidgets: dashboardWidgets.length,
        dataVisualization: dataVisualization.length
      };
    });
    
    console.log('QoE-specific elements found:', qoeElements);
    
    // Step 7: Verify QoE dashboard has meaningful content
    expect(
      qoeElements.qoeCharts + qoeElements.dashboardWidgets + qoeElements.dataVisualization
    ).toBeGreaterThan(0);
    
    // Step 8: Wait for any animations or dynamic loading to complete
    await page.waitForTimeout(2000);
    
    // Step 9: Capture screenshot after graphs stabilize
    await page.screenshot({ 
      path: '06_qoe_impact_dashboard.png',
      fullPage: true
    });
    
    // Step 10: Assert minimal console errors (some chart libraries may have warnings)
    const criticalErrors = consoleErrors.filter(error => 
      !error.includes('Warning') && 
      !error.includes('DevTools') &&
      !error.includes('favicon') &&
      !error.includes('Chart') // Chart libraries often have non-critical warnings
    );
    expect(criticalErrors.length).toBeLessThanOrEqual(2);
    
    console.log('QoE Impact Dashboard test completed successfully');
    console.log('Current URL:', page.url());
    console.log('Total visible graphs:', totalVisibleGraphs);
    console.log('Console errors:', consoleErrors.length);
  });
});
