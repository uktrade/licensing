import os

from django.conf import settings
from django.test.testcases import TransactionTestCase
from playwright.sync_api import sync_playwright

from . import data


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

    @classmethod
    def get_form_step_page(cls, form_step):
        print(f"{cls.base_url}/{form_step}/")
        return f"{cls.base_url}/report_a_suspected_breach/{form_step}/"

    @classmethod
    def email_details(cls, page, details=data.EMAIL_DETAILS):
        page.get_by_label("What is your email address?").fill(details["email"])
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def verify_email(cls, page, details=data.EMAIL_DETAILS):
        page.get_by_role("heading", name="We've sent you an email").click()
        page.get_by_label("Enter the 6 digit security").fill(details["verify_code"])
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def verify_email_details(cls, page, details=data.EMAIL_DETAILS):
        #
        # Email page
        #
        page = cls.email_details(page, details)
        #
        # Verify page
        #
        page = cls.verify_email(page, details)

        return page

    def fill_uk_address_details(cls, page, type, details=data.UK_ADDRESS_DETAILS):
        # UK Address Details Page
        if type == "recipient" or type == "business":
            page.get_by_label(f"Name of {type}").fill(details["name"])
        page.get_by_label("Address line 1").fill(details["address_line_1"])
        page.get_by_label("Town or city").fill(details["town"])
        page.get_by_label("Postcode").fill(details["postcode"])
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def fill_non_uk_address_details(cls, page, details=data.NON_UK_ADDRESS_DETAILS):
        # NON UK Address Details Page
        page.get_by_label("Name of business").fill(details["name"])
        page.get_by_label("Country").select_option(details["country"])
        page.get_by_label("Town").fill(details["town"])
        page.get_by_label("Address line 1").fill(details["address_line_1"])
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def declaration_and_complete_page(cls, page):
        #
        # Declaration Page
        #
        page.get_by_label("I agree and accept").check()
        page.get_by_role("button", name="Submit").click()
        #
        # Complete Page
        #
        return page

    def no_more_additions(cls, page):
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()

    def check_your_answers(cls, page):
        # TODO
        pass

    def your_details(cls, page, type, details=data.YOUR_DETAILS):
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


class StartBase(PlaywrightTestBase):
    def business_third_party(self, page):
        page.get_by_label("A business or businesses with").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Yes").check()
        page.get_by_role("button", name="Continue").click()
        self.verify_email_details(page)
        return page

    def business_not_third_party(self, page):
        page.get_by_label("A business or businesses with").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        self.verify_email_details(page)
        return page

    def individual_third_party(self, page):
        page.get_by_label("Named individuals with a UK").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Yes").check()
        page.get_by_role("button", name="Continue").click()
        self.verify_email_details(page)
        return page

    def myself(self, page):
        page.get_by_label("Myself").check()
        page.get_by_role("button", name="Continue").click()
        self.verify_email_details(page)
        return page


class ProviderBase(PlaywrightTestBase):
    def provider_business_located_in_uk(self, page):
        self.your_details(page, "business")
        page.get_by_label("No", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("In the UK").check()
        page.get_by_role("button", name="Continue").click()
        self.fill_uk_address_details(page, "business")
        return page

    def provider_business_located_outside_uk(self, page):
        self.your_details(page, "business")
        page.get_by_label("No", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Outside the UK").check()
        page.get_by_role("button", name="Continue").click()
        self.fill_non_uk_address_details(page)
        return page

    def provider_individual_located_in_uk(self, page):
        self.your_details(page, "individual")
        page.get_by_label("First name").fill("Test first name")
        page.get_by_label("Last name").fill("Test last name")
        page.get_by_label("UK national located in the UK", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        self.fill_uk_address_details(page, "individual")
        return page

    def provider_myself_located_in_uk(self, page):
        self.your_details(page, "myself")
        self.fill_uk_address_details(page, "individual")
        return page


class RecipientBase(PlaywrightTestBase):
    def recipient_simple(self, page, type):
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        if type == "individual":
            self.fill_non_uk_address_details(page)
        page.get_by_label("Energy-related services (").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Describe the specific").fill("Test description")
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("In the UK").check()
        page.get_by_role("button", name="Continue").click()
        self.fill_uk_address_details(page, "recipient")
        page.get_by_label("What is the relationship").fill("Test relationship")
        page.get_by_role("button", name="Continue").click()


class LicensingGroundsBase(PlaywrightTestBase):
    def licensing_grounds_simple(self, page):
        page.get_by_label("What is your purpose for").fill("Test purpose")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("button", name="Continue").click()
