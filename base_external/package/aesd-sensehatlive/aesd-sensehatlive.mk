
##############################################################
#
# AESD-SENSEHATLIVE
#
##############################################################

#TODO: Fill up the contents below in order to reference your assignment 3 git contents
AESD_SENSEHATLIVE_VERSION = c4090c307ceb8e0ef92d24bd91e9943f61d8eb6f
# Note: Be sure to reference the *ssh* repository URL here (not https) to work properly
# with ssh keys and the automated build/test system.
# Your site should start with git@github.com:
AESD_SENSEHATLIVE_SITE = git@github.com:cu-ecen-aeld/final-project-emma-harper.git
AESD_SENSEHATLIVE_SITE_METHOD = git
AESD_SENSEHATLIVE_GIT_SUBMODULES = YES


define AESD_ASENSEHATLIVE_INSTALL_TARGET_CMDS
	$(INSTALL) -d 0755 $(@D)/sensehatlive/ $(TARGET_DIR)/root/sensehatlilve/
	$(INSTALL) -m 0755 $(@D)/sensehatlive/* $(TARGET_DIR)/root/sensehatlilve/
endef

$(eval $(generic-package))
