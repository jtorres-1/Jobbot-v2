require('dotenv').config();
const puppeteer = require('puppeteer');
const path = require('path');

const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const USER_DATA = path.join(__dirname, 'puppeteer-profile');

async function run() {
  try {
    const browser = await puppeteer.launch({ 
      headless: false,
      pipe: true,
      userDataDir: USER_DATA,
      args: [
        '--no-sandbox',
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--disable-web-security'
      ]
    });
    const page = await browser.newPage();
    await page.setDefaultNavigationTimeout(60000);
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36');
    await page.goto('https://www.linkedin.com', { waitUntil: 'domcontentloaded' });
    console.log('LinkedIn loaded. Log in if needed, then press ENTER.');
    await new Promise(resolve => process.stdin.once('data', resolve));
    await page.screenshot({ path: 'session.png' });
    console.log('Done.');
    await browser.close();
  } catch (err) {
    console.error('Error:', err.message);
  }
}

run();
