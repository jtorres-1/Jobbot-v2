from playwright.sync_api import sync_playwright
import os
import time

def fill_form(page, resume_data, pdf_path):
    first = resume_data.get('name', '').split()[0] if resume_data.get('name') else ''
    last = ' '.join(resume_data.get('name', '').split()[1:])
    email = resume_data.get('email', '')
    phone = resume_data.get('phone', '')
    for sel, val in [
        ('input[name*=first]', first), ('input[id*=first]', first),
        ('input[name*=last]', last), ('input[id*=last]', last),
        ('input[name*=email]', email), ('input[id*=email]', email),
        ('input[type=email]', email),
        ('input[name*=phone]', phone), ('input[id*=phone]', phone),
        ('input[name*=name]', first),
    ]:
        try:
            el = page.locator(sel).first
            if el.is_visible() and el.count() > 0:
                el.fill(val)
        except:
            pass
    for sel in ['input[type=file][name*=resume]', 'input[type=file][id*=resume]', 'input[type=file][name*=cv]', 'input[type=file]']:
        try:
            el = page.locator(sel).first
            if el.count() > 0:
                el.set_input_files(pdf_path)
                break
        except:
            pass

def find_submit(page):
    for sel in ['input[type=submit]', 'button[type=submit]']:
        try:
            els = page.locator(sel).all()
            for el in els:
                if el.is_visible():
                    return el
        except:
            pass
    return None

def get_apply_url(page):
    for sel in ['a:has-text("Apply Now")', 'a:has-text("Apply for this job")', 'a:has-text("Apply")', 'a[href*=apply]']:
        try:
            el = page.locator(sel).first
            if el.count() > 0 and el.is_visible():
                href = el.get_attribute('href')
                if href and href.startswith('http') and 'remotive' not in href:
                    return href
        except:
            pass
    return None

def apply_to_job(job, resume_data):
    url = job.get('url', '')
    pdf_path = resume_data.get('pdf_path', '')
    if not url or not os.path.exists(pdf_path):
        return {'status': 'failed', 'reason': 'missing url or resume'}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            page = context.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_load_state('networkidle')
            time.sleep(2)
            apply_url = get_apply_url(page)
            if not apply_url:
                browser.close()
                return {'status': 'failed', 'reason': 'no apply link found'}
            page.goto(apply_url, timeout=30000)
            page.wait_for_load_state('networkidle')
            time.sleep(2)
            fill_form(page, resume_data, pdf_path)
            submit = find_submit(page)
            if submit:
                submit.click()
                time.sleep(3)
                browser.close()
                return {'status': 'applied', 'job': job.get('title'), 'company': job.get('company')}
            else:
                browser.close()
                return {'status': 'failed', 'reason': 'no submit button found'}
    except Exception as e:
        return {'status': 'failed', 'reason': str(e)}
