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
