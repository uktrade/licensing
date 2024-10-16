import os
import re

from django.conf import settings
from django.test.testcases import TransactionTestCase
from playwright.sync_api import expect, sync_playwright

from tests.test_frontend.fixtures import data


class PlaywrightTestBase(TransactionTestCase):
    create_new_test_breach = True
    base_url = settings.BASE_FRONTEND_TESTING_URL

    @classmethod
    def setUpClass(cls):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=settings.HEADLESS)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def setUp(self) -> None:
        """Create a new page for each test"""
        self.page = self.browser.new_page()

    def tearDown(self) -> None:
        """Close the page after each test"""
        self.page.close()

    def get_form_step_page(cls, form_step):
        return f"{cls.base_url}/report_a_suspected_breach/{form_step}/"

    def email_details(cls, page, details=data.EMAIL_DETAILS):
        page.get_by_label("What is your email address?").fill(details["email"])
        page.get_by_role("button", name="Continue").click()

    def verify_email(cls, page, details=data.EMAIL_DETAILS):
        page.get_by_role("heading", name="We've sent you an email").click()
        page.get_by_label("Enter the 6 digit security").fill(details["verify_code"])
        page.get_by_role("button", name="Continue").click()

    def verify_email_details(cls, page):
        cls.email_details(page)
        cls.verify_email(page)

    def fill_uk_address_details(cls, page, type="business", details=data.UK_ADDRESS_DETAILS):
        if type == "recipient" or type == "business":
            page.get_by_label(f"Name of {type}").fill(details["name"])
        page.get_by_label("Address line 1").fill(details["address_line_1"])
        page.get_by_label("Town or city").fill(details["town"])
        page.get_by_label("Postcode").fill(details["postcode"])
        page.get_by_role("button", name="Continue").click()

    def fill_non_uk_address_details(cls, page, type="business", details=data.NON_UK_ADDRESS_DETAILS):
        if type == "recipient" or type == "business":
            page.get_by_label(f"Name of {type}").fill(details["name"])
        page.get_by_label("Country").select_option(details["country"])
        page.get_by_label("Town").fill(details["town"])
        page.get_by_label("Address line 1").fill(details["address_line_1"])
        page.get_by_role("button", name="Continue").click()

    def declaration_and_complete_page(cls, page):
        page.get_by_label("I agree and accept").check()
        page.get_by_role("button", name="Submit").click()

    def no_more_additions(cls, page):
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()

    def your_details(cls, page, type="business", details=data.YOUR_DETAILS):
        if type == "myself":
            page.get_by_label("First name").fill("Test first name")
            page.get_by_label("Last name").fill("Test last name")
            page.get_by_label("UK national located in the UK", exact=True).check()
            page.get_by_role("button", name="Continue").click()
        else:
            page.get_by_label("Full name").fill(details["full_name"])
            page.get_by_label("Business you work for").fill(details["business"])
            page.get_by_label("Your role").fill(details["role"])
            page.get_by_role("button", name="Continue").click()

    def check_your_answers(cls, page, third_party=True, type="business"):
        expect(page).to_have_url(re.compile(r".*/check-your-answers"))
        if type != "myself":
            cls.cya_your_details(page, third_party)
        expect(page.get_by_test_id("previous-licence")).to_have_text("No")
        cls.cya_overview(page)
        cls.cya_recipients(page)
        cls.cya_purposes(page)

    def cya_your_details(cls, page, third_party):
        expect(page.get_by_test_id("your-details-name")).to_have_text("Test full name")
        expect(page.get_by_test_id("your-details-business")).to_have_text("Test business")
        expect(page.get_by_test_id("your-details-role")).to_have_text("Test role")
        if third_party:
            expect(page.get_by_test_id("your-details-third-party")).to_have_text("Yes")
        else:
            expect(page.get_by_test_id("your-details-third-party")).to_have_text("No")

    def cya_overview(cls, page):
        expect(page.get_by_test_id("services-type")).to_have_text("Energy-related services (Russia)")
        expect(page.get_by_test_id("services-description")).to_have_text("Test description")

    def cya_recipients(cls, page):
        expect(page.get_by_test_id("recipient-name-and-address")).to_have_text("business\nA1, Town, AA0 0AA, United Kingdom")
        expect(page.get_by_test_id("recipient-relationship")).to_have_text("Test relationship")

    def cya_purposes(cls, page):
        expect(page.get_by_test_id("purpose")).to_have_text("Test purpose")
        expect(page.get_by_test_id("supporting-documents")).to_have_text("None uploaded")

    def check_submission_complete_page(cls, page):
        expect(page).to_have_url(re.compile(r".*/application-complete"))
        expect(page.locator("text=Submission complete")).to_be_visible()
        expect(page.locator("text=Your reference number")).to_be_visible()


class StartBase(PlaywrightTestBase):
    def business_third_party(self, page):
        page.get_by_label("A business or businesses with").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Yes").check()
        page.get_by_role("button", name="Continue").click()
        self.verify_email_details(page)

    def business_not_third_party(self, page):
        page.get_by_label("A business or businesses with").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        self.verify_email_details(page)

    def individual_third_party(self, page):
        page.get_by_label("Named individuals with a UK").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Yes").check()
        page.get_by_role("button", name="Continue").click()
        self.verify_email_details(page)

    def myself(self, page):
        page.get_by_label("Myself").check()
        page.get_by_role("button", name="Continue").click()
        self.verify_email_details(page)


class ProviderBase(PlaywrightTestBase):
    def provider_business_located_in_uk(self, page):
        self.your_details(page, "business")
        page.get_by_label("No", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("In the UK").check()
        page.get_by_role("button", name="Continue").click()
        self.fill_uk_address_details(page, "business")

    def provider_business_located_outside_uk(self, page):
        self.your_details(page, "business")
        page.get_by_label("No", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Outside the UK").check()
        page.get_by_role("button", name="Continue").click()
        self.fill_non_uk_address_details(page)

    def provider_individual_located_in_uk(self, page, first_individual_added=False):
        if first_individual_added:
            self.your_details(page, "individual")
        page.get_by_label("First name").fill("Test first name")
        page.get_by_label("Last name").fill("Test last name")
        page.get_by_label("UK national located in the UK", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        self.fill_uk_address_details(page, "individual")

    def provider_myself_located_in_uk(self, page):
        self.your_details(page, "myself")
        self.fill_uk_address_details(page, "individual")


class RecipientBase(PlaywrightTestBase):
    def recipient(self, page, service_type):
        page.get_by_label(service_type).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Describe the specific").fill("Test description")
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("In the UK").check()
        page.get_by_role("button", name="Continue").click()
        self.fill_uk_address_details(page, "recipient")
        page.get_by_label("What is the relationship").fill("Test relationship")
        page.get_by_role("button", name="Continue").click()

    def recipient_simple(self, page, reporter_type="business"):
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        if reporter_type == "individual":
            self.fill_non_uk_address_details(page)
        self.recipient(page, "Energy-related services (")

    def recipient_legal(self, page, reporter_type="business"):
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        if reporter_type == "individual":
            self.fill_non_uk_address_details(page)
        page.get_by_label("Professional and business").check()
        page.get_by_role("button", name="Continue").click()
        self.recipient(page, "Legal advisory")

    def recipient_non_legal(self, page, reporter_type="business"):
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        if reporter_type == "individual":
            self.fill_non_uk_address_details(page)
        page.get_by_label("Professional and business").check()
        page.get_by_role("button", name="Continue").click()
        self.recipient(page, "Auditing")

    def recipient_legal_and_other(self, page, reporter_type="business"):
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        if reporter_type == "individual":
            self.fill_non_uk_address_details(page)
        page.get_by_label("Professional and business").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Auditing").check()
        self.recipient(page, "Legal advisory")


class LicensingGroundsBase(PlaywrightTestBase):
    def licensing_grounds_simple(self, page):
        page.get_by_label("What is your purpose for").fill("Test purpose")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("button", name="Continue").click()
