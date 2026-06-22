import requests
import anthropic
import json

client = anthropic.Anthropic()

def generate_custom_answer(question, resume_data):
    prompt = f"""You are filling out a job application on behalf of this candidate.

Candidate info:
Name: {resume_data['name']}
Skills: {', '.join(resume_data['skills'])}
Resume: {resume_data['raw_text'][:2000]}

Answer this application question in 2-3 sentences, first person, professional but natural:
{question}

Return only the answer, nothing else."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()

def apply_greenhouse(job, resume_data):
    try:
        company = job["company"]
        job_id = job["id"]

        info_url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs/{job_id}"
        r = requests.get(info_url, timeout=10)
        if r.status_code != 200:
            return {"status": "failed", "reason": "could not fetch job details"}

        job_data = r.json()
        questions = job_data.get("questions", [])

        payload = {
            "first_name": resume_data["name"].split()[0] if resume_data["name"] else "",
            "last_name": " ".join(resume_data["name"].split()[1:]) if resume_data["name"] else "",
            "email": resume_data["email"],
            "phone": resume_data["phone"],
            "resume": open(resume_data["pdf_path"], "rb").read().hex(),
        }

        for q in questions:
            label = q.get("label", "")
            field = q.get("fields", [{}])[0]
            field_name = field.get("name", "")
            field_type = field.get("type", "")
            if field_type in ["input_text", "textarea"] and label and field_name:
                if field_name not in ["first_name", "last_name", "email", "phone", "resume"]:
                    payload[field_name] = generate_custom_answer(label, resume_data)

        submit_url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs/{job_id}/applications"
        response = requests.post(submit_url, json=payload, timeout=15)

        if response.status_code in [200, 201]:
            return {"status": "applied", "job": job["title"], "company": company}
        else:
            return {"status": "failed", "reason": response.text}

    except Exception as e:
        return {"status": "failed", "reason": str(e)}

def apply_lever(job, resume_data):
    try:
        company = job["company"]
        job_id = job["id"]

        payload = {
            "name": resume_data["name"],
            "email": resume_data["email"],
            "phone": resume_data["phone"],
            "resume": open(resume_data["pdf_path"], "rb").read().hex(),
        }

        submit_url = f"https://jobs.lever.co/{company}/{job_id}/apply"
        response = requests.post(submit_url, json=payload, timeout=15)

        if response.status_code in [200, 201]:
            return {"status": "applied", "job": job["title"], "company": company}
        else:
            return {"status": "failed", "reason": response.text}

    except Exception as e:
        return {"status": "failed", "reason": str(e)}

def apply_workable(job, resume_data):
    try:
        company = job["company"]
        job_id = job["id"]

        payload = {
            "firstname": resume_data["name"].split()[0] if resume_data["name"] else "",
            "lastname": " ".join(resume_data["name"].split()[1:]) if resume_data["name"] else "",
            "email": resume_data["email"],
            "phone": resume_data["phone"],
        }

        submit_url = f"https://apply.workable.com/api/v1/widget/accounts/{company}/jobs/{job_id}/candidates"
        response = requests.post(submit_url, json=payload, timeout=15)

        if response.status_code in [200, 201]:
            return {"status": "applied", "job": job["title"], "company": company}
        else:
            return {"status": "failed", "reason": response.text}

    except Exception as e:
        return {"status": "failed", "reason": str(e)}

def apply_to_job(job, resume_data):
    source = job.get("source")
    if source == "greenhouse":
        return apply_greenhouse(job, resume_data)
    elif source == "lever":
        return apply_lever(job, resume_data)
    elif source == "workable":
        return apply_workable(job, resume_data)
    else:
        return {"status": "failed", "reason": "unknown source"}
