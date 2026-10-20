import calendar
from datetime import date
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import FinancialEntry


def auth(request):
    if request.method != 'POST':
        return render(request, 'core/auth.html')

    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')
    user = authenticate(request, username=username, password=password)

    if user is None or not user.is_superuser:
        return render(
            request,
            'core/auth.html',
            {'error_message': 'Nome de usuário ou senha inválidos.'},
        )

    login(request, user)
    return redirect('Control')


@require_http_methods(['GET', 'POST'])
def dashboard(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('Auth')

    today = timezone.localdate()
    month_start = today.replace(day=1)
    month_end = today.replace(day=calendar.monthrange(today.year, today.month)[1])

    if request.method == 'POST':
        action = request.POST.get('action', 'create')

        if action == 'delete':
            entry = get_object_or_404(FinancialEntry, pk=request.POST.get('entry_id'))
            entry.delete()
            messages.success(request, 'Lançamento excluído.')
            return redirect('Control')

        entry = None
        if action == 'update':
            entry = get_object_or_404(FinancialEntry, pk=request.POST.get('entry_id'))
        elif action != 'create':
            messages.error(request, 'Ação inválida.')
            return redirect('Control')

        description = request.POST.get('description', '').strip()
        kind = request.POST.get('kind', '')
        raw_amount = request.POST.get('amount', '').strip().replace(',', '.')
        raw_date = request.POST.get('date', '')

        try:
            amount = Decimal(raw_amount)
            entry_date = date.fromisoformat(raw_date)
            if not amount.is_finite() or amount <= 0:
                raise ValueError
            if kind not in FinancialEntry.Kind.values:
                raise ValueError
            if not description or len(description) > 120:
                raise ValueError
            FinancialEntry._meta.get_field('amount').clean(amount, None)
        except (InvalidOperation, ValueError, ValidationError):
            messages.error(
                request,
                'Confira os dados: descrição, tipo, valor positivo e data válidos.',
            )
        else:
            if entry is None:
                entry = FinancialEntry()
            entry.description = description
            entry.kind = kind
            entry.amount = amount
            entry.date = entry_date
            entry.save()
            messages.success(
                request,
                'Lançamento atualizado.' if action == 'update' else 'Lançamento adicionado.',
            )
            return redirect('Control')

    all_totals = FinancialEntry.objects.aggregate(
        income=Sum(
            'amount',
            filter=Q(kind=FinancialEntry.Kind.INCOME),
            default=Decimal('0.00'),
        ),
        expenses=Sum(
            'amount',
            filter=Q(kind=FinancialEntry.Kind.EXPENSE),
            default=Decimal('0.00'),
        ),
    )
    month_entries = FinancialEntry.objects.filter(
        date__gte=month_start,
        date__lte=month_end,
    )
    month_totals = month_entries.aggregate(
        income=Sum(
            'amount',
            filter=Q(kind=FinancialEntry.Kind.INCOME),
            default=Decimal('0.00'),
        ),
        expenses=Sum(
            'amount',
            filter=Q(kind=FinancialEntry.Kind.EXPENSE),
            default=Decimal('0.00'),
        ),
    )
    daily_totals = {
        item['date']: item
        for item in month_entries.values('date').annotate(
            income=Sum('amount', filter=Q(kind=FinancialEntry.Kind.INCOME)),
            expenses=Sum('amount', filter=Q(kind=FinancialEntry.Kind.EXPENSE)),
        )
    }
    chart_data = [
        {
            'day': day,
            'income': float(
                daily_totals.get(date(today.year, today.month, day), {}).get('income') or 0
            ),
            'expenses': float(
                daily_totals.get(date(today.year, today.month, day), {}).get('expenses') or 0
            ),
        }
        for day in range(1, month_end.day + 1)
    ]

    context = {
        'today': today,
        'month_income': month_totals['income'],
        'month_expenses': month_totals['expenses'],
        'month_result': month_totals['income'] - month_totals['expenses'],
        'balance': all_totals['income'] - all_totals['expenses'],
        'chart_data': chart_data,
        'recent_entries': FinancialEntry.objects.all()[:10],
        'entry_date': today.isoformat(),
    }
    return render(request, 'core/dashboard.html', context)
