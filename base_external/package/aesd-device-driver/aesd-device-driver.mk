
##############################################################
#
# AESD-DEVICE-DRIVER
#
##############################################################

# Fill up the contents below in order to reference your assignment 3 git contents
AESD_DEVICE_DRIVER_VERSION = 56dd677e070272f7ec2bd779d98825a5b7aa8369
# Note: Be sure to reference the *ssh* repository URL here (not https) to work properly
# with ssh keys and the automated build/test system.
# Your site should start with git@github.com:
AESD_DEVICE_DRIVER_SITE = git@github.com:cu-ecen-aeld/assignments-3-and-later-kejo1166.git
AESD_DEVICE_DRIVER_SITE_METHOD = git
AESD_DEVICE_DRIVER_GIT_SUBMODULES = YES

AESD_DEVICE_DRIVER_MODULE_SUBDIRS = aesd-char-driver
AESD_DEVICE_DRIVER_MODULE_MAKE_OPTS = KVERSION=$(LINUX_VERSION_PROBED)

# Added your writer, finder and finder-test utilities/scripts to the installation steps below
# Added aesdsocket bin and system v script
define AESD_DEVICE_DRIVER_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 $(@D)/aesd-char-driver/aesdchar_load $(TARGET_DIR)/usr/bin
	$(INSTALL) -m 0755 $(@D)/aesd-char-driver/aesdchar_unload $(TARGET_DIR)/usr/bin
	$(INSTALL) -m 0755 $(@D)/assignment-autotest/test/assignment8/* $(TARGET_DIR)/usr/bin
endef

$(eval $(kernel-module))
$(eval $(generic-package))
