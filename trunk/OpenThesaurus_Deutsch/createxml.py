#!/usr/bin/env python
# -*- coding: utf-8 -*-

# DIESES SCRIPT BITTE NICHT MANUELL AUSFÜHREN
# ES WIRD PER "MAKE" AUFGERUFEN

import os,sys,time,re,codecs,datetime,urllib,string,subprocess

def progress(a,b,c):
    sys.stdout.write(".")

def sort_by_value(d):
    """ Returns the keys of dictionary d sorted by their values """
    items=d.items()
    backitems=[ [v[1],v[0]] for v in items]
    backitems.sort()
    return [ backitems[i][1] for i in range(0,len(backitems))]
    
os.system("clear")

print "Lexikon-Plugin auf Basis von OpenThesaurus.de"
print "CreateXML v0.6 von Wolfgang Reszel, 2008-03-15"
print
print "Aktueller Thesaurus wird herunterladen ",

bundleVersion = datetime.datetime.today().strftime("%Y.%m.%d")
marketingVersion = "v" + bundleVersion

urllib.urlcleanup()
download = urllib.urlretrieve("http://www.openthesaurus.de/download/thesaurus.txt.gz","thesaurus.txt.gz",progress)
if string.find(str(download[1]),"Error") > 0:
    print "\nHerunterladen fehlgeschlagen, bitte später noch mal versuchen\n"
    print download[1]
    exit()

print "\nHeruntergeladene Datei wird entpackt ..."    
os.system('gzip -d -f thesaurus.txt.gz')

print "\nDatei wird analysiert ..."
sourcefile = codecs.open('thesaurus.txt','r','Windows-1252')

result = {}
dvalues = {}
titles = {}
headlines = {}
lengths = {}
linkwords = {}

for line in sourcefile:
    if line[0] == "#":
        continue
    line = line.strip()
    line = line.replace("&","&amp;")
    line = line.replace("<","&lt;")
    line = line.replace(">","&gt;")
    elements = line.split(";")

    for element in elements:
        if element == "":
            continue
        translations = ""
        for i in elements:
            if i == "":
                continue
            if i != element:
                translations = translations + "; " + i

        translations = translations[2:len(translations)]
        translations = re.sub('(\([^)]+\))', r'<i>\1</i>',translations)

        id = re.sub('(?u)[\"<>]','_',element)
        id = re.sub("(?u)_+","_",id)
        id = re.sub("(?u)(.)_$","\\1",id)
    
        dvalue = re.sub('\([^)]+\)',"",element).strip()
                      
        if result.has_key(id):
            result[id] = result[id] + "\n<div>" + translations + "</div>"
        else:
            lengths[id] = len(id)
            result[id] = "<div>" + translations + "</div>"
            dvalues[id] = u'<d:index d:value="'+dvalue+u'" d:title="'+dvalue+u'"/>'
            titles[id] = element
            linkwords[id] = urllib.quote(re.sub('\([^)]+\)|{[^}]+}|\[[^\]]+\]',"",element).strip().encode("utf-8"))
            headlines[id] = re.sub('(\([^)]+\))', r'<i>\1</i>',element)

        dvalueSplit = dvalue.split()
        for i in dvalueSplit:
            if len(i) > 1:
                devalueHyphenSplit = i.split("-")
                for j in range(1,len(devalueHyphenSplit)):
                    if len(devalueHyphenSplit[j]) > 1:
                        if u'<d:index d:value="'+devalueHyphenSplit[j].lower()+u'"' not in dvalues[id].lower():
                            dvalues[id] = dvalues[id] + '\n<d:index d:value="'+devalueHyphenSplit[j]+u'" d:title="⇒ '+dvalue+'"/>'
                if '<d:index d:value="'+i.lower()+'"' not in dvalues[id].lower():
                    if i[0] != "-" and i[len(i)-1] != "-":
                        dvalues[id] = dvalues[id] + '\n<d:index d:value="'+i+u'" d:title="⇒ '+dvalue+'"/>'

sourcefile.close()

print "\nXML-Datei wird erzeugt ..."
destfile = codecs.open('ThesaurusDeutsch.xml','w','utf-8')
destfile.write("""<?xml version="1.0" encoding="utf-8"?>
<d:dictionary xmlns="http://www.w3.org/1999/xhtml" xmlns:d="http://www.apple.com/DTDs/DictionaryService-1.0.rng">""")
                
for id in sort_by_value(lengths):    
    destfile.write( u"""
<d:entry id="%s" d:title="%s">
%s
<h2 d:pr="1">%s</h2>
%s
<div class="copyright" d:priority="2">
<span><a href="http://www.openthesaurus.de/overview.php?word=%s">aus OpenThesaurus.de</a> · © 2008 Daniel Naber</span></div>
</d:entry>""" % (id,titles[id],dvalues[id],headlines[id], result[id], linkwords[id] ) ) 
        
destfile.write( u"""
<d:entry id="front_back_matter" d:title="Voderer/Hinterer Teil">
    <h1>Thesaurus Deutsch</h1>
    <div><small><b>Version: %s</b></small></div>
    <p>
    	Dieser Thesaurus basiert auf dem Online-Thesaurus<br/>
    	<a href="http://www.openthesaurus.de">www.openthesaurus.de</a> von Daniel Naber.
    </p>
    <p>
        Das Python-Skript zur Umwandlung der OpenThesaurus-Wortliste<br/>in ein Lexikon-Plugin wurde von Wolfgang Reszel entwickelt.
    </p>
    <p>
        <b>Updates:</b> Die aktuellste Version finden Sie unter <a href="http://www.tekl.de">www.tekl.de</a>.<br/>
        Support und den Quellcode finden Sie unter <a href="http://apple-dictionary-plugins.googlecode.com"><b>apple-dictionary-plugins.googlecode.com</b></a>.
    </p>
    <p>
        <img src="Images/cc-LGPL-a.png" align="left" style="padding-right:10px" alt=""/>
        <b>Lizenz:</b><br/>
        Die Wortliste und dieses Lexikon-Plugin unterliegen der
        <a href="http://creativecommons.org/licenses/LGPL/2.1/">CC-GNU LPGL</a><br/>
    </p>
</d:entry>
</d:dictionary>""" % (marketingVersion )  )
destfile.close()

print "\nHeruntergeladene Datei wird gelöscht ..."
os.system("rm thesaurus.txt")

print "\nVersionsnummer in ThesaurusDeutsch.pmdoc und finishup_xx.rtfd wird angepasst ..."
rtfFiles = ['ThesaurusDeutsch.pmdoc/index.xml','finishup_de.rtfd/TXT.rtf','finishup_en.rtfd/TXT.rtf']
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
