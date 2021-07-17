import re
from nltk.tokenize import sent_tokenize

reaction_texts = [['beifall'], ['zuruf', 'zurufe'], ['lachen'], ['heiterkeit'], \
             ['sagen', 'sagt'], ['reden', 'rede'], ['hört'], ['wissen'], [ 'steht'], \
             [ 'lesen'], ['kommen', 'kommt'], ['erzählen']]
party_texts =  [['spd'], ['cdu/csu'], ['gruene', 'grünen', '90/die' , '90/diegrünen', 'bündnis', 'bündnisses'], ['fdp'], ['afd'], ['linke', 'linken']]

reactions = [t[0] for t in party_texts] + ['speech', 'unspecified']
parties = [t[0] for t in party_texts] + ['unspecified']

def replace_special_cases(text):
    text = re.sub(r"abg\.", "Abgeordneten", text, flags=re.IGNORECASE)
    return text


def parse_comment(comment):
    # print("comment", type(comment), comment)
    cstr = replace_special_cases(comment.lower())
    cs = cstr.split("–") if cstr != '' else []
    
    # sent_tokenize(cstr, language="german")
    
    result = ['']*len(parties)
    for c in cs:        
        if ":" in c:
            sub_reaction = "speech"
        else:
            # TODO: report error case (if parsed_reactions more then one)
            rs = [rarr[0] for rarr in reaction_texts if any(r in c for r in rarr)]
            sub_reaction = rs[0] if len(rs) > 0 else "unspecified"
        
        sub_performers = sorted([parr[0] for parr in party_texts if any(p in c for p in parr)])
        if len(sub_performers) == 0:
            result[-1] = ' '.join([result[-1], sub_reaction]).strip()
        else:
            for p in sub_performers:
                idx = parties.index(p)
                result[idx] = ' '.join([result[idx], sub_reaction]).strip()
    
    return result
