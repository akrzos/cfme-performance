#!/usr/bin/env bash

if hash dnf;
then
  YUM=dnf
else
  YUM=yum
fi

sudo $YUM install -y numpy \
                     python-virtualenv \
                     gcc \
                     postgresql-devel \
                     libxml2-devel \
                     libxslt-devel \
                     libcurl-devel \
                     redhat-rpm-config \
                     gcc-c++ \
                     python-virtualenv \
                     libffi-devel \
                     libpng \
                     libpng-devel \
                     freetype-devel \
                     freetype-devel \
                     openssl-devel

echo "### Creating Virtual Environment: .cfme_perf"
virtualenv .cfme_perf

echo "### Activating .cfme_per"
echo "export PYTHONPATH='`pwd`'" | tee -a ./.cfme_perf/bin/activate
echo "export PYTHONDONTWRITEBYTECODE=yes" | tee -a ./.cfme_perf/bin/activate
. ./.cfme_perf/bin/activate

echo "### Upgrading pip"
pip install --upgrade pip

echo "### Installing Requirements"
PYCURL_SSL_LIBRARY=nss pip install -Ur ./requirements.txt

echo "Run '. ./.cfme_perf/bin/activate' to load the virtualenv"

exit 0
