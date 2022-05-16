# Word-Lemma-Lists and Lexica used by PTA

The folder `sources` contains the source files of the used lexica; for more information see the `README.md` in this folder.

The repository has the following files at the moment:

* `pta_lexicon_grc.json`: 
    - compiled from LSJ, TBESG, and Pape
    - has: lemma – grc_eng – grc_eng2 – grc_deu
    - grc_eng = LSJ, grc_eng2 = TBESG, grc_deu = Pape 
    - grc_eng und grc_deu sind jeweils Listen, weil es homonyme Lemmata gibt. 
    - If there is no entry in one of the dictionaries, the entry is empty.
* The folder `pta_lexicon_grc` contains xml-version of the above
* `wordlemma_grc.json`: 
    - result of lemmatizing the texts in in [pta_data](https://github.com/PatristicTextArchive/pta_data)
    - has word – lemma – morphology
    - words which have not been lemmatized (for whatever reason), are not in the file. 
* `wordlemma_grc.xml`:
    - xml-version of the above
* JSON-versions of the lexica in the `source`-folder, adapted for use in PTA, the folder `pta_dictionaries` contains xml-versions of these.
* The folder `scripts` contains a Jupyter notebook used to generate all files.
