party_texts =  [['spd'], ['cdu/csu'], ['gruene', 'grünen', '90/die' , '90/diegrünen', 'bündnis', 'bündnisses'], \
                ['fdp'], ['afd'], ['linke', 'linken'], ['alterspräsident'], ['vizepräsident'], ['präsident']]

parties = [t[0] for t in party_texts] + ['unspecified']

def detect_parties(text):
    text = text.lower()
    parties = sorted([parr[0] for parr in party_texts if any(p in text for p in parr)])
    return parties

def parse_party(text):
    parties = detect_parties(text)
    return parties[0] if len(parties) > 0 else 'unspecified'
