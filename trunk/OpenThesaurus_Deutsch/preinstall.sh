#!/bin/sh

parentID=`ls -nld ~/Library | cut -d ' ' -f 4`
mkdir ~/Library/Dictionaries
chown ${parentID} ~/Library/Dictionaries
exit 0