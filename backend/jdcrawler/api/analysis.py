import re
from collections import Counter

from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

COMMON_TECH_KEYWORDS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "vue",
    "angular",
    "nodejs",
    "spring",
    "django",
    "flask",
    "fastapi",
    "docker",
    "kubernetes",
    "aws",
    "gcp",
    "azure",
    "mysql",
    "postgresql",
    "mongodb",
    "redis",
    "kafka",
    "elasticsearch",
    "git",
    "ci/cd",
    "linux",
    "go",
    "rust",
    "cpp",
    "ruby",
    "php",
    "swift",
    "kotlin",
    "scala",
    "clojure",
    "haskell",
    "erlang",
    "elixir",
]


def get_db(request: Request):
    return request.app.state.db


@router.get("/tech-stacks")
def get_tech_stacks(request: Request):
    db = get_db(request)
    jobs = db.get_jobs(limit=1000)

    tech_stacks: Counter[str] = Counter()

    for job in jobs:
        text = f"{job.title} {job.company}".lower()
        for tech in COMMON_TECH_KEYWORDS:
            if re.search(r"\b" + re.escape(tech) + r"\b", text):
                tech_stacks[tech] += 1

    return dict(tech_stacks)
