#!/usr/bin/env bash

if hash dnf;
then
  YUM=dnf
else
  YUM=yum
fi

sudo $YUM install -y python-virtualenv gcc postgresql-devel libxml2-devel libxslt-devel zeromq3-devel libcurl-devel redhat-rpm-config  gcc-c++  freetype-devel libffi-dev
virtualenv .cfme_perf
echo "export PYTHONPATH='`pwd`'" | tee -a ./.cfme_perf/bin/activate
echo "export PYTHONDONTWRITEBYTECODE=yes" | tee -a ./.cfme_perf/bin/activate

. ./.cfme_perf/bin/activate
PYCURL_SSL_LIBRARY=nss pip install -Ur ./requirements.txt
echo "Run '. ./.cfme_perf/bin/activate' to load the virtualenv"

