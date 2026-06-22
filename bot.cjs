require('dotenv').config();
const puppeteer = require('puppeteer');

const EMAIL = process.env.INDEED_EMAIL;
const PASSWORD = process.env.INDEED_PASSWORD;

async function login(page) {
  await page.goto('https://secure.indeed.com/auth', { waitUntil: 'networkidle2' });
  await page.type('input[name="emailAddress"]', EMAIL, { delay: 50 });
  await page.click('button[type="submit"]');
  await page.waitForTimeout(2000);
  await page.type('input[name="password"]', PASSWORD, { delay: 50 });
  await page.click('button[type="submit"]');
  await page.waitForTimeout(3000);
}

async function run() {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  await login(page);
  console.log('Logged in');
  await browser.close();
}

run();
