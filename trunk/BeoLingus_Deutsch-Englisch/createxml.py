#!/usr/bin/env python
# -*- coding: utf-8 -*-

# DIESES SCRIPT BITTE NICHT MANUELL AUSFÜHREN
# ES WIRD PER "MAKE" AUFGERUFEN

import os,sys,time,re,codecs,datetime,urllib,string,subprocess,pickle,email,time

def progress(a,b,c):
    sys.stdout.write(".")

def sort_by_value(d):
    """ Returns the keys of dictionary d sorted by their values """
    items=d.items()
    backitems=[ [v[1],v[0]] for v in items]
    backitems.sort()
    return [ backitems[i][1] for i in range(0,len(backitems))]
    
def normalize(s):
    s = s.replace(u"ä","a")
    s = s.replace(u"ö","o")
    s = s.replace(u"ü","u")
    s = s.replace(u"Ä","A")
    s = s.replace(u"Ö","O")
    s = s.replace(u"Ü","U")
    return s

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
print "CreateXML v1.2 von Wolfgang Reszel, 2008-10-02"
print
morphology = {}
for file in ["morphology-cache.txt","../Morphologie_Deutsch/morphology-cache.txt"]:
    if os.path.isfile(file):
        print "Morpholgie-Cache-Datei gefunden und geladen.\n"
        morphcache = open(file,'r')
        morphology = pickle.load(morphcache)
        morphcache.close()
        break

print "Aktuelle Wortliste wird herunterladen ..."

bundleVersion = datetime.datetime.today().strftime("%Y.%m.%d")
marketingVersion = "v" + bundleVersion

urllib.urlcleanup()
download = urllib.urlretrieve("http://ftp.tu-chemnitz.de/pub/Local/urz/ding/"+dict+"-devel/"+dict+".txt.gz","de-en.txt.gz",progress)
if string.find(str(download[1]),"Error") > 0:
    print "\nHerunterladen fehlgeschlagen, bitte später noch mal versuchen\n"
    print download[1]
    exit()
    
timestamp = re.sub("(?s)^.*Last-Modified: ([^\n]+)\n.*$","\\1",str(download[1]))
downloadfiledate = datetime.datetime.fromtimestamp(time.mktime(email.Utils.parsedate(timestamp))).strftime("%d.%m.%Y")

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
seealsos = {}

for line in sourcefile:
    if line[0] == "#" or line.strip() == "":
        continue
    if "rose" not in line.lower():
        continue

    line = line.strip()
    line = line.replace("&","&amp;")
    line = line.replace(":: ::","::")
    line = line.replace("| ::","|")
    line = line.replace("; ", " ; ")
    line = re.sub("(\([^)]+) ; ([^)]+\))",r"\1; \2", line)
    line = re.sub("(\{[^}]+) ; ([^}]+\})",r"\1; \2", line)
    line = line.replace("<","&lt;")
    line = line.replace(">","&gt;")
    
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
            
            translations = re.sub('(\([^)]+\))', u' <span class="s1">\\1</span>',translations)
            translations = re.sub('(\{[^}]+\})', u' <i>\\1</i>',translations)
            translations = re.sub('(\[[^]]+\])', u' <span class="s2">\\1</span>',translations)
            translations = re.sub(' +', ' ',translations)
            translations = translations.replace(" ; ", "; ").strip()
            translations = re.sub('> *<',u'> <',translations).strip() # six-per-em space U+2006

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
                        element = element.strip() + " " + fachgebiet.strip()
                
                if id == "":
                    id = re.sub('(?u)[\"<>, ]','_',element.lower())
                    id = re.sub("(?u)_+","_",id)
                    id = re.sub("(?u)(.)_$","\\1",id)
                    id = str(lng) + "_" + id
                    
                dvalue = re.sub('\([^)]+\)|\{[^}]+\}|\[[^]]+\]',"",element).strip()
                dvalue = re.sub("\s*/\s*([^/]+)\s*/(\W)",r" / \1\2",dvalue).strip()
                dvalue = re.sub("(.+?) &gt;.*&lt;.*/",r"\1",dvalue).strip()
                if dvalue == "":
                    dvalue = re.sub('\{[^}]+\}|\[[^]]+\]',"",element).strip()
                    dvalue = re.sub('\(|\)',"",dvalue).strip()
                if dvalue == "":
                    continue

                if fachgebiet != "":
                    if fachgebiet not in sourceelement:
                        sourceelement = sourceelement + fachgebiet

                formattedsource = re.sub('(\([^)]+\))', u' <span class="s1">\\1</span>',sourceelement)
                formattedsource = re.sub('(\[[^\]]+\])', u' <span class="s2">\\1</span>',formattedsource)
                formattedsource = re.sub('(\{[^}]+\})', u' <i>\\1</i>',formattedsource)
                formattedsource = re.sub('(&gt;.*&lt;)', u' <i>\\1</i>',formattedsource)
                formattedsource = re.sub('^([^<>;]+)(;|<|$)', r'<b>\1</b>\2',formattedsource)
                formattedsource = re.sub(' +', ' ',formattedsource)
                formattedsource = re.sub('> *<',u'> <',formattedsource).strip() # six-per-em space U+2006
                formattedsource = formattedsource.replace(" </","</")
                
                # normalization
                # prepare index string // remove all kinds of additional descriptions
                id_norm = dvalue
                if id_norm.startswith("to "): id_norm =  id_norm[3:] # strip (to)
                id_norm = re.sub('(\([^)]+\))', r'',id_norm)
                id_norm = re.sub('(\{[^}]+\})', r'',id_norm)
                id_norm = re.sub('(\[[^]]+\])', r'',id_norm)
                if str(lng) == "0":
                    id_norm = re.sub('(^|\s)(er/sie|er/sie/es|ich/er/sie/es|ich|er|sie|es|ist/war|hat/hatte|ist|war|hat|hatte|sich|etw.|jmd.)(\s|$)', r'\1',id_norm)
                    id_norm = re.sub('(^|\s)(er/sie|er/sie/es|ich/er/sie/es|ich|er|sie|es|ist/war|hat/hatte|ist|war|hat|hatte|sich|etw.|jmd.)(\s|$)', r'\1',id_norm)
                else:
                    id_norm = re.sub('(^|\s)(he/she|he/she/it|i/he/she/it|i|he|she|it|has/had|is/was|has|was|is|of|sth.|sbd.)(\s|$)', r'\1',id_norm)
                    id_norm = re.sub('(^|\s)(he/she|he/she/it|i/he/she/it|i|he|she|it|has/had|is/was|has|was|is|of|sth.|sbd.)(\s|$)', r'\1',id_norm)
                id_norm = re.sub('  ', r' ', id_norm) # remove
                id_norm = re.sub('  ', r' ', id_norm) # remove
                id_norm = id_norm.strip()   # .lower()
                id_norm = id_norm.lower()
                if id_norm.endswith("-"): id_norm = id_norm[:-1]
                id = id_norm
                dvalue2 = id_norm
                
                print str(lng)+"_"+id_norm+"..."+dvalue+"..."+id
                
                if result.has_key(id):
                    for srcElement in formattedsource.split(";"):
                        if srcElement.strip()+";" not in formatted[id]+";":
                            formatted[id] = formatted[id] + '; '+srcElement.strip()
                    if "<p>" + translations.lower() + "</p>" not in result[id].lower():
                        result[id] = result[id] + "\n<p>" + translations + "</p>"
                    if '<d:index d:value="'+normalize(dvalue.lower())+'"' not in normalize(dvalues[id].lower()):
                        dvalues[id] = dvalues[id] + '\n<d:index d:value="'+dvalue+'" d:title="'+dvalue+'"/>'
                    if '<d:index d:value="'+normalize(dvalue2.lower())+'"' not in normalize(dvalues[id].lower()):
                        dvalues[id] = dvalues[id] + '\n<d:index d:value="'+dvalue2+'" d:title="'+dvalue2+'"/>'

                    result[id] = result[id] + "<p>" + translations + "</p>"
                    linkwords[id] = linkwords[id] + urllib.quote(re.sub('\([^)]+\)|{[^}]+}|\[[^\]]+\]',"",element).strip().encode("utf-8"))
                    titles[id] = titles[id] + element
                    formatted[id] = formatted[id] + formattedsource
                else:
                    lengths[id] = len(id)
                    result[id] = "<p>" + translations + "</p>"
                    dvalues[id] = '<d:index d:value="'+dvalue2+'" d:title="'+dvalue2+'"/>'
                    if dvalue != dvalue2:
                        dvalues[id] = dvalues[id] + '\n<d:index d:value="'+dvalue+'" d:title="'+dvalue+'"/>'
                    linkwords[id] = urllib.quote(re.sub('\([^)]+\)|{[^}]+}|\[[^\]]+\]',"",element).strip().encode("utf-8"))
                    titles[id] = element
                    formatted[id] = formattedsource
                    dvalueSplit = dvalue.split()
                    seealsos[id] = ""
                    
                cases = re.sub(" \{([^{}]*); ([^{}]*)\}",r";\1;\2", element)
                cases = re.sub("&gt;(.+?)&lt;",r";\1", cases)
                cases = re.sub(" /([^/]+)/",r";\1", cases)
                if cases is not element:
                    for sElement in cases.split(";"):
                        if u'<d:index d:value="'+normalize(sElement.lower())+u'"' not in normalize(dvalues[id].lower()):
                            dvalues[id] = dvalues[id] + '\n<d:index d:value="'+sElement+u'" d:title="'+sElement+' {'+dvalue+'}"/>'

                for sElements in source:
                    for sElement in sElements.split(" ; "):
                        seealso = re.sub('\([^)]+\)|\{[^}]+\}|\[[^]]+\]',"",sElement).strip()
                        if seealso == "":
                            seealso = re.sub('\{[^}]+\}|\[[^]]+\]',"",sElement).strip()
                            seealso = re.sub('\(|\)',"",seealso).strip()
                        seealso = seealso.replace(" , ",", ")
                        if re.search("(\W|^)"+re.escape(seealso)+"(\W|$)",formattedsource):
                            if seealsos[id] != "":
                                seealsos[id] = re.sub("(^|, )"+re.escape(seealso)+"($|, )","\\1",seealsos[id]) 
                                seealsos[id] = re.sub(", $|^, ","",seealsos[id]) 
                            continue
                        if dvalue in seealso or seealso in seealsos[id] or seealso == "":
                            continue
                        if seealsos[id] == "":
                            seealsos[id] = seealso
                        else:
                            seealsos[id] = seealsos[id].strip() + ", " + seealso

                if morphology.has_key(dvalue2) and lng == 0:
                    for x in morphology[dvalue2].split(","):
                        if u'<d:index d:value="'+normalize(x.lower())+u'"' not in normalize(dvalues[id].lower()):
                            if x[:len(dvalue)].lower() == dvalue.lower():
                                dvalues[id] = dvalues[id] + '\n<d:index d:value="'+x+u'" d:title="→ '+dvalue+'"/>'
                            else:
                                dvalues[id] = dvalues[id] + '\n<d:index d:value="'+x+u'" d:title="⇒ '+dvalue+'"/>'
                if morphology.has_key(dvalue) and lng == 0:
                    for x in morphology[dvalue].split(","):
                        if u'<d:index d:value="'+normalize(x.lower())+u'"' not in normalize(dvalues[id].lower()):
                            if x[:len(dvalue)].lower() == dvalue.lower():
                                dvalues[id] = dvalues[id] + '\n<d:index d:value="'+x+u'" d:title="→ '+dvalue+'"/>'
                            else:
                                dvalues[id] = dvalues[id] + '\n<d:index d:value="'+x+u'" d:title="⇒ '+dvalue+'"/>'

                dvalueSplit = dvalue.split()
                for i in dvalueSplit:
                    if len(i) > 1:
                        devalueHyphenSplit = i.split("-")
                        for j in range(1,len(devalueHyphenSplit)):
                            if len(devalueHyphenSplit[j]) > 1:
                                if '<d:index d:value="'+normalize(devalueHyphenSplit[j].lower())+'"' not in normalize(dvalues[id].lower()):
                                    dvalues[id] = dvalues[id] + '\n<d:index d:value="'+devalueHyphenSplit[j]+u'" d:title="⇒ '+dvalue+'"/>'
                                if morphology.has_key(devalueHyphenSplit[j]):
                                    for x in morphology[devalueHyphenSplit[j]].split(","):
                                        if u'<d:index d:value="'+normalize(x.lower())+u'"' not in normalize(dvalues[id].lower()):
                                            if x[:len(dvalue)].lower() == dvalue.lower():
                                                dvalues[id] = dvalues[id] + '\n<d:index d:value="'+x+u'" d:title="→ '+dvalue+'"/>'
                                            else:
                                                dvalues[id] = dvalues[id] + '\n<d:index d:value="'+x+u'" d:title="⇒ '+dvalue+'"/>'
                        if '<d:index d:value="'+normalize(i.lower())+'"' not in normalize(dvalues[id].lower()):
                            if i[0] != "-" and i[len(i)-1] != "-":
                                if dvalue[:len(i)].lower() != i.lower():
                                    dvalues[id] = dvalues[id] + '\n<d:index d:value="'+i+u'" d:title="⇒ '+dvalue+'"/>'
                                if morphology.has_key(i):
                                    for x in morphology[i].split(","):
                                        if u'<d:index d:value="'+normalize(x.lower())+u'"' not in normalize(dvalues[id].lower()):
                                            if x[:len(dvalue)].lower() == dvalue.lower():
                                                dvalues[id] = dvalues[id] + '\n<d:index d:value="'+x+u'" d:title="→ '+dvalue+'"/>'
                                            else:
                                                dvalues[id] = dvalues[id] + '\n<d:index d:value="'+x+u'" d:title="⇒ '+dvalue+'"/>'

            index+=1

sourcefile.close()
                      
print "\nXML-Datei wird erzeugt ..."
destfile = codecs.open(dictFull+'.xml','w','utf-8')
destfile.write("""<?xml version="1.0" encoding="utf-8"?>
<d:dictionary xmlns="http://www.w3.org/1999/xhtml" xmlns:d="http://www.apple.com/DTDs/DictionaryService-1.0.rng">""")

for id in sort_by_value(lengths):    
    if seealsos[id] != "":
        seealsos[id] = '<div class="seealso"><b>Siehe auch:</b> ' + seealsos[id] + '</div>'
    formatted[id] = '<h2 d:pr="1">'+formatted[id]+'</h2>'
    destfile.write( re.sub("  +| *\n *","", u"""
<d:entry id="%s" d:title="%s">
%s
%s
%s
%s
<div id="c" style="display:none" d:priority="2">
<span><a href="http://www.beolingus.de/dings.cgi?query=%s">Aus BeoLingus.de</a> · © 2008 TU Chemnitz</span>
<script id="u2" charset="utf-8" src="u.js"></script></div>
</d:entry>""" % (id,titles[id],dvalues[id],formatted[id], result[id], seealsos[id], linkwords[id]) ) )
        
destfile.write( u"""
<d:entry id="front_back_matter" d:title="Voderer/Hinterer Teil">
    <h1><b>BeoLingus %s</b></h1>
    <div><small><b>Version: %s</b></small>
        <div id="u1"><small>
        <span id="UpdateMessage"><img src="Images/progress_indicator.gif" valign="middle" alt=""/> Aktuelle Version wird ermittelt ...</span>
        <script type="text/javascript" charset="utf-8">
        var req;
        var currentVersion = "%s";
        var updateURL = 'http://www.tekl.de/deutsch/BeoLingus_Deutsch-Englisch.html';

        window.setTimeout("loadXMLDoc(updateURL)", 500);

        function loadXMLDoc(url) {
           try {
              req = new XMLHttpRequest();
           } catch(e) {
              req = false;
           }
           if(req) {
              req.onreadystatechange = processReqChange;
              req.open("GET", url, true);
              req.send("");
           }
        }

        function processReqChange() {
           // only if req shows "loaded"
           if (req.readyState == 4) {
              // only if "OK"
              if (req.status == 200) {
                 newestVersion = req.responseText.match(/v\d\d\d\d.\d\d.\d\d/);
                 if (newestVersion != null) {
                    newestVersion = newestVersion.toString();
                    if (newestVersion > currentVersion) {
                       result = '<a class="newVersion" href="'+updateURL+'">Neue Version verfügbar!</a> ('+newestVersion+')';
                    } else {
                       result = 'Keine neuere Version verfügbar.';
                    }
                 } else {
                    result = '<em>Aktuelle Version konnte nicht ermittelt werden.</em>';
                 }
              } else {
                 result = '<em>Verbindung zu www.tekl.de fehlgeschlagen.</em>'
              }
              document.getElementById("UpdateMessage").innerHTML = '<img src="Images/update.gif" valign="middle" alt=""/> '+result;
           }
        }
        </script>
        </small>
        </div>
    </div>
    <p>
        <img src="Images/beolingus.gif" align="right" style="padding-left:10px" alt=""/>
        Dieses Wörterbuch basiert auf dem Online-Wörterbuch<br/>
        <a href="http://www.beolingus.de">www.beolingus.de</a> der TU Chemnitz. (Stand: %s)
    </p>
    <p>
        <b>Updates</b> finden Sie unter <a href="http://www.tekl.de">www.tekl.de</a>.<br/>
        Support und den Quellcode finden Sie unter <a href="http://apple-dictionary-plugins.googlecode.com"><b>apple-dictionary-plugins.googlecode.com</b></a>.
    </p>
    <p>
        Das Python-Skript zur Umwandlung der Beolingus-Wortliste<br/>in eine Apple Lexikon-Datei wurde von Wolfgang Reszel entwickelt.
    </p>
    <p>
        Die Wortform-Datei (Morphologie), durch welche auch die Suche nach Worten im Plural möglich ist, wurde mit dem Windows-Tool <a href="http://www.wolfganglezius.de/doku.php?id=public:cl:morphy">Morphy</a> erstellt.    
    </p>
    <p>
        <img src="Images/gplv3-88x31.png" align="left" style="padding-right:10px" alt=""/>
        <b>Lizenz:</b>
        Dieses Lexikon-Plugin unterliegt der <a href="http://www.gnu.org/licenses/gpl.html">GPLv3</a><br/>
        Die Wortliste von BeoLingus unterliegt der 
        <a href="http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt">GNU public license v2</a><br/>
    </p>
</d:entry>
</d:dictionary>""" % (dictFull, marketingVersion, marketingVersion, downloadfiledate )  )
destfile.close()

print "\nHeruntergeladene Datei wird gelöscht ..."
#os.system('rm '+dict+'.txt')

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

print "\nVersionsnummer in u.js wird angepasst ..."
plistFile = codecs.open('OtherResources/u.js','r','UTF-8')
plist = plistFile.read()
plist = re.sub("(?u)(var currentVersion = \")[^\"]+(\")", "\\g<1>"+marketingVersion+"\\2", plist) 
plistFile.close()
plistFile = codecs.open('OtherResources/u.js','w','UTF-8')
plistFile.write( plist )
plistFile.close()

print "\nXML-Datei wird ausgewertet (Making) ...\n-----------------------------------------------------"
