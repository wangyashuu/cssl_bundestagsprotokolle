import os


def parse_protocols(dir_name, parse_protocol):
    file_names = [f for f in os.listdir(dir_name) if f[-4:] == '.xml']
    paragraphs = []
    for file_name in file_names:
        paragraphs = paragraphs + parse_protocol(dir_name, file_name)
    return paragraphs
