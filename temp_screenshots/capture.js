const puppeteer = require('puppeteer');

(async () => {
    try {
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        await page.setViewport({ width: 1200, height: 800 });
        console.log('Navigating to local dev server...');
        await page.goto('http://localhost:1420', { waitUntil: 'networkidle2' });
        // wait an extra second for fonts/animations
        await new Promise(r => setTimeout(r, 1000));
        await page.screenshot({ path: 'ui_snapshot.png' });
        console.log('Screenshot saved to ui_snapshot.png');
        await browser.close();
    } catch (e) {
        console.error('Failed to capture screenshot:', e);
        process.exit(1);
    }
})();
