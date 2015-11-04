#!/usr/bin/ipython3
# Copyright 2015 ETH Zurich
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
:mod:`trust_store` --- Storage and management of trust objects (TRCs and certs).
================================================================================
"""
# Stdlib
from collections import defaultdict
import glob
import logging
import re

# SCION
from lib.crypto.certificate import CertificateChain, TRC
from lib.util import CERT_DIR


class TrustStore(object):
    """
    Trust Store class.
    """

    def __init__(self, conf_dir):
        self._dir = "%s/%s" % (conf_dir, CERT_DIR)
        self._certs = defaultdict(list)
        self._trcs = defaultdict(list)
        self._init_trcs()
        self._init_certs()
        logging.info(self._trcs)
        logging.info(self._certs)

    def _init_trcs(self):
        for path in glob.glob("%s/*.trc" % self._dir):
            # isd, ver = re.findall("\d+", path)[-2:]
            f = open(path)
            trc_raw = f.read()
            f.close()
            # trc = TRC(trc_raw)
            self.add_trc(TRC(trc_raw))
            logging.info("Loaded: %s" % path)

    def _init_certs(self):
        for path in glob.glob("%s/*.crt" % self._dir):
            isd, ad, ver = map(int, re.findall("\d+", path)[-3:])
            f = open(path)
            cert_raw = f.read()
            f.close()
            self.add_cert(isd, ad, ver, CertificateChain(cert_raw))
            logging.info("Loaded: %s" % path)

    def get_trc(self, isd, version=None):
        if not self._trcs[isd]:
            return None
        if version is None:  # Return the most recent TRC.
            _, trc = sorted(self._trcs[isd])[-1]
            return trc
        else:  # Try to find a TRC with given version.
            for ver, trc in self._trcs[isd]:
                if version == ver:
                    return trc
        return None

    def get_cert(self, isd, ad, version=None):
        if not self._certs[(isd, ad)]:
            return None
        if version is None:  # Return the most recent cert.
            _, cert = sorted(self._certs[(isd, ad)])[-1]
            return cert
        else:  # Try to find a cert with given version.
            for ver, cert in self._certs[(isd, ad)]:
                if version == ver:
                    return cert

    def add_trc(self, trc):
        isd = trc.isd_id
        version = trc.version
        for ver, _ in self._trcs[isd]:
            if version == ver:
                return
        self._trcs[isd].append((version, trc))

    # FIXME(psz): Inconsistent API for now
    def add_cert(self, isd, ad, version, cert):
        for ver, _ in self._certs[(isd, ad)]:
            if version == ver:
                return
        self._certs[(isd, ad)].append((version, cert))
