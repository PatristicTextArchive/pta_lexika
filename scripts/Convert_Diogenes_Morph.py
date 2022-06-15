# %%
from cltk.alphabet.grc.beta_to_unicode import BetaCodeReplacer
import json

# %%
with open('/home/stockhausen/Dokumente/projekte/pta_lexika/sources/greek-analyses.txt', 'r', encoding='utf8') as file:
    reader = file.readlines()
    data = []
    beta_code_replace = BetaCodeReplacer()
    for line in reader:
        entry_dict = {}
        entry = line.split("\t{")
        entry_dict["word"] = beta_code_replace.replace_beta_code(entry[0])
        forms = [x.split("\t") for x in entry[1].split("}{")]
        forms_list = []
        for item in forms:
            word = beta_code_replace.replace_beta_code(item[0].split()[2])
            try:
                word = word.split(",")[1]
            except:
                pass
            # translation = item[1] # remove translation 
            analysis = item[2].replace("}\n","")
            morph = {word: analysis}
            forms_list.append(morph)
        merged = {k: [d.get(k) for d in forms_list if k in d] for k in set().union(*forms_list)}
        entry_dict["lemma"] = merged
        data.append(entry_dict)


# %%
# Write lemmata to file
with open('/home/stockhausen/Dokumente/projekte/pta_lexika/wordlemma_grc_diogenes.json', 'w') as fout:
# Ergebnisse werden in eine json-Datei geschrieben
    json.dump(data, fout, indent=4, ensure_ascii=False)


