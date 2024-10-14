import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import PlaywrightTestBase, ProviderBase, StartBase


class TestCompaniesHouse(StartBase, ProviderBase):
    """Tests for the companies house journey"""

    def test_companies_house_number_unknown(self):
        self.page.goto(PlaywrightTestBase.base_url)
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.your_details(self.page, "business")
        self.page.get_by_label("Yes", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/where-business-located"))

    def test_companies_house_number_incorrect(self):
        self.page.goto(PlaywrightTestBase.base_url)
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.your_details(self.page, "business")
        self.page.get_by_label("Yes", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Yes", exact=True).check()
        number_input = self.page.get_by_label("Registered company number")  # Wait 10 seconds for popup to load
        number_input.wait_for(state="visible", timeout=10000)
        number_input.fill("0")
        self.page.get_by_role("button", name="Continue").click()
        expect(
            self.page.get_by_text(
                "Number not recognised with Companies House. Enter the correct registered company number."
                " This is usually an 8-digit number."
            )
        ).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/registered-company-number"))

    def test_companies_house_number(self):
        self.page.goto(PlaywrightTestBase.base_url)
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.your_details(self.page, "business")
        self.page.get_by_label("Yes", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Yes", exact=True).check()
        number_input = self.page.get_by_label("Registered company number")  # Wait 10 seconds for popup to load
        number_input.wait_for(state="visible", timeout=10000)
        number_input.fill("12345678")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="Check company details")).to_be_visible()
        expect(self.page.get_by_text("12345678")).to_be_visible()
