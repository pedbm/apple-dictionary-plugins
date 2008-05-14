#
# Makefile
#
#
#

###########################

# You need to edit these values.

DICT_NAME		=	OpenThesaurus Deutsch
DICT_SRC_PATH	=	ThesaurusDeutsch.xml
CSS_PATH		=	ThesaurusDeutsch.css
PMDOC_NAME      =   ThesaurusDeutsch.pmdoc
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

package:
	@echo "- Creating Install Package."
	@hdiutil create -type SPARSE -ov -fs HFS+ -attach -noscrub -layout NONE "DMG.sparseimage" -volname "$(DICT_NAME)"
	@mkdir -p "/Volumes/$(DICT_NAME)/.bg"
	@cp dmg.background.png "/Volumes/$(DICT_NAME)/.bg/background.png"
	@cp dmg.DS_Store "/Volumes/$(DICT_NAME)/.DS_Store"
	@/Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS/PackageMaker -d $(PMDOC_NAME) -o "/Volumes/$(DICT_NAME)/$(DICT_NAME) $(DATE).pkg" --filter '/\.svn$$'
	@echo "Done."
	@echo "Position the icon and type 'make finish'."
	@open "/Volumes/$(DICT_NAME)"
	
finish:
	@echo "- Finishing internet-enabled disk image."
	@hdiutil eject "/Volumes/$(DICT_NAME)"
	@hdiutil convert -ov -format UDBZ DMG.sparseimage -o "$(DICT_NAME) $(DATE).dmg"
	@hdiutil internet-enable "$(DICT_NAME) $(DATE).dmg"
	@rm DMG.sparseimage
	@echo "Done."

install:
	@echo "Installing into $(DESTINATION_FOLDER)".
	@mkdir -p $(DESTINATION_FOLDER)
	@ditto --noextattr --norsrc "$(DICT_DEV_KIT_OBJ_DIR)/$(DICT_NAME).dictionary"  "$(DESTINATION_FOLDER)/$(DICT_NAME).dictionary"
	@touch $(DESTINATION_FOLDER)
	@echo "Done."
	@echo "To test the new dictionary, try Dictionary.app."

clean:
	$(RM) -rf $(DICT_DEV_KIT_OBJ_DIR)
	$(RM) -f $(DICT_SRC_PATH)
