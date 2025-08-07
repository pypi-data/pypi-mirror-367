import zipfile

from io import BytesIO
from os import walk
from os.path import commonpath, join, relpath

def zip_filepaths(file_paths):
    temporary_file = BytesIO()
    relative_start = commonpath(file_paths)

    with zipfile.ZipFile(temporary_file, 'w', zipfile.ZIP_DEFLATED) as zip_temporary_file:
        for file_path in file_paths:
            arcname = relpath(file_path, start = relative_start)
            zip_temporary_file.write(file_path, arcname = arcname)

    return temporary_file.getvalue()

def zip_folder(directory):
    file_paths = []
    for root, dirs, files in walk(directory):
        for file in files:
            file_paths.append(join(root, file))

    return zip_filepaths(file_paths = file_paths)
