from datetime import datetime
from pathlib import Path


def save_file(filename, data):
    data_folder = Path("static", "data")
    data_folder.mkdir(parents=True, exist_ok=True)

    target = Path(data_folder).joinpath(filename)
    target = Path(target.with_name(f"input{target.suffix}"))
    with open(target, "wb") as f:
        f.write(data)
    return target


def parse_int(num):
    try:
        return int(num)
    except ValueError:
        return False


def parse_float(num):
    if isinstance(num, float):
        return num
    try:
        return float(num.replace(".", "").replace(",", ".")) if num else 0
    except ValueError:
        return False


def parse_date(d):
    return datetime.strptime(d, "%d/%m/%Y").date()
