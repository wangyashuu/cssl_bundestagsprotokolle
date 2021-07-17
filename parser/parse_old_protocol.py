import xml.etree.ElementTree as ET
import re
import os


def read_speech_text(filename):
    try:
        tree = ET.ElementTree(file=filename)
    except ET.ParseError:
        print("err parse error", filename)
        return ''

    root = tree.getroot()
    text_node = root.find('.//TEXT') or root.find('TEXT')
    t = text_node.text

    beginn_match = re.search(r'[\r|\n|\(]Beginn:* *\d+', t)
    schluss_match = re.search(r'[\r|\n|\(]Schluss:* *\d+', t)
    if beginn_match == None or schluss_match == None:
        print("error not begin or end", filename)

    start_index, end_index = t.index("\n", beginn_match.end())+1, schluss_match.start() - 1
    if start_index < end_index:
        return t[start_index:end_index]
    print("error", start_index, end_index, t)
    return ''


def extract_segments(text):
    segments = []
    segment_splitor = 'Deutscher Bundestag –'
    left_text = text

    while segment_splitor in left_text:
        index = left_text.index(segment_splitor)
        segments.append(left_text[:index])
        st_index = left_text.index("\n", index) + 1 if "\n" in left_text else index
        left_text = left_text[st_index:]
    segments.append(left_text)
    return segments

def extract_paragraphs(raw_text):
    """
    returns:
        paragraphs: content, comment
    """
    splitor = '==[SPLITOR]=='
    discardor = '==[DISCARDOR]=='
    filtered = re.sub('\:[\r|\n]', ':\n\n', raw_text)
    filtered0 = re.sub('[\r|\n]+\(A\) \(C\)[\r|\n]+\(D\)\(B\)', discardor, filtered)
    filtered1 = re.sub(r',[\r|\n]+', ', ', filtered0)
    filtered2 = re.sub(r'[\r|\n]{2,}', splitor, filtered1)
    filtered3 = re.sub(r'-[\r|\n]\b', '', filtered2) # concat ' -'
    filtered4 = re.sub(r'\/[\r|\n]', '/', filtered3)
    filtered5 = re.sub(r'[\r|\n]', ' ', filtered4)
    filtered_text = filtered5

    lines = filtered_text.split(splitor)
    lines = [l for l in lines if l != '' and (len(l) > 60 or l[-1] != ':') and (discardor not in l)]

    paragraphs = []
    short_length = 120
    for l in lines:
        if len(paragraphs) > 0:
            if l[0] == "(" and l[-1] == ")":
                paragraphs[-1][-1] = l[1:-1]
            elif len(l) < short_length:
                # forward detect short paragraphs
                if (not re.search('\d+', l) or len(l) > 5) and paragraphs[-1][-1] == '':
                    paragraphs[-1][0] = paragraphs[-1][0] + " " + l
            else:
                # backward detect short paragraphs
                # if paragraphs[-1][0] < short_length:
                paragraphs.append([l, ''])
        else:
            paragraphs.append([l, ''])
    return paragraphs


def parse_old_protocol(dir_name, file_name):
    """
    returns:
        paragraphs: file_id, segment_id, ...
    """
    idx = file_name.replace(".xml", "")
    file_path = os.path.join(dir_name, file_name)
    text = read_speech_text(file_path)
    segments = extract_segments(text)
    paragraphs = []
    for segment_idx, s in enumerate(segments):
        paragraphs_of_segment = extract_paragraphs(s)
        paragraphs = paragraphs + [[idx, segment_idx] + p for p in paragraphs_of_segment]
    return paragraphs
