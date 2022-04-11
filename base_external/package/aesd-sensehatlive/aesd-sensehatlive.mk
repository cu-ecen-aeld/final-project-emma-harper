
##############################################################
#
# AESD-SENSEHATLIVE
#
##############################################################

#TODO: Fill up the contents below in order to reference your assignment 3 git contents
AESD_SENSEHATLIVE_VERSION = 'bbbbaedd481eaa70bba2fa12da1179cba2bc3c85'
# Note: Be sure to reference the *ssh* repository URL here (not https) to work properly
# with ssh keys and the automated build/test system.
# Your site should start with git@github.com:
AESD_SENSEHATLIVE_SITE = 'git@github.com:cu-ecen-aeld/final-project-emma-harper.git'
AESD_SENSEHATLIVE_SITE_METHOD = git
AESD_SENSEHATLIVE_GIT_SUBMODULES = YES

AESD_SENSEHATLIVE_GIT_SUBDIR = sensehatlive 

define AESD_SENSEHATLIVE_INSTALL_TARGET_CMDS
	$(INSTALL) -d 0755 $(@D)/sensehatlive/ $(TARGET_DIR)/opt/sensehatlilve/

	$(INSTALL) -m 0755 $(@D)/sensehatlive//basebroker.py $(TARGET_DIR)/opt/sensehatlilve/basebroker.py
	$(INSTALL) -m 0755 $(@D)/sensehatlive//cloud4Rpi.py $(TARGET_DIR)/opt/sensehatlilve/cloud4Rpi.py
	$(INSTALL) -m 0755 $(@D)/sensehatlive//main.py $(TARGET_DIR)/opt/sensehatlilve/main.py
	$(INSTALL) -m 0755 $(@D)/sensehatlive//rabbitmq.py $(TARGET_DIR)/opt/sensehatlilve/rabbitmq.py
	$(INSTALL) -m 0755 $(@D)/sensehatlive//sensehathandler.py $(TARGET_DIR)/opt/sensehatlilve/sensehathandler.py
	$(INSTALL) -m 0755 $(@D)/sensehatlive//config.json $(TARGET_DIR)/opt/sensehatlilve/config.json

	$(INSTALL) -d 0755 $(@D)/sensehatlive/sensehatlive/log $(TARGET_DIR)/opt/sensehatlilve/log/
	$(INSTALL) -m 0755 $(@D)/sensehatlive/sensehatlive/log/logger.py $(TARGET_DIR)/opt/sensehatlilve/log/logger.py

	$(INSTALL) -d 0755 $(@D)/sensehatlive/lib $(TARGET_DIR)/opt/sensehatlilve/lib/
	$(INSTALL) -d 0755 $(@D)/sensehatlive/lib/logutils $(TARGET_DIR)/opt/sensehatlilve/lib/logutils/
	$(INSTALL) -m 0755 $(@D)/sensehatlive/lib/logutils/* $(TARGET_DIR)/opt/sensehatlilve/lib/logutils/

	$(INSTALL) -m 0755 $(@D)/sensehatlive/lib/RTIMULib-7.2.1.egg-info $(TARGET_DIR)/opt/sensehatlilve/lib/RTIMULib-7.2.1.egg-info

endef

$(eval $(generic-package))
