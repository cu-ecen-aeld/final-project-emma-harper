
##############################################################
#
# AESD-SENSEHATLIVE
#
##############################################################

#TODO: Fill up the contents below in order to reference your assignment 3 git contents
AESD_SENSEHATLIVE_VERSION = 'f8819d47c39a4cbf4138cf59ffcfc47bd10eb6ee'
# Note: Be sure to reference the *ssh* repository URL here (not https) to work properly
# with ssh keys and the automated build/test system.
# Your site should start with git@github.com:
AESD_SENSEHATLIVE_SITE = 'git@github.com:cu-ecen-aeld/final-project-emma-harper.git'
AESD_SENSEHATLIVE_SITE_METHOD = git
AESD_SENSEHATLIVE_GIT_SUBMODULES = YES

AESD_SENSEHATLIVE_GIT_SUBDIR = sensehatlive 

define AESD_SENSEHATLIVE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/opt/aesd-sensehatlive/
	cp -rf $(@D)/aesd-sensehatlive/* $(TARGET_DIR)/opt/aesd-sensehatlive/
	chmod -R 755 $(TARGET_DIR)/opt/aesd-sensehatlive
endef

$(eval $(generic-package))
