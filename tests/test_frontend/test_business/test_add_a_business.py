import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import StartTestBase


class TestBusinessJourney(StartTestBase):
    """Tests for the business journey"""

    def test_journey(self):
        self.page.goto("http://apply-for-a-licence:28000/apply/")
        self.business_input_goes_to_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
