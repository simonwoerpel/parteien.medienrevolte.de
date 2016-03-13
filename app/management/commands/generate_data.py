from django.core.management.base import BaseCommand

from ...models import Party


class Command(BaseCommand):
    help = 'Generates data (and wordcloud) for every party'

    def handle(self, *args, **options):
        i = 0
        for party in Party.all():
            self.stdout.write('Processing {} ({}) ...'.format(party.name, party.state.name))
            party.generate()
            i += 1

        self.stdout.write(self.style.SUCCESS('Successfully processed {} parties'.format(i)))
