import subprocess
import tempfile
import os
import sys

def test_cli_clean_import():
    input_content = """import os, sys
import numpy as np
from math import (
    sqrt,
    floor,
)
print(np.array([1, 2, 3]))
result = sqrt(9)
print('done')
"""

    expected_output = [
        "import numpy as np",
        "from math import (",
        "    sqrt,",
        ")",
        "print(np.array([1, 2, 3]))",
        "result = sqrt(9)",
        "print('done')",
    ]

    with tempfile.NamedTemporaryFile(mode='w+', suffix=".py", delete=False) as tmp_input:
        tmp_input.write(input_content)
        tmp_input_path = tmp_input.name

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pycleaner.cli", "clean-import", tmp_input_path],
            capture_output=True,
            text=True,
            check=True,
        )

        with open(tmp_input_path, "r") as f:
            cleaned_lines = f.read().splitlines()

        assert cleaned_lines == expected_output

        assert "Cleaning imports" in result.stderr
        assert "Done" in result.stderr


    finally:
        os.remove(tmp_input_path)
