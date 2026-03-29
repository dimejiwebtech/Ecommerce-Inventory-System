from django.core.management.base import BaseCommand
from django.utils import timezone
from stockpile.models import Stockpile, StockpileFeeLog

class Command(BaseCommand):
    help = 'Accrue daily storage fees (₦200) for stockpile items held >30 days.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        # Find all unreleased stockpile items
        active_stockpiles = Stockpile.objects.filter(is_released=False)
        
        accrued_count = 0
        for s in active_stockpiles:
            # Check if it has been stored for more than 30 days
            # delta.days is integer
            if s.days_stored > 30:
                # Check if we already accrued today's fee
                if not StockpileFeeLog.objects.filter(stockpile=s, date_accrued=today).exists():
                    StockpileFeeLog.objects.create(
                        stockpile=s,
                        amount=200.00
                    )
                    accrued_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully accrued fees for {accrued_count} items.'))
