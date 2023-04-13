#! /usr/bin/python3

import sys
from os import listdir

from xml.dom.minidom import parse

from deptree import *
#import patterns


## ------------------- 
## -- Convert a pair of drugs and their context in a feature vector

def extract_features(tree, entities, e1, e2) :
   feats = set()

   # get head token for each gold entity
   tkE1 = tree.get_fragment_head(entities[e1]['start'],entities[e1]['end'])
   tkE2 = tree.get_fragment_head(entities[e2]['start'],entities[e2]['end'])
   
   
   if tkE1 is not None and tkE2 is not None:
      
      # Find clue words before first entity
      clues = {'advise': False,
                     'mechanism': False,
                     'effect': False,
                     'int': False}

      # Features from before entities
      for tk in range(0, tkE1):
         try:
            while (tree.is_stopword(tk)):
               tk += 1
         except:
            return set()
         
         tk_lemma = tree.get_lemma(tk).lower()

         for c in clue_words.keys():
            if tk_lemma in clue_words[c]:
               # print(tkE1, tk_lemma, tkE2)
               clues[c] = True

      for c in clues.keys():
         feats.add('clue_'+ c + '_be=' + str(clues[c]))

   
      # Find clue words in-between drug entities.
      clues = {'advise': False,
                     'mechanism': False,
                     'effect': False,
                     'int': False}
      
      # Features between entities
      # Finding entities between the drug entities
      eib  = False
      # Finding conjunctions ('and', 'or' for now) between the drug entities
      conj_ib = False
      # features for tokens in-between E1 and E2
      for tk in range(tkE1+1, tkE2) :
         tk=tkE1+1
         
         if tree.get_word(tk) == 'and' or tree.get_word(tk) == 'or':
            conj_ib = True
         
         try:
            while (tree.is_stopword(tk)):
               if tree.get_word(tk) == 'and' or tree.get_word(tk) == 'or':
                  conj_ib = True
               tk += 1
         except:
            return set()
         word  = tree.get_word(tk)
         lemma = tree.get_lemma(tk).lower()
         tag = tree.get_tag(tk)
         feats.add("lib=" + lemma)
         feats.add("wib=" + word)
         feats.add("lpib=" + lemma + "_" + tag)
         
         tk_lemma = tree.get_lemma(tk).lower()

         for c in clue_words.keys():
            if tk_lemma in clue_words[c]:
               # print(tkE1, tk_lemma, tkE2)
               clues[c] = True

         if tree.is_entity(tk, entities):
            eib = True 
      
      for c in clues.keys():
         feats.add('clue_'+ c + '_ib=' + str(clues[c]))

      
      # Features after entities
      # Finding clue words after second drug entity
      clues = {'advise': False,
                     'mechanism': False,
                     'effect': False,
                     'int': False}
      
      try:
         end_tree = tree.get_n_nodes()
      except:
         end_tree = 0

      for tk in range(tkE2, end_tree):
         try:
            while (tree.is_stopword(tk)) and tk < end_tree - 1:
               tk += 1
         except:
            return set()
         
         if tk <= end_tree and not tree.is_stopword(tk):
            tk_lemma = tree.get_lemma(tk).lower()
            
            for c in clue_words.keys():
               if tk_lemma in clue_words[c]:
                  # print(tkE1, tk_lemma, tkE2)
                  clues[c] = True

      for c in clues.keys():
         feats.add('clue_'+ c + '_af=' + str(clues[c]))
	 
     # feature indicating the presence of an entity in-between E1 and E2
      feats.add('eib='+ str(eib))
      
     # feature indicating the presence of an 'and' or 'or' in-between E1 and E2
      feats.add('conj_ib='+ str(conj_ib))

      # features about paths in the tree
      lcs = tree.get_LCS(tkE1,tkE2)
      
      path_up = tree.get_up_path(tkE1,lcs)
      path_down = tree.get_down_path(lcs,tkE2)

      path1 = "<".join([tree.get_lemma(x)+"_"+tree.get_rel(x) for x in path_up])
      path2 = ">".join([tree.get_lemma(x)+"_"+tree.get_rel(x) for x in path_down])

      path3 = "<".join([tree.get_lemma(x) for x in path_up])
      path4 = ">".join([tree.get_lemma(x) for x in path_down])

      path5 = "<".join([tree.get_rel(x) for x in path_up])
      path6 = ">".join([tree.get_rel(x) for x in path_down])

      path7 = "<".join([tree.get_tag(x) for x in path_up])
      path8 = ">".join([tree.get_tag(x) for x in path_down])

      path = path1+"<"+tree.get_lemma(lcs)+"_"+tree.get_rel(lcs)+">"+path2      
      
      # Try other path info

      feats.add("path1="+path1)
      feats.add("path2="+path2)
      feats.add("path3="+path3)
      feats.add("path4="+path4)
      feats.add("path5="+path5)
      feats.add("path6="+path6)
      feats.add("path7="+path7)
      feats.add("path8="+path8)
      feats.add("path="+path)

      # print()
      
   return feats


## --------- MAIN PROGRAM ----------- 
## --
## -- Usage:  extract_features targetdir
## --
## -- Extracts feature vectors for DD interaction pairs from all XML files in target-dir
## --

# directory with files to process
datadir = sys.argv[1]

clue_words = {'advise':['recommend', 'advise', 'caution', 'suggest', 'propose', 'counsel', 'warn', 'should'],
              'effect': ['modify', 'alter', 'change', 'increase', 'decrease', 'potentiate', 'weaken', 'enhance', 'reduce', 'affect', 'suppress', 'exarcebate', 'ameliorate', 'cause', 'lead', 'result'],
              'mechanism': ['inhibit', 'induce', 'block', 'activate', 'suppress', 'compete', 'influence', 'interfere', 'modulate', 'metabolize', 'alter', 'affect', 'interact', 'compete', 'bind', 'impact', 'change', 'slow', 'speed'],
              'int': ['interact', 'concomitant', 'combination', 'co-administration', 'mixing', 'concurrent', 'simultaneous', 'together']}

# process each file in directory
for f in listdir(datadir) :

    # parse XML file, obtaining a DOM tree
    tree = parse(datadir+"/"+f)

    # process each sentence in the file
    sentences = tree.getElementsByTagName("sentence")
    for s in sentences :
        sid = s.attributes["id"].value   # get sentence id
        stext = s.attributes["text"].value   # get sentence text
        # load sentence entities
        entities = {}
        ents = s.getElementsByTagName("entity")
        for e in ents :
           id = e.attributes["id"].value
           offs = e.attributes["charOffset"].value.split("-")           
           entities[id] = {'start': int(offs[0]), 'end': int(offs[-1])}

        # there are no entity pairs, skip sentence
        if len(entities) <= 1 : continue

        # analyze sentence
        analysis = deptree(stext)

        # for each pair in the sentence, decide whether it is DDI and its type
        pairs = s.getElementsByTagName("pair")
        for p in pairs:
            # ground truth
            ddi = p.attributes["ddi"].value
            if (ddi=="true") : dditype = p.attributes["type"].value
            else : dditype = "null"
            # target entities
            id_e1 = p.attributes["e1"].value
            id_e2 = p.attributes["e2"].value
            # feature extraction


            feats = extract_features(analysis,entities,id_e1,id_e2) 
            # resulting vector
            if len(feats) != 0:
              print(sid, id_e1, id_e2, dditype, "\t".join(feats), sep="\t")

