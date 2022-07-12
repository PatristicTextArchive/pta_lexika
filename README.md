# Word-Lemma-Lists and Lexica used by PTA

The folder `sources` contains the source files of the used lexica; for more information see the `README.md` in this folder.

The folder `scripts` contains the Python scripts used to generate all files.

## Greek

The repository has the following files at the moment:

* `pta_lexicon_grc.json`: 
    - compiled from LSJ, TBESG, and Pape
    - has: lemma – grc_eng – grc_eng2 – grc_deu
    - grc_eng = LSJ, grc_eng2 = TBESG, grc_deu = Pape 
    - grc_eng and grc_deu are lists, as there are homonymous lemmata. 
    - If there is no entry in one of the dictionaries, the entry is empty.
* The folder `pta_lexicon_grc` contains xml-version of the above
* `wordlemma_grc_cltk.json`:
    - result of lemmatizing all texts in in [pta_data](https://github.com/PatristicTextArchive/pta_data); it currently has 132.814 entries. Lemmatization was done using the [Classical Language Toolkit (CLTK)](http://cltk.org/).
    - has word - lemma - [POS](https://universaldependencies.org/u/pos/index.html) - [morphology](https://universaldependencies.org/u/feat/index.html) (according to  [Universal Dependencies (UD) project](https://universaldependencies.org))
* `wordlemma_grc.json` (outdated): 
    - result of lemmatizing part of the texts in in [pta_data](https://github.com/PatristicTextArchive/pta_data); it has 42346 entries. Lemmatization was done using the [Morpheus morphological analysis engine used at morph.perseids.org](morph.perseids.org).
    - has word – lemma – morphology
    - words which have not been lemmatized (for whatever reason), are not in the file. 
* `wordlemma_grc.xml` (outdated):
    - xml-version of the file above
* `wordlemma_grc_diogenes.json`:
    - morphology data from [Diogenes](https://d.iogen.es/d/); Greek is converted to utf-8 (from Betacode).
    - has word - lemma (list of possible morphology)
* JSON-versions of the lexica in the `source`-folder, adapted for use in PTA, the folder `pta_dictionaries` contains xml-versions of these.

## Latin

* `Georges.json`: tbd

* `LewisShort.json`: tbd

* `TLL.json`:
    - built from <https://publikationen.badw.de/de/api/thesaurus/html-xml/thesaurus/index.json">
    - has lemma - url of entry in [THESAVRVS LINGVAE LATINAE Open Access](http://tll-open.badw.de)
* `wordlemma_lat_diogenes.json`:
    - morphology data from [Diogenes](https://d.iogen.es/d/)
    - has word - lemma (list of possible morphology)
