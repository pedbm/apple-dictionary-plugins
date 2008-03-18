#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys,time,re,codecs,datetime,urllib,string,subprocess,struct

def sort_by_value(d):
    """ Returns the keys of dictionary d sorted by their values """
    items=d.items()
    backitems=[ [v[1],v[0]] for v in items]
    backitems.sort()
    return [ backitems[i][1] for i in range(0,len(backitems))]

os.system("clear")

dictFull = "StarDict Deutsch"
dicts = ["ldaf","duden"]

print "Lexikon-Plugin ("+dictFull+") auf Basis von StarDict.org"
print "CreateXML v0.1 von Wolfgang Reszel, 2008-03-16"
print 

writeTestHtml = 1
html = codecs.open('test.html','w','utf-8')
if writeTestHtml == 1:
    html.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
  "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <meta http-equiv="Content-type" content="text/html; charset=utf-8">
  <title>Page Title</title>
  <link rel="stylesheet" href="StarDictDeutsch.css" type="text/css" media="screen" title="no title" charset="utf-8">
</head>
<body id="" onload="">""")

bundleVersion = datetime.datetime.today().strftime("%Y.%m.%d")
marketingVersion = "v" + bundleVersion

dictionary = {}
lengths = {}
dvalues = {}
titles = {}
copyright = {}

copyright['ldaf'] = u'<div class="copyright" d:priority="2"><span>Nach der Rechtschreibreform von 1996<br/><a href="http://stardict.sourceforge.net/Dictionaries_de.php">aus LDaF.dict</a> · Erstellt 2006 von Hu Zheng für <a href="http://stardict.sourceforge.net">StarDict</a></span></div>'
copyright['duden'] = u'<div class="copyright" d:priority="2"><span>Nach der Rechtschreibreform von 1996<br/><a href="http://stardict.sourceforge.net/Dictionaries_de.php">aus Duden.dict</a> · Erstellt 2006 von Hu Zheng für <a href="http://stardict.sourceforge.net">StarDict</a></span></div>'
copyright['ftypes'] = u'<div class="copyright" d:priority="2"><span><a href="http://de.wikipedia.org/w/index.php?title=Liste_der_Dateiendungen">aus de.Wikipedia.org</a></span></div>'

ftypesFile = codecs.open('dateitypen.txt','r','utf-8')

for line in ftypesFile:
    if "|---" in line[:4] or line == "":
        continue
    cells = line.split("||")
    id = cells[0][2:].strip() 
    id = re.sub("\[|\]","",id).strip()
    translationStr = "<h1>Dateiendung: "+id+"</h1>\n"
    if cells[1].strip() != "-":
        translationStr = translationStr+"<p>"+cells[1].strip()+"</p>\n"
    if len(cells) == 3:
        translationStr = translationStr+"<p>"+cells[2].strip()+"</p>\n"
    translationStr = translationStr+copyright['ftypes']
    
    translationStr = re.sub("\[+([a-z]+:/[^\[\] ]+)\]+","<a href=\"\\1\">\\1</a>",translationStr)
    translationStr = re.sub("\[+([a-z]+:/[^\[\] ]+) ([^\[\]]+)\]+","<a href=\"\\1\">\\2</a>",translationStr)
    translationStr = re.sub("\[+([^\[\]|]+)\]+","<a href=\"x-dictionary:d:\\1\">\\1</a>",translationStr)    
    translationStr = re.sub("\[+([^\[\]|]+)\|([^\[\]]+)\]+","<a href=\"x-dictionary:d:\\1\">\\2</a>",translationStr)    
    translationStr = re.sub("''+([^']+?)''+","<b>\\1</b>",translationStr)    
        
    if lengths.has_key(id):
        if translationStr.lower() not in dictionary[id].lower():
            dictionary[id] = dictionary[id]+translationStr
    else:
        dictionary[id] = translationStr
        lengths[id] = len(id)
        dvalues[id] = ''
        titles[id] = id
    
    dvalueSplit = id.split(",")
    for dvalue in dvalueSplit:
        dvalue = dvalue.strip()
        if dvalue == "..." or dvalue == u"…":
            continue
        dvalue = re.sub("(\.[^ ]+).*","\\1",dvalue)
        if '<d:index d:value="'+dvalue.lower()+'"' not in dvalues[id].lower():
            dvalues[id] = dvalues[id]+'<d:index d:value="'+dvalue+u'" d:title="Dateiendung: '+id+'"/>\n'
            dvalues[id] = dvalues[id]+'<d:index d:value="'+dvalue[1:]+u'" d:title="Dateiendung: '+id+'"/>\n'

    # print dvalues[id].encode("utf-8")
    # print translationStr.encode("utf-8")
    
ftypesFile.close()      

for dictName in dicts:
    print "Lese %s ..." % (dictName)
    ifoParameters = {}   
    ifoFile = open(dictName+'.ifo','r')
    for line in ifoFile:
        parameter = line.split("=",2)
        if len(parameter) == 2:
            ifoParameters[parameter[0]] = parameter[1].strip()
    ifoFile.close()

    idxFile = open(dictName+'.idx','r')
    dictFile = open(dictName+'.dict','r')

    word = ''
    char = idxFile.read(1)
    while char != "":
        if char != chr(0):
            word = word + char
        else:
            indexOffset = struct.unpack(">L",idxFile.read(4))[0]
            indexSize = struct.unpack(">L",idxFile.read(4))[0]
            dictFile.seek(indexOffset)

            indexStr = unicode(word,'utf-8')

            indexStr = re.sub("(?ui)^(?:\d, ?\d|\d)([a-z])","\\1",indexStr) 

            if "zutageX" not in indexStr[:6]:
                translationStr = unicode(dictFile.read(indexSize),'utf-8') 
                # <...> durch {...} ersetzen 
                translationStr = re.sub("(?u)<([^<>]+)>","{\\1}",translationStr)
                # Entities für einzelne spitze Klammern < >
                translationStr = translationStr.replace("&","&amp;")
                translationStr = translationStr.replace(">","&gt;")
                translationStr = translationStr.replace("<","&lt;")
                # Texte mit || beginnend als Notiz markieren
#                translationStr = re.sub("(?us)(\|\|)(.*?)(\n+|$|<| \|)","<div class=\"note\">\\1\\2</div>\\3",translationStr)
#                translationStr = re.sub("(?us)([^>])(\|\|)(.*?)(\n+|$|<| \|)","\\1<div class=\"note\">\\2\\3</div>\\4",translationStr)
                translationStr = re.sub("(?us)\n+\s*\|\| "," || ",translationStr)
                translationStr = re.sub("(?us)(\|\|)(.*?)(\n+|$|<)","<div class=\"note\">\\1\\2</div>\\3",translationStr)
                #translationStr = re.sub("(?us)([^>])(\|\|)(.*?)(\n+|$|<)","\\1<div class=\"note\">\\2\\3</div>\\4",translationStr)
                # {...} schräg setzen (mit <i></i> umschließen)
                translationStr = re.sub("(?u){([^{}]+)}","<i>{\\1}</i>",translationStr)
                # Nummerierung fett setzen
                translationStr = re.sub("(?ui)(?: |^)(\d\. [\w=]\)|\d+\.|[a-z]\)) "," <b>\\1</b> ",translationStr)
                translationStr = re.sub("(?ui)(\()(\d\. [\w=]\)|\d+\.) ","\\1<b>\\2</b> ",translationStr)
                translationStr = re.sub("(?u)(\] |; |\) )(\d+) ","\\1\n<b>\\2</b> ",translationStr)
                translationStr = re.sub("(?u)(?:\n|^)(\d+) ","\n<b>\\1</b> ",translationStr)
                translationStr = re.sub("(?u)(; nur in )(\d+) ","\n\\1<b class=\"bigger\">\\2</b> ",translationStr)
                # Fehlerhafte Fettsetzung zurücknehmen
                translationStr = re.sub("(?ui)(im *|der *|wird *|mit *|beim *|im *|eigtl\. *|des *)<b>([^<>]+)</b> *","\\1 \\2 ",translationStr)
                translationStr = re.sub("(?ui)<b>([^<>]+)</b> *(ist\W*|wird\W*|(und \d. )?Person\W*|Part\.)","\\1 \\2",translationStr)
                translationStr = re.sub("(?ui)<b>([^<>]+)</b> *(ist\W*|wird\W*|(und \d. )?Person\W*|Part\.)","\\1 \\2",translationStr)
                translationStr = re.sub("(?u)(\(\d+ *|\d\., *)<b>([^<>]+)</b> *","\\1 \\2 ",translationStr)
                translationStr = re.sub("(?u)(\([^\(\)]+)<b>([^<>\(\)]+\))</b>","\\1 \\2 ",translationStr)
                # Erster Text bis zum ; in mit Schreibweisen-Tag umschließen (d:pr)
                if dictName == "ldaf":
                    translationStr = re.sub("(?u)^([^\n:{]+);","<span class=\"syntax\" d:pr=\"1\">\\1;</span>",translationStr)
                    translationStr = re.sub("(?u)^([^;\n]+)(\) *|\] *)(\n<b>\d)","<span class=\"syntax\" d:pr=\"1\">\\1\\2</span>\\3",translationStr)

                # Zwischenüberschrift einer Aufzählung fett setzen
                translationStr = re.sub("(?u)(^[\n\s]*|\n\n)([^0-9\n][^b][^>][^\n\|]+)(\n<b>)","\\1<h2>\\2</h2>\\3",translationStr)
                #translationStr = re.sub("(?u)(\.|:) <b>(\d)","\\1\n<b>\\2",translationStr)
                # Einzeln stehende Zwichenüberschrift
                translationStr = re.sub("(?u)>\n([^\n><]+)(\n\n|$)",">\n\n<h2>\\1</h2>\n",translationStr)
                
                # Nummerierung größer setzen
                translationStr = re.sub("(?u)\n<b>","\n<b class=\"bigger\">",translationStr)
                translationStr = re.sub("(?ui)([a-z.:] *)<b>(\d+\.) ([a-z]\))","\\1\n<b class=\"bigger\">\\2</b> <b>\\3",translationStr)
                if dictName == "duden":
                    translationStr = re.sub("(?ui)([a-z.:] *)<b>(\d+\.</b>)","\\1\n<b class=\"bigger\">\\2",translationStr) 
                    translationStr = re.sub("(?ui)(<b class=\"bigger\">\d+\. )([a-z]\))","\\1</b><b>\\2",translationStr) 
                    # Bigger innerhalb von [] wieder entfernen
                    for r in range(3):
                        translationStr = re.sub("(?us)(\[[^\[\]]+?)\n<b class=\"bigger\">([^\[\]]+?\])","\\1<b>\\2",translationStr)
                    # Bigger innerhalb von () wieder entfernen
                    for r in range(3):
                        translationStr = re.sub("(?us)(\([^\(\)]+?)\n<b class=\"bigger\">([^\(\)]+?\))","\\1<b>\\2",translationStr)
                    # Punkt hinter Zahl entfernen
                    translationStr = re.sub("(?u)(<b class=\"bigger\">\d+)\.</b>","\\1</b>",translationStr) 

                translationStr = re.sub("(?ui)([^b][^>] )(<b>[a-z]+\)</b>)","\\1<br/>\\2",translationStr) # Umbruch für Unterpunkte a)...

                # Zwischenüberschrift einer Aufzählung fett setzen
                translationStr = re.sub("(?u)(^[\n\s]*|\n\n)([^0-9\n][^bh][^>][^\n\|]+)(\n<b )","\\1<h2>\\2</h2>\\3",translationStr)

                #Zeilenumbrüche in <br/> umwandeln
                #translationStr = translationStr.replace("\n","<br/>\n")
                
                #Aufzählungen in DIVs packen
                translationStr = re.sub("(?us)([^>])(<b class=\"bigger\">\d\D*</b>.+?)(\n| )(<b class=\"bigger\">|\n)","\\1<div class=\"list\">\\2</div>\\3\\4",translationStr)
                translationStr = re.sub("(?us)([^v][^>])(<b class=\"bigger\">\d\D*</b>.+?)(\n| )(<div class=\"list\">|<b class=\"bigger\">|\n)","\\1<div class=\"list\">\\2</div>\\3\\4",translationStr)
                translationStr = re.sub("(?us)([^v][^>])(<b class=\"bigger\">\d\D*</b>.+?)\n*$","\\1<div class=\"list\">\\2</div>\n",translationStr)

                translationStr = re.sub("(?us)([^>])(<b class=\"bigger\">\d\d+\D*</b>.+?)(\n| )(<b class=\"bigger\">|\n)","\\1<div class=\"listB\">\\2</div>\\3\\4",translationStr)
                translationStr = re.sub("(?us)([^v][^>])(<b class=\"bigger\">\d\d+\D*</b>.+?)(\n| )(<div class=\"listB?\">|<b class=\"bigger\">|\n)","\\1<div class=\"listB\">\\2</div>\\3\\4",translationStr)
                translationStr = re.sub("(?us)([^v][^>])(<b class=\"bigger\">\d\d+\D*</b>.+?)\n*$","\\1<div class=\"listB\">\\2</div>\n",translationStr)
                #  translationStr = re.sub("(?us)([^>])(<b class=\"bigger\">.+?[^>])(\n?<b class=\"bigger\">)","\\1<div class=\"list\">\\2</div>\\3",translationStr)
                #  translationStr = re.sub("(?u)</div>\n(<i class=\"note\">.+</i>)\n","\\1</div>\n",translationStr)

                # Fehlerhaftes </div> nach </h2> vertauschen
                translationStr = re.sub("(?u)(\n<h2>[^\n]+?</h2>)</div>","</div>\\1",translationStr)

                translationStr = re.sub("(?u)>\|\|",u"><span class=\"noteB\"> </span>",translationStr)
                translationStr = re.sub("(?u)\|\|","<br/>",translationStr)
        
                # Probleme beim Schreibweisen-Tag korrigieren
                if dictName == "ldaf":
                    translationStr = re.sub("(?u)(<span class=\"syntax\" d:pr=\"1\">.*?)</span> *<br/>","\\1<br/></span>",translationStr)
                    translationStr = re.sub("(?u)(<span class=\"syntax\" d:pr=\"1\">.*?)</span> *</b> *<br/>","\\1<br/></span></b>",translationStr)
                    
                # Letzte Zeile ohne Tag taggen
                translationStr = re.sub("(?u)(\n\n)([^<\n][^\n]+)$","\\1<p>\\2</p>",translationStr)

                # Hochgestellte Zahlen korrigieren und setzen 
                translationStr = re.sub("\xb2","2",translationStr)
                translationStr = re.sub("\xb3","3",translationStr)
                translationStr = re.sub("(?ui)([a-z][a-z]+)(\d+)(\W)","\\1<sup d:priority=\"2\">\\2</sup>\\3",translationStr)
                # Fake-Anführungszeichen durch echte Anführungszeichen ersetzen
                translationStr = re.sub(",,([^\"]+)\"",u"„\\1“",translationStr)
                # Lautschirft der Klasse ipa zuweisen, damit eine andere Schrift verwendet werden kann
                translationStr = re.sub("(?u)(\[[^\[\]]+\])","<span class=\"ipa\">\\1</span>",translationStr)
                # Siblentrennung durch <span class=hsb> ersetzen, somit erscheint das Trennungszeichen nicht beim Kopieren von Text
                translationStr = translationStr.replace(u"·","<span class=\"hsb\"></span>")
                # Hauptüberschrift voranstellen und Copyright anhängen
                translationStr = "\n<h1>"+indexStr+"</h1>\n"+translationStr+copyright[dictName]
                # Sonderzeichen in Lautschrift umwandeln
                translationStr = re.sub("\x01",u"ɪ",translationStr)
                translationStr = re.sub("\x02",u"ɛ",translationStr)
                translationStr = re.sub("\x06",u"ɔ",translationStr)
                translationStr = re.sub("\x0B",u"θ",translationStr)
                translationStr = re.sub("\x0E",u"ʊ",translationStr)
                translationStr = re.sub(":\x10",u"ːɐ̯'",translationStr)
                translationStr = re.sub("\x10",u"ə",translationStr)
                translationStr = re.sub("\x19",u"ŋ",translationStr)
                translationStr = re.sub("\x1D",u"ʃ",translationStr)
                translationStr = re.sub("\x1E",u"ʒ",translationStr)

                id = re.sub('(?u)[\"<>]','_',indexStr)
                id = re.sub("(?u)_+","_",id)
                id = re.sub("(?u)(.)_$","\\1",id)
                
                dvalue = re.sub('(?u)\([^)]+(\)|$)|<[^>]+(>|$)|\[[^]]+(\]|$)',"",indexStr).strip()

                if lengths.has_key(id):
                    if translationStr.lower() not in dictionary[id].lower():
                        dictionary[id] = dictionary[id]+translationStr
                else:
                    dictionary[id] = translationStr
                    lengths[id] = len(id)
                    dvalues[id] = ''
                    titles[id] = dvalue

                for dvalueStrip in re.split(",|\w+;",dvalue):
                    dvalueStrip = dvalueStrip.strip()
                    if len(dvalueStrip) < 2 or dvalueStrip[:1] == '-':
                        continue
                    if '<d:index d:value="'+dvalueStrip.lower()+'"' not in dvalues[id].lower():
                        if dvalueStrip == indexStr:
                            dvalues[id] = dvalues[id]+'<d:index d:value="'+dvalueStrip+'" d:title="'+indexStr+'"/>\n'
                        else:
                            dvalues[id] = dvalues[id]+'<d:index d:value="'+dvalueStrip+u'" d:title="⇒ '+indexStr+'"/>\n'
                        dvalueSplit = dvalueStrip.split()
                        indexI = 0
                        for i in dvalueSplit:
                            indexI += 1
                            if len(i) > 1:
                                devalueHyphenSplit = i.split("-")
                                for j in range(1,len(devalueHyphenSplit)):
                                    if len(devalueHyphenSplit[j]) > 1:
                                        if '<d:index d:value="'+devalueHyphenSplit[j].lower()+'"' not in dvalues[id].lower():
                                            dvalues[id] = dvalues[id] + '\n<d:index d:value="'+devalueHyphenSplit[j]+u'" d:title="⇒ '+indexStr+'"/>'
                                if '<d:index d:value="'+i.lower()+'"' not in dvalues[id].lower() and indexI > 1:
                                    if i[0] != "-" and i[len(i)-1] != "-":
                                        dvalues[id] = dvalues[id] + '\n<d:index d:value="'+i+u'" d:title="⇒ '+indexStr+'"/>'
            
            word = ''

        char = idxFile.read(1)
    
    idxFile.close()    
    dictFile.close()

print "\nXML-Datei wird erzeugt ..."
destfile = codecs.open('StarDictDeutsch.xml','w','utf-8')
destfile.write("""<?xml version="1.0" encoding="utf-8"?>
<d:dictionary xmlns="http://www.w3.org/1999/xhtml" xmlns:d="http://www.apple.com/DTDs/DictionaryService-1.0.rng">""")
                
for id in sort_by_value(lengths):    
    destfile.write( u"""
<d:entry id="%s" d:title="%s">
%s
%s
</d:entry>""" % (id,titles[id],dvalues[id],dictionary[id]) )
if writeTestHtml == 1:
    html.write(dictionary[id])
        
destfile.write( u"""
<d:entry id="front_back_matter" d:title="Voderer/Hinterer Teil">
    <h1>StarDict Deutsch</h1>
    <div><small><b>Version: %s</b></small></div>
    <p>
    	Dieser Thesaurus basiert auf den Wörterbuch-Dateien <a href="http://stardict.sourceforge.net/Dictionaries_de.php">LDaF.dict</a>
        und <a href="http://stardict.sourceforge.net/Dictionaries_de.php">Duden.dict</a> für <a href="http://stardict.sourceforge.net">StarDict</a> von Hu Zheng.<br/>
        Beide Quellen wurden nach der Rechtschreibreform von 1996 erstellt, berücksichtigen aber nicht die Überarbeitung von 2004/2006.
    </p>
    <p>
        Das Python-Skript zur Umwandlung der StarDict-Wörterbücher<br/>in ein Lexikon-Plugin wurde von Wolfgang Reszel entwickelt.
    </p>
    <p>
        <b>Updates:</b> Die aktuellste Version finden Sie unter <a href="http://www.tekl.de">www.tekl.de</a>.<br/>
        Support und den Quellcode finden Sie unter <a href="http://apple-dictionary-plugins.googlecode.com"><b>apple-dictionary-plugins.googlecode.com</b></a>.
    </p>
    <p>
        <img src="Images/cc-LGPL-a.png" align="left" style="padding-right:10px" alt=""/>
        <b>Lizenz:</b><br/>
        Dieses Lexikon-Plugin unterliegt der
        <a href="http://creativecommons.org/licenses/LGPL/2.1/">CC-GNU LPGL</a><br/>
        Welcher Lizenz die Original-Wörterbücher unterliegen, ist auf den Download-Seiten nicht ersichtlich.<br/>
        Bei Verletzung von Rechten Dritter, nehmen Sie bitte unverzüglich Kontakt mit <a href="mailto:support.tekl@mac.com">mir</a> auf.
    </p>
</d:entry>
</d:dictionary>""" % (marketingVersion )  )
destfile.close()

if writeTestHtml == 1:
    html.write("""</body></html>""")

print "\nVersionsnummer in %s.pmdoc und finishup_xx.rtfd wird angepasst ..." % (dictName)
rtfFiles = ['StarDictDeutsch.pmdoc/index.xml','finishup_de.rtfd/TXT.rtf','finishup_en.rtfd/TXT.rtf']
for filename in rtfFiles:
    pmdocFile = codecs.open(filename,'r','UTF-8')
    pmdoc = pmdocFile.read()
    pmdoc = re.sub("Version: .\d+.\d+.\d+", "Version: "+ marketingVersion, pmdoc)
    pmdocFile.close()
    pmdocFile = codecs.open(filename,'w','UTF-8')
    pmdocFile.write( pmdoc )
    pmdocFile.close()

print "\nVersionsnummer in der Info.plist wird angepasst ..."
plistFile = codecs.open('Info.plist','r','UTF-8')
plist = plistFile.read()
plist = re.sub("(?u)(<key>CFBundleVersion</key>\s+<string>)[^<]+(</string>)", "\\g<1>"+bundleVersion+"\\2", plist) 
plist = re.sub("(?u)(<key>CFBundleShortVersionString</key>\s+<string>)[^<]+(</string>)", "\\g<1>"+marketingVersion+"\\2", plist) 
plistFile.close()
plistFile = codecs.open('Info.plist','w','UTF-8')
plistFile.write( plist )
plistFile.close()

print "\nXML-Datei wird ausgewertet (Making) ...\n-----------------------------------------------------"
