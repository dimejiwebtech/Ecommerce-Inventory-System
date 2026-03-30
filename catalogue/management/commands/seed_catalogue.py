import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalogue.models import Category, Collection, Jewellery, JewelleryImage

class Command(BaseCommand):
    help = 'Seeds the database with initial categories and jewellery products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding categories...')
        
        categories_data = [
            {'name': 'Rings', 'description': 'Elegant diamond and gold rings for every occasion.'},
            {'name': 'Necklaces', 'description': 'Exquisite necklaces and pendants crafted with precision.'},
            {'name': 'Earrings', 'description': 'Stunning earrings that add a touch of sparkle.'},
            {'name': 'Bracelets', 'description': 'Timeless bracelets and bangles for a sophisticated look.'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat.name] = cat
            if created:
                self.stdout.write(f'Created category: {cat.name}')

        self.stdout.write('Seeding collections...')
        collections_data = [
            {'name': 'Bridal Collection', 'is_featured': True},
            {'name': 'Vintage Glamour', 'is_featured': False},
            {'name': 'Modern Minimalist', 'is_featured': True},
        ]

        collections = {}
        for coll_data in collections_data:
            coll, created = Collection.objects.get_or_create(
                name=coll_data['name'],
                defaults={'is_featured': coll_data['is_featured']}
            )
            collections[coll.name] = coll
            if created:
                self.stdout.write(f'Created collection: {coll.name}')

        self.stdout.write('Seeding jewellery...')
        jewellery_data = [
            {
                'name': 'Diamond Solitaire Ring',
                'category': 'Rings',
                'collection': 'Bridal Collection',
                'retail_price': 150000.00,
                'wholesale_price': 120000.00,
                'stock': 10,
                'description': 'A classic 1-carat diamond solitaire ring set in 18k white gold.'
            },
            {
                'name': 'Gold Pendant Necklace',
                'category': 'Necklaces',
                'collection': 'Modern Minimalist',
                'retail_price': 45000.00,
                'wholesale_price': 35000.00,
                'stock': 25,
                'description': 'Simple yet elegant gold pendant necklace, perfect for daily wear.'
            },
            {
                'name': 'Sapphire Stud Earrings',
                'category': 'Earrings',
                'collection': 'Vintage Glamour',
                'retail_price': 85000.00,
                'wholesale_price': 70000.00,
                'stock': 15,
                'description': 'Deep blue sapphire stud earrings surrounded by a halo of diamonds.'
            },
            {
                'name': 'Tennis Bracelet',
                'category': 'Bracelets',
                'collection': 'Bridal Collection',
                'retail_price': 250000.00,
                'wholesale_price': 210000.00,
                'stock': 5,
                'description': 'A stunning diamond tennis bracelet set in 14k yellow gold.'
            }
        ]

        for item_data in jewellery_data:
            jewellery, created = Jewellery.objects.get_or_create(
                name=item_data['name'],
                defaults={
                    'category': categories[item_data['category']],
                    'collection': collections[item_data['collection']] if item_data['collection'] else None,
                    'retail_price': item_data['retail_price'],
                    'wholesale_price': item_data['wholesale_price'],
                    'stock': item_data['stock'],
                    'description': item_data['description'],
                    'sku': f"AURA-{random.randint(1000, 9999)}"
                }
            )
            if created:
                self.stdout.write(f'Created jewellery: {jewellery.name}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database!'))
