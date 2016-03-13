from django.core.management.base import BaseCommand

from ...models import Party


class Command(BaseCommand):
    help = 'Creates wordclouds for all parties'

    def handle(self, *args, **options):
        i = 0
        for party in Party.all():
            self.stdout.write('Processing {} ({}) ...'.format(party.name, party.state.name))
            party.wordcloud.generate()
            i += 1

        self.stdout.write(self.style.SUCCESS('Successfully converted {} files'.format(i)))
