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
You are a Senior Career Consultant. Analyze the fit between the candidate and this job posting with depth and insight.
Do NOT just list matching keywords. Instead, evaluate the strategic fit, potential for growth, and alignment with the candidate's evident career direction.

Analysis Guidelines:
1. **Tech Stack Fit**: Analyze how the candidate's specific stack (e.g., if they know C++, how easy is it to pick up the job's requirements?) relates to the job. Look for foundational transferability.
2. **Growth Potential**: Does this job offer a chance to expand into the candidate's interest areas (AI, AX)?
3. **Gap Analysis**: Identify *critical* gaps versus *learnable* gaps. Be realistic but supportive.
4. **Cultural/Strategic Fit**: Based on the job description's tone and requirements, does this seem like a place where the candidate would thrive?

Output Format:
Return a JSON object with:
- "score": number (0-100, representing overall suitability)
- "summary": string (A concise, professional assessment in Korean. Use markdown formatting like bolding for emphasis. Structure it as 3-4 distinct points: '✅ 강점', '⚠️ 고려사항', '💡 성장 포인트' etc.)

Example Summary Style:
"✅ **핵심 역량 일치**: 보유한 C++ 및 언리얼 엔진 경험은 해당 포지션의 코어 요구사항과 정확히 부합하며, 즉시 전력감이 될 수 있습니다.
⚠️ **기술 스택 차이**: 백엔드 프레임워크 경험이 부족하나, 탄탄한 CS 지식을 바탕으로 빠르게 습득 가능한 수준입니다.
💡 **커리어 기회**: 관심 있는 AI 분야와의 접점이 명확하여, 향후 AI 엔지니어로의 커리어 확장이 기대됩니다."

Return ONLY the JSON object.
"""
        return prompt

    async def extract_image_content(self, image_url: str):
        """
        Placeholder for future multimodal analysis.
        GLM-4V or similar can be used here later.
        """
        # Design: This will receive an image URL and return extracted text or analysis.
        pass
