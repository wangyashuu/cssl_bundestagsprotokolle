import xml.etree.ElementTree as ET
import re
import os


def read_speech_text(filename):
    try:
        tree = ET.ElementTree(file=filename)
    except ET.ParseError:
        print("err parse error", filename)
        return '', ''

    root = tree.getroot()
    text_node = root.find('.//TEXT') or root.find('TEXT')
    t = text_node.text

    beginn_match = re.search(r'[\r|\n|\(]Beginn:* *\d+', t)
    schluss_match = re.search(r'[\r|\n|\(]Schluss:* *\d+', t)
    if beginn_match == None or schluss_match == None:
        print("error not begin or end", filename)

    start_index, end_index = t.index("\n", beginn_match.end())+1, schluss_match.start() - 1
    if start_index < end_index:
        # print("stst", start_index, len(t[:start_index]), len(t))
        return t[start_index:end_index], t[:start_index]
    print("error", start_index, end_index, t)
    return ''


def extract_segments(text):
    segments = []
    segment_splitor = 'Deutscher Bundestag –'
    left_text = text
    speaker, next_speaker = '', ''
    while segment_splitor in left_text:
        index = left_text.index(segment_splitor)
        segment = left_text[:index].strip()
        if '\n' in segment:
            idx = segment.rindex('\n')
            potential_speaker = segment[idx:].strip()
            if is_speaker(potential_speaker):
                next_speaker = potential_speaker
                segments = segments[:idx]
        segments.append((speaker + "\n\n" if speaker != '' else '') + segment)
        speaker = next_speaker
        next_speaker = ''
        st_index = left_text.index("\n", index) + 1 if "\n" in left_text else index
        left_text = left_text[st_index:]

    segments.append(left_text)
    return segments


def is_speaker(l):
    l = l.strip()
    if len(l) > 120 or len(l) < 3:
        return False
    if l[0] == '(':
        return False

    first_part = l.split(',')[0].split(' ')
    if first_part[0] in ['Art.', 'Die', 'Herr', 'Dort', 'Drucksache', 'hier', 'Der', 'Ich', 'Wir', 'Und', 'Es']:
        return False
    if any(t in ['Präsident', 'Vizepräsident', 'Bundesminister', \
                 'Präsidentin', 'Vizepräsidentin', 'Bundesministerin', \
                 'Dr.'] for t in first_part[:3]):
        return True
    if any(re.search(r'\d+', t) != None for t in first_part[:3]):
        return False
    if any(t in ['für', 'die', 'des', 'der', 'das', 'den', 'zu', 'im'] for t in first_part[:3]):
        return False
    if l[-1] == ')' or l[-1] == ']' or l[-2] == ')' or l[-2] == ']' :
        return True

    return len(first_part) >=2 and len(first_part) <= 4


def extract_paragraphs(raw_text, filename):
    """
    returns:
        paragraphs: speaker, content, comment
    """
    splitor = '==[SPLITOR]=='
    discardor = '==[DISCARDOR]=='
    # filtered = re.sub('\:[\r|\n]', ':\n\n', raw_text)
    filtered = re.sub('([\r|\n]+)?\(A\)( ?\(C\))?[\r|\n]+\(D\)( ?\(B\))?', ':\n\n', raw_text)
    filtered0 = re.sub('([\r|\n]+)?(\(A\) ?)?\(C\)[\r|\n]+(\(D\) ?)?\(B\)', ':\n\n', filtered)
    filtered1 = re.sub(r',[\r|\n]+', ', ', filtered0)
    filtered2 = re.sub(r'[\r|\n]{2,}', splitor, filtered1)
    filtered3 = re.sub(r'-[\r|\n]\b', '', filtered2) # concat ' -'
    filtered4 = re.sub(r'\/[\r|\n]', '/', filtered3)
    filtered5 = re.sub(r'\:[\r|\n]', ':-', filtered4)
    filtered6 = re.sub(r'[\r|\n]', ' ', filtered5)
    filtered_text = filtered6

    lines = filtered_text.split(splitor)
    lines = [l for l in lines if l != '' and (discardor not in l)]

    short_length = 30
    speaker = ''
    paragraphs = []
    i = 0
    while i < len(lines):
        l = lines[i].strip()
        # print('lines', l)
        if len(l) < 3 or l == "Zweites Zitat:":
            i += 1
            continue
        if l[0] == "(" and l[-1] == ")" and len(paragraphs) > 0:
            paragraphs[-1][-1] = l[1:-1]
        elif '(Beifall' in l and l.index('(Beifall') == 0 and ')' in l:
            if len(paragraphs) > 0:
                idx = l.index(')') + 1
                paragraphs[-1][-1] = l[:idx]
                left_text = l[idx:].strip()
                if is_speaker(left_text):
                    speaker = left_text
                else:
                    paragraphs.append([speaker, l[idx:].strip(), ''])
        elif l[-1] == ':':
            if l[0] == '(' and len(paragraphs) > 0:
                if i+1 < len(lines) and lines[i+1][-1] == ')':
                    comment =  l + " " + lines[i+1]
                    paragraphs[-1][-1] = comment
                    i += 1
                elif 'Beifall' in l:
                    comment = l
                    paragraphs[-1][-1] = comment
            elif is_speaker(l):
                speaker = l
            else:
                content = l + " " + lines[i+1] if i+1 < len(lines) else l
                paragraphs.append([speaker, content, ''])
                i += 1
        elif ':-' in l:
            splits = l.split(':-')
            contents = splits
            if is_speaker(splits[0]):
                speaker = splits[0] + ":"
                contents = splits[1:]
            paragraphs.append([speaker, ':'.join(contents), ''])
        elif len(l) < short_length and len(paragraphs) > 0:
            # forward detect short paragraphs
            if (not re.search('\d+', l) or len(l) > 5) and paragraphs[-1][-1] == '':
                paragraphs[-1][1] = paragraphs[-1][1] + " " + l
        # else: # if paragraphs[-1][0] < short_length: backward detect short paragraphs
        else:
            paragraphs.append([speaker, l, ''])
        i += 1
    return paragraphs


def parse_speaker_with_party(text, catalog):
    if len(text) > 0:
        noted_speaker = text[:-1] if text[-1] == ':' else text
        p = re.compile(re.escape(noted_speaker) + '\s\([^\)]+\)(\s\([^\)]+\))?')
        match = re.search(p, catalog)
        if match != None:
            return match.group().replace('\n', ' ') + ":"
    return text


def parse_old_protocol(dir_name, file_name):
    """
    returns:
        paragraphs: file_id, segment_id, speaker, ...
    """
    idx = file_name.replace(".xml", "")
    file_path = os.path.join(dir_name, file_name)
    text, catalog = read_speech_text(file_path)
    segments = extract_segments(text)
    paragraphs = []

    for segment_idx, s in enumerate(segments):
        paragraphs_of_segment = extract_paragraphs(s, idx)
        paragraphs = paragraphs + [[idx, segment_idx] + p for p in paragraphs_of_segment]

    speaker_map = {}
    for i in range(len(paragraphs)):
        speaker = paragraphs[i][2]
        if speaker not in speaker_map:
            speaker_map[speaker] = parse_speaker_with_party(speaker, catalog)
        paragraphs[i][2] = speaker_map[speaker]

    return paragraphs
