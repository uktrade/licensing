from datetime import timedelta
from typing import Any

from core.crispy_fields import HTMLTemplate, get_field_with_label_id
from core.forms.base_forms import BaseBusinessDetailsForm, BaseForm, BaseModelForm
from core.utils import is_request_ratelimited
from crispy_forms_gds.choices import Choice
from crispy_forms_gds.layout import (
    ConditionalQuestion,
    ConditionalRadios,
    Field,
    Fieldset,
    Fluid,
    Layout,
    Size,
)
from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.timezone import now
from utils.companies_house import (
    get_details_from_companies_house,
    get_formatted_address,
)

from . import choices
from .exceptions import CompaniesHouse500Error, CompaniesHouseException
from .models import (
    Address,
    Applicant,
    ApplicationType,
    BaseApplication,
    ExistingLicences,
    Individual,
    Organisation,
    Regime,
    Services,
    UserEmailVerification,
)


class StartForm(BaseModelForm):
    class Meta:
        model = ApplicationType
        fields = ["who_do_you_want_the_licence_to_cover"]
        widgets = {
            "who_do_you_want_the_licence_to_cover": forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        CHOICES = (
            Choice(
                choices.WhoDoYouWantTheLicenceToCoverChoices.business.value,
                choices.WhoDoYouWantTheLicenceToCoverChoices.business.label,
                hint="The licence will cover all employees, members, partners, consultants, officers and directors",
            ),
            Choice(
                choices.WhoDoYouWantTheLicenceToCoverChoices.individual.value,
                choices.WhoDoYouWantTheLicenceToCoverChoices.individual.label,
                hint="The licence will cover the named individuals only but not the business they work for",
            ),
            Choice(
                choices.WhoDoYouWantTheLicenceToCoverChoices.myself.value,
                choices.WhoDoYouWantTheLicenceToCoverChoices.myself.label,
                hint="You can add other named individuals if they will be providing the services with you",
            ),
        )
        self.fields["who_do_you_want_the_licence_to_cover"].choices = CHOICES


class ThirdPartyForm(BaseForm):
    are_you_applying_on_behalf_of_someone_else = forms.TypedChoiceField(
        choices=choices.YES_NO_CHOICES,
        coerce=lambda x: x == "True",
        widget=forms.RadioSelect,
        label="Are you a third-party applying on behalf of a business you represent?",
        error_messages={"required": "Select yes if you're a third party applying on behalf of a business you represent"},
    )


class WhatIsYourEmailForm(BaseForm):
    email = forms.EmailField(
        label="What is your email address?",
        error_messages={
            "required": "Enter your email address",
            "invalid": "Enter a valid email address",
        },
    )


class YourDetailsForm(BaseModelForm):
    form_h1_header = "Your details"

    class Meta:
        model = Applicant
        fields = ["full_name", "business", "role"]
        labels = {
            "full_name": "Full name",
            "business": "Business you work for",
            "role": "Your role",
        }
        help_texts = {
            "business": "If you're a third-party agent, this is the business that employs you, "
            "not the business needing the licence",
        }
        error_messages = {
            "full_name": {"required": "Enter your full name"},
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout(
            Field.text("full_name", field_width=Fluid.TWO_THIRDS),
            Field.text("business", field_width=Fluid.TWO_THIRDS),
            Field.text("role", field_width=Fluid.TWO_THIRDS),
        )


class EmailVerifyForm(BaseForm):
    bold_labels = False
    form_h1_header = "We've sent you an email"
    revalidate_on_done = False

    email_verification_code = forms.CharField(
        label="Enter the 6 digit security code",
        error_messages={"required": "Enter the 6 digit security code we sent to your email"},
    )

    def clean_email_verification_code(self) -> str:
        # first we check if the request is rate-limited
        if is_request_ratelimited(self.request):
            raise forms.ValidationError("You've tried to verify your email too many times. Try again in 1 minute")

        email_verification_code = self.cleaned_data["email_verification_code"]
        email_verification_code = email_verification_code.replace(" ", "")

        verify_timeout_seconds = settings.EMAIL_VERIFY_TIMEOUT_SECONDS

        verification_objects = UserEmailVerification.objects.filter(user_session=self.request.session.session_key).latest(
            "date_created"
        )
        verify_code = verification_objects.email_verification_code
        if email_verification_code != verify_code:
            raise forms.ValidationError("Code is incorrect. Enter the 6 digit security code we sent to your email")

        # check if the user has submitted the verify code within the specified timeframe
        allowed_lapse = verification_objects.date_created + timedelta(seconds=verify_timeout_seconds)
        if allowed_lapse < now():
            raise forms.ValidationError("The code you entered is no longer valid. Please verify your email again")

        verification_objects.verified = True
        verification_objects.save()
        return email_verification_code

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.request = kwargs.pop("request") if "request" in kwargs else None
        request_verify_code = reverse_lazy("request_verify_code")
        self.helper["email_verification_code"].wrap(
            Field,
            HTMLTemplate(
                "apply_for_a_licence/form_steps/partials/not_received_code_help_text.html",
                {"request_verify_code": request_verify_code},
            ),
        )


class SummaryForm(BaseForm):
    pass


class ExistingLicencesForm(BaseModelForm):
    hide_optional_label_fields = ["licences"]

    class Meta:
        model = ExistingLicences
        fields = ("held_existing_licence", "licences")
        labels = {
            "licences": "Enter all previous licence numbers",
        }
        error_messages = {
            "held_existing_licence": {
                "required": "Select yes if the business has held a licence before to provide these services"
            },
            "licences": {"required": "Licence number cannot be blank"},
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["held_existing_licence"].empty_label = None
        # todo - abstract the following logic to apply to all ConditionalRadios forms
        self.helper.legend_tag = "h1"
        self.helper.legend_size = Size.LARGE
        self.helper.label_tag = ""
        self.helper.label_size = None
        self.helper.layout = Layout(
            ConditionalRadios(
                "held_existing_licence",
                ConditionalQuestion(
                    "Yes",
                    Field.text("licences", field_width=Fluid.TWO_THIRDS),
                ),
                "No",
            )
        )
        self.held_existing_licence_label = (
            "Have any of the businesses you've added held a licence before to provide sanctioned services?"
        )

        if start_view := self.request.session.get("StartView", False):
            if start_view.get("who_do_you_want_the_licence_to_cover") == "myself":
                self.held_existing_licence_label = (
                    "Have you, or has anyone else you've added, held a licence before to provide sanctioned services?"
                )
            elif start_view.get("who_do_you_want_the_licence_to_cover") == "individual":
                self.held_existing_licence_label = (
                    "Have any of the individuals you've added held a licence before to provide sanctioned services?"
                )
        self.fields["held_existing_licence"].label = self.held_existing_licence_label

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        if cleaned_data.get("held_existing_licence") == "yes" and not cleaned_data["licences"]:
            self.add_error("licences", self.Meta.error_messages["licences"]["required"])
        return cleaned_data


class IsTheBusinessRegisteredWithCompaniesHouseForm(BaseModelForm):
    class Meta:
        model = BaseApplication
        fields = ["business_registered_on_companies_house"]
        widgets = {"business_registered_on_companies_house": forms.RadioSelect}
        labels = {
            "business_registered_on_companies_house": "Is the business you want the "
            "licence to cover registered with UK Companies House?"
        }
        error_messages = {
            "business_registered_on_companies_house": {
                "required": "Select yes if the business you want the licence to cover is registered with UK Companies House"
            }
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["business_registered_on_companies_house"].choices.pop(0)


class DoYouKnowTheRegisteredCompanyNumberForm(BaseModelForm):
    hide_optional_label_fields = ["registered_company_number"]

    registered_company_name = forms.CharField(required=False)
    registered_office_address = forms.CharField(required=False)

    class Meta:
        model = Organisation
        fields = ["do_you_know_the_registered_company_number", "registered_company_number"]
        widgets = {"do_you_know_the_registered_company_number": forms.RadioSelect}
        labels = {
            "do_you_know_the_registered_company_number": "Do you know the registered company number?",
            "registered_company_number": "Registered company number",
        }
        error_messages = {
            "do_you_know_the_registered_company_number": {"required": "Select yes if you know the registered company number"},
            "registered_company_number": {
                "required": "Enter the registered company number",
                "invalid": "Number not recognised with Companies House. Enter the correct registered company number. "
                "This is usually an 8-digit number.",
            },
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        # emptying the form if the user has requested to change the details
        if self.request.GET.get("change") == "yes":
            self.is_bound = False
            self.data = {}

        # remove companies house 500 error if it exists
        self.request.session.pop("company_details_500", None)
        self.request.session.modified = True

        # todo - abstract the following logic to apply to all ConditionalRadios forms
        self.helper.legend_tag = "h1"
        self.helper.legend_size = Size.LARGE
        self.helper.label_tag = ""
        self.helper.label_size = None
        self.helper.layout = Layout(
            ConditionalRadios(
                "do_you_know_the_registered_company_number",
                ConditionalQuestion(
                    "Yes",
                    Field.text("registered_company_number", field_width=Fluid.ONE_THIRD),
                ),
                "No",
            )
        )

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        # first we check if the request is rate-limited
        if is_request_ratelimited(self.request):
            raise forms.ValidationError(
                "You've tried to enter the registered company number too many times. Try again in 1 minute"
            )

        do_you_know_the_registered_company_number = cleaned_data.get("do_you_know_the_registered_company_number")
        registered_company_number = cleaned_data.get("registered_company_number")
        if do_you_know_the_registered_company_number == "yes":
            if not registered_company_number:
                self.add_error(
                    "registered_company_number",
                    forms.ValidationError(
                        code="required", message=self.Meta.error_messages["registered_company_number"]["required"]
                    ),
                )
                # we don't need to continue if the company number is missing
                return cleaned_data

            try:
                company_details = get_details_from_companies_house(registered_company_number)
                cleaned_data["registered_company_number"] = company_details["company_number"]
                cleaned_data["registered_company_name"] = company_details["company_name"]
                cleaned_data["registered_office_address"] = get_formatted_address(company_details["registered_office_address"])
            except CompaniesHouseException:
                self.add_error(
                    "registered_company_number",
                    forms.ValidationError(
                        code="invalid", message=self.Meta.error_messages["registered_company_number"]["invalid"]
                    ),
                )
            except CompaniesHouse500Error:
                self.request.session["company_details_500"] = True
                self.request.session.modified = True

        return cleaned_data


class ManualCompaniesHouseInputForm(BaseForm):
    manual_companies_house_input = forms.ChoiceField(
        label="Where is the business located?",
        choices=(
            ("in_the_uk", "In the UK"),
            ("outside_the_uk", "Outside the UK"),
        ),
        widget=forms.RadioSelect,
        error_messages={
            "required": "Select if the address of the business suspected of "
            "breaching sanctions is in the UK, or outside the UK"
        },
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                Field.radios(
                    "manual_companies_house_input",
                    legend_size=Size.MEDIUM,
                )
            )
        )


class WhereIsTheBusinessLocatedForm(BaseForm):
    where_is_the_address = forms.ChoiceField(
        label="Where is the business located?",
        choices=(
            ("in_the_uk", "In the UK"),
            ("outside_the_uk", "Outside the UK"),
        ),
        widget=forms.RadioSelect,
        error_messages={"required": "Select if the business is located in the UK, or outside the UK"},
    )


class AddABusinessForm(BaseBusinessDetailsForm):
    form_h1_header = "Add a business"

    class Meta(BaseBusinessDetailsForm.Meta):
        model = Organisation
        fields = (
            "name",
            "town_or_city",
            "country",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "address_line_4",
            "county",
            "postcode",
        )
        widgets = BaseBusinessDetailsForm.Meta.widgets
        labels = BaseBusinessDetailsForm.Meta.labels
        error_messages = BaseBusinessDetailsForm.Meta.error_messages

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        # all fields on this form are optional. Except if it's a non-UK user, then we need the country at least
        for _, field in self.fields.items():
            field.required = False

        if not self.is_uk_address:
            self.fields["country"].required = True

        if self.is_uk_address:
            address_layout = Fieldset(
                Field.text("country", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_1", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_2", field_width=Fluid.ONE_THIRD),
                Field.text("town_or_city", field_width=Fluid.ONE_THIRD),
                Field.text("county", field_width=Fluid.ONE_THIRD),
                Field.text("postcode", field_width=Fluid.ONE_THIRD),
                legend="Address",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            )
        else:
            address_layout = Fieldset(
                Field.text("town_or_city", field_width=Fluid.ONE_THIRD),
                Field.text("country", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_1", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_2", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_3", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_4", field_width=Fluid.ONE_THIRD),
                legend="Address",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            )

        self.helper.layout = Layout(
            Fieldset(
                Field.text("name", field_width=Fluid.ONE_HALF),
                legend="Name",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            address_layout,
        )


class BusinessAddedForm(BaseForm):
    revalidate_on_done = False

    do_you_want_to_add_another_business = forms.TypedChoiceField(
        choices=(
            Choice(True, "Yes"),
            Choice(False, "No"),
        ),
        coerce=lambda x: x == "True",
        label="Do you want to add another business?",
        error_messages={"required": "Select yes if you want to add another business"},
        widget=forms.RadioSelect,
        required=True,
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.legend_size = Size.MEDIUM
        self.helper.legend_tag = None


class AddAnIndividualForm(BaseModelForm):
    form_h1_header = "Add an individual"

    class Meta:
        model = Individual
        fields = [
            "first_name",
            "last_name",
            "nationality_and_location",
        ]
        widgets = {"first_name": forms.TextInput, "last_name": forms.TextInput, "nationality_and_location": forms.RadioSelect}
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "nationality_and_location": "What is the individual's nationality and location?",
        }
        help_texts = {"nationality_and_location": "Hint text"}
        error_messages = {"first_name": {"required": "Enter your first name"}, "last_name": {"required": "Enter your last name"}}

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["nationality_and_location"].choices.pop(0)
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout(
            Field.text("first_name", field_width=Fluid.ONE_THIRD),
            Field.text("last_name", field_width=Fluid.ONE_THIRD),
            Field.radios("nationality_and_location", legend_size=Size.MEDIUM, legend_tag="h2"),
        )


class IndividualAddedForm(BaseForm):
    revalidate_on_done = False

    do_you_want_to_add_another_individual = forms.TypedChoiceField(
        choices=(
            Choice(True, "Yes"),
            Choice(False, "No"),
        ),
        coerce=lambda x: x == "True",
        label="Do you want to add another individual?",
        error_messages={"required": "Select yes if you want to add another individual"},
        widget=forms.RadioSelect,
        required=True,
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.legend_size = Size.MEDIUM
        self.helper.legend_tag = None


class BusinessEmployingIndividualForm(BaseBusinessDetailsForm):
    form_h1_header = "Details of the business employing the individual[s]"

    class Meta(BaseBusinessDetailsForm.Meta):
        model = Organisation
        fields = (
            "name",
            "country",
            "town_or_city",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "address_line_4",
            "county",
            "postcode",
        )
        widgets = BaseBusinessDetailsForm.Meta.widgets
        labels = BaseBusinessDetailsForm.Meta.labels
        error_messages = BaseBusinessDetailsForm.Meta.error_messages

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        # all fields on this form are optional except country
        for _, field in self.fields.items():
            field.required = False

        self.fields["country"].required = True

        self.helper.layout = Layout(
            Fieldset(
                Field.text("name", field_width=Fluid.ONE_HALF),
                legend="Name",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            Fieldset(
                Field.text("country", field_width=Fluid.ONE_THIRD),
                Field.text("town_or_city", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_1", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_2", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_3", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_4", field_width=Fluid.ONE_THIRD),
                legend="Address",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
        )


class AddYourselfForm(BaseModelForm):
    form_h1_header = "Your details"

    class Meta:
        model = Individual
        fields = [
            "first_name",
            "last_name",
            "nationality_and_location",
        ]
        widgets = {"first_name": forms.TextInput, "last_name": forms.TextInput, "nationality_and_location": forms.RadioSelect}
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "nationality_and_location": "What is your nationality and location?",
        }
        help_texts = {"nationality_and_location": "Hint text"}
        error_messages = {"first_name": {"required": "Enter your first name"}, "last_name": {"required": "Enter your last name"}}

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["nationality_and_location"].choices.pop(0)
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout(
            Field.text("first_name", field_width=Fluid.ONE_THIRD),
            Field.text("last_name", field_width=Fluid.ONE_THIRD),
            Field.radios("nationality_and_location", legend_size=Size.MEDIUM, legend_tag="h2"),
        )


class AddYourselfAddressForm(BaseBusinessDetailsForm):
    form_h1_header = "What is your work address?"

    class Meta(BaseBusinessDetailsForm.Meta):
        model = Address
        fields = (
            "town_or_city",
            "country",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "address_line_4",
            "county",
            "postcode",
        )
        widgets = BaseBusinessDetailsForm.Meta.widgets
        labels = BaseBusinessDetailsForm.Meta.labels
        error_messages = BaseBusinessDetailsForm.Meta.error_messages

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        # all fields on this form are optional. Except if it's a non-UK user, then we need the country at least
        for _, field in self.fields.items():
            field.required = False

        if not self.is_uk_address:
            self.fields["country"].required = True

        self.helper.layout = Layout(
            Field.text("town_or_city", field_width=Fluid.ONE_THIRD),
            Field.text("country", field_width=Fluid.ONE_THIRD),
            Field.text("address_line_1", field_width=Fluid.ONE_THIRD),
            Field.text("address_line_2", field_width=Fluid.ONE_THIRD),
            Field.text("address_line_3", field_width=Fluid.ONE_THIRD),
            Field.text("address_line_4", field_width=Fluid.ONE_THIRD),
            Field.text("county", field_width=Fluid.ONE_THIRD),
            Field.text("postcode", field_width=Fluid.ONE_THIRD),
        )


class TypeOfServiceForm(BaseModelForm):
    class Meta:
        model = Services
        fields = ["type_of_service"]
        widgets = {"type_of_service": forms.RadioSelect}
        error_messages = {
            "type_of_service": {
                "required": "Select the type of service you want to provide",
            }
        }
        labels = {
            "type_of_service": "What type of service do you want to provide?",
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["type_of_service"].choices.pop(0)


class WhichSanctionsRegimeForm(BaseForm):
    form_h1_header = "Which sanctions regime is the licence for?"

    which_sanctions_regime = forms.MultipleChoiceField(
        help_text=("Select all that apply"),
        widget=forms.CheckboxSelectMultiple,
        choices=(()),
        required=True,
        error_messages={
            "required": "Select the sanctions regime the licence is for",
        },
    )

    class Media:
        js = ["report_a_suspected_breach/javascript/which_sanctions_regime.js"]

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        checkbox_choices = []
        sanctions = Regime.objects.values("full_name")
        if professional_or_business_services := self.request.session.get("TypeOfServiceView", False):
            if professional_or_business_services.get("type_of_service", False) == "internet":
                sanctions = Regime.objects.filter(short_name__in=["Russia", "Belarus"]).values("full_name")

        for i, item in enumerate(sanctions):
            checkbox_choices.append(Choice(item["full_name"], item["full_name"]))

        self.fields["which_sanctions_regime"].choices = checkbox_choices
        self.fields["which_sanctions_regime"].label = False
        self.helper.label_size = None
        self.helper.label_tag = None
        self.helper.layout = Layout(
            Fieldset(
                get_field_with_label_id("which_sanctions_regime", field_method=Field.checkboxes, label_id="checkbox"),
                aria_describedby="checkbox",
            )
        )


class ProfessionalOrBusinessServicesForm(BaseModelForm):
    form_h1_header = "What are the professional or business services you want to provide?"
    professional_or_business_service = forms.MultipleChoiceField(
        help_text=("Select all that apply"),
        widget=forms.CheckboxSelectMultiple,
        choices=choices.ProfessionalOrBusinessServicesChoices.choices,
        required=True,
        error_messages={
            "required": "Select the professional or business services the licence is for",
        },
    )

    class Meta:
        model = Services
        fields = ["professional_or_business_service"]
        widgets = {"professional_or_business_service": forms.CheckboxSelectMultiple}
        help_texts = {"professional_or_business_service": "Select all that apply"}

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        self.fields["professional_or_business_service"].label = False


class ServiceActivitiesForm(BaseModelForm):
    class Meta:
        model = Services
        fields = ["service_activities"]
        labels = {
            "service_activities": "Describe the specific activities within the services you want to provide",
        }
        help_texts = {
            "service_activities": "Tell us about the services you want to provide. You will need to show how they "
            "match to the specific meaning of services in the sanctions regime that applies to your intended activity",
        }
        error_messages = {
            "service_activities": {"required": "Enter the specific activities within the services you want to provide"},
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["service_activities"].widget.attrs = {"rows": 5}

        if professional_or_business_services := self.request.session.get("TypeOfServiceView", False):
            if professional_or_business_services.get("type_of_service", False) == "professional_and_business":
                self.fields["service_activities"].help_text = render_to_string(
                    "apply_for_a_licence/form_steps/partials/professional_or_business_services.html"
                )
