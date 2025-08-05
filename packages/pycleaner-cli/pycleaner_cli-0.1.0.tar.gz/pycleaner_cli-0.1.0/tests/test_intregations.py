import os
import tempfile
from pycleaner.utils import read_file,write_file,get_clean_import

def test_write_and_read():
    data = ["kobe","micheal","lebron"]

    with tempfile.NamedTemporaryFile(delete=False) as tf:
        temp = tf.name

    try:
        write_file(temp,data)
        result = read_file(temp)
        assert result == data
    finally:
        os.remove(temp)       


def test_import_cleaner():
    input_content = [
        "import os, sys",
        "import numpy as np",
        "from math import (",
        "    sqrt,",
        "    floor,",
        ")",
        "print(np.array([1,2,3]))",
        "result = sqrt(9)",
        "print('done')"
    ]

    expected_filtered = [
        "import numpy as np",
        "from math import (",
        "    sqrt,",
        ")",
        "print(np.array([1,2,3]))",
        "result = sqrt(9)",
        "print('done')"
    ]

    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as input_file:
        input_file.writelines(line + "\n" for line in input_content)
        input_file_path = input_file.name

    with tempfile.NamedTemporaryFile(mode='r+', delete=False) as output_file:
        output_file_path = output_file.name

    try:
        filtered = get_clean_import(input_file_path)
        write_file(output_file_path, filtered)

        with open(output_file_path, 'r') as f:
            result_lines = f.read().splitlines()

        assert result_lines == expected_filtered
    finally:
        os.remove(input_file_path)
        os.remove(output_file_path)

