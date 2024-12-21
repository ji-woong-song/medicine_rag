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


async def get_medicine(user_id: int):
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
            AND mb.registration_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 30 DAY) AND CURDATE();
    """
    async with conn.cursor() as cur:
        await cur.execute(sql, user_id)
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


async def get_blood_sugur(user_id: int):
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
            AND h.registration_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 30 DAY) AND CURDATE()
            AND h.type = 'bloodsugar';
    """
    async with conn.cursor() as cur:
        await cur.execute(sql, user_id)
        items = await cur.fetchall()
        info = [{'measure_type': item[0], 'measure_value': item[1], 'measure_data': item[2]} for item in items]
        return info


async def get_blood_pressure(user_id: int):
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
               AND h.registration_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 30 DAY) AND CURDATE()
               AND h.type = 'bloodpressure';
       """
    async with conn.cursor() as cur:
        await cur.execute(sql, user_id)
        items = await cur.fetchall()
        info = [{'measure_type': item[0], 'measure_value': item[1], 'measure_data': item[2]} for item in items]
        return info

