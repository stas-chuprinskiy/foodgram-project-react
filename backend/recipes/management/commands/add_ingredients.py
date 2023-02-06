import csv
import logging

from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient

logger = logging.getLogger(__name__)

DATA_PATH = BASE_DIR.parent.joinpath('data')

DATA_FILES = {
    'ingredients.csv': (Ingredient, ['name', 'measurement_unit']),
}


class Command(BaseCommand):
    help = 'Adding ingredients in database.'

    def handle(self, *args, **options):
        for file_name in DATA_FILES:
            file_path = DATA_PATH.joinpath(file_name)
            model, fieldnames = DATA_FILES[file_name]

            with open(file_path, mode='r') as file:
                reader = csv.DictReader(file, fieldnames=fieldnames)
                for row in reader:
                    try:
                        instance = model.objects.get_or_create(**row)
                        logger.info(instance)
                    except Exception as err:
                        logger.error(err, exc_info=True)
