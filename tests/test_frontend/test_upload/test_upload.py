import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    LicensingGroundsBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)


class TestUpload(StartBase, ProviderBase, RecipientBase, LicensingGroundsBase):
    """Test upload works"""

    def test_third_party_located_in_uk(self):
        self.page.goto("http://apply-for-a-licence:28000/apply/")
        self.business_third_party(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.provider_business_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/add-business"))
        self.no_more_additions(self.page)
        self.recipient_simple(self.page, "business")
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.no_more_additions(self.page)
        self.page.get_by_label("What is your purpose for").fill("Test purpose")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_text("Choose files").click()
        # self.page.get_by_label("Upload a file").set_input_files("./tests/test_frontend/fixturesTest.pdf")
        self.page.get_by_label("Upload a file").set_input_files("./tests/test_frontend/fixtures/Test.pdf")
        expect(self.page.locator("text=Test.pdf")).to_be_visible()
        self.page.get_by_role("button", name="Continue").click()
        self.check_your_answers(self.page)
