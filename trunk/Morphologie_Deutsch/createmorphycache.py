#!/usr/bin/env python
# -*- coding: utf-8 -*-

# DIESES SCRIPT BITTE NICHT MANUELL AUSFÜHREN
# ES WIRD PER "MAKE" AUFGERUFEN

import os,sys,time,re,codecs,datetime,urllib,string,subprocess,pickle
    
os.system("clear")

print "Morphologie-Chache aus der Ausgabe-Datei von Morphy erzeugen"
print "createmorphycache v0.1 von Wolfgang Reszel, 2008-03-20"
print

morphology = {}
processedfiles = 0

for file in os.listdir("."):
    if os.path.splitext(file)[1] == ".fle":
        processedfiles += 1
        print "\nDie Datei %s wird analysiert ..." % (file)
        sourcefile = codecs.open(file,'r','Windows-1252')
        id = ""
        for line in sourcefile:
            if "nicht gefunden:" in line or line.strip() == "":
                continue
            if "--------------" in line:
                id = ""
                continue
            if line[:4] == "GRU ":
                continue
            if id == "":
                id = line.split(" ")[1].strip()
                morphology[id] = ""
            if u"Zusätze: " not in line and u"Präfixe: " not in line:
                for word in line.split(" "):
                    word = word.strip()
                    if word == "":
                        continue
                    if word not in morphology[id] and word != id:
                        if morphology[id] == "":
                            morphology[id] = word
                        else:
                            morphology[id] = morphology[id]+","+word
            else:
                line = line.replace(u"Zusätze: ","")
                line = line.replace(u"Präfixe: ","")
                for x in line.split(" "):
                    x = x.strip()
                    if x == "":
                        continue
                    if not morphology.has_key(x+id):
                        morphology[x+id] = ""
                        for y in morphology[id].split(","):
                            y = y.strip()
                            if y == "":
                                continue
                            if morphology[x+id] == "":
                                if x+y not in morphology[x+id]:
                                    morphology[x+id] = x+y
                            else:
                                if x+y not in morphology[x+id]:
                                    morphology[x+id] = morphology[x+id]+","+x+y
        sourcefile.close()

if processedfiles > 0:
    morphcache = open('morphology-cache.txt','w')
    pickle.dump(morphology,morphcache)
    morphcache.close()
else:
    print """Aus wurde keine Morpholigie-Ausgabe-Datei gefunden. 
Sie muss mit dem Windows-Programm Morphy über die Funktion 'Generierung' erstellt werden und mit '.fle' enden. 
Es können auch mehrere Dateien im Verzeichnis von createmorphycache.py abgelegt werden."""
