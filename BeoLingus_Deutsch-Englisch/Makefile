#
# Makefile
#
#
#

###########################

# You need to edit these values.

DICT_NAME		=	BeoLingus Deutsch-Englisch
DICT_SRC_PATH	=	Deutsch-Englisch.xml
CSS_PATH		=	Deutsch-Englisch.css
PMDOC_NAME      =   Deutsch-Englisch.pmdoc
PLIST_PATH		=	Info.plist
DATE            =   `date +"v%Y.%m.%d"`

DICT_BUILD_OPTS		=
# Suppress adding supplementary key.
# DICT_BUILD_OPTS		=	-s 0	# Suppress adding supplementary key.

###########################

# The DICT_BUILD_TOOL_DIR value is used also in "build_dict.sh" script.
# You need to set it when you invoke the script directly.

DICT_BUILD_TOOL_DIR	=	"/Developer/Extras/Dictionary Development Kit"
DICT_BUILD_TOOL_BIN	=	"$(DICT_BUILD_TOOL_DIR)/bin"

###########################

DICT_DEV_KIT_OBJ_DIR	=	./objects
export	DICT_DEV_KIT_OBJ_DIR

DESTINATION_FOLDER	=	/Library/Dictionaries
RM			=	/bin/rm

###########################

all:
	@/usr/bin/python createxml.py
	@"$(DICT_BUILD_TOOL_BIN)/build_dict.sh" $(DICT_BUILD_OPTS) "$(DICT_NAME)" $(DICT_SRC_PATH) $(CSS_PATH) $(PLIST_PATH)
	@echo "Done."
	@echo "Use 'sudo make install' to install the dictionary or 'make package' to create the Install Package."

make:
	@"$(DICT_BUILD_TOOL_BIN)/build_dict.sh" $(DICT_BUILD_OPTS) "$(DICT_NAME)" $(DICT_SRC_PATH) $(CSS_PATH) $(PLIST_PATH)
	@echo "Done."

smallpackage:
	@/usr/bin/python createxml.py small
	@"$(DICT_BUILD_TOOL_BIN)/build_dict.sh" $(DICT_BUILD_OPTS) "$(DICT_NAME)" $(DICT_SRC_PATH) $(CSS_PATH) $(PLIST_PATH)

	@echo "- Creating Install Package."
	@/Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS/PackageMaker -d $(PMDOC_NAME) -o "$(DICT_NAME) $(DATE).pkg" --filter '/\.svn$$'
	@echo "- Creating internet-enabled disk image."
	@hdiutil create -ov -format UDBZ -layout NONE -srcdir "$(DICT_NAME) $(DATE).pkg" "$(DICT_NAME) $(DATE).dmg" -volname "$(DICT_NAME)"
	@hdiutil internet-enable "$(DICT_NAME) $(DATE).dmg"
	@echo "Done."
	@echo "Execute '$(DICT_NAME) $(DATE).pkg' to install the dictionary."

package:
	@echo "- Creating install package."
	@hdiutil create -type SPARSE -ov -fs HFS+ -attach -noscrub -layout NONE "DMG.sparseimage" -volname "$(DICT_NAME)"
	@mkdir -p "/Volumes/$(DICT_NAME)/.bg"
	@cp dmg.background.png "/Volumes/$(DICT_NAME)/.bg/background.png"
	@cp dmg.DS_Store "/Volumes/$(DICT_NAME)/.DS_Store"
	@cp dmg.VolumeIcon.icns "/Volumes/$(DICT_NAME)/.VolumeIcon.icns"
	@SetFile -a C "/Volumes/$(DICT_NAME)/"
	@/Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS/PackageMaker -d $(PMDOC_NAME) -o "/Volumes/$(DICT_NAME)/$(DICT_NAME) $(DATE).pkg" --filter '/\.svn$$'
	@osascript -e 'tell application "Finder" to open "$(DICT_NAME):"'
	@osascript -e 'tell application "Finder" to set background picture of (icon view options of Finder window 1) to "$(DICT_NAME):.bg:background.png"'
	@osascript -e 'tell application "Finder" to set toolbar visible of Finder window 1 to false'
	@osascript -e 'tell application "Finder" to set bounds of Finder window 1 to {100, 100, 660, 470}'
	@osascript -e 'tell application "Finder" to set arrangement of icon view options of Finder window 1 to not arranged'
	@osascript -e 'tell application "Finder" to set position of item 1 of Finder window 1 to {131, 159}'
	@osascript -e 'tell application "Finder" to set current view of Finder window 1 to icon view'
	@osascript -e 'tell application "Finder" to set icon size of icon view options of Finder window 1 to 128'
	@osascript -e 'tell application "Finder" to close Finder window 1'
	@osascript -e 'tell application "Finder" to delay 3'
	@osascript -e 'tell application "Finder" to open "$(DICT_NAME):"'
	@osascript -e 'tell application "Finder" to close Finder window 1'
	@osascript -e 'tell application "Finder" to delay 3'
	@echo "- Finishing internet-enabled disk image."
	@hdiutil eject "/Volumes/$(DICT_NAME)"
	@hdiutil convert -ov -format UDBZ DMG.sparseimage -o "$(DICT_NAME) $(DATE).dmg"
	@hdiutil internet-enable "$(DICT_NAME) $(DATE).dmg"
	@rm DMG.sparseimage
	@echo "Done."
	
install:
	@echo "Installing into $(DESTINATION_FOLDER)".
	@mkdir -p $(DESTINATION_FOLDER)
	@ditto --noextattr --norsrc "$(DICT_DEV_KIT_OBJ_DIR)/$(DICT_NAME).dictionary" "$(DESTINATION_FOLDER)/$(DICT_NAME).dictionary"
	@touch $(DESTINATION_FOLDER)
	@echo "Done."
	@echo "To test the new dictionary, try Dictionary.app."

clean:
	$(RM) -rf $(DICT_DEV_KIT_OBJ_DIR)
	$(RM) -f $(DICT_SRC_PATH)
	
