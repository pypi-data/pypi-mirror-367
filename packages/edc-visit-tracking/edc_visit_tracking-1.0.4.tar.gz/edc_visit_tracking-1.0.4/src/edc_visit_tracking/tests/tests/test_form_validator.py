from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django import forms
from django.test import TestCase
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_constants.constants import ALIVE, OTHER, YES
from edc_facility.import_holidays import import_holidays
from edc_form_validators import APPLICABLE_ERROR, REQUIRED_ERROR
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED, UNSCHEDULED
from edc_visit_tracking.form_validators import VisitFormValidator
from edc_visit_tracking.models import SubjectVisit
from visit_tracking_app.consents import consent_v1
from visit_tracking_app.visit_schedule import visit_schedule1, visit_schedule2

from ..helper import Helper

utc_tz = ZoneInfo("UTC")


@time_machine.travel(datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz))
class TestSubjectVisitFormValidator(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        self.subject_identifier = "12345"
        site_consents.registry = {}
        site_consents.register(consent_v1)
        self.helper = self.helper_cls(subject_identifier=self.subject_identifier)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        self.appointment = Appointment.objects.all().order_by("timepoint_datetime")[0]

    def test_form_validator_ok(self):
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]
        subject_visit = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        cleaned_data = dict(
            appointment=appointment,
            reason=SCHEDULED,
            is_present=YES,
            survival_status=ALIVE,
            last_alive_date=get_utcnow().date(),
        )
        form_validator = VisitFormValidator(cleaned_data=cleaned_data, instance=subject_visit)
        form_validator.validate()

    def test_visit_code_reason_with_visit_code_sequence_0(self):
        cleaned_data = {"appointment": self.appointment, "reason": UNSCHEDULED}
        form_validator = VisitFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn("reason", form_validator._errors)

    @patch("edc_appointment.form_validators.utils.get_appointment_url")
    def test_visit_code_reason_with_visit_code_sequence_1(self, mock_urlnames):
        mock_urlnames.return_value = ""
        SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)

        opts = self.appointment.__dict__
        opts.pop("_state")
        opts.pop("id")
        opts.pop("created")
        opts.pop("modified")
        opts.update(
            visit_code_sequence=1,
            appt_datetime=self.appointment.appt_datetime + relativedelta(days=1),
        )
        appointment = Appointment.objects.create(**opts)

        cleaned_data = {"appointment": appointment, "reason": SCHEDULED}
        form_validator = VisitFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn("reason", form_validator._errors)

    def test_visit_code_reason_with_visit_code_sequence_2(self):
        SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)

        opts = self.appointment.__dict__
        opts.pop("_state")
        opts.pop("id")
        opts.pop("created")
        opts.pop("modified")
        opts.update(
            visit_code_sequence=1,
            appt_datetime=self.appointment.appt_datetime + relativedelta(days=1),
        )
        Appointment.objects.create(**opts)
        opts.update(
            visit_code_sequence=2,
            appt_datetime=self.appointment.appt_datetime + relativedelta(days=2),
        )
        appointment = Appointment.objects.create(**opts)

        cleaned_data = {"appointment": appointment, "reason": SCHEDULED}
        form_validator = VisitFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn(
            "Previous visit report required",
            ",".join([str(e) for e in form_validator._errors.values()]),
        )
        self.assertIn("1000.1", ",".join([str(e) for e in form_validator._errors.values()]))

    def test_reason_missed(self):
        options = {
            "appointment": self.appointment,
            "reason": MISSED_VISIT,
            "reason_missed": None,
        }
        form_validator = VisitFormValidator(cleaned_data=options)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn("reason_missed", form_validator._errors)

    @patch("edc_appointment.form_validators.utils.get_appointment_url")
    def test_reason_unscheduled(self, mock_urlnames):
        mock_urlnames.return_value = ""
        SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)

        # create unscheduled appointment (XXXX.1)
        opts = self.appointment.__dict__
        opts.pop("_state")
        opts.pop("id")
        opts.pop("created")
        opts.pop("modified")
        opts.update(
            appt_datetime=self.appointment.appt_datetime + relativedelta(days=1),
            visit_code_sequence=1,
        )
        appointment = Appointment.objects.create(**opts)
        # start subject visit form with unscheduled appointment
        options = {
            "appointment": appointment,
            "reason": UNSCHEDULED,
            "reason_unscheduled": None,
        }
        form_validator = VisitFormValidator(cleaned_data=options)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn("reason_unscheduled", form_validator._errors)
        self.assertIn(APPLICABLE_ERROR, form_validator._error_codes)

    @patch("edc_appointment.form_validators.utils.get_appointment_url")
    def test_reason_unscheduled_other(self, mock_urlnames):
        mock_urlnames.return_value = ""
        SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)

        opts = self.appointment.__dict__
        opts.pop("_state")
        opts.pop("id")
        opts.pop("created")
        opts.pop("modified")
        opts.update(
            visit_code_sequence=1,
            appt_datetime=self.appointment.appt_datetime + relativedelta(days=1),
        )
        appointment = Appointment.objects.create(**opts)

        options = {
            "appointment": appointment,
            "reason": UNSCHEDULED,
            "reason_unscheduled": OTHER,
            "reason_unscheduled_other": None,
        }
        form_validator = VisitFormValidator(cleaned_data=options)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn("reason_unscheduled_other", form_validator._errors)
        self.assertIn(REQUIRED_ERROR, form_validator._error_codes)

    def test_info_source_other(self):
        options = {
            "appointment": self.appointment,
            "info_source": OTHER,
            "info_source_other": None,
        }
        form_validator = VisitFormValidator(cleaned_data=options)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn("info_source_other", form_validator._errors)
        self.assertIn(REQUIRED_ERROR, form_validator._error_codes)
