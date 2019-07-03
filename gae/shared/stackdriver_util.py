# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os

from google.auth.exceptions import DefaultCredentialsError

def start():
    if os.getenv('GAE_ENV', '').startswith('standard'):
        logging.info('Enabling stackdriver features.')
        try:
            import googleclouddebugger
            googleclouddebugger.enable()
            logging.debug('Enabled Cloud Debugger')
        except ImportError:
            logging.exception('Unable to import Cloud Debugger')
        except DefaultCredentialsError:
            logging.exception('Unable to enable Cloud Debugger, no creds')
        try:
            import googlecloudprofiler
            googlecloudprofiler.start(verbose=0)
            logging.debug('Enabled Cloud Profiler')
        except ImportError:
            logging.exception('Unable to import Cloud Profiler')
        except DefaultCredentialsError:
            logging.exception('Unable to enable Cloud Profiler, no creds')
    else:
        logging.warn('Not enabling stackdriver features on %s',
                     os.getenv('GAE_ENV', ''))
