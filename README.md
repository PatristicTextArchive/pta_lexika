# Lexika und Lemmatisierungen

## Griechisch
* `pta_lexicon.json`: 
    - besteht aus lemma – grc_eng – grc_deu 
    - grc_eng und grc_deu sind jeweils Listen, weil es homonyme Lemmata gibt. 
    - Falls Lemma in keinem der Lexika zu finden ist, ist momentan der Eintrag leer; hier muss ich dann aus anderen Lexika die Bedeutungen noch manuell nachtragen.
* `wordlemma.json`: 
    - besteht aus Word (wie im Text) - Lemma - Morphology
    - Wortformen, die nicht analysiert wurden, fehlen ganz. 

