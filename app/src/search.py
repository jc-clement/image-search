import os
from database import get_connection, pool, get_images
from datetime import datetime

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

    images = get_images(timestamp, lat, lng, labels, orderby)
    return images
