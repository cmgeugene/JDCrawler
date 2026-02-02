import pytest

from jdcrawler.crawlers.wanted import WantedCrawler


@pytest.fixture
def wanted_html():
    return """
    <div class="JobCard_container__FpkCx">
        <div class="JobCard_title__ddkwM">
            <a href="https://www.wanted.co.kr/job/1">Senior Python Engineer</a>
        </div>
        <div class="JobCard_company_info__JZFWJ">
            <span class="JobCard_company_name__vZTrq">원티드랩</span>
            <span class="JobCard_location__dEzJb">서울</span>
        </div>
    </div>
    <div class="JobCard_container__FpkCx">
        <div class="JobCard_title__ddkwM">
            <a href="https://www.wanted.co.kr/job/2">Frontend Developer</a>
        </div>
        <div class="JobCard_company_info__JZFWJ">
            <span class="JobCard_company_name__vZTrq">토스</span>
            <span class="JobCard_location__dEzJb">서울 판교</span>
        </div>
    </div>
    """


class TestWantedParser:
    def test_parse_jobs(self, wanted_html):
        crawler = WantedCrawler()
        jobs = crawler._parse_jobs(wanted_html)

        assert len(jobs) == 2
        assert jobs[0].title == "Senior Python Engineer"
        assert jobs[0].company == "원티드랩"
        assert jobs[0].location == "서울"
        assert str(jobs[0].url) == "https://www.wanted.co.kr/job/1"
        assert jobs[0].site == "wanted"

    def test_parse_jobs_empty_html(self):
        crawler = WantedCrawler()
        jobs = crawler._parse_jobs("<div></div>")
        assert jobs == []
