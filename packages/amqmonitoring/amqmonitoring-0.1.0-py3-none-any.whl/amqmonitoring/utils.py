from pathlib import Path
import json


def read_dict_file(path_to_file: Path):
    with open(path_to_file, encoding='UTF-8') as _fh:
        return json.load(_fh)