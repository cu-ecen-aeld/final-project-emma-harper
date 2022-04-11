################################################################################
#
# cloud4rpi
#
################################################################################

CLOUD4RPI_VERSION = 1.1.2
CLOUD4RPI_SOURCE = cloud4rpi-$(CLOUD4RPI_VERSION).tar.gz
CLOUD4RPI_SITE = https://files.pythonhosted.org/packages/05/de/15c36db072a8edccea95c1ab3c0f3ce46ab8a05840ca33b1d2dff44eab6f
CLOUD4RPI_LICENSE = BSD
CLOUD4RPI_LICENSE_FILES = LICENSE
CLOUD4RPI_SETUP_TYPE = distutils

$(eval $(python-package))