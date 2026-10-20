from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import FinancialEntry


class DashboardTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='test-password-123',
        )
        self.client.force_login(self.admin)
        self.url = reverse('Control')

    def test_dashboard_shows_current_balance_and_monthly_totals(self):
        today = timezone.localdate()
        FinancialEntry.objects.create(
            description='Venda',
            kind=FinancialEntry.Kind.INCOME,
            amount=Decimal('125.50'),
            date=today,
        )
        FinancialEntry.objects.create(
            description='Conta',
            kind=FinancialEntry.Kind.EXPENSE,
            amount=Decimal('45.25'),
            date=today,
        )
        FinancialEntry.objects.create(
            description='Despesa anterior',
            kind=FinancialEntry.Kind.EXPENSE,
            amount=Decimal('10.00'),
            date=today - timedelta(days=40),
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['balance'], Decimal('70.25'))
        self.assertEqual(response.context['month_income'], Decimal('125.50'))
        self.assertEqual(response.context['month_expenses'], Decimal('45.25'))
        self.assertEqual(response.context['month_result'], Decimal('80.25'))

    def test_superuser_can_create_update_and_delete_entries(self):
        today = timezone.localdate().isoformat()
        create_response = self.client.post(
            self.url,
            {
                'action': 'create',
                'description': 'Venda inicial',
                'kind': FinancialEntry.Kind.INCOME,
                'amount': '100.00',
                'date': today,
            },
        )
        self.assertRedirects(create_response, self.url)

        entry = FinancialEntry.objects.get()
        update_response = self.client.post(
            self.url,
            {
                'action': 'update',
                'entry_id': entry.pk,
                'description': 'Venda corrigida',
                'kind': FinancialEntry.Kind.EXPENSE,
                'amount': '75.50',
                'date': today,
            },
        )
        self.assertRedirects(update_response, self.url)
        entry.refresh_from_db()
        self.assertEqual(entry.description, 'Venda corrigida')
        self.assertEqual(entry.kind, FinancialEntry.Kind.EXPENSE)
        self.assertEqual(entry.amount, Decimal('75.50'))

        delete_response = self.client.post(
            self.url,
            {'action': 'delete', 'entry_id': entry.pk},
        )
        self.assertRedirects(delete_response, self.url)
        self.assertFalse(FinancialEntry.objects.exists())

    def test_non_superuser_cannot_open_dashboard(self):
        user = get_user_model().objects.create_user(
            username='user',
            password='test-password-123',
        )
        self.client.force_login(user)

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('Auth'))

    def test_invalid_entry_is_not_saved(self):
        response = self.client.post(
            self.url,
            {
                'action': 'create',
                'description': 'Valor incorreto',
                'kind': FinancialEntry.Kind.INCOME,
                'amount': '-20',
                'date': timezone.localdate().isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(FinancialEntry.objects.exists())
