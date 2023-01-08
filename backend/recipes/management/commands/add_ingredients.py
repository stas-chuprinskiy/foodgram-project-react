import csv
import logging

from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient

logger = logging.getLogger(__name__)

DATA_PATH = BASE_DIR.parent.joinpath('data')

FILES_MODELS = {
    'ingredients.csv': Ingredient,
}


class Command(BaseCommand):
    help = 'Command adds ingredients in database'

    def handle(self, *args, **options):
        for file_name in FILES_MODELS:
            file_path = DATA_PATH.joinpath(file_name)
            model = FILES_MODELS.get(file_name)

            with open(file_path, mode='r') as data_file:
                fieldnames = ['name', 'measurement_unit']
                reader = csv.DictReader(data_file, fieldnames=fieldnames)

                for row in reader:
                    try:
                        logger.info(
                            Ingredient.objects.get_or_create(**row)
                        )
                    except Exception:
                        logger.error(
                            f'File: {file_name} | Model: {model} | Row: {row}\n',
                            exc_info=True
                        )
