from datetime import datetime

def parse_datetime(date_str, time_str):
    dt = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %I:%M %p")
    return dt.strftime("%Y-%m-%d %H:%M:%S")
