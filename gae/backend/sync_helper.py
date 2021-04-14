# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from shared.exceptions import SyncException


def do(worker, work_key=None, method='sync'):
    work_name = worker.__class__.__name__
    try:
        logging.debug('Worker starting: %s/%s', work_name, work_key)
        getattr(worker, method)()  # Dynamically run the provided method.
        logging.info('Worker completed: %s/%s', work_name, work_key)
    except Exception as e:
        logging.exception('Worker failed: %s/%s', work_name, work_key)
        raise SyncException(
            'Worker failed: %s/%s: %s' % (work_name, work_key, e)
        ) from e
