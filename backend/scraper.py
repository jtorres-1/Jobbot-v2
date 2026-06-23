import requests
import re

def scrape_remotive(keywords):
    jobs = []
    try:
        r = requests.get("https://remotive.com/api/remote-jobs", timeout=15)
        if r.status_code != 200:
            return jobs
        for job in r.json().get("jobs", []):
            title = job.get("title", "")
            if any(k.lower() in title.lower() for k in keywords):
                jobs.append({
                    "title": title,
                    "company": job.get("company_name", ""),
                    "url": job.get("url", ""),
                    "source": "remotive"
                })
    except Exception as e:
        print(f"Remotive error: {e}")
    return jobs

def scrape_remoteok(keywords):
    jobs = []
    try:
        r = requests.get("https://remoteok.com/api", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if r.status_code != 200:
            return jobs
        for job in r.json()[1:]:
            title = job.get("position", "")
            if any(k.lower() in title.lower() for k in keywords):
                jobs.append({
                    "title": title,
                    "company": job.get("company", ""),
                    "url": job.get("url", ""),
                    "source": "remoteok"
                })
    except Exception as e:
        print(f"RemoteOK error: {e}")
    return jobs

def scrape_jobicy(keywords):
    jobs = []
    try:
        r = requests.get("https://jobicy.com/api/v2/remote-jobs?count=50", timeout=15)
        if r.status_code != 200:
            return jobs
        for job in r.json().get("jobs", []):
            title = job.get("jobTitle", "")
            if any(k.lower() in title.lower() for k in keywords):
                jobs.append({
                    "title": title,
                    "company": job.get("companyName", ""),
                    "url": job.get("url", ""),
                    "source": "jobicy"
                })
    except Exception as e:
        print(f"Jobicy error: {e}")
    return jobs

def scrape_jobs(keywords, location=None, remote=True, user_companies=None):
    if not keywords:
        return []
    all_jobs = []
    seen = set()
    for job in scrape_remotive(keywords) + scrape_remoteok(keywords) + scrape_jobicy(keywords):
        if job["url"] and job["url"] not in seen:
            seen.add(job["url"])
            all_jobs.append(job)
    return all_jobs
