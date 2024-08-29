import pytest
from apply_for_a_licence.choices import (
    LicensingGroundsChoices,
    TypeOfRelationshipChoices,
)
from django.forms import model_to_dict
from utils.companies_house import get_formatted_address

from tests.factories import IndividualFactory, LicenceFactory, OrganisationFactory


@pytest.mark.django_db
class TestLicenceModel:
    def test_assign_reference(self):
        licence = LicenceFactory()
        licence.reference = None
        licence.assign_reference()
        assert licence.reference
        assert len(licence.reference) == 6
        assert licence.reference.isupper()

    def test_recipients(self):
        licence = LicenceFactory()
        assert licence.recipients.count() == 0

        # add recipients
        organisation1 = OrganisationFactory(licence=licence, type_of_relationship=TypeOfRelationshipChoices.recipient)
        OrganisationFactory(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)

        assert licence.recipients.count() == 1
        assert licence.recipients.get() == organisation1

    def test_licensing_grounds_display(self):
        licence = LicenceFactory(
            licensing_grounds=[LicensingGroundsChoices.civil_society.value, LicensingGroundsChoices.energy.value]
        )
        assert licence.get_licensing_grounds_display() == [
            LicensingGroundsChoices.civil_society.label,
            LicensingGroundsChoices.energy.label,
        ]

    def test_get_licensees(self):
        licence = LicenceFactory(who_do_you_want_the_licence_to_cover="business")
        organisation = OrganisationFactory(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)
        licensees = licence.licensees()

        assert len(licensees) == 1
        assert licensees[0].name == organisation.name
        assert licensees[0].address == organisation.registered_office_address
        assert licensees[0].label_name == "Business"

        licence = LicenceFactory(who_do_you_want_the_licence_to_cover="individual")
        individual = IndividualFactory(licence=licence)

        licensees = licence.licensees()
        assert len(licensees) == 1
        assert licensees[0].name == individual.full_name
        assert licensees[0].address == get_formatted_address(model_to_dict(individual))
        assert licensees[0].label_name == "Individual"
