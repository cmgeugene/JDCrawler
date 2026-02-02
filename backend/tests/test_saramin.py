import pytest

from jdcrawler.crawlers.saramin import SaraminCrawler


@pytest.fixture
def saramin_html():
    return """
    <div class="item_recruit">
        <div class="job_tit">
            <a href="https://www.saramin.co.kr/job/1">Python 개발자</a>
        </div>
        <div class="corp_name">
            <a href="#">테스트 회사</a>
        </div>
        <div class="job_condition">
            <span class="work_place">서울</span>
            <span class="career">경력무관</span>
            <span>3000~5000만원</span>
        </div>
    </div>
    <div class="item_recruit">
        <div class="job_tit">
            <a href="https://www.saramin.co.kr/job/2">Backend Engineer</a>
        </div>
        <div class="corp_name">
            <a href="#">스타트업 A</a>
        </div>
        <div class="job_condition">
            <span class="work_place">판교</span>
        </div>
    </div>
    """


class TestSaraminParser:
    def test_parse_jobs(self, saramin_html):
        crawler = SaraminCrawler()
        jobs = crawler._parse_jobs(saramin_html)

        assert len(jobs) == 2
        assert jobs[0].title == "Python 개발자"
        assert jobs[0].company == "테스트 회사"
        assert jobs[0].location == "서울"
        assert jobs[0].salary == "3000~5000만원"
        assert str(jobs[0].url) == "https://www.saramin.co.kr/job/1"
        assert jobs[0].site == "saramin"

    def test_parse_jobs_empty_html(self):
        crawler = SaraminCrawler()
        jobs = crawler._parse_jobs("<div></div>")
        assert jobs == []
