import requests
import os

ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID", "35d01329")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY", "db9888d3020cea750c721826375eedf3")

def is_greenhouse(url):
    return "greenhouse.io" in url or "boards.greenhouse" in url

def is_lever(url):
    return "lever.co" in url

def is_workable(url):
    return "workable.com" in url

def get_ats_type(url):
    if is_greenhouse(url):
        return "greenhouse"
    if is_lever(url):
        return "lever"
    if is_workable(url):
        return "workable"
    return "other"

def extract_company_slug(url, ats_type):
    try:
        if ats_type == "greenhouse":
            return url.split("boards.greenhouse.io/")[1].split("/")[0]
        if ats_type == "lever":
            return url.split("jobs.lever.co/")[1].split("/")[0]
        if ats_type == "workable":
            return url.split("apply.workable.com/")[1].split("/")[0]
    except:
        return None
    return None

def scrape_jobs(keywords, location, remote, user_companies=None):
    all_jobs = []
    seen = set()

    keyword_str = " ".join(keywords) if keywords else ""
    if not keyword_str:
        return []

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 50,
        "what": keyword_str,
        "content-type": "application/json"
    }

    if remote:
        params["what"] = keyword_str + " remote"
    elif location:
        params["where"] = location

    try:
        for page in range(1, 5):
            r = requests.get(
                f"https://api.adzuna.com/v1/api/jobs/us/search/{page}",
                params=params,
                timeout=15
            )
            if r.status_code != 200:
                break
            data = r.json()
            results = data.get("results", [])
            if not results:
                break
            for job in results:
                url = job.get("redirect_url", "")
                if url in seen:
                    continue
                seen.add(url)
                ats_type = get_ats_type(url)
                slug = extract_company_slug(url, ats_type)
                job_id = url.split("/")[-1].split("?")[0] if url else ""
                all_jobs.append({
                    "title": job.get("title", ""),
                    "company": job.get("company", {}).get("display_name", ""),
                    "location": job.get("location", {}).get("display_name", ""),
                    "url": url,
                    "source": ats_type,
                    "slug": slug,
                    "id": job_id
                })
    except Exception as e:
        print(f"Adzuna scrape error: {e}")

    return all_jobs
