import psycopg2
import psycopg2.pool
import os

host = os.environ.get('POSTGRES_HOST')
dbname = os.environ.get('POSTGRES_DB')
user = os.environ.get('POSTGRES_USER')
password = os.environ.get('POSTGRES_PASSWORD')

pool = None


def init_pool():
    global pool
    try:
        pool = psycopg2.pool.SimpleConnectionPool(1, 2, host=host, dbname=dbname, user=user, password=password)
    except psycopg2.OperationalError as e:
        print(f"Database connection failed: {e}")
        exit(1)


def get_connection():
    try:
        return pool.getconn()
    except psycopg2.OperationalError as e:
        print(f"Couldn't assign DB connection from pool: {e}")
        exit(1)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    create_statement = """CREATE TABLE IF NOT EXISTS images (
    image_id SERIAL PRIMARY KEY,
    filepath TEXT,
    filename TEXT,
    timestamp TIMESTAMP,
    lat DECIMAL(9,6),
    lng DECIMAL(9,6),
    tags TEXT[],
    file_exists BOOLEAN DEFAULT TRUE,
    favourite BOOLEAN DEFAULT FALSE)"""
    try:
        cursor.execute(create_statement)
        conn.commit()
        print("Database initialised successfully")
    except psycopg2.Error as e:
        print(f"Database initialisation failed: {e}")
        conn.rollback()
        exit(1)
    finally:
        pool.putconn(conn)


def get_indexed_files():
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT filepath, filename FROM images"
    try:
        images_in_db = set()
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            filepath, filename = row
            thisfile = os.path.join(filepath, filename)
            images_in_db.add(thisfile)
        return images_in_db
    except psycopg2.Error as e:
        print(f"Couldn't query DB: {e}")
        exit(1)
    finally:
        pool.putconn(conn)


def save_image(filepath, filename, timestamp, lat, lng, tags, favourite):
    conn = get_connection()
    cursor = conn.cursor()
    insert_statement = """
    INSERT INTO images (filepath, filename, timestamp, lat, lng, tags, favourite)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    data = (filepath, filename, timestamp, lat, lng, tags, favourite)
    try:
        cursor.execute(insert_statement, data)
        conn.commit()
        print(f"Inserted {filename}")
    except psycopg2.Error as e:
        print(f"Failed for {filename}: {e}")
        conn.rollback()
    finally:
        pool.putconn(conn)


def get_images(year, month, day, lat, lng, labels, orderby):
    conn = get_connection()
    cursor = conn.cursor()
    params = []
    conditions = []

    if labels:
        for label in labels:
            conditions.append("%s ILIKE ANY(tags)")
            params.append(label)

    if year:
        conditions.append("EXTRACT(year FROM timestamp) = %s")
        params.append(year)

    if month:
        conditions.append("EXTRACT(month FROM timestamp) = %s")
        params.append(month)

    if day:
        conditions.append("EXTRACT(day FROM timestamp) = %s")
        params.append(day)

    if conditions:
        where = "WHERE " + " AND ".join(conditions)
    else:
        where = ""

    select_statement = f"""
        SELECT image_id, filepath, filename, timestamp, lat, lng, tags
        FROM images
        {where}
        ORDER BY {orderby}
    """
    try:
        cursor.execute(select_statement, params if params else None)
        results = cursor.fetchall()
        images = []
        for row in results:
            image_id, filepath, filename, timestamp, lat, lng, tags = row
            images.append({
                'image_id': image_id,
                'filepath': filepath,
                'filename': filename,
                'timestamp': timestamp,
                'lat': lat,
                'lng': lng,
                'tags': tags,
                'thumb': f"{filepath}/.thumbs/{filename}",
                'display': f"{filepath}/.display/{filename}"
            })
        cursor.execute("SELECT COUNT(*) FROM images")
        total = cursor.fetchone()[0]
        return images, total
    except psycopg2.Error as e:
        print(f"DB query failed: {e}")
        return []
    finally:
        pool.putconn(conn)


def get_labels_cloud():
    conn = get_connection()
    cursor = conn.cursor()
    select_statement = """SELECT unnest(tags) as label, COUNT(*) as freq
        FROM images
        GROUP BY label
        ORDER BY freq DESC
    """
    try:
        cursor.execute(select_statement)
        results = cursor.fetchall()
        labs = []
        for row in results:
            label, freq = row
            labs.append({
                'label': label,
                'freq': freq
            })
        return labs
    except psycopg2.Error as e:
        print(f"DB query failed: {e}")
        return []
    finally:
        pool.putconn(conn)
