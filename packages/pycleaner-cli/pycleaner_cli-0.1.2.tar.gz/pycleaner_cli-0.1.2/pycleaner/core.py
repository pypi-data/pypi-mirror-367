from .utils import get_clean_import,write_file

def clean_import(file):
    clean_ = get_clean_import(file)
    write_file(file,clean_)
    

