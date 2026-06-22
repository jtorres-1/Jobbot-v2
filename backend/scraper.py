import requests

GREENHOUSE_API = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
LEVER_API = "https://api.lever.co/v0/postings/{company}?mode=json"
WORKABLE_API = "https://apply.workable.com/api/v1/widget/accounts/{company}/jobs"

def search_greenhouse(company, keywords, location, remote):
    try:
        r = requests.get(GREENHOUSE_API.format(company=company), timeout=10)
        if r.status_code != 200:
            return []
        jobs = r.json().get("jobs", [])
        results = []
        for job in jobs:
            title = job.get("title", "").lower()
            loc = job.get("location", {}).get("name", "").lower()
            if any(k.lower() in title for k in keywords):
                if remote and "remote" in loc:
                    results.append({"title": job["title"], "location": loc, "url": job["absolute_url"], "source": "greenhouse", "company": company, "id": job["id"]})
                elif location and location.lower() in loc:
                    results.append({"title": job["title"], "location": loc, "url": job["absolute_url"], "source": "greenhouse", "company": company, "id": job["id"]})
        return results
    except:
        return []

def search_lever(company, keywords, location, remote):
    try:
        r = requests.get(LEVER_API.format(company=company), timeout=10)
        if r.status_code != 200:
            return []
        jobs = r.json()
        results = []
        for job in jobs:
            title = job.get("text", "").lower()
            loc = job.get("categories", {}).get("location", "").lower()
            commitment = job.get("categories", {}).get("commitment", "").lower()
            if any(k.lower() in title for k in keywords):
                if remote and ("remote" in loc or "remote" in commitment):
                    results.append({"title": job["text"], "location": loc, "url": job["hostedUrl"], "source": "lever", "company": company, "id": job["id"]})
                elif location and location.lower() in loc:
                    results.append({"title": job["text"], "location": loc, "url": job["hostedUrl"], "source": "lever", "company": company, "id": job["id"]})
        return results
    except:
        return []

def search_workable(company, keywords, location, remote):
    try:
        r = requests.get(WORKABLE_API.format(company=company), timeout=10)
        if r.status_code != 200:
            return []
        jobs = r.json().get("results", [])
        results = []
        for job in jobs:
            title = job.get("title", "").lower()
            loc = job.get("location", {}).get("city", "").lower()
            remote_flag = job.get("remote", False)
            if any(k.lower() in title for k in keywords):
                if remote and remote_flag:
                    results.append({"title": job["title"], "location": loc, "url": f"https://apply.workable.com/{company}/j/{job['shortcode']}", "source": "workable", "company": company, "id": job["shortcode"]})
                elif location and location.lower() in loc:
                    results.append({"title": job["title"], "location": loc, "url": f"https://apply.workable.com/{company}/j/{job['shortcode']}", "source": "workable", "company": company, "id": job["shortcode"]})
        return results
    except:
        return []

def scrape_jobs(keywords, location, remote, companies):
    all_jobs = []
    for company in companies:
        all_jobs += search_greenhouse(company, keywords, location, remote)
        all_jobs += search_lever(company, keywords, location, remote)
        all_jobs += search_workable(company, keywords, location, remote)
    return all_jobs
