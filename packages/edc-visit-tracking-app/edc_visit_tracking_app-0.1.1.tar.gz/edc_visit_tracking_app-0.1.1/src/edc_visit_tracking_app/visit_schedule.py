from dateutil.relativedelta import relativedelta
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.tests.dummy_panel import DummyPanel
from edc_visit_schedule.visit import (
    Crf,
    CrfCollection,
    Requisition,
    RequisitionCollection,
    Visit,
)
from edc_visit_schedule.visit_schedule import VisitSchedule

from .consents import consent_v1


class Panel(DummyPanel):
    """`requisition_model` is normally set when the lab profile
    is set up.
    """

    def __init__(self, name):
        super().__init__(
            requisition_model="edc_visit_tracking_app.subjectrequisition", name=name
        )


crfs = CrfCollection(
    Crf(show_order=1, model="edc_visit_tracking_app.crfone", required=True),
    Crf(show_order=2, model="edc_visit_tracking_app.crftwo", required=True),
    Crf(show_order=3, model="edc_visit_tracking_app.crfthree", required=True),
    Crf(show_order=4, model="edc_visit_tracking_app.crffour", required=True),
    Crf(show_order=5, model="edc_visit_tracking_app.crffive", required=True),
)

requisitions = RequisitionCollection(
    Requisition(show_order=10, panel=Panel("one"), required=True, additional=False),
    Requisition(show_order=20, panel=Panel("two"), required=True, additional=False),
    Requisition(show_order=30, panel=Panel("three"), required=True, additional=False),
    Requisition(show_order=40, panel=Panel("four"), required=True, additional=False),
    Requisition(show_order=50, panel=Panel("five"), required=True, additional=False),
    Requisition(show_order=60, panel=Panel("six"), required=True, additional=False),
)

visit_schedule1 = VisitSchedule(
    name="visit_schedule1",
    offstudy_model="edc_visit_tracking_app.subjectoffstudy",
    death_report_model="edc_visit_tracking_app.deathreport",
    locator_model="edc_locator.subjectlocator",
)

visit_schedule2 = VisitSchedule(
    name="visit_schedule2",
    offstudy_model="edc_visit_tracking_app.subjectoffstudy",
    death_report_model="edc_visit_tracking_app.deathreport",
    locator_model="edc_locator.subjectlocator",
)

schedule1 = Schedule(
    name="schedule1",
    onschedule_model="edc_visit_tracking_app.onscheduleone",
    offschedule_model="edc_visit_tracking_app.offscheduleone",
    consent_definitions=[consent_v1],
)

schedule2 = Schedule(
    name="schedule2",
    onschedule_model="edc_visit_tracking_app.onscheduletwo",
    offschedule_model="edc_visit_tracking_app.offscheduletwo",
    consent_definitions=[consent_v1],
    base_timepoint=4,
)

visits = []
for index in range(0, 4):
    visits.append(
        Visit(
            code=f"{index + 1}000",
            title=f"Day {index + 1}",
            timepoint=index,
            rbase=relativedelta(months=index),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            requisitions=requisitions,
            crfs=crfs,
            allow_unscheduled=True,
        )
    )
for visit in visits:
    schedule1.add_visit(visit)

visits = []
for index in range(4, 8):
    visits.append(
        Visit(
            code=f"{index + 1}000",
            title=f"Day {index + 1}",
            timepoint=index,
            rbase=relativedelta(days=index),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            requisitions=requisitions,
            crfs=crfs,
        )
    )
for visit in visits:
    schedule2.add_visit(visit)

visit_schedule1.add_schedule(schedule1)
visit_schedule2.add_schedule(schedule2)
