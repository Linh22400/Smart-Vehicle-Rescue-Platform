import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import MechanicProfile
from apps.services.models import Service

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds database with random mechanics for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding mechanics...')
        
        # Hanoi center approx
        base_lat = 21.0285
        base_lon = 105.8542
        
        mechanic_names = ['Minh Tuan', 'Hoang Nam', 'Gara Bao Viet', 'Sua Xe 24h', 'Cuu Ho Nhanh']
        
        services_list = [
            ("Thay nhớt Motul", 150000, "Nhớt chính hãng nhập khẩu"),
            ("Rửa xe bọt tuyết", 50000, "Rửa sạch bụi bẩn, bảo vệ sơn"),
            ("Vá lốp không săm", 30000, "Vá nhanh, độ bền cao"),
            ("Bảo dưỡng toàn bộ", 300000, "Kiểm tra phanh, nhông xích, động cơ")
        ]

        for i, name in enumerate(mechanic_names):
            username = f'mechanic_{i+1}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    password='password123',
                    email=f'{username}@example.com',
                    is_mechanic=True,
                    first_name=name
                )
                
                # Random location within ~3-5km
                lat_offset = random.uniform(-0.03, 0.03)
                lon_offset = random.uniform(-0.03, 0.03)
                
                profile = MechanicProfile.objects.create(
                    user=user,
                    latitude=base_lat + lat_offset,
                    longitude=base_lon + lon_offset,
                    is_available=True,
                    rating=round(random.uniform(3.5, 5.0), 1),
                    specialty=random.choice(['Vá săm', 'Chết máy', 'Thay acquy', 'Đa năng'])
                )
                
                # Add services
                for s_name, price, desc in random.sample(services_list, 3):
                    Service.objects.create(
                        mechanic=profile,
                        name=s_name,
                        price=price,
                        description=desc
                    )
                
                self.stdout.write(self.style.SUCCESS(f'Created mechanic: {name} ({username}) with services'))
            else:
                 # Ensure existing mechanics have services
                 user = User.objects.get(username=username)
                 if hasattr(user, 'mechanic_profile') and not user.mechanic_profile.services.exists():
                     for s_name, price, desc in random.sample(services_list, 3):
                        Service.objects.create(
                            mechanic=user.mechanic_profile,
                            name=s_name,
                            price=price,
                            description=desc
                        )
                     self.stdout.write(f'Added services to existing mechanic {username}')
                 else:
                     self.stdout.write(f'Mechanic {username} exists and has services')
                 
        self.stdout.write(self.style.SUCCESS('Seeding Completed!'))
