import os
from database import get_connection, pool, get_indexed_files, save_image
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
import requests
import base64

IMG_PATH = os.environ.get('IMAGE_PATH')

def scan_images():
    results = set()
    for root, dirs, files in os.walk(IMG_PATH):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for filename in files:
            thisfile = os.path.join(root, filename)
            results.add(thisfile)
    return results

def get_exif(img_in):
    img = Image.open(img_in)
    exif_raw = img.getexif()
    if exif_raw is None:
        return {}
    exif = {}
    for tag_id, value in exif_raw.items():
        tag = TAGS.get(tag_id, tag_id)
        exif[tag] = value

    #DateTimeOriginal separately
    exif_ifd = exif_raw.get_ifd(0x8769)
    for tag_id, value in exif_ifd.items():
        tag = TAGS.get(tag_id, tag_id)
        exif[tag] = value

    #Get GPS separately
    gps_ifd = exif_raw.get_ifd(0x8825)
    gps = {}
    for tag_id, value in gps_ifd.items():
        tag = GPSTAGS.get(tag_id, tag_id)
        gps[tag] = value
    exif['GPSInfo'] = gps

    return exif

def get_timestamp(exif):
    timestamp = exif.get('DateTimeOriginal')
    if not timestamp:
        return None
    return datetime.strptime(timestamp, '%Y:%m:%d %H:%M:%S')

def convert_to_decimal(value):
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m /60.0) + (s / 3600.0)

def get_gps(exif):
    gps = exif.get('GPSInfo')
    if not gps:
        return None, None
    if 'GPSLatitude' not in gps or 'GPSLongitude' not in gps:
        return None, None

    lat = convert_to_decimal(gps['GPSLatitude'])
    lat_ref = gps['GPSLatitudeRef']
    lng = convert_to_decimal(gps['GPSLongitude'])
    lng_ref = gps['GPSLongitudeRef']
    
    if lat_ref != 'N':
        lat = -lat
    if lng_ref != 'E':
        lng = -lng
    return lat, lng

def get_labels(img_in):
    # API calls disabled while debugging timestamp
    with open(img_in, 'rb') as f:
        content = base64.b64encode(f.read()).decode('utf-8')

    api_key = os.environ.get('GOOGLE_VISION_API_KEY')
    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"

    payload = {
        "requests": [{
            "image": {"content": content},
            "features": [{"type": "LABEL_DETECTION", "maxResults": 50}]
        }]
    }

    response = requests.post(url, json=payload)
    result = response.json()
    annotations = result.get('responses', [{}])[0].get('labelAnnotations', [])
    if not annotations:
        print(f"No labels returned for {os.path.basename(img_in)}, skipping")
        return None
    # debug Google Vision calls
    # print(f"API response: {result}")
    return [label['description'] for label in annotations]

def create_thumb(dir, file):
    source = os.path.join(dir, file)

    thumb_dir = '.thumbs'
    mk_thumb_dir = os.path.join(dir, thumb_dir)
    os.makedirs(mk_thumb_dir, exist_ok=True)
    img = Image.open(source)
    exif = img.info.get('exif', b'')
    img.thumbnail((400, 400))
    img.save(os.path.join(mk_thumb_dir, file), exif=exif)
    print(f"Created thumb for {file}")

    display_dir = '.display'
    mk_disp_dir = os.path.join(dir, display_dir)
    os.makedirs(mk_disp_dir, exist_ok=True)
    img = Image.open(source)
    exif = img.info.get('exif', b'')
    img.thumbnail((1200, 1200))
    img.save(os.path.join(mk_disp_dir, file), exif=exif)
    print(f"Created websize for {file}")

if __name__ == "__main__":
    from database import init_pool
    init_pool()
    on_disk = scan_images()
    in_db = get_indexed_files()
    to_index = on_disk - in_db
    print(f"Images in DB: {len(in_db)}")
    print(f"Images on disk: {len(on_disk)}")
    print(f"Images to index: {len(to_index)}")

    #create thumbnails
    for thisimg in on_disk:
        filename = os.path.basename(thisimg)
        directory = os.path.dirname(thisimg)
        thumb_path = os.path.join(directory, '.thumbs', filename)
        if not os.path.exists(thumb_path):
            create_thumb(directory, filename)

    #index new images
    for thisimg in to_index:
        filename = os.path.basename(thisimg)
        directory = os.path.dirname(thisimg)
        exif = get_exif(thisimg)
        timestamp  = get_timestamp(exif)
        lat, lng = get_gps(exif)
        disp_img = os.path.join(directory, '.display', filename)
        tags = get_labels(disp_img)
        if tags is None:
            print(f"Skipping: {thisimg}")
            continue
        # Favourite check (Google takeout) - TODO
        save_image(directory, filename, timestamp, lat, lng, tags, False)
