from django.core.management.base import BaseCommand
from app.models import EmergencyProtocol

class Command(BaseCommand):
    help = 'Setup emergency protocols for different altitude ranges'

    def handle(self, *args, **options):
        protocols = [
            {
                'altitude_range_min': 3000,
                'altitude_range_max': 4000,
                'location_name': 'Namche Bazaar Region',
                'rescue_contact': '+977-38-540001',
                'helicopter_service': '+977-1-4442094',
                'nearest_hospital': 'Kunde Hospital, Khumjung',
                'descent_route': 'Descend to Lukla (2860m) via Namche Bazaar. Follow main trekking route.',
                'safe_altitude': 2860,
                'estimated_descent_time': '4-6 hours',
                'oxygen_availability': True,
                'medical_post_location': 'Namche Bazaar Health Post'
            },
            {
                'altitude_range_min': 4000,
                'altitude_range_max': 5000,
                'location_name': 'Dingboche/Lobuche Region',
                'rescue_contact': '+977-38-540001',
                'helicopter_service': '+977-1-4442094',
                'nearest_hospital': 'Pheriche Health Post',
                'descent_route': 'Immediate descent to Pheriche (4371m) then continue to Namche Bazaar (3440m).',
                'safe_altitude': 3440,
                'estimated_descent_time': '6-8 hours to Pheriche, 12-15 hours to Namche',
                'oxygen_availability': True,
                'medical_post_location': 'Pheriche Aid Post (HRA)'
            },
            {
                'altitude_range_min': 5000,
                'altitude_range_max': 6000,
                'location_name': 'Everest Base Camp Region',
                'rescue_contact': '+977-38-540001',
                'helicopter_service': '+977-1-4442094',
                'nearest_hospital': 'Pheriche Health Post',
                'descent_route': 'Emergency descent to Pheriche (4371m). Do not delay - descend immediately.',
                'safe_altitude': 4371,
                'estimated_descent_time': '4-6 hours',
                'oxygen_availability': False,
                'medical_post_location': 'Pheriche Aid Post (HRA) - 6-8 hours descent'
            },
            {
                'altitude_range_min': 3500,
                'altitude_range_max': 4500,
                'location_name': 'Annapurna Circuit - Manang',
                'rescue_contact': '+977-66-520048',
                'helicopter_service': '+977-1-4442094',
                'nearest_hospital': 'Manang Health Post',
                'descent_route': 'Descend to Manang (3519m) then continue to Besisahar (760m) if symptoms persist.',
                'safe_altitude': 3519,
                'estimated_descent_time': '2-4 hours to Manang',
                'oxygen_availability': True,
                'medical_post_location': 'Manang Health Post'
            },
            {
                'altitude_range_min': 4500,
                'altitude_range_max': 5500,
                'location_name': 'Thorong La Pass Region',
                'rescue_contact': '+977-66-520048',
                'helicopter_service': '+977-1-4442094',
                'nearest_hospital': 'Manang Health Post',
                'descent_route': 'If on Annapurna side: descend to Manang. If on Mustang side: descend to Muktinath then Jomsom.',
                'safe_altitude': 3519,
                'estimated_descent_time': '4-8 hours depending on location',
                'oxygen_availability': False,
                'medical_post_location': 'Manang Health Post or Jomsom Hospital'
            },
            {
                'altitude_range_min': 3000,
                'altitude_range_max': 4000,
                'location_name': 'Langtang Valley',
                'rescue_contact': '+977-10-560048',
                'helicopter_service': '+977-1-4442094',
                'nearest_hospital': 'Dhunche Health Post',
                'descent_route': 'Descend via Langtang village to Dhunche (1960m).',
                'safe_altitude': 1960,
                'estimated_descent_time': '6-8 hours',
                'oxygen_availability': False,
                'medical_post_location': 'Dhunche Health Post'
            },
            {
                'altitude_range_min': 4000,
                'altitude_range_max': 5000,
                'location_name': 'Gokyo Lakes Region',
                'rescue_contact': '+977-38-540001',
                'helicopter_service': '+977-1-4442094',
                'nearest_hospital': 'Kunde Hospital, Khumjung',
                'descent_route': 'Descend to Dole (4200m) then continue to Namche Bazaar (3440m).',
                'safe_altitude': 3440,
                'estimated_descent_time': '6-10 hours',
                'oxygen_availability': False,
                'medical_post_location': 'Namche Bazaar Health Post'
            }
        ]

        created_count = 0
        for protocol_data in protocols:
            protocol, created = EmergencyProtocol.objects.get_or_create(
                altitude_range_min=protocol_data['altitude_range_min'],
                altitude_range_max=protocol_data['altitude_range_max'],
                location_name=protocol_data['location_name'],
                defaults=protocol_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created protocol for {protocol.location_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} emergency protocols')
        )