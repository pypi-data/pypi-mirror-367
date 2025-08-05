from pycleaner.utils import get_clean_import

def test_benchmark_get_clean_import(benchmark):
    file_path = "tests/test_files/sample.py"
    benchmark(get_clean_import, file_path)
