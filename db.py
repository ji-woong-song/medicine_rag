import datetime
import aiomysql

import config


async def get_connection():
    return await aiomysql.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        db=config.DB_NAME,
        charset='utf8',
    )


async def get_medicine(user_id: int, start_date: datetime.datetime, end_date: datetime.datetime):
    conn = await get_connection()

    sql = """
        SELECT 
        mi.medicine_name AS medicine_name,
        mb.registration_date AS start_date,
        mb.end_date AS end_date
        FROM 
            medicine_bag mb
        JOIN 
            medicine_input mi ON mb.medicine_bag_id = mi.medicine_bag_id
        WHERE 
            mb.user_id = %s
            AND mb.registration_date BETWEEN %s AND %s
    """
    async with conn.cursor() as cur:
        await cur.execute(sql, user_id, start_date.strftime("%Y-%m-%d %H:%M:%S"), end_date.strftime("%Y-%m-%d %H:%M:%S"))
        items = await cur.fetchall()
        info = [
            {
                'name': item[0],
                'start_date': item[1],
                'end_date': item[2]
            }
            for item in items
        ]
        return info


async def get_blood_sugur(user_id: int, start_date: datetime.datetime, end_date: datetime.datetime):
    conn = await get_connection()
    sql = """
        SELECT
            h.key_name AS measure_type,
            h.key_value AS measure_value,
            h.registration_date AS measure_date
        FROM
            healthcare h
        WHERE
            h.user_id = %s
            AND h.type = 'bloodsugar'
            AND h.registration_date BETWEEN %s AND %s;
    """
    async with conn.cursor() as cur:
        await cur.execute(sql, user_id, start_date.strftime("%Y-%m-%d %H:%M:%S"), end_date.strftime("%Y-%m-%d %H:%M:%S"))
        items = await cur.fetchall()
        info = [{'measure_type': item[0], 'measure_value': item[1], 'measure_data': item[2]} for item in items]
        return info

async def get_blood_pressure(user_id: int, start_date: datetime.datetime, end_date: datetime.datetime):
    conn = await get_connection()
    sql = """
           SELECT 
               h1.key_value AS high_pressure,
               h2.key_value AS low_pressure,
               h1.registration_date AS measure_date
           FROM 
               healthcare h1
           JOIN 
               healthcare h2 
           ON 
               h1.registration_date = h2.registration_date
               AND h1.user_id = h2.user_id
           WHERE 
               h1.user_id = %s
               AND h1.type = 'bloodpresure'
               AND h2.type = 'bloodpresure'
               AND h1.key_name = 'highpressure'
               AND h2.key_name = 'lowpressure'
               AND h1.registration_date BETWEEN %s AND %s
           ORDER BY
               h1.registration_date DESC;
       """
    async with conn.cursor() as cur:
        await cur.execute(sql, user_id, start_date.strftime("%Y-%m-%d %H:%M:%S"), end_date.strftime("%Y-%m-%d %H:%M:%S"))
        items = await cur.fetchall()
        info = [{'high_pressure': item[0], 'low_pressure': item[1], 'measure_date': item[2]} for item in items]
        return info


async def get_food(user_id: int, start_date: datetime.datetime, end_date: datetime.datetime):
    conn = await get_connection()
    sql = """
        SELECT
            h.key_name AS measure_type,
            h.key_value AS measure_value,
            h.registration_date AS measure_date
        FROM
            healthcare h
        WHERE
            h.user_id = %s
            AND h.type = 'meal'
            AND h.registration_date BETWEEN %s AND %s;
    """
    async with conn.cursor() as cur:
        await cur.execute(sql, user_id, start_date.strftime("%Y-%m-%d %H:%M:%S"), end_date.strftime("%Y-%m-%d %H:%M:%S"))
        items = await cur.fetchall()
        info = [{'measure_type': item[0], 'measure_value': item[1], 'measure_data': item[2]} for item in items]
        return info


async def get_gi():
    conn = await get_connection()
    sql = """
        SELECT
            g.name AS name,
            g.giScore as score
        FROM
            gi g
    """
    async with conn.cursor() as cur:
        await cur.execute(sql)
        items = await cur.fetchall()
        info = [{'name': item[0], 'value': item[1]} for item in items]
        return info

