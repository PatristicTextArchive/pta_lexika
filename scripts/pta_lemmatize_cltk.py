# %% [markdown]
# # Lemmatize PTA data with CLTK (+ POS, + morphology)

# %% [markdown]
# ## Functions

# %%
import os,glob,re
import json
import subprocess
import collections
import pandas as pd
from copy import deepcopy
from dataclasses import dataclass
from boltons.cacheutils import cachedproperty
from cltk import NLP
#from cltk.alphabet import grc
from cltk.core.data_types import Doc, Pipeline, Process
from cltk.core.exceptions import CLTKException
from cltk.stops.processes import StopsProcess
from cltk.dependency import GreekStanzaProcess
from cltk.tokenizers import GreekTokenizationProcess

# %%
@dataclass
class NormalisationProcess(Process):
    """
    
    """

    language: str = None

    @cachedproperty
    def algorithm(self):
        if self.language == "grc":
            nor_grc_class = GRCNormalisationProcess()
        else:
            raise CLTKException(f"No normalisation algorithm for language '{self.language}'.")
        return nor_grc_class

    def run(self, input_doc: Doc) -> Doc:
        normalisation_algo = self.algorithm
        output_doc = deepcopy(input_doc)
        for index, word_obj in enumerate(output_doc.words):
            if self.language == "grc":
                word_obj.raw_string = word_obj.string
                word_obj.string = normalisation_algo.normalise(word_obj.string)
                output_doc.words[index] = word_obj
                
            else:
                raise CLTKException(
                    f"``NormalisationProcess()`` not available for language '{self.language}' This should never happen."
                )
        return output_doc


class GRCNormalisationProcess(NormalisationProcess):

    hard_written_dictionary = {
            "ἀλλ’": "ἀλλά",
            "ἀνθ’": "ἀντί",
            "ἀπ’": "ἀπό",
            "ἀφ’": "ἀπό",
            "γ’": "γε",
            "δ’": "δέ",
            "δεῦρ’": "δεῦρο",
            "δι’": "διά",
            "εἶτ’": "εἶτα",
            "ἐπ’": "ἐπί",
            "ἔτ’": "ἔτι",
            "ἐφ’": "ἐπί",
            "ἵν’": "ἵνα",
            "καθ’": "κατά",
            "κατ’": "κατά",
            "μ’": "με",
            "μεθ’": "μετά",
            "μετ’": "μετά",
            "μηδ’": "μηδέ",
            "μήδ’": "μηδέ",  # @@@
            "ὅτ’": "ὅτε",
            "οὐδ’": "οὐδέ",
            "πάνθ’": "πάντα",
            "πάντ’": "πάντα",
            "παρ’": "παρά",
            "ποτ’": "ποτε",
            "σ’": "σε",
            "τ’": "τε",
            "ταῦθ’": "ταῦτα",
            "ταῦτ’": "ταῦτα",
            "τοῦτ’": "τοῦτο",
            "ὑπ’": "ὑπό",
            "ὑφ’": "ὑπό",
        }

    def normalise(self, token: str):
        if token in self.hard_written_dictionary:
            return self.hard_written_dictionary[token]
        return token

# %%
#deelision = NormalisationProcess
#text = Doc(raw="ἠγαπημένῳ ὑπ’ αὐτοῦ· μετὰ ταῦτα ἐπὶ τῆς γῆς ὤφθη, καὶ τοῖς ἀνθρώποις συνανεστράφη. Ἐὰν ")
#tokenizes = GreekTokenizationProcess().run(input_doc=text)
#print(tokenizes.words[1])
#example = deelision(language="grc").run(input_doc=tokenizes)
#print(example[1])

# %%
def tokenize(inputText):
    return [token for token in re.findall(r'\w+', inputText)]

# %%
def remove_interpunction(inputText):
    return re.sub(r'[.,:··;()›»«‹⁘—><\[\]\+\-\n]+', r'', inputText) 

# %%
def remove_numbering(inputText):
    return re.sub(r'[0-9a-zA-Z]+', r' ', inputText) # also latin alphabet

# %%
def tei_xml_to_plaintext(file_path):
    """Use Saxon and xslt to convert TEI to plaintext."""
    # plaintext_path = ".".join(file_path.split("/")[-1].split(".")[:3])
    stylesheet = '/home/stockhausen/Dokumente/Severian/xslt/plaintext.xsl'
    saxon = '/home/stockhausen/Dokumente/projekte/pta_collator/vendor/saxon9he.jar'
    buffer = subprocess.run(['java', '-jar', saxon, f'-s:{file_path}', f'-xsl:{stylesheet}'],
                            stdout=subprocess.PIPE).stdout
    plaintext = buffer.decode('utf-8')
    # save plaintext
    # with open('/home/stockhausen/Dokumente/projekte/pta_data/plaintext/'+plaintext_path+'.txt', 'w') as outfile:
    #    outfile.write(plaintext)
    return plaintext

# %%
def analyze_files(files_path):
    '''
    Load all files from files_path and analyze with CLTK,
    finally write out two dicts: 
    - wordlemma_grc: all words in corpus and their analysis
    - pta_dict: per URN info on words (counted, stopwords removed) and lemmata (counted, stopwords removed)
    - also plaintext files of text and lemmatized text are written to pta_data repo. 
    '''
    xml_dir = os.path.expanduser(files_path)
    xml_paths = glob.glob(xml_dir)
    grc_paths = [path for path in sorted(xml_paths) if 'grc' in path]
    pta_dict = []
    wordlemma_grc = []
    grc_pipeline_custom_1 = Pipeline(language="grc", description="", processes=[GreekTokenizationProcess, NormalisationProcess, GreekStanzaProcess, StopsProcess])
    cltk_nlp_grc = NLP(language="grc", custom_pipeline=grc_pipeline_custom_1, suppress_banner=True)
    print("Analysing...")
    for xml_path in grc_paths:
        file_dict = {}
        short_path = "/".join(xml_path.split("/")[8:])
        print(short_path)
        ptaid = "".join(short_path).split(".xml")[0]
        text = tei_xml_to_plaintext(xml_path)
        text_lowered = text.lower() # Remove capitals
        #text_ana = grc.filter_non_greek(text_lowered) # leave only Greek letters, removes also Apostrophe -> not good
        text_ana = remove_interpunction(remove_numbering(text_lowered))
        file_dict["urn"] = "urn:cts:pta:"+ptaid
        nlp = cltk_nlp_grc.analyze(text=text_ana)
        words = nlp.words
        for entry in words:
            tokens = {}
            tokens["Word"] = entry.string
            tokens["Lemma"] = entry.lemma
            tokens["POS"] = entry.upos
            features = entry.features
            tokens["Morphology"] = ', '.join(f'{k}: {v}' for k, v in features.items())
            wordlemma_grc.append(tokens)
        tokens_counted = collections.Counter(nlp.tokens_stops_filtered).most_common() #without stopwords
        lemmata = [x.lemma for x in nlp.words if x.stop == False] # without stopwords
        lemmata_counted = collections.Counter(lemmata).most_common()
        #with open("/home/stockhausen/Dokumente/projekte/pta_data/plaintext/"+ptaid+".txt", "w") as text_file:
        #    text_file.write(remove_interpunction(text))
        with open("/home/stockhausen/Dokumente/projekte/pta_data/plaintext_lemmatized/"+ptaid+".txt", "w") as text_file:
            text_file.write(" ".join(nlp.lemmata))
        file_dict["tokens"] = tokens_counted
        file_dict["lemmata"] = lemmata_counted
        pta_dict.append(file_dict)
    return pta_dict, wordlemma_grc 


# %%
pta_dict, wordlemma_grc = analyze_files("/home/stockhausen/Downloads/pta_data/data/*/*/*.xml")

# %%
# Write analytical data to file
print("Saving results")
with open('/home/stockhausen/Dokumente/projekte/pta_metadata/pta_statistics.json', 'w') as fout:
# Ergebnisse werden in eine json-Datei geschrieben
    json.dump(pta_dict, fout, indent=4, ensure_ascii=False)

# %%
df = pd.DataFrame(wordlemma_grc)
df.drop_duplicates(inplace=True)
#df.columns = ["Word","Lemma","POS","Morphology"]
#df.drop(['POS'], axis=1, inplace=True) # for the time being to be in concordance to prior format

# %%
#df

# %%
# Export dataframe to json
df.to_json(r'/home/stockhausen/Dokumente/projekte/pta_lexika/wordlemma_grc_cltk.json', orient='records', force_ascii=False, indent=4)


