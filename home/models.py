from django.db import models
from django.utils import timezone


class FinancialEntry(models.Model):
    class Kind(models.TextChoices):
        INCOME = 'income', 'Receita'
        EXPENSE = 'expense', 'Despesa'

    description = models.CharField('descrição', max_length=120)
    kind = models.CharField('tipo', max_length=10, choices=Kind.choices)
    amount = models.DecimalField('valor', max_digits=12, decimal_places=2)
    date = models.DateField('data', default=timezone.localdate)

    class Meta:
        ordering = ['-date', '-id']
        verbose_name = 'lançamento financeiro'
        verbose_name_plural = 'lançamentos financeiros'

    def __str__(self):
        return f'{self.get_kind_display()}: {self.description} ({self.amount})'
