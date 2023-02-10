import csv
import logging

from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient

logger = logging.getLogger(__name__)

DATA_PATH = BASE_DIR.joinpath('fixtures')

DATA_FILES = {
    'ingredients.csv': (Ingredient, ['name', 'measurement_unit']),
}


class Command(BaseCommand):
    help = 'Adding ingredients in database.'

    def handle(self, *args, **options):
        for file_name in DATA_FILES:
            file = DATA_PATH.joinpath(file_name)
            model, fieldnames = DATA_FILES[file_name]

            if file.exists():
                with open(file, mode='r') as file:
                    reader = csv.DictReader(file, fieldnames=fieldnames)
                    data = [model(**row) for row in reader]
                    try:
                        logger.info(model.objects.bulk_create(data))
                    except Exception as err:
                        logger.error(err, exc_info=True)
            else:
                logger.error(f'File "{file_name}" does not exist at: {file}')
