# coding: utf-8

def write_lines(lines, file_path, add=False):
    mode = 'a' if add else 'w'
    lines = map(lambda l: l + '\n', lines)
    with open(file_path, mode) as file:
        file.writelines(lines)