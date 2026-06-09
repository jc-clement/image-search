from database import get_images
import re


def interpret_search(search, order):
    # Interpret search string

    year, month, day = None, None, None
    lat, lng = None, None
    labels = None
    orderby = 'timestamp DESC'

    if search:
        tokens = search.split()
        label_tokens = []
        for token in tokens:
            if re.match(r'^\d{4}-\d{2}-\d{2}$', token):
                parts = token.split('-')
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
            elif re.match(r'^\d{4}-\d{2}$', token):
                parts = token.split('-')
                year = int(parts[0])
                month = int(parts[1])
            elif re.match(r'^\d{4}$', token):
                year = int(token)
            else:
                label_tokens.append(token)
        if label_tokens:
            labels = label_tokens

    images, total = get_images(year, month, day, lat, lng, labels, orderby)
    return images, total
