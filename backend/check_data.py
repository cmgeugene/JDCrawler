from jdcrawler.db.client import DatabaseClient
from jdcrawler.models.job import JobSite

db = DatabaseClient("sqlite:///./data/jobs.db")
try:
    jobs = db.get_jobs(site=JobSite.SARAMIN, limit=5)
    print(f"Found {len(jobs)} jobs:")
    for job in jobs:
        print(f"Title: {job.title}")
        print(f"Experience: {job.experience}")
        print(f"Salary: {job.salary}")
        print(f"Deadline: {job.deadline}")
        print("-" * 20)
finally:
    db.close()
