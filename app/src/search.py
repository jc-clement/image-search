from database import get_images


def interpret_search(search, order):
    # Interpret search string

    timestamp = None
    # - Create timestamp range if included

    lat, lng = None, None
    # - Create lat/lng range if included

    labels = None
    # - Create label search terms if included

    orderby = 'timestamp desc'
    # default - show newest first
    # if order is set update ORDER BY


    if search:
        labels = [search]

    images, total = get_images(timestamp, lat, lng, labels, orderby)
    return images, total
