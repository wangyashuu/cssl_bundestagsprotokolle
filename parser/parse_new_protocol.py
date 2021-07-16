import xml.etree.ElementTree as ET
import os

"""
- vorspann / headers
    - *ort*
    - *datum*
    - session number ...

- sitzungsverlauf / session history
    - tagesordnungspunkt / agenda item
        - (a list of) rede
            - speaker
                - vorname
                - nachname
                - rolle
                    - rolle_lang
                    - rolle_kurz
            - kommentar: (Heiterkeit)
            - a list of paragraph
- anlagen
- rednerliste
"""


def parse_new_protocol(dir_name, file_name):
    """
    returns:
        paragraphs: file_id, segment_id, ...
    """
    tree = ET.ElementTree(file=os.path.join(dir_name, file_name))
    root = tree.getroot()
    session_history = root.find('sitzungsverlauf')
    idx = file_name.replace(".xml", "")
    paragraphs = []
    for agenda_idx, agenda_item in enumerate(session_history.findall('tagesordnungspunkt')):
        for rede in agenda_item.findall('rede'):
            redner = rede.find('.//redner')
            for i in range(1, len(rede)):
                comment = rede[i+1].text[1:-1] if i+1 < len(rede) and rede[i+1].tag == 'kommentar' else ''
                content = rede[i].text
                if rede[i].tag == 'p':
                    if content != None: # a new speaker
                        paragraphs.append([idx, agenda_idx, content, comment])
    return paragraphs
