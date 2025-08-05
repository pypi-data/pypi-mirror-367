from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.creators import UnscheduledAppointmentCreator
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED
from edc_visit_tracking.models import SubjectVisit
from visit_tracking_app.consents import consent_v1
from visit_tracking_app.models import BadCrfOneInline, CrfOne, CrfOneInline, OtherModel
from visit_tracking_app.visit_schedule import visit_schedule1, visit_schedule2

from ..helper import Helper

utc_tz = ZoneInfo("UTC")


@time_machine.travel(datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz))
class TestVisit(TestCase):
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

    def test_methods(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=visit_schedule1.name, schedule_name="schedule1"
        )
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]
        subject_visit = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        instance = CrfOne(subject_visit=subject_visit)

        self.assertEqual(instance.subject_visit, subject_visit)
        self.assertEqual(instance.related_visit_model_attr(), "subject_visit")
        self.assertEqual(CrfOne.related_visit_model_attr(), "subject_visit")
        self.assertEqual(CrfOne.related_visit_model_cls(), SubjectVisit)

    def test_crf_related_visit_model_attrs(self):
        """Assert models using the CrfModelMixin can determine which
        attribute points to the visit model foreignkey.
        """
        self.assertEqual(CrfOne().related_visit_model_attr(), "subject_visit")
        self.assertEqual(CrfOne.objects.all().count(), 0)

    def test_crf_visit_model(self):
        """Assert models using the CrfModelMixin can determine which
        visit model is in use for the app_label.
        """
        self.assertEqual(CrfOne().related_visit_model_cls(), SubjectVisit)
        self.assertEqual(CrfOne.objects.all().count(), 0)

    def test_crf_inline_model_attrs(self):
        """Assert inline model can find visit instance from parent."""
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=visit_schedule1.name, schedule_name="schedule1"
        )
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]
        subject_visit = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        other_model = OtherModel.objects.create()
        crf_one_inline = CrfOneInline.objects.create(crf_one=crf_one, other_model=other_model)
        self.assertEqual(crf_one_inline.related_visit.pk, subject_visit.pk)

    def test_crf_inline_model_parent_model(self):
        """Assert inline model cannot find parent, raises exception."""
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=visit_schedule1.name, schedule_name="schedule1"
        )
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]
        subject_visit = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        other_model = OtherModel.objects.create()
        self.assertRaises(
            ImproperlyConfigured,
            BadCrfOneInline.objects.create,
            crf_one=crf_one,
            other_model=other_model,
        )

    def test_crf_inline_model_attrs2(self):
        """Assert inline model can find visit instance from parent."""
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=visit_schedule1.name, schedule_name="schedule1"
        )
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]
        subject_visit = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        other_model = OtherModel.objects.create()
        crf_one_inline = CrfOneInline.objects.create(crf_one=crf_one, other_model=other_model)
        self.assertIsInstance(crf_one_inline.related_visit, SubjectVisit)

    def test_get_previous_model_instance(self):
        """Assert model can determine the previous."""
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=visit_schedule1.name, schedule_name="schedule1"
        )
        for index, appointment in enumerate(
            Appointment.objects.all().order_by("timepoint", "visit_code_sequence")
        ):
            SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=get_utcnow() - relativedelta(months=10 - index),
                reason=SCHEDULED,
            )
        subject_visits = SubjectVisit.objects.all().order_by(
            "appointment__timepoint", "appointment__visit_code_sequence"
        )
        self.assertEqual(subject_visits.count(), 4)
        subject_visit = subject_visits[0]
        self.assertIsNone(subject_visit.previous_visit)
        subject_visit = subject_visits[1]
        self.assertEqual(subject_visit.previous_visit.pk, subject_visits[0].pk)
        subject_visit = subject_visits[2]
        self.assertEqual(subject_visit.previous_visit.pk, subject_visits[1].pk)
        subject_visit = subject_visits[3]
        self.assertEqual(subject_visit.previous_visit.pk, subject_visits[2].pk)

    def test_get_previous_model_instance2(self):
        """Assert model can determine the previous even when unscheduled
        appointment are inserted.
        """
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=visit_schedule1.name, schedule_name="schedule1"
        )
        appointments = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")

        for index, appointment in enumerate(appointments):
            SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=get_utcnow() - relativedelta(months=10 - index),
                reason=SCHEDULED,
            )
            appointment.appt_status = INCOMPLETE_APPT
            appointment.save()

        appointment = appointments.last()
        for i in [1, 2]:
            appointment = UnscheduledAppointmentCreator(
                subject_identifier=self.subject_identifier,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name,
                visit_code=appointment.visit_code,
                suggested_visit_code_sequence=appointment.visit_code_sequence + 1,
                facility=appointment.facility,
            ).appointment
            SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=(appointment.appt_datetime + relativedelta(days=i)),
                reason=UNSCHEDULED,
            )
            appointment.appt_status = INCOMPLETE_APPT
            appointment.save()

        subject_visits = SubjectVisit.objects.all().order_by(
            "appointment__timepoint", "appointment__visit_code_sequence"
        )
        self.assertEqual(subject_visits.count(), 6)

        subject_visit = subject_visits[0]
        self.assertIsNone(subject_visit.previous_visit)
        subject_visit = subject_visits[1]
        self.assertEqual(subject_visit.previous_visit, subject_visits[0])
        subject_visit = subject_visits[2]
        self.assertEqual(subject_visit.previous_visit, subject_visits[1])
        subject_visit = subject_visits[3]
        self.assertEqual(subject_visit.previous_visit, subject_visits[2])

    def test_missed_no_crfs(self):
        pass
