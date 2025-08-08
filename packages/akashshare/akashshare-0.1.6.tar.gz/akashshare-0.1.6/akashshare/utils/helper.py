
def get_filename(file_path):
    return file_path.split("/")[-1]

def get_dirname(dir_path):
    files = dir_path.split("/")
    if files[-1] != "":
        return files[-1]
    else:
        return files[-2]

def get_file_names_from_dir(dir_path):
    files = dir_path.split("/")
    if files[-1] != "":
        files.pop(-1) 
        return files   

    return files
