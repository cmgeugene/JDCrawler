import json
import os
from zai import ZaiClient
from jdcrawler.models.job import Job
from jdcrawler.models.profile import UserProfile

class AnalysisService:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY")
        if not self.api_key:
            print("Warning: ZHIPU_API_KEY not found. AI analysis will be disabled.")
            self.client = None
        else:
            self.client = ZaiClient(api_key=self.api_key)

    async def analyze_job_suitability(self, job: Job, profile: UserProfile) -> dict:
        """
        Analyze how well a job matches the user's profile using GLM-4-Flash.
        GLM-4-Flash often has a free tier or different quota limits.
        """
        if not self.client:
            return {
                "score": 0,
                "summary": "AI analysis is disabled (missing API key).",
                "status": "failed"
            }

        prompt = self._build_analysis_prompt(job, profile)

        try:
            # Using glm-4-flash which is often free/cheap and bypasses "Coding Plan" restrictions
            response = self.client.chat.completions.create(
                model="glm-4.7-flash",
                messages=[
                    {"role": "system", "content": "You are a professional technical recruiter and career advisor. Analyze job postings against a candidate's profile and return a JSON object with 'score' (0-100) and 'summary' (3-4 concise bullet points in Korean)."},
                    {"role": "user", "content": prompt}
                ],
                # 'thinking' might not be supported on Flash, so we remove it for compatibility
            )

            result_content = response.choices[0].message.content
            
            # Clean up potential markdown formatting
            if "```json" in result_content:
                result_content = result_content.split("```json")[1].split("```")[0].strip()
            elif "```" in result_content:
                result_content = result_content.split("```")[1].split("```")[0].strip()
            
            # Ensure we only have the JSON part if there's trailing text
            start_idx = result_content.find("{")
            end_idx = result_content.rfind("}")
            if start_idx != -1 and end_idx != -1:
                result_content = result_content[start_idx:end_idx+1]

            result = json.loads(result_content)
            
            return {
                "score": result.get("score", 0),
                "summary": result.get("summary", ""),
                "status": "completed"
            }
        except Exception as e:
            print(f"AI Analysis Error: {e}")
            return {
                "score": 0,
                "summary": f"Analysis failed: {str(e)}",
                "status": "failed"
            }

    def _build_analysis_prompt(self, job: Job, profile: UserProfile) -> str:
        # Build a detailed tech stack description including levels
        tech_details = []
        for skill in profile.tech_stack:
            detail = f"{skill.name} ({skill.level}"
            if skill.description:
                detail += f" - {skill.description}"
            detail += ")"
            tech_details.append(detail)
            
        tech_stack_str = ", ".join(tech_details)
        interests = ", ".join(profile.interest_keywords)
        exclude = ", ".join(profile.exclude_keywords)
        
        prompt = f"""
Candidate Profile:
- Detailed Tech Stack & Proficiency: {tech_stack_str}
- Experience: {profile.experience_years} years
- Interests: {interests}
- Exclude Keywords: {exclude}

Job Details:
- Title: {job.title}
- Company: {job.company}
- Experience Required: {job.experience}
- Description: {job.description or "No detailed description available."}

Task:
1. Analyze the match between the candidate's skill levels and the job requirements.
2. If a job requires "Expert" or "Lead" level in a skill where the candidate is a "Beginner", reflect this in the score.
3. Consider the specific proficiency descriptions (e.g., "can distinguish variables/functions" means basic knowledge).
4. Evaluate if the job matches the candidate's career interests (AX, AI, etc.).
5. Provide a suitability score (0-100).
6. Provide a summary in Korean (3-4 bullet points). Be honest about gaps in skill levels.

Return ONLY a JSON object: {{"score": number, "summary": "string"}}
"""
        return prompt

    async def extract_image_content(self, image_url: str):
        """
        Placeholder for future multimodal analysis.
        GLM-4V or similar can be used here later.
        """
        # Design: This will receive an image URL and return extracted text or analysis.
        pass
