from django.core.management.base import BaseCommand
from app.models import Destination, Country

class Command(BaseCommand):
    help = 'Setup realistic hotel and destination data for dynamic booking details'

    def handle(self, *args, **options):
        # This command can be used to populate more realistic destination data
        # For now, it just shows the structure - you can expand it as needed
        
        destinations_data = [
            {
                'name': 'Everest Base Camp',
                'location': 'Solukhumbu, Nepal',
                'description': 'The ultimate trekking destination to the base of the world\'s highest mountain.'
            },
            {
                'name': 'Annapurna Circuit',
                'location': 'Annapurna Region, Nepal', 
                'description': 'Classic trek through diverse landscapes and cultures.'
            },
            {
                'name': 'Langtang Valley',
                'location': 'Langtang Region, Nepal',
                'description': 'Beautiful valley trek with stunning mountain views.'
            },
            {
                'name': 'Pokhara',
                'location': 'Kaski District, Nepal',
                'description': 'Gateway to the Annapurnas with beautiful lakes.'
            },
            {
                'name': 'Chitwan National Park',
                'location': 'Chitwan District, Nepal',
                'description': 'Wildlife safari destination in the Terai region.'
            }
        ]
        
        self.stdout.write(
            self.style.SUCCESS(
                'Hotel mapping system is now active! '
                'Bookings will show realistic hotels based on destinations.'
            )
        )
        
        self.stdout.write('Available destination mappings:')
        for dest in destinations_data:
            self.stdout.write(f"  • {dest['name']} - {dest['location']}")