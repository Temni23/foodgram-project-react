import csv

from django.core.management.base import BaseCommand

from foodgram.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from CSV file'

    def handle(self, *args, **options):
        file_path = '../data/ingredients.csv'
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                ingredient = Ingredient(name=row['абрикосовое варенье'],
                                        measurement_unit=row['г'])
                ingredient.save()
        self.stdout.write(
            self.style.SUCCESS('Ingredient imported successfully'))
