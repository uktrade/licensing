from typing import Any

from apply_for_a_licence.exceptions import (
    CompaniesHouse500Error,
    CompaniesHouseException,
)
from apply_for_a_licence.models import BaseApplication, Organisation
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
from utils.companies_house import (
    get_details_from_companies_house,
    get_formatted_address,
)


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
            "required": "Select if the address of the business you would like the licence for is in the UK, or outside the UK"
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