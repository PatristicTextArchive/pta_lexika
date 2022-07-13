# %% [markdown]
# # Lemmatize PTA data with CLTK (+ POS, + morphology)
# 
# for Greek and Latin texts

# %% [markdown]
# ## Functions

# %%
import os,glob,re
from MyCapytain.resources.texts.local.capitains.cts import CapitainsCtsText
from MyCapytain.common.constants import Mimetypes, XPATH_NAMESPACES
import json
import collections
import pandas as pd
from copy import deepcopy
from dataclasses import dataclass
from boltons.cacheutils import cachedproperty
from cltk import NLP
from cltk.alphabet import lat
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
    return re.sub(r'[.,:··;\?()›»«‹⁘—><\[\]\+\-\n]+', r'', inputText) 

# %%
def remove_numbering(inputText):
    return re.sub(r'[0-9]+', r' ', inputText) 

# %%
def remove_latin(inputText):
    return re.sub(r'[a-zA-Z]+',r'', inputText)

# %%
def tei_xml_to_plaintext(file_path):
    plaintext = ''
    with open(file_path) as file_open:
        text = CapitainsCtsText(resource=file_open)
        for ref in text.getReffs(level=len(text.citation)):
            psg = text.getTextualNode(subreference=ref, simple=True)
            psg.plaintext_string_join = "" 
            text_line = psg.export(Mimetypes.PLAINTEXT, exclude=["tei:note","tei:rdg"])
            plaintext += text_line
    return plaintext

# %%
def analyze_grc_files(files_path):
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
    pta_grc_dict = []
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
        text_ana = remove_latin(remove_interpunction(remove_numbering(text_lowered)))
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
        with open("/home/stockhausen/Dokumente/projekte/pta_data_plaintext/lemmatized/"+ptaid+".txt", "w") as text_file:
            text_file.write(" ".join(nlp.lemmata))
        file_dict["tokens"] = tokens_counted
        file_dict["lemmata"] = lemmata_counted
        pta_grc_dict.append(file_dict)
    return pta_grc_dict, wordlemma_grc 


# %%
def analyze_lat_files(files_path):
    '''
    Load all files from files_path and analyze with CLTK,
    finally write out two dicts: 
    - wordlemma_grc: all words in corpus and their analysis
    - pta_dict: per URN info on words (counted, stopwords removed) and lemmata (counted, stopwords removed)
    - also plaintext files of text and lemmatized text are written to pta_data repo. 
    '''
    xml_dir = os.path.expanduser(files_path)
    xml_paths = glob.glob(xml_dir)
    lat_paths = [path for path in sorted(xml_paths) if 'lat' in path]
    pta_lat_dict = []
    wordlemma_lat = []
    cltk_nlp_lat = NLP(language="lat", suppress_banner=True)
    cltk_nlp_lat.pipeline.processes.pop(-1)
    print("Analysing...")
    for xml_path in lat_paths:
        file_dict = {}
        short_path = "/".join(xml_path.split("/")[8:])
        print(short_path)
        ptaid = "".join(short_path).split(".xml")[0]
        text = tei_xml_to_plaintext(xml_path)
        text_lowered = text.lower() # Remove capitals
        text_ana = lat.drop_latin_punctuation(text_lowered)
        text_ana = lat.disappear_round_brackets(text_ana)
        file_dict["urn"] = "urn:cts:pta:"+ptaid
        nlp = cltk_nlp_lat.analyze(text=text_ana)
        words = nlp.words
        for entry in words:
            if entry.upos !="PUNCT":
                tokens = {}
                tokens["Word"] = entry.string
                tokens["Lemma"] = entry.lemma
                tokens["POS"] = entry.upos
                features = entry.features
                tokens["Morphology"] = ', '.join(f'{k}: {v}' for k, v in features.items())
                wordlemma_lat.append(tokens)
        tokens_counted = collections.Counter(nlp.tokens_stops_filtered).most_common() #without stopwords
        lemmata = [x.lemma for x in nlp.words if x.stop == False] # without stopwords
        lemmata_counted = collections.Counter(lemmata).most_common()
        #with open("/home/stockhausen/Dokumente/projekte/pta_data/plaintext/"+ptaid+".txt", "w") as text_file:
        #    text_file.write(remove_interpunction(text))
        #lemma_for_file = [x for x in nlp.lemmata if re.search(r'[^0-9.,()?!:;]',x)]
        with open("/home/stockhausen/Dokumente/projekte/pta_data_plaintext/lemmatized/"+ptaid+".txt", "w") as text_file:
            text_file.write(" ".join(nlp.lemmata))
        file_dict["tokens"] = tokens_counted
        file_dict["lemmata"] = lemmata_counted
        pta_lat_dict.append(file_dict)
    return pta_lat_dict, wordlemma_lat 

# %%
pta_grc_dict, wordlemma_grc = analyze_grc_files("/home/stockhausen/Downloads/pta_data/data/*/*/*.xml")

# %%
pta_lat_dict, wordlemma_lat = analyze_lat_files("/home/stockhausen/Downloads/pta_data/data/*/*/*.xml")

# %%
# Combine pta_grc_dict and pta_lat_dict 
pta_dict = pta_grc_dict+pta_lat_dict

# %% [markdown]
# ## Save results

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
#df
# Export dataframe to json
df.to_json(r'/home/stockhausen/Dokumente/projekte/pta_lexika/wordlemma_grc_cltk.json', orient='records', force_ascii=False, indent=4)

# %%
df = pd.DataFrame(wordlemma_lat)
df.drop_duplicates(inplace=True)
#df.columns = ["Word","Lemma","POS","Morphology"]
#df.drop(['POS'], axis=1, inplace=True) # for the time being to be in concordance to prior format
#df
# Export dataframe to json
df.to_json(r'/home/stockhausen/Dokumente/projekte/pta_lexika/wordlemma_lat_cltk.json', orient='records', force_ascii=False, indent=4)


