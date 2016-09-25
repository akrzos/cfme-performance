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
		     zeromq3-devel \
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
                     openssl-devel

if [[ ! -d .cfme_perf ]]; then
    virtualenv -p python2 .cfme_perf
fi

echo "export PYTHONPATH='`pwd`'" | tee -a ./.cfme_perf/bin/activate
echo "export PYTHONDONTWRITEBYTECODE=yes" | tee -a ./.cfme_perf/bin/activate

. ./.cfme_perf/bin/activate

PYCURL_SSL_LIBRARY=nss pip install -Ur ./requirements.txt

echo "Run '. ./.cfme_perf/bin/activate' to load the virtualenv"
