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

dict = "de-en"
dictFull = "Deutsch-Englisch"

dictAdd = ""
smallversion = 0
if len(sys.argv) == 2:
    if sys.argv[1] == "small":
        smallversion = 1
        dictAdd = " small"

print "Lexikon-Plugin ("+dictFull+dictAdd+") auf Basis von Beolingus.de"
print "CreateXML v0.8 von Wolfgang Reszel, 2008-03-17"
print
print "Aktuelle Wortliste wird herunterladen ..."

bundleVersion = datetime.datetime.today().strftime("%Y.%m.%d")
marketingVersion = "v" + bundleVersion

urllib.urlcleanup()
download = urllib.urlretrieve("ftp://ftp.tu-chemnitz.de/pub/Local/urz/ding/"+dict+"-devel/"+dict+".txt.gz","de-en.txt.gz",progress)
if string.find(str(download[1]),"Error") > 0:
    print "\nHerunterladen fehlgeschlagen, bitte später noch mal versuchen\n"
    print download[1]
    exit()

print "\nHeruntergeladene Datei wird entpackt ..."    
os.system('gzip -d -f '+dict+'.txt.gz')

print "\nDatei wird analysiert ..."
sourcefile = codecs.open(dict+'.txt','r','UTF-8')

result = {}
dvalues = {}
titles = {}    
formatted = {}
lengths = {}
linkwords = {}

for line in sourcefile:
    if line[0] == "#":
        continue

    line = line.strip()
    line = line.replace("&","&amp;")
    line = line.replace("<","&lt;")
    line = line.replace(">","&gt;")
    line = line.replace(":: ::","::")
    line = line.replace("| ::","|")
    line = line.replace("; ", " ; ")
    line = re.sub("(\([^)]+) ; ([^)]+\))",r"\1; \2", line)
    
    wordlist = line.split("::")
    wordlist[0] = re.sub('"([^"]+)"',r'„\1“'.decode("utf-8"),wordlist[0])
    wordlist[1] = re.sub('"([^"]+)"',r'“\1”'.decode("utf-8"),wordlist[1])
  
    for lng in range(2-smallversion):
        if lng == 0:
            source = re.split('\||',wordlist[0])
            destination = re.split('\||',wordlist[1]) 
        else:
            source = re.split('\||',wordlist[1])
            destination = re.split('\||',wordlist[0]) 
    
        index = 0
        fachgebiet = ''
        fachgebietListe = re.findall('(\[[^\]]+\])', wordlist[0])
        if len(fachgebietListe) > 0:
            fachgebiet = fachgebietListe[0]

        for sourceelement in source:
            sourceelement = sourceelement.strip()
            if sourceelement == "":
                continue
            translations = destination[index]
            
            translations = re.sub('(\([^)]+\))', r' <span class="s1">\1</span>',translations)
            translations = re.sub('(\{[^}]+\})', r' <i>\1</i>',translations)
            translations = re.sub('(\[[^]]+\])', r' <span class="s2">\1</span>',translations)
            translations = re.sub(' +', ' ',translations)
            translations = translations.replace(" ; ", "; ").strip()
            translations = translations.replace("><", "> <").strip()
        
            if smallversion == 1:
                elements = re.split(" ; ",sourceelement)
                elements = elements + re.split(" ; ",destination[index].strip())
            else:
                elements = re.split(" ; ",sourceelement)
            sourceelement = sourceelement.replace(" ; ", "; ").strip()

            id = ''
            for element in elements:
                if element == "":
                    continue

                if fachgebiet != "":
                    if fachgebiet not in element:
                        element = element + fachgebiet
            
                if id == "":
                    id = element
                    id = re.sub('(?u)[\"<>, ]','_',element)
                    id = re.sub("(?u)_+","_",id)
                    id = re.sub("(?u)(.)_$","\\1",id)
                    
                dvalue = re.sub('\([^)]+\)|\{[^}]+\}|\[[^]]+\]',"",element).strip()
                if dvalue == "":
                    dvalue = re.sub('\{[^}]+\}|\[[^]]+\]',"",element).strip()
                    dvalue = re.sub('\(|\)',"",element).strip()
                dvalue2 = dvalue
                dvalue2 = re.sub('(?u)(^|\W)to (\w)',r'\1\2',dvalue).strip()

                if fachgebiet != "":
                    if fachgebiet not in sourceelement:
                        sourceelement = sourceelement + fachgebiet
           
                formattedsource = re.sub('(\([^)]+\))', r' <span class="s1">\1</span>',sourceelement)
                formattedsource = re.sub('(\[[^\]]+\])', r' <span class="s2">\1</span>',formattedsource)
                formattedsource = re.sub('(\{[^}]+\})', r' <i>\1</i>',formattedsource)
                formattedsource = re.sub('^([^<>;]+)(;|<|$)', r'<b>\1</b>\2',formattedsource)
                formattedsource = re.sub(' +', ' ',formattedsource)
                formattedsource = formattedsource.replace("><","> <")
                formattedsource = formattedsource.replace(" </","</")
                   
                if result.has_key(id):
                    if "<p>" + translations.lower() + "</p>" not in result[id].lower():
                        result[id] = result[id] + "\n<p>" + translations + "</p>"
                    if '<d:index d:value="'+dvalue.lower()+'"' not in dvalues[id].lower():
                        dvalues[id] = dvalues[id] + '\n<d:index d:value="'+dvalue+'" d:title="'+dvalue+'"/>'
                    if '<d:index d:value="'+dvalue2.lower()+'"' not in dvalues[id].lower():
                        dvalues[id] = dvalues[id] + '\n<d:index d:value="'+dvalue2+'" d:title="'+dvalue2+'"/>'
                else:
                    lengths[id] = len(id)
                    result[id] = "<p>" + translations + "</p>"
                    dvalues[id] = '<d:index d:value="'+dvalue2+'" d:title="'+dvalue2+'"/>'
                    if dvalue != dvalue2:
                        dvalues[id] = dvalues[id] + '\n<d:index d:value="'+dvalue+'" d:title="'+dvalue+'"/>'
                    linkwords[id] = urllib.quote(re.sub('\([^)]+\)|{[^}]+}|\[[^\]]+\]',"",element).strip().encode("utf-8"))
                    titles[id] = element
                    formatted[id] = '<h2 d:pr="1">'+formattedsource+'</h2>'
                    dvalueSplit = dvalue.split()
                    
                dvalueSplit = dvalue.split()
                for i in dvalueSplit:
                    if len(i) > 1:
                        devalueHyphenSplit = i.split("-")
                        for j in range(1,len(devalueHyphenSplit)):
                            if len(devalueHyphenSplit[j]) > 1:
                                if '<d:index d:value="'+devalueHyphenSplit[j].lower()+'"' not in dvalues[id].lower():
                                    dvalues[id] = dvalues[id] + '\n<d:index d:value="'+devalueHyphenSplit[j]+u'" d:title="⇒ '+dvalue+'"/>'
                        if '<d:index d:value="'+i.lower()+'"' not in dvalues[id].lower():
                            if i[0] != "-" and i[len(i)-1] != "-":
                                dvalues[id] = dvalues[id] + '\n<d:index d:value="'+i+u'" d:title="⇒ '+dvalue+'"/>'

            index+=1

sourcefile.close()
                      
print "\nXML-Datei wird erzeugt ..."
destfile = codecs.open(dictFull+'.xml','w','utf-8')
destfile.write("""<?xml version="1.0" encoding="utf-8"?>
<d:dictionary xmlns="http://www.w3.org/1999/xhtml" xmlns:d="http://www.apple.com/DTDs/DictionaryService-1.0.rng">""")

for id in sort_by_value(lengths):    
   destfile.write( u"""
<d:entry id="%s" d:title="%s">
%s
%s
%s
<div class="copyright" d:priority="2">
<span><a href="http://www.beolingus.de/dings.cgi?query=%s">Aus BeoLingus.de</a> · © 2008 TU Chemnitz</span></div>
</d:entry>""" % (id,titles[id],dvalues[id],formatted[id], result[id], linkwords[id]) )
        
destfile.write( u"""
<d:entry id="front_back_matter" d:title="Voderer/Hinterer Teil">
    <h1><b>BeoLingus %s</b></h1>
    <div><small><b>Version: %s</b></small></div>
    <p>
        <img src="Images/beolingus.gif" align="right" style="padding-left:10px" alt=""/>
    	Dieses Wörterbuch basiert auf dem Online-Wörterbuch<br/>
    	<a href="http://www.beolingus.de">www.beolingus.de</a> der TU Chemnitz.
    </p>
    <p>
        Das Python-Skript zur Umwandlung der Beolingus-Wortliste<br/>in eine Apple Lexikon-Datei wurde von Wolfgang Reszel entwickelt.
    </p>
    <p>
        <b>Updates:</b> Die aktuellste Version finden Sie unter <a href="http://www.tekl.de">www.tekl.de</a>.<br/>
        Support und den Quellcode finden Sie unter <a href="http://apple-dictionary-plugins.googlecode.com"><b>apple-dictionary-plugins.googlecode.com</b></a>.
    </p>
    <p>
        <img src="Images/gplv3-88x31.png" align="left" style="padding-right:10px" alt=""/>
        <b>Lizenz:</b><br/>
        Dieses Lexikon-Plugin unterliegt der <a href="http://www.gnu.org/licenses/gpl.html">GPLv3</a><br/>
        Die Wortliste von BeoLingus unterliegt der 
        <a href="http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt">GNU public license v2</a><br/>
    </p>
</d:entry>
</d:dictionary>""" % (dictFull, marketingVersion )  )
destfile.close()

print "\nHeruntergeladene Datei wird gelöscht ..."
os.system('rm '+dict+'.txt')

print "\nVersionsnummer in %s.pmdoc-Datei und finishup_xx.rtfd wird angepasst ..." % (dictFull)

rtfFiles = [dictFull+'.pmdoc/index.xml','finishup_de.rtfd/TXT.rtf','finishup_en.rtfd/TXT.rtf','gplv3_de.rtf','gplv3_en.rtf']
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
