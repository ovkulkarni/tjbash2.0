from django.core.management.base import BaseCommand, CommandError
from quotes.models import Quote, Tag

import csv

class Command(BaseCommand):
    help = 'Import Quotes from CSV file formatted "quote,votes,tags"'

    def add_arguments(self, parser):
        parser.add_argument("-f", "--csv_file", help="CSV file to use", nargs=1, default="quotes.csv")

    def handle(self, *args, **options):
        with open(options['csv_file'], 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                q = Quote.objects.create(content=row[0], votes=row[1], approved=True)
                for tag_name in row[2].split(","):
                    if tag_name is not "":
                        tag, created = Tag.objects.get_or_create(name=tag_name)
                        q.tags.add(tag)
        self.stdout.write(self.style.SUCCESS("All quotes from %s imported" % options['csv_file']))
