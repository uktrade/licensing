from typing import Any

from core.forms.base_forms import BaseModelForm
from crispy_forms_gds.layout import Field, Fieldset, Layout, Size
from django import forms

from .choices import DidYouExperienceAnyIssues
from .crispy_fields import HTMLTemplate, get_field_with_label_id
from .models import FeedbackItem


class FeedbackForm(BaseModelForm):
    submit_button_text = "Submit"

    did_you_experience_any_issues = forms.MultipleChoiceField(
        choices=DidYouExperienceAnyIssues.choices,
        widget=forms.CheckboxSelectMultiple,
        label="Did you experience any of the following issues?",
        required=False,
    )

    class Meta:
        model = FeedbackItem
        fields = ("rating", "did_you_experience_any_issues", "how_we_could_improve_the_service")
        labels = {
            "how_we_could_improve_the_service": "How could we improve the service?",
            "rating": "Overall, how satisfied did you feel with using this service?",
        }
        widgets = {
            "rating": forms.RadioSelect,
        }

    class Media:
        js = ["feedback/javascript/feedback.js"]
        css = {
            "all": ["feedback/stylesheets/feedback.css"],
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["rating"].choices.pop(0)
        self.helper.layout = Layout(
            Field.radios("rating", legend_size=Size.MEDIUM, legend_tag="h2"),
            Fieldset(
                Field.checkboxes("did_you_experience_any_issues", legend=""),
                legend="What did not work so well? (optional)",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
                css_class="optional_question",
            ),
            Fieldset(
                get_field_with_label_id(
                    "how_we_could_improve_the_service",
                    label_id="how_we_could_improve_the_service-label",
                    field_method=Field.textarea,
                    rows=5,
                    label_size=Size.MEDIUM,
                    label_tag="h2",
                    max_characters=1200,
                    aria_describedby="how_we_could_improve_the_service-label",
                ),
                css_class="optional_question",
            ),
            HTMLTemplate("feedback/feedback_disclaimer.html"),
        )
