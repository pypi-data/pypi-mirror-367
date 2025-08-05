from unittest.mock import mock_open, patch
from pycleaner.utils import _is_module_used,_get_next_words,read_file,write_file,clean_multiline_import,get_clean_import

def test_module_used():
    content = [
        "import numpy as np",
        "data = np.array([1, 2, 3])"
    ]
    assert _is_module_used("np",content) is True

def test_module_not_used():
    content = [
        "import numpy as np",
    ]
    assert _is_module_used("np",content) is False

def test_module_used_in_multiline_import():
    content = [
        "from os import (",
        "    path,",
        "    system",
        ")",
        "system('ls')"

    ]
    assert _is_module_used("system",content) is True        

def test_module_not_used_after_multiline_import():
    content = [
        "from os import (",
        "    path,",
        "    system",
        ")"
    ]
    assert _is_module_used("system",content) is False   

def test_next_word_found_not_split():
    line = "import numpy as np"     
    assert _get_next_words("import",line,False) == "numpy as np"   

def test_next_word_not_found_not_split():
    line = "import"     
    assert _get_next_words("import",line,False) == None

def test_next_words_found_split():
    line = "import numpy as np"     
    assert _get_next_words("import",line) == ["numpy as np"]    

def test_read():
    fake_content = "hello\nworld"
    m = mock_open(read_data=fake_content)
    with patch("builtins.open", m):
        lines = read_file("dummy.txt")

    assert lines == ["hello", "world"]

def test_write():
    data = ["one", "two", "three"]
    m = mock_open()

    with patch("builtins.open", m):
        write_file("dummy.txt", data)

    m().writelines.assert_called_once()

    actual_arg = m().writelines.call_args[0][0]

    assert hasattr(actual_arg, '__iter__') and not isinstance(actual_arg, list)

    assert list(actual_arg) == [line + '\n' for line in data]


def test_clean_multiline_used():
    content = [
        "from os import (",
        "    path,",
        "    system",
        ")",
        "system('ls')"
    ]
    import_block = "from os import (\n    path,\n    system\n)"
    assert clean_multiline_import(import_block,content) == "from os import (\n    system,\n)"

def test_clean_multiline_not_used():
    content = [
        "from os import (",
        "    path,",
        "    system",
        ")",
    ]
    import_block = "from os import (\n    path,\n    system\n)"
    assert clean_multiline_import(import_block,content) == ""   

@patch("pycleaner.utils.read")
def test_get_clean_import_filters_correctly(mock_read):
    mock_read.return_value = [
        "import numpy as np",
        "import os, sys",
        "from math import (",
        "    sqrt,",
        "    floor",
        ")",
        "result = np.array([1, 2, 3])",
        "print('Done')"
    ]

    result = get_clean_import("fake_file.py")

    assert result == [
        "import numpy as np",                                                
        "result = np.array([1, 2, 3])",
        "print('Done')"
    ]
    
@patch("pycleaner.utils.read")
def test_get_clean_import_filters_empty_list(mock_read):
    mock_read.return_value = []

    result = get_clean_import("fake_file.py")

    assert result == []

@patch("pycleaner.utils.read")
def test_get_clean_only_imports(mock_read):
    mock_read.return_value = [
        "import numpy as np",
        "import os, sys",
    ]

    result = get_clean_import("fake_file.py")

    assert result == []

@patch("pycleaner.utils.read")
def test_get_clean_only_code(mock_read):
    mock_read.return_value = [
        "c= 5+5",
        "print(c)"
    ]

    result = get_clean_import("fake_file.py")

    assert result == [ 
        "c= 5+5",
        "print(c)"
    ]

@patch("pycleaner.utils.read")    
def test_get_clean_import_multiline_no_usage(mock_read):
    mock_read.return_value = [
        "from math import (",
        "    sqrt,",
        "    floor",
        ")",
        "print('Done')"
    ]

    result = get_clean_import("fake_file.py")

    assert result == [
        "print('Done')"
    ]    

       