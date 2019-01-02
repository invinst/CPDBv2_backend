from django.contrib.gis.db import models
from django.db.models import F

from .common import TimeStampsModel


class SalaryManager(models.Manager):
    def rank_histories_without_joined(self):
        salaries = self.exclude(
            spp_date__isnull=True
        ).exclude(
            spp_date=F('officer__appointed_date'),
            officer__appointed_date__isnull=False
        ).order_by('officer_id', 'year')
        last_salary = salaries.first()
        result = [last_salary]
        for salary in salaries:
            if salary.officer_id == last_salary.officer_id:
                if salary.rank != last_salary.rank:
                    result.append(salary)
            else:
                result.append(salary)
            last_salary = salary
        return result

    def rank_objects(self):
        class Rank(object):
            def __init__(self, pk, rank):
                self.pk = pk
                self.rank = rank

        ranks = []
        for index, salary in enumerate(Salary.objects.values_list('rank', flat=True).distinct()):
            ranks.append(Rank(pk=index, rank=salary))

        return ranks


class Salary(TimeStampsModel):
    pay_grade = models.CharField(max_length=16)
    rank = models.CharField(max_length=64, null=True)
    salary = models.PositiveIntegerField()
    employee_status = models.CharField(max_length=32)
    org_hire_date = models.DateField(null=True)
    spp_date = models.DateField(null=True)
    start_date = models.DateField(null=True)
    year = models.PositiveSmallIntegerField()
    age_at_hire = models.PositiveSmallIntegerField(null=True)
    officer = models.ForeignKey('data.Officer', on_delete=models.CASCADE)
    rank_changed = models.BooleanField(default=False)

    objects = SalaryManager()

    class Meta:
        indexes = [
            models.Index(fields=['year']),
        ]
