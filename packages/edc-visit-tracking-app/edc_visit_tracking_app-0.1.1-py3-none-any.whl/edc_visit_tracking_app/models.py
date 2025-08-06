from datetime import date

from django.db import models
from django.db.models.deletion import PROTECT
from edc_consent.managers import ConsentObjectsByCdefManager, CurrentSiteByCdefManager
from edc_constants.constants import HOSPITALIZED, OTHER
from edc_crf.model_mixins import CrfInlineModelMixin
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_lab.model_mixins import RequisitionModelMixin
from edc_list_data.model_mixins import ListModelMixin
from edc_model.models import BaseUuidModel
from edc_offstudy.model_mixins import OffstudyModelMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_screening.model_mixins import ScreeningModelMixin
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
from edc_visit_tracking.model_mixins import VisitTrackingCrfModelMixin
from edc_visit_tracking.models import SubjectVisit

from .consents import consent_v1

list_data = {
    "edc_visit_tracking.subjectvisitmissedreasons": [
        ("forgot", "Forgot / Can’t remember being told about appointment"),
        ("family_emergency", "Family emergency (e.g. funeral) and was away"),
        ("travelling", "Away travelling/visiting"),
        ("working_schooling", "Away working/schooling"),
        ("too_sick", "Too sick or weak to come to the centre"),
        ("lack_of_transport", "Transportation difficulty"),
        (HOSPITALIZED, "Hospitalized"),
        (OTHER, "Other reason (specify below)"),
    ],
}


class SubjectScreening(ScreeningModelMixin, BaseUuidModel):
    consent_definition = consent_v1
    objects = SubjectIdentifierManager()


class SubjectConsent(
    SiteModelMixin,
    NonUniqueSubjectIdentifierFieldMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    BaseUuidModel,
):
    report_datetime = models.DateTimeField(default=get_utcnow)

    consent_datetime = models.DateTimeField(default=get_utcnow)

    version = models.CharField(max_length=25, default="1")

    identity = models.CharField(max_length=25)

    confirm_identity = models.CharField(max_length=25)

    dob = models.DateField(default=date(1995, 1, 1))


class SubjectConsentV1(SubjectConsent):
    objects = ConsentObjectsByCdefManager()
    on_site = CurrentSiteByCdefManager()

    class Meta:
        proxy = True


class OnScheduleOne(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    class Meta(BaseUuidModel.Meta):
        pass


class OnScheduleTwo(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    class Meta(BaseUuidModel.Meta):
        pass


class OffSchedule(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    class Meta(BaseUuidModel.Meta):
        pass


class OffScheduleOne(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    class Meta(BaseUuidModel.Meta):
        pass


class SubjectOffstudy(SiteModelMixin, OffstudyModelMixin, BaseUuidModel):
    class Meta(OffstudyModelMixin.Meta):
        pass


class SubjectRequisition(RequisitionModelMixin, BaseUuidModel):
    def update_reference_on_save(self):
        pass

    class Meta(RequisitionModelMixin.Meta):
        pass


class CrfOne(SiteModelMixin, VisitTrackingCrfModelMixin, BaseUuidModel):
    f1 = models.CharField(max_length=50, null=True)

    f2 = models.CharField(max_length=50, null=True)

    f3 = models.CharField(max_length=50, null=True)

    class Meta(BaseUuidModel.Meta):
        pass


class CrfTwo(SiteModelMixin, VisitTrackingCrfModelMixin, BaseUuidModel):
    f1 = models.CharField(max_length=50, null=True)

    f2 = models.CharField(max_length=50, null=True)

    f3 = models.CharField(max_length=50, null=True)

    class Meta(BaseUuidModel.Meta):
        pass


class CrfThree(SiteModelMixin, VisitTrackingCrfModelMixin, BaseUuidModel):
    f1 = models.CharField(max_length=50, null=True)

    f2 = models.CharField(max_length=50, null=True)

    f3 = models.CharField(max_length=50, null=True)

    class Meta(BaseUuidModel.Meta):
        pass


class CrfFour(SiteModelMixin, VisitTrackingCrfModelMixin, BaseUuidModel):
    f1 = models.CharField(max_length=50, null=True)

    f2 = models.CharField(max_length=50, null=True)

    f3 = models.CharField(max_length=50, null=True)

    class Meta(BaseUuidModel.Meta):
        pass


class CrfFive(SiteModelMixin, VisitTrackingCrfModelMixin, BaseUuidModel):
    f1 = models.CharField(max_length=50, null=True)

    f2 = models.CharField(max_length=50, null=True)

    f3 = models.CharField(max_length=50, null=True)

    class Meta(BaseUuidModel.Meta):
        pass


class BadCrfNoRelatedVisit(SiteModelMixin, VisitTrackingCrfModelMixin, BaseUuidModel):
    subject_visit = None

    f1 = models.CharField(max_length=50, null=True)

    f2 = models.CharField(max_length=50, null=True)

    f3 = models.CharField(max_length=50, null=True)

    class Meta(BaseUuidModel.Meta):
        pass


class OtherModel(SiteModelMixin, BaseUuidModel):
    f1 = models.CharField(max_length=10, default="erik")

    class Meta(BaseUuidModel.Meta):
        pass


class CrfOneInline(CrfInlineModelMixin, BaseUuidModel):
    crf_one = models.ForeignKey(CrfOne, on_delete=PROTECT)

    other_model = models.ForeignKey(OtherModel, on_delete=PROTECT)

    f1 = models.CharField(max_length=10, default="erik")

    def natural_key(self) -> tuple:
        return tuple()

    class Meta(CrfInlineModelMixin.Meta):
        crf_inline_parent = "crf_one"


class BadCrfOneInline(CrfInlineModelMixin, BaseUuidModel):
    """A model class missing _meta.crf_inline_parent."""

    crf_one = models.ForeignKey(CrfOne, on_delete=PROTECT)

    other_model = models.ForeignKey(OtherModel, on_delete=PROTECT)

    f1 = models.CharField(max_length=10, default="erik")

    def natural_key(self) -> tuple:
        return tuple()

    class Meta:
        pass


class BadCrfOneInline2(CrfInlineModelMixin, BaseUuidModel):
    crf_one = models.ForeignKey(CrfOne, on_delete=PROTECT)

    other_model = models.ForeignKey(OtherModel, on_delete=PROTECT)

    f1 = models.CharField(max_length=10, default="erik")

    def natural_key(self) -> tuple:
        return tuple()

    class Meta(CrfInlineModelMixin.Meta):
        crf_inline_parent = None


class CustomSubjectVisitMissedReasons(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Subject Visit Missed Reason"
        verbose_name_plural = "Subject Visit Missed Reasons"


class SubjectVisit2(SubjectVisit):
    class Meta:
        proxy = True
