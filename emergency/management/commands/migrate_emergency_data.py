from django.core.management.base import BaseCommand
from emergency.models import District, EmergencyContact, Hospital, UniversalEmergencyNumber
from emergency.data import districts, EMERGENCY_NUMBERS

class Command(BaseCommand):
    help = 'Migrate emergency data from data.py to database models'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting emergency data migration...'))
        
        # Create universal emergency numbers
        self.create_universal_numbers()
        
        # Create districts and their data
        self.create_districts_data()
        
        self.stdout.write(self.style.SUCCESS('Emergency data migration completed successfully!'))

    def create_universal_numbers(self):
        """Create universal emergency numbers"""
        universal_numbers = [
            ('Tourist Police', '1144', 'Tourist Police helpline for travelers'),
            ('Universal Emergency', '112', 'Universal emergency number'),
            ('Fire Brigade', '101', 'Fire emergency services'),
            ('Ambulance', '102', 'Medical emergency and ambulance services'),
            ('Police', '100', 'Police emergency services'),
        ]
        
        for name, number, description in universal_numbers:
            obj, created = UniversalEmergencyNumber.objects.get_or_create(
                name=name,
                defaults={
                    'number': number,
                    'description': description,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created universal number: {name} - {number}')

    def create_districts_data(self):
        """Create districts with their emergency contacts and hospitals"""
        for district_name, district_data in districts.items():
            # Create district
            district, created = District.objects.get_or_create(
                name=district_name,
                defaults={'province': self.get_province(district_name)}
            )
            
            if created:
                self.stdout.write(f'Created district: {district_name}')
            
            # Create police contacts
            if 'police' in district_data:
                for phone in district_data['police']:
                    EmergencyContact.objects.get_or_create(
                        district=district,
                        contact_type='police',
                        phone_number=phone,
                        defaults={
                            'name': f'{district_name} Police',
                            'is_primary': True,
                            'is_active': True
                        }
                    )
            
            # Create hospitals
            if 'hospitals' in district_data:
                for hospital_data in district_data['hospitals']:
                    Hospital.objects.get_or_create(
                        name=hospital_data['name'],
                        district=district,
                        defaults={
                            'latitude': hospital_data['lat'],
                            'longitude': hospital_data['lng'],
                            'has_emergency_ward': True,
                            'is_active': True
                        }
                    )
            
            self.stdout.write(f'Processed {district_name}: {len(district_data.get("hospitals", []))} hospitals')

    def get_province(self, district_name):
        """Map districts to provinces (simplified mapping)"""
        province_mapping = {
            # Province 1
            'Taplejung': 'Province 1', 'Panchthar': 'Province 1', 'Ilam': 'Province 1',
            'Jhapa': 'Province 1', 'Morang': 'Province 1', 'Sunsari': 'Province 1',
            'Dhankuta': 'Province 1', 'Terhathum': 'Province 1', 'Sankhuwasabha': 'Province 1',
            'Bhojpur': 'Province 1', 'Solukhumbu': 'Province 1', 'Okhaldhunga': 'Province 1',
            'Khotang': 'Province 1', 'Udayapur': 'Province 1',
            
            # Madhesh Province
            'Saptari': 'Madhesh Province', 'Siraha': 'Madhesh Province', 'Dhanusha': 'Madhesh Province',
            'Mahottari': 'Madhesh Province', 'Sarlahi': 'Madhesh Province', 'Bara': 'Madhesh Province',
            'Parsa': 'Madhesh Province', 'Rautahat': 'Madhesh Province',
            
            # Bagmati Province
            'Sindhuli': 'Bagmati Province', 'Ramechhap': 'Bagmati Province', 'Dolakha': 'Bagmati Province',
            'Sindhupalchok': 'Bagmati Province', 'Kavrepalanchok': 'Bagmati Province', 'Lalitpur': 'Bagmati Province',
            'Bhaktapur': 'Bagmati Province', 'Kathmandu': 'Bagmati Province', 'Nuwakot': 'Bagmati Province',
            'Rasuwa': 'Bagmati Province', 'Dhading': 'Bagmati Province', 'Chitwan': 'Bagmati Province',
            'Makwanpur': 'Bagmati Province',
            
            # Gandaki Province
            'Gorkha': 'Gandaki Province', 'Lamjung': 'Gandaki Province', 'Tanahun': 'Gandaki Province',
            'Syangja': 'Gandaki Province', 'Kaski': 'Gandaki Province', 'Manang': 'Gandaki Province',
            'Mustang': 'Gandaki Province', 'Myagdi': 'Gandaki Province', 'Parbat': 'Gandaki Province',
            'Baglung': 'Gandaki Province', 'Nawalpur': 'Gandaki Province',
            
            # Lumbini Province
            'Kapilvastu': 'Lumbini Province', 'Rupandehi': 'Lumbini Province', 'Palpa': 'Lumbini Province',
            'Arghakhanchi': 'Lumbini Province', 'Gulmi': 'Lumbini Province', 'Dang': 'Lumbini Province',
            'Pyuthan': 'Lumbini Province', 'Rolpa': 'Lumbini Province', 'Rukum East': 'Lumbini Province',
            'Banke': 'Lumbini Province', 'Bardiya': 'Lumbini Province', 'Parasi': 'Lumbini Province',
            
            # Karnali Province
            'Rukum West': 'Karnali Province', 'Salyan': 'Karnali Province', 'Dolpa': 'Karnali Province',
            'Humla': 'Karnali Province', 'Jumla': 'Karnali Province', 'Kalikot': 'Karnali Province',
            'Mugu': 'Karnali Province', 'Surkhet': 'Karnali Province', 'Dailekh': 'Karnali Province',
            'Jajarkot': 'Karnali Province',
            
            # Sudurpashchim Province
            'Bajura': 'Sudurpashchim Province', 'Bajhang': 'Sudurpashchim Province', 'Achham': 'Sudurpashchim Province',
            'Doti': 'Sudurpashchim Province', 'Kailali': 'Sudurpashchim Province', 'Kanchanpur': 'Sudurpashchim Province',
            'Dadeldhura': 'Sudurpashchim Province', 'Baitadi': 'Sudurpashchim Province', 'Darchula': 'Sudurpashchim Province'
        }
        
        return province_mapping.get(district_name, 'Unknown Province')