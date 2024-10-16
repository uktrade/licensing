# Generated by Django 4.2.14 on 2024-09-02 10:14

import core.document_storage
from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import simple_history.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("sessions", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Licence",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "licensing_grounds",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[
                                (
                                    "civil_society",
                                    "Civil society activities that directly promote democracy, human rights or the rule of law in Russia",
                                ),
                                ("energy", "Services necessary for ensuring critical energy supply to any country"),
                                (
                                    "divest",
                                    "Services necessary for non - Russian persons to divest from Russia, or to wind down business operations in Russia",
                                ),
                                ("humanitarian", "The delivery of humanitarian assistance activity"),
                                (
                                    "parent_or_subsidiary_company",
                                    "Services to a person connected with Russia by a UK parent company or UK subsidiary of that parent company",
                                ),
                                (
                                    "medical_and_pharmaceutical",
                                    "Medical and pharmaceutical purposes for the benefit of the civilian population",
                                ),
                                (
                                    "safety",
                                    "Services required to enable activities necessary for the urgent prevention or mitigation of an event likely to have a serious and significant impact on human health or safety, including the safety of existing infrastructure, or the environment",
                                ),
                                (
                                    "food",
                                    "Services in connection with the production or distribution of food for the benefit of the civilian population",
                                ),
                            ]
                        ),
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "licensing_grounds_legal_advisory",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[
                                (
                                    "civil_society",
                                    "Civil society activities that directly promote democracy, human rights or the rule of law in Russia",
                                ),
                                ("energy", "Services necessary for ensuring critical energy supply to any country"),
                                (
                                    "divest",
                                    "Services necessary for non - Russian persons to divest from Russia, or to wind down business operations in Russia",
                                ),
                                ("humanitarian", "The delivery of humanitarian assistance activity"),
                                (
                                    "parent_or_subsidiary_company",
                                    "Services to a person connected with Russia by a UK parent company or UK subsidiary of that parent company",
                                ),
                                (
                                    "medical_and_pharmaceutical",
                                    "Medical and pharmaceutical purposes for the benefit of the civilian population",
                                ),
                                (
                                    "safety",
                                    "Services required to enable activities necessary for the urgent prevention or mitigation of an event likely to have a serious and significant impact on human health or safety, including the safety of existing infrastructure, or the environment",
                                ),
                                (
                                    "food",
                                    "Services in connection with the production or distribution of food for the benefit of the civilian population",
                                ),
                            ]
                        ),
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "regimes",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=255), blank=True, null=True, size=None
                    ),
                ),
                ("reference", models.CharField(max_length=6)),
                (
                    "business_registered_on_companies_house",
                    models.CharField(choices=[("yes", "Yes"), ("no", "No"), ("do_not_know", "I do not know")], max_length=11),
                ),
                (
                    "type_of_service",
                    models.CharField(
                        choices=[
                            ("professional_and_business", "Professional and business services (Russia)"),
                            ("energy_related", "Energy-related services (Russia)"),
                            (
                                "infrastructure_and_tourism_related",
                                "Infrastructure and tourism-related services to non-government controlled Ukrainian territories (Russia)",
                            ),
                            (
                                "interception_or_monitoring",
                                "Interception or monitoring services (Russia, Belarus, Iran, Myanmar, Syria and Venezuela)",
                            ),
                            (
                                "mining_manufacturing_or_computer",
                                "Mining manufacturing or computer services (Democratic People's Republic of Korea",
                            ),
                            (
                                "ships_or_aircraft_related",
                                "Ships or aircraft-related services (Democratic People's Republic of Korea)",
                            ),
                        ]
                    ),
                ),
                ("professional_or_business_service", models.CharField()),
                ("service_activities", models.TextField()),
                ("description_provision", models.TextField(blank=True, null=True)),
                ("purpose_of_provision", models.TextField(blank=True, null=True)),
                ("held_existing_licence", models.CharField(choices=[("yes", "Yes"), ("no", "No")], null=True)),
                ("existing_licences", models.TextField(blank=True, null=True)),
                ("is_third_party", models.BooleanField(null=True)),
                (
                    "who_do_you_want_the_licence_to_cover",
                    models.CharField(
                        choices=[
                            ("business", "A business or several businesses"),
                            ("individual", "A named individual or several named individuals"),
                            ("myself", "Myself"),
                        ],
                        max_length=255,
                    ),
                ),
                ("applicant_user_email_address", models.EmailField(blank=True, max_length=254, null=True)),
                ("applicant_full_name", models.CharField(max_length=255, null=True)),
                ("applicant_business", models.CharField(max_length=300, null=True, verbose_name="Business you work for")),
                ("applicant_role", models.CharField(max_length=255, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="UserEmailVerification",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("email_verification_code", models.CharField(max_length=6)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("verified", models.BooleanField(default=False)),
                ("user_session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="sessions.session")),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Organisation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("address_line_1", models.CharField(blank=True, max_length=200, null=True)),
                ("address_line_2", models.CharField(blank=True, max_length=200, null=True)),
                ("address_line_3", models.CharField(blank=True, max_length=200, null=True)),
                ("address_line_4", models.CharField(blank=True, max_length=200, null=True)),
                ("postcode", models.CharField(blank=True, max_length=20, null=True)),
                ("country", django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ("town_or_city", models.CharField(blank=True, max_length=250, null=True)),
                ("county", models.CharField(blank=True, max_length=250, null=True)),
                ("name", models.CharField()),
                ("website", models.URLField(blank=True, null=True)),
                (
                    "do_you_know_the_registered_company_number",
                    models.CharField(choices=[("yes", "Yes"), ("no", "No")], null=True),
                ),
                ("registered_company_number", models.CharField(blank=True, max_length=15, null=True)),
                ("registered_office_address", models.CharField(blank=True, null=True)),
                ("email", models.EmailField(blank=True, max_length=254, null=True)),
                ("additional_contact_details", models.CharField(blank=True, null=True)),
                (
                    "type_of_relationship",
                    models.CharField(
                        choices=[
                            ("recipient", "Recipient"),
                            ("business", "Business"),
                            ("named_individuals", "Named Individuals"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "relationship_provider",
                    models.TextField(
                        blank=True, db_comment="what is the relationship between the provider and the recipient?", null=True
                    ),
                ),
                (
                    "licence",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="organisations",
                        to="apply_for_a_licence.licence",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="licence",
            name="user_email_verification",
            field=models.OneToOneField(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to="apply_for_a_licence.useremailverification"
            ),
        ),
        migrations.CreateModel(
            name="Individual",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("address_line_1", models.CharField(blank=True, max_length=200, null=True)),
                ("address_line_2", models.CharField(blank=True, max_length=200, null=True)),
                ("address_line_3", models.CharField(blank=True, max_length=200, null=True)),
                ("address_line_4", models.CharField(blank=True, max_length=200, null=True)),
                ("postcode", models.CharField(blank=True, max_length=20, null=True)),
                ("country", django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ("town_or_city", models.CharField(blank=True, max_length=250, null=True)),
                ("county", models.CharField(blank=True, max_length=250, null=True)),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                (
                    "nationality_and_location",
                    models.CharField(
                        choices=[
                            ("uk_national_uk_location", "UK national located in the UK"),
                            ("uk_national_non_uk_location", "UK national located outside the UK"),
                            ("dual_national_uk_location", "Dual national (includes UK) located in the UK"),
                            ("dual_national_non_uk_location", "Dual national (includes UK) located outside the UK"),
                            ("non_uk_national_uk_location", "Non-UK national located in the UK"),
                        ]
                    ),
                ),
                ("additional_contact_details", models.CharField(blank=True, null=True)),
                (
                    "relationship_provider",
                    models.TextField(
                        blank=True, db_comment="what is the relationship between the provider and the recipient?", null=True
                    ),
                ),
                (
                    "licence",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="individuals", to="apply_for_a_licence.licence"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="HistoricalUserEmailVerification",
            fields=[
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("modified_at", models.DateTimeField(blank=True, editable=False)),
                ("id", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ("email_verification_code", models.CharField(max_length=6)),
                ("date_created", models.DateTimeField(blank=True, editable=False)),
                ("verified", models.BooleanField(default=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_type", models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1)),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "user_session",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="sessions.session",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical user email verification",
                "verbose_name_plural": "historical user email verifications",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalOrganisation",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("modified_at", models.DateTimeField(blank=True, editable=False)),
                ("address_line_1", models.CharField(blank=True, max_length=200, null=True)),
                ("address_line_2", models.CharField(blank=True, max_length=200, null=True)),
                ("address_line_3", models.CharField(blank=True, max_length=200, null=True)),
                ("address_line_4", models.CharField(blank=True, max_length=200, null=True)),
                ("postcode", models.CharField(blank=True, max_length=20, null=True)),
                ("country", django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ("town_or_city", models.CharField(blank=True, max_length=250, null=True)),
                ("county", models.CharField(blank=True, max_length=250, null=True)),
                ("name", models.CharField()),
                ("website", models.URLField(blank=True, null=True)),
                (
                    "do_you_know_the_registered_company_number",
                    models.CharField(choices=[("yes", "Yes"), ("no", "No")], null=True),
                ),
                ("registered_company_number", models.CharField(blank=True, max_length=15, null=True)),
                ("registered_office_address", models.CharField(blank=True, null=True)),
                ("email", models.EmailField(blank=True, max_length=254, null=True)),
                ("additional_contact_details", models.CharField(blank=True, null=True)),
                (
                    "type_of_relationship",
                    models.CharField(
                        choices=[
                            ("recipient", "Recipient"),
                            ("business", "Business"),
                            ("named_individuals", "Named Individuals"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "relationship_provider",
                    models.TextField(
                        blank=True, db_comment="what is the relationship between the provider and the recipient?", null=True
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_type", models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1)),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "licence",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="apply_for_a_licence.licence",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical organisation",
                "verbose_name_plural": "historical organisations",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalLicence",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("modified_at", models.DateTimeField(blank=True, editable=False)),
                (
                    "licensing_grounds",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[
                                (
                                    "civil_society",
                                    "Civil society activities that directly promote democracy, human rights or the rule of law in Russia",
                                ),
                                ("energy", "Services necessary for ensuring critical energy supply to any country"),
                                (
                                    "divest",
                                    "Services necessary for non - Russian persons to divest from Russia, or to wind down business operations in Russia",
                                ),
                                ("humanitarian", "The delivery of humanitarian assistance activity"),
                                (
                                    "parent_or_subsidiary_company",
                                    "Services to a person connected with Russia by a UK parent company or UK subsidiary of that parent company",
                                ),
                                (
                                    "medical_and_pharmaceutical",
                                    "Medical and pharmaceutical purposes for the benefit of the civilian population",
                                ),
                                (
                                    "safety",
                                    "Services required to enable activities necessary for the urgent prevention or mitigation of an event likely to have a serious and significant impact on human health or safety, including the safety of existing infrastructure, or the environment",
                                ),
                                (
                                    "food",
                                    "Services in connection with the production or distribution of food for the benefit of the civilian population",
                                ),
                            ]
                        ),
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "licensing_grounds_legal_advisory",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[
                                (
                                    "civil_society",
                                    "Civil society activities that directly promote democracy, human rights or the rule of law in Russia",
                                ),
                                ("energy", "Services necessary for ensuring critical energy supply to any country"),
                                (
                                    "divest",
                                    "Services necessary for non - Russian persons to divest from Russia, or to wind down business operations in Russia",
                                ),
                                ("humanitarian", "The delivery of humanitarian assistance activity"),
                                (
                                    "parent_or_subsidiary_company",
                                    "Services to a person connected with Russia by a UK parent company or UK subsidiary of that parent company",
                                ),
                                (
                                    "medical_and_pharmaceutical",
                                    "Medical and pharmaceutical purposes for the benefit of the civilian population",
                                ),
                                (
                                    "safety",
                                    "Services required to enable activities necessary for the urgent prevention or mitigation of an event likely to have a serious and significant impact on human health or safety, including the safety of existing infrastructure, or the environment",
                                ),
                                (
                                    "food",
                                    "Services in connection with the production or distribution of food for the benefit of the civilian population",
                                ),
                            ]
                        ),
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "regimes",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=255), blank=True, null=True, size=None
                    ),
                ),
                ("reference", models.CharField(max_length=6)),
                (
                    "business_registered_on_companies_house",
                    models.CharField(choices=[("yes", "Yes"), ("no", "No"), ("do_not_know", "I do not know")], max_length=11),
                ),
                (
                    "type_of_service",
                    models.CharField(
                        choices=[
                            ("professional_and_business", "Professional and business services (Russia)"),
                            ("energy_related", "Energy-related services (Russia)"),
                            (
                                "infrastructure_and_tourism_related",
                                "Infrastructure and tourism-related services to non-government controlled Ukrainian territories (Russia)",
                            ),
                            (
                                "interception_or_monitoring",
                                "Interception or monitoring services (Russia, Belarus, Iran, Myanmar, Syria and Venezuela)",
                            ),
                            (
                                "mining_manufacturing_or_computer",
                                "Mining manufacturing or computer services (Democratic People's Republic of Korea",
                            ),
                            (
                                "ships_or_aircraft_related",
                                "Ships or aircraft-related services (Democratic People's Republic of Korea)",
                            ),
                        ]
                    ),
                ),
                ("professional_or_business_service", models.CharField()),
                ("service_activities", models.TextField()),
                ("description_provision", models.TextField(blank=True, null=True)),
                ("purpose_of_provision", models.TextField(blank=True, null=True)),
                ("held_existing_licence", models.CharField(choices=[("yes", "Yes"), ("no", "No")], null=True)),
                ("existing_licences", models.TextField(blank=True, null=True)),
                ("is_third_party", models.BooleanField(null=True)),
                (
                    "who_do_you_want_the_licence_to_cover",
                    models.CharField(
                        choices=[
                            ("business", "A business or several businesses"),
                            ("individual", "A named individual or several named individuals"),
                            ("myself", "Myself"),
                        ],
                        max_length=255,
                    ),
                ),
                ("applicant_user_email_address", models.EmailField(blank=True, max_length=254, null=True)),
                ("applicant_full_name", models.CharField(max_length=255, null=True)),
                ("applicant_business", models.CharField(max_length=300, null=True, verbose_name="Business you work for")),
                ("applicant_role", models.CharField(max_length=255, null=True)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_type", models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1)),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "user_email_verification",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="apply_for_a_licence.useremailverification",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical licence",
                "verbose_name_plural": "historical licences",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalIndividual",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("modified_at", models.DateTimeField(blank=True, editable=False)),
                ("address_line_1", models.CharField(blank=True, max_length=200, null=True)),
                ("address_line_2", models.CharField(blank=True, max_length=200, null=True)),
                ("address_line_3", models.CharField(blank=True, max_length=200, null=True)),
                ("address_line_4", models.CharField(blank=True, max_length=200, null=True)),
                ("postcode", models.CharField(blank=True, max_length=20, null=True)),
                ("country", django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ("town_or_city", models.CharField(blank=True, max_length=250, null=True)),
                ("county", models.CharField(blank=True, max_length=250, null=True)),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                (
                    "nationality_and_location",
                    models.CharField(
                        choices=[
                            ("uk_national_uk_location", "UK national located in the UK"),
                            ("uk_national_non_uk_location", "UK national located outside the UK"),
                            ("dual_national_uk_location", "Dual national (includes UK) located in the UK"),
                            ("dual_national_non_uk_location", "Dual national (includes UK) located outside the UK"),
                            ("non_uk_national_uk_location", "Non-UK national located in the UK"),
                        ]
                    ),
                ),
                ("additional_contact_details", models.CharField(blank=True, null=True)),
                (
                    "relationship_provider",
                    models.TextField(
                        blank=True, db_comment="what is the relationship between the provider and the recipient?", null=True
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_type", models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1)),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "licence",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="apply_for_a_licence.licence",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical individual",
                "verbose_name_plural": "historical individuals",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalDocument",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("modified_at", models.DateTimeField(blank=True, editable=False)),
                ("file", models.TextField(blank=True, max_length=100, null=True)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_type", models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1)),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "licence",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="apply_for_a_licence.licence",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical document",
                "verbose_name_plural": "historical documents",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="Document",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "file",
                    models.FileField(
                        blank=True, null=True, storage=core.document_storage.PermanentDocumentStorage(), upload_to=""
                    ),
                ),
                (
                    "licence",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="apply_for_a_licence.licence"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
