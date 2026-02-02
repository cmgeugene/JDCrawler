import pytest

from jdcrawler.crawlers.jobkorea import JobkoreaCrawler


@pytest.fixture
def jobkorea_html():
    return """
    <div class="list-post">
        <div class="post-list-info">
            <h5 class="title">
                <a href="https://www.jobkorea.co.kr/job/1">React Developer</a>
            </h5>
            <span class="company">테스트 기업</span>
            <p class="etc">
                <span class="loc">서울 강남구</span>
                <span class="exp">경력 3년이상</span>
            </p>
        </div>
    </div>
    <div class="list-post">
        <div class="post-list-info">
            <h5 class="title">
                <a href="https://www.jobkorea.co.kr/job/2">Full Stack Engineer</a>
            </h5>
            <span class="company">빅테크 B</span>
            <p class="etc">
                <span class="loc">수원</span>
            </p>
        </div>
    </div>
    """


class TestJobkoreaParser:
    def test_parse_jobs(self, jobkorea_html):
        crawler = JobkoreaCrawler()
        jobs = crawler._parse_jobs(jobkorea_html)

        assert len(jobs) == 2
        assert jobs[0].title == "React Developer"
        assert jobs[0].company == "테스트 기업"
        assert jobs[0].location == "서울 강남구"
        assert str(jobs[0].url) == "https://www.jobkorea.co.kr/job/1"
        assert jobs[0].site == "jobkorea"

    def test_parse_jobs_empty_html(self):
        crawler = JobkoreaCrawler()
        jobs = crawler._parse_jobs("<div></div>")
        assert jobs == []
