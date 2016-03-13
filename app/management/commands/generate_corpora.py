from django.core.management.base import BaseCommand

from ...models import Party


class Command(BaseCommand):
    help = 'Converts all pdf files from all Parties into plain text'

    def handle(self, *args, **options):
        i = 0
        for party in Party.all():
            self.stdout.write('Processing {} ({}) ...'.format(party.name, party.input_file))
            party.pdftotext()
            i += 1

        self.stdout.write(self.style.SUCCESS('Successfully converted {} files'.format(i)))
