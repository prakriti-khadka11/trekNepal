from django.core.management.base import BaseCommand
from app.models import ExpenseCategory

class Command(BaseCommand):
    help = 'Create default expense categories for travel'

    def handle(self, *args, **options):
        categories = [
            {'name': 'Accommodation', 'icon': 'fas fa-bed', 'color': '#007bff'},
            {'name': 'Transportation', 'icon': 'fas fa-plane', 'color': '#28a745'},
            {'name': 'Food & Dining', 'icon': 'fas fa-utensils', 'color': '#ffc107'},
            {'name': 'Activities & Tours', 'icon': 'fas fa-camera', 'color': '#17a2b8'},
            {'name': 'Shopping', 'icon': 'fas fa-shopping-bag', 'color': '#e91e63'},
            {'name': 'Medical & Health', 'icon': 'fas fa-first-aid', 'color': '#dc3545'},
            {'name': 'Permits & Fees', 'icon': 'fas fa-file-invoice', 'color': '#6f42c1'},
            {'name': 'Equipment & Gear', 'icon': 'fas fa-backpack', 'color': '#fd7e14'},
            {'name': 'Communication', 'icon': 'fas fa-phone', 'color': '#20c997'},
            {'name': 'Emergency', 'icon': 'fas fa-exclamation-triangle', 'color': '#dc3545'},
            {'name': 'Miscellaneous', 'icon': 'fas fa-ellipsis-h', 'color': '#6c757d'},
        ]

        created_count = 0
        for category_data in categories:
            category, created = ExpenseCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'icon': category_data['icon'],
                    'color': category_data['color']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )

        if created_count == 0:
            self.stdout.write(
                self.style.WARNING('All categories already exist')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} categories')
            )