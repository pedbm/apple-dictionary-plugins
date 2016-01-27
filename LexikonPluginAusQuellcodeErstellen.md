# Lexikon-Plugin aus dem Quellcode selber erstellen #

Interessierte können sich das Lexikon-Plugin selbst erzeugen und installieren lassen.

# Details #

Zu Beginn muss man den aktuellen Quellcode des gewünschten Plugins (siehe rechte Seitenleiste) herunterladen und entpacken. Nun ruft man Terminal auf und führt dort folgende Befehle aus ([Xcode](http://www.macupdate.com/info.php/id/13621/apple-xcode) erforderlich):
```
cd ~/Downloads/PluginVerzeichnis
make
sudo make install
```

  * Beim cd-Befehl muss man den entsprechenden Pfad zum Verzeichnis angeben, welches beim Entpacken angelegt wurde.
  * Der make-Prozess kann sehr lange dauern, je nach Geschwindigkeit des Computers.
  * Mit `sudo make install` wird das Dictionary in `/Library/Dictionaries` kopiert, dazu ist ein Benutzer mit Kennwort Vorraussetzung
  * Mit `make package`kann man sich auch automatisch ein Installationspaket erzeugen lassen
  * `make clean` löscht die vom Skript erstellten Dateien wieder, das Paket bleibt aber bestehen