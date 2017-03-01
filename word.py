import os
from Diploma_project.settings import BASE_DIR

def split_row(file_name, dir_path = BASE_DIR):
    f = open(os.path.join(dir_path,file_name), 'r')
    data = f.read().split('\n')
    return reduce(lambda res, x: res + [x], data, [])