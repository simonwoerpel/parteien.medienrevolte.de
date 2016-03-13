from __future__ import unicode_literals

import os
import yaml

from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property

from .analysis import Corpus, WordCloud

CORPORA_DIR = os.path.join(settings.BASE_DIR, settings.APP['config']['corpora_dir'])
DATA_DIR = os.path.join(settings.BASE_DIR, settings.APP['config']['data_dir'])
DATA = settings.APP['states']


@python_2_unicode_compatible
class State(object):

    def __init__(self, slug):
        self._data = DATA[slug]
        self.slug = slug
        self.name = self._data['name']

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.name)

    def get_absolute_url(self):
        return '/#{}'.format(self.slug)

    @property
    def parties(self):
        return [Party(self.slug, slug)
                for slug in self._data['parties'].keys()]

    @classmethod
    def all(cls):
        return [cls(slug) for slug in DATA.keys()]


@python_2_unicode_compatible
class Party(object):

    def __init__(self, state_slug, slug):
        self._data = DATA[state_slug]['parties'][slug]
        self.state_slug = state_slug
        self.slug = slug
        self.name = self._data['name']
        self.start_page = self._data['start_page']
        self.end_page = self._data['end_page']

    def __str__(self):
        return '{} ({})'.format(self.name, self.state)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, str(self))

    def get_absolute_url(self):
        return '/#{}-{}'.format(self.state_slug, self.slug)

    @property
    def state(self):
        return State(self.state_slug)

    @property
    def data(self):
        return yaml.load(open(self._data_fp))

    @property
    def input_file(self):
        return '{}.pdf'.format(self._corpora_fp)

    @property
    def output_file(self):
        return '{}.txt'.format(self._corpora_fp)

    @property
    def corpus(self):
        return Corpus(self.output_file)

    @cached_property
    def wordcloud(self):
        return self.get_wordcloud(self.corpus.lemmatized_text)

    def get_wordcloud(self, text):
        return WordCloud(self._data['file'], text)

    @property
    def wordcloud_url(self):
        return '{}/{}/{}.png'.format(
            settings.MEDIA_URL.rstrip('/'),
            settings.APP['config']['wordcloud_dir'],
            self._data['file'],
        )

    @property
    def _data_fp(self):
        return os.path.join(
            DATA_DIR,
            '{}.yaml'.format(self._data['file']),
        )

    @property
    def _corpora_fp(self):
        return os.path.join(CORPORA_DIR, self._data['file'])

    def pdftotext(self):
        os.system('pdftotext -f {} -l {} {} {}'.format(
            self.start_page,
            self.end_page,
            self.input_file,
            self.output_file,
        ))

    def generate(self):
        """
        generate data and save to disk as yaml
        also generate wordcloud
        """
        self.wordcloud.generate()
        data = self.get_data()
        yaml.dump(data, open(self._data_fp, 'w'))

    def get_data(self):
        corpus = self.corpus
        data = {
            'stats': {
                k: getattr(corpus.stats, k) for k in
                dir(corpus.stats) if '__' not in k
                and not k == 'blob'
            },
            'phrases': corpus.get_phrases(),
            'words': corpus.get_words(),
            '2grams': corpus.ngrams.get(2)[:10],
            '3grams': corpus.ngrams.get(3)[:10],
        }
        return data

    @classmethod
    def all(cls):
        return [cls(state_slug, slug) for state_slug in DATA.keys()
                for slug in DATA[state_slug]['parties']]
