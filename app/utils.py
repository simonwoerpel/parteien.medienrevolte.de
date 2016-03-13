from collections import Counter


def cleanup_line(line):
    '''cleanup (convert \n to space and strip out line numbers)'''
    l = line.replace('\n', ' ')
    try:
        int(l.strip())
        return ''
    except ValueError:
        return l


def lower_words(iterable):
    """
    turn all words in `iterable` to lower
    """
    return [w.lower() for w in iterable]


def get_occurences(iterable):
    """
    count occurences of same items in iterable,
    ordered from most,
    represented as tuple:
        (item, n)
    """
    return sorted(
        [(i, Counter(iterable).get(i)) for i in list(set(iterable))],
        key=lambda x: x[1],
        reverse=True
    )
