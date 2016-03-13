"""
analysing corpora with textblob_de

"""

import os

from django.conf import settings
from django.utils.functional import cached_property
from nltk.util import ngrams
from textblob_de import TextBlobDE as TextBlob
from wordcloud import WordCloud as WC

from .utils import cleanup_line, lower_words, get_occurences


STOPWORDS = set([
    w.rstrip('\n') for w in
    open(os.path.join(
        settings.BASE_DIR,
        settings.APP['config']['stopwords_file']
    )).readlines()
])


class BaseBlobStats(object):

    def __init__(self, blob):
        self.blob = blob

    @cached_property
    def sentences(self):
        return len(self.blob.sentences)

    @cached_property
    def sentences_unique(self):
        return len(list(set(self.blob.sentences)))

    @cached_property
    def phrases(self):
        return len(self.blob.noun_phrases)

    @cached_property
    def phrases_unique(self):
        return len(list(set(self.blob.noun_phrases)))

    @cached_property
    def words(self):
        return len(self.blob.words)

    @cached_property
    def words_unique(self):
        return len(list(set(lower_words(self.blob.words))))


class Ngrams(object):
    def __init__(self, words):
        self.words = words

    def get(self, n):
        """
        return n-grams as single space-separated strings
        with their occurences
        """
        parts = [' '.join(g) for g in ngrams(self.words, n)]
        return get_occurences(parts)


class Corpus(object):

    def __init__(self, fp):
        self.fp = fp

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, str(self))

    @property
    def name(self):
        return self.fp.split('/')[-1]

    def get_phrases(self, first=10):
        """
        return most used noun_phrases
        """
        return get_occurences(self.lemmatized_phrases)[:first]

    def get_words(self, first=10):
        """
        return most used words
        """
        return get_occurences(self.lemmatized_words)[:first]

    @cached_property
    def ngrams(self):
        return Ngrams(self.lemmatized_words)

    @cached_property
    def blob(self):
        return TextBlob(self.text)

    @cached_property
    def text(self):
        lines = open(self.fp).readlines()
        return ' '.join([cleanup_line(l) for l in lines])

    @cached_property
    def lemmatized_phrases(self):
        """
        lemmatize words in noun_phrases,
        exclude phrases with `STOPWORDS`
        """
        phrases = [set(lower_words(TextBlob(p).words.lemmatize()))
                   for p in self.blob.noun_phrases]
        return [' '.join(p) for p in phrases if not STOPWORDS.intersection(p)]

    @cached_property
    def lemmatized_words(self):
        return [w for w in lower_words(self.blob.words.lemmatize())
                if w not in STOPWORDS]

    @cached_property
    def lemmatized_text(self):
        return ' '.join(self.lemmatized_words)

    @cached_property
    def stats(self):
        return BaseBlobStats(self.blob)


class WordCloud(object):
    def __init__(self, slug, text):
        self.text = text
        self.slug = slug
        self._configure()

    def __str__(self):
        return self.slug

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.slug)

    def generate(self):
        wc = self._wordcloud.generate(self.text)
        wc.to_file(self.fp)

    @property
    def _wordcloud(self):
        return WC(
            stopwords=list(STOPWORDS),
            background_color=self.background_color,
            width=self.width,
            height=self.height,
        )

    @property
    def fp(self):
        return os.path.join(
            settings.MEDIA_ROOT,
            settings.APP['config']['wordcloud_dir'],
            '{}.png'.format(self.slug)
        )

    def _configure(self):
        for k, v in settings.APP['config']['wordcloud'].items():
            setattr(self, k, v)
