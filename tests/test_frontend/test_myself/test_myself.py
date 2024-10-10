import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    LicensingGroundsBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)


class TestAddMyself(StartBase, ProviderBase, RecipientBase, LicensingGroundsBase):
    """Tests for the myself journey"""

    def test_entire_journey_uk(self):
        self.page.goto("http://apply-for-a-licence:28000/apply/")
        self.myself(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-name-nationality-location"))
        self.provider_myself_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        self.no_more_additions(self.page)
        self.recipient_simple(self.page, "myself")
        expect(self.page).to_have_url(re.compile(r".*/add-recipient"))
        self.no_more_additions(self.page)
        self.licensing_grounds_simple(self.page)
        self.check_your_answers(self.page)
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)
        expect(self.page).to_have_url(re.compile(r".*/application-complete"))
        # TODO check there is a reference number
