from datetime import datetime


def row_format(*wargs):
    content = "|"
    for arg in wargs:
        content += f" {arg} |"
    content += "\n"
    return content

def table_medicine(infos: list[str,datetime.date, datetime.date]) -> str:
    content = ""
    for info in infos:
        start_date = info['start_date'].strftime("%Y-%m-%d")
        end_date = info['end_date'].strftime("%Y-%m-%d")
        name = info['name']
        content += row_format(start_date, end_date, name)
    return content


def table_blood_sugar(infos: list[str,int, datetime.date]) -> str:
    content = ""
    for info in infos:
        date = info['measure_data'].strftime("%Y-%m-%d %H:%M")
        # measure = info['measure_type']
        value = info['measure_value']
        content += row_format(date, value)
    return content

def table_blood_pressure(infos: list[str,int, datetime.date]) -> str:
    content = ""
    for info in infos:
        date = info['measure_date'].strftime("%Y-%m-%d %H:%M")
        high_value = info['high_pressure']
        low_value = info['low_pressure']
        content += row_format(high_value, low_value, date)
    return content

def table_food(infos: list[str,str, datetime.date]) -> str:
    content = ""
    for info in infos:
        date = info['measure_data'].strftime("%Y-%m-%d %H:%M")
        # name = info['measure_type']
        value = info['measure_value']
        content += row_format(date, value)
    return content


def table_gi(infos: list[str,int]) -> str:
    content = ""
    for info in infos:
        name = info['name']
        value = info['value']
        content += row_format(name, value)
    return content

