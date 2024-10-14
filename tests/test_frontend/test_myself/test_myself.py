import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import (
    LicensingGroundsBase,
    PlaywrightTestBase,
    ProviderBase,
    RecipientBase,
    StartBase,
)


class TestAddMyself(StartBase, ProviderBase, RecipientBase, LicensingGroundsBase):
    """Tests for the myself journey"""

    def test_located_in_uk(self):
        self.page.goto(PlaywrightTestBase.base_url)
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

    def test_add_another_individual_and_remove(self):
        self.page.goto(PlaywrightTestBase.base_url)
        self.myself(self.page)
        expect(self.page).to_have_url(re.compile(r".*/your-name-nationality-location"))
        self.provider_myself_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.provider_individual_located_in_uk(self.page)
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        expect(self.page.get_by_role("heading", name="You've added yourself plus 1 individual to the licence")).to_be_visible()
        self.page.get_by_role("button", name="Remove individual 1").click()
        expect(self.page).to_have_url(re.compile(r".*/check-your-details-add-individuals"))
        expect(self.page.get_by_role("heading", name="You've added yourself to the licence")).to_be_visible()
