from pathlib import Path


def read_sql_file(file_name):
    sql_path = Path(__file__).parent / "versions" / "sql" / file_name
    with open(sql_path, "r") as file:
        return file.read()