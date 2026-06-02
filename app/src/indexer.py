import os
from database import get_connection, pool, get_indexed_files
from google.cloud import vision

IMG_PATH = os.environ.get('IMAGE_PATH')

def scan_images():
    results = set()
    for root, dirs, files in os.walk(IMG_PATH):
        for filename in files:
            thisfile = os.path.join(root, filename)
            results.add(thisfile)
    return results

if __name__ == "__main__":
    from database import init_pool
    init_pool()
    on_disk = scan_images()
    in_db = get_indexed_files()
    to_index = on_disk - in_db
    print(f"Images in DB: {len(in_db)}")
    print(f"Images on disk: {len(on_disk)}")
    print(f"Images to index: {len(to_index)}")
