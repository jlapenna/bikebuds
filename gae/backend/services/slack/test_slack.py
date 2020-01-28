# Copyright 2020 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json
import mock
import re
import unittest

from google.cloud.datastore.entity import Entity

from stravalib.model import Athlete, Map, Route

from services.slack import slack
from shared import ds_util
from shared import responses


class MainTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    @mock.patch('shared.slack_util.slack_client.chat_unfurl')
    @mock.patch('services.slack.slack.ClientWrapper')
    @mock.patch('shared.ds_util.client.get')
    def test_route_link(
        self, ds_util_client_get_mock, ClientWrapperMock, chat_unfurl_mock
    ):
        service = Entity(ds_util.client.key('Service', 'strava'))
        service['credentials'] = {'access_token': 'validrefreshtoken'}
        ds_util_client_get_mock.return_value = service

        client_mock = mock.Mock()
        client_mock.get_route.side_effect = route_generator
        ClientWrapperMock.return_value = client_mock

        chat_unfurl_mock.return_value = {'ok': True}

        event = json.loads(
            """
            {
               "event_id" : "EvSFJZPZGA",
               "token" : "unYFPYx2dZIR4Eb2MwfabpoI",
               "authed_users" : [
                  "USR4L7ZGW"
               ],
               "event_time" : 1579378856,
               "type" : "event_callback",
               "event" : {
                  "channel" : "CL2QA9X1C",
                  "links" : [
                     {
                        "domain" : "strava.com",
                        "url" : "https://www.strava.com/routes/10285651"
                     }
                  ],
                  "user" : "UL2NGJARL",
                  "message_ts" : "1579378855.001300",
                  "type" : "link_shared"
               },
               "team_id" : "TL2DVHG3H",
               "api_app_id" : "AKU8ZGJG1"
            }
        """
        )
        result = slack.process_slack_event(event)

        chat_unfurl_mock.assert_called_once()
        self.assertEqual(result, responses.OK)

    @mock.patch('shared.slack_util.slack_client.chat_unfurl')
    @mock.patch('shared.services.strava.client.ClientWrapper')
    @mock.patch('shared.ds_util.client.query')
    @mock.patch('shared.ds_util.client.get')
    def test_activity_link(
        self,
        ds_util_client_get_mock,
        ds_util_client_query_mock,
        ClientWrapperMock,
        chat_unfurl_mock,
    ):
        service = Entity(ds_util.client.key('Service', 'strava'))
        service['credentials'] = {'access_token': 'validrefreshtoken'}
        ds_util_client_get_mock.return_value = service

        query_mock = mock.Mock()
        query_mock.add_filter.return_value = None
        query_mock.fetch.return_value = [activity_entity_for_test(3046711547)]
        ds_util_client_query_mock.return_value = query_mock

        chat_unfurl_mock.return_value = {'ok': True}

        event = json.loads(
            """
            {
               "event_id" : "EvSFJZPZGA",
               "token" : "unYFPYx2dZIR4Eb2MwfabpoI",
               "authed_users" : [
                  "USR4L7ZGW"
               ],
               "event_time" : 1579378856,
               "type" : "event_callback",
               "event" : {
                  "channel" : "CL2QA9X1C",
                  "links" : [
                     {
                        "domain" : "strava.com",
                        "url" : "https://www.strava.com/activities/3046711547"
                     }
                  ],
                  "user" : "UL2NGJARL",
                  "message_ts" : "1579378855.001300",
                  "type" : "link_shared"
               },
               "team_id" : "TL2DVHG3H",
               "api_app_id" : "AKU8ZGJG1"
            }
        """
        )
        result = slack.process_slack_event(event)

        chat_unfurl_mock.assert_called_once()
        self.assertEqual(result, responses.OK)

    @mock.patch('shared.slack_util.slack_client.chat_unfurl')
    @mock.patch('shared.services.strava.client.ClientWrapper')
    @mock.patch('shared.ds_util.client.query')
    @mock.patch('shared.ds_util.client.get')
    def test_activity_link_unknown(
        self,
        ds_util_client_get_mock,
        ds_util_client_query_mock,
        ClientWrapperMock,
        chat_unfurl_mock,
    ):
        service = Entity(ds_util.client.key('Service', 'strava'))
        service['credentials'] = {'access_token': 'validrefreshtoken'}
        ds_util_client_get_mock.return_value = service

        query_mock = mock.Mock()
        query_mock.add_filter.return_value = None
        query_mock.fetch.return_value = []
        ds_util_client_query_mock.return_value = query_mock

        chat_unfurl_mock.return_value = {'ok': True}

        event = json.loads(
            """
            {
               "event_id" : "EvSFJZPZGA",
               "token" : "unYFPYx2dZIR4Eb2MwfabpoI",
               "authed_users" : [
                  "USR4L7ZGW"
               ],
               "event_time" : 1579378856,
               "type" : "event_callback",
               "event" : {
                  "channel" : "CL2QA9X1C",
                  "links" : [
                     {
                        "domain" : "strava.com",
                        "url" : "https://www.strava.com/activities/3046711547"
                     }
                  ],
                  "user" : "UL2NGJARL",
                  "message_ts" : "1579378855.001300",
                  "type" : "link_shared"
               },
               "team_id" : "TL2DVHG3H",
               "api_app_id" : "AKU8ZGJG1"
            }
        """
        )
        result = slack.process_slack_event(event)

        chat_unfurl_mock.assert_not_called()
        self.assertEqual(result, responses.OK)

    def test_generate_url(self):
        route = route_for_test()
        # Strip out the key params to avoid deailing with it in the expected url.
        url = re.sub(r'key=.*?&', '', slack._generate_url(route))
        expected_url = EXPECTED_URL
        self.assertEqual(url, expected_url)

    def test_route_block(self):
        route = route_for_test()
        block = slack._route_block(
            {'url': 'https://www.strava.com/routes/10285651'}, route
        )
        self.assertTrue(block)

    def test_activity_block(self):
        activity = activity_entity_for_test(11111)
        block = slack._activity_block(
            {'url': 'https://www.strava.com/activities/11111'}, activity
        )
        self.assertTrue(block)

    def test_activity_block_with_primary_photo(self):
        activity = activity_entity_for_test(11111, with_photo=True)
        block = slack._activity_block(
            {'url': 'https://www.strava.com/activities/11111'}, activity
        )
        self.assertTrue(block)


def route_for_test():
    route = Entity(ds_util.client.key('Route', 10285651))
    route.update(
        {
            'id': 10285651,
            'timestamp': datetime.datetime.fromtimestamp(1503517240),
            'description': 'East Peak, Reverse Alpine, Gestalt Haus',
            'distance': 98353.19420993332,
            'elevation_gain': 1829.1980834963906,
            'name': 'The  ̶N̶i̶g̶h̶t̶ Day is  ̶D̶a̶r̶k̶ Mostly Cloudy, Probably and Full of  ̶T̶e̶r̶r̶o̶r̶ Pickles',
            'athlete': {
                'id': 1021133,
                'firstname': 'Rayco, A Shopping Cart 🛒',
                'lastname': 'of All the Feelings',
            },
            'map': {'id': 10285651, 'summary_polyline': SUMMARY_POLYLINE},
        }
    )
    return route


def activity_entity_for_test(activity_id, with_photo=False):
    activity = Entity(ds_util.client.key('Activity', activity_id))
    activity['name'] = 'Activity ' + str(activity_id)
    activity['id'] = activity_id
    activity['description'] = 'Description: ' + str(activity_id)
    activity['distance'] = 10
    activity['moving_time'] = 200
    activity['elapsed_time'] = 100
    activity['total_elevation_gain'] = 300
    activity['start_date'] = datetime.datetime.fromtimestamp(1503517240)
    activity['athlete'] = Entity(ds_util.client.key('Athlete', 111))
    activity['athlete']['id'] = 111
    activity['athlete']['firstname'] = 'ActivityFirstName'
    activity['athlete']['lastname'] = 'ActivityLastName'
    activity['map'] = Entity(ds_util.client.key('Map', 111))
    activity['map']['summary_polyline'] = SUMMARY_POLYLINE
    if with_photo:
        activity['photos'] = {
            'primary': {
                'id': 1234,
                'unique_id': 'a807-23q4-23',
                'urls': {
                    '600': 'https://12341234.cloudfront.net/yw7_-ahaahahahahaha_E-576x768.jpg',
                    '100': 'https://12341234.cloudfront.net/yw7_-ahashdhaahashahah_E-96x128.jpg',
                },
            }
        }
    return activity


def route_generator(route_id):
    route = Route()
    route.name = 'Route' + str(route_id)
    route.id = route_id
    route.timestamp = 1503517240
    route.distance = 98353.19420993332
    route.elevation_gain = 1829.1980834963906
    route.athlete = Athlete()
    route.athlete.firstname = 'Rayco, A Shopping Cart 🛒'
    route.athlete.lastname = 'of All the Feelings'
    route.map = Map()
    route.map.id = 10285651
    route.map.summary_polyline = SUMMARY_POLYLINE
    return route


# The generated url will be quoted, we remove the key= param here so we don't
# have to deal with it when running unittests with a dev or prod config.
EXPECTED_URL = r'https://maps.googleapis.com/maps/api/staticmap?size=512x512&maptype=roadmap&path=enc%3AuaneFzjrjVsOb%40e%40%7BYqKb%40cDiFaC%5BJuHzCaOiIfGeIcB%7BIpFaEdHKvJgAzAo~AfFgAeL%7BEwEe%5EkIgFPoKuJsFl%40yJoC%7BTcNwFjB%7BFkD%7DA%60BgCqD%7BBhGcAsA~BjE_%40_AmIrDaeC~NiFhD_EtNcJxH%7DIyJkOuBuAiDUmQ%7DEiFkLnCmHwAwH~%40qCvCErI%7D%40%60%40cOIQsDaIqD%7BS%3F_J~E%7DG%7CKgTjo%40cBbZuHdQ_%5C%60%5EoV%7CNa_Bj%7CB%7DS~Ec%5Dfu%40wo%40%7Cu%40yG%60UgHdH%7CDnHx%40tI_BjEpAfHjDeHzB%7BM%7CEmAiC%7CBr%40dC%7DAdC%60ChCL%60CyBl%40yAbEhHeC%60AsIdBcB%60%40bLqHlQpA%60K~Nu%40jJ%60BnIyAnG%7BEnGTuB%7CDmKdE%7DK%7CSqHb%40aC%7CIbA%60D_GxRaGfFoGJuD%7CEgCpMoRfR%7DKvE_CvIuBbAcLpRcKdCxGxGxKxBNlGtIbBW%60ElIbIuBbQoEfHpAlCwOvNhLu%40aApDnBpArCdQbZrK%60J%60IaIbQkEpAj%40fFoFtLpDlGm%40pD~LERfBqOnCaCuCaCDgEcHcFDg%40eCgEaDkFxAwFeFeDcNaW%7BHiE%7BG_%40yFaKmGmDcIpAmLcCaG~%40mJuP%7D%40gIwNO%7DBlCeJ%7CH%7DN_CoAg%40gDsJo%40q%40sE%7BDuDhGoJXaRY%60RiGnJzDtDp%40rErJn%40f%40fD~BnA%7DH%7CNmCdJVpC~HbNtP%7C%40_AlJbC%60GqAlLzFbLrHlD%5ExFpDhGxWlIdDbNvFdF%7CEaBhFdEd%40bGzGdO%5DpRwGdIeDz%5C%7BG%7BDgHvJkKbE%7B%40%7CFaMEcHrFoErRgT%60e%40%5EnF_JjDsRrP_ZrNaKfXtAfK_AhFoGzRyC%60%40kCzDqDdAcG_BeD%60BfAcCfKuDl%40uEbCoAlAeEaAtB%7DEb%40i%40fC_%40aAfBkLzAiB%5ByGyBqBq%40%7BDjCeEnBqKiC%7BFxCkC%7C%40oE%7DDeHf%40_CeAyFl%40yHfGOpEsD%7BX%7CB_BwEwC%7D%40~A%7BDiB%7DEReG%7BEyAQqDuBQ%7DJdHuD%7BD_NjI_%40cGtByFwGNuB%7BB_A~EsF%7CBgBbGaDlA%7DBhHeJhBtCcJFsDgCeEfBgHiEiImEiB%7BHI%7BDoCwVhRz%40%7BKsBuCgD%5DgQjN%7CAqIxGsKjQqIgAyEyUs%40kFlEcIuBuDbI%7DFeHeG~FpAeHgAaFlEwDr%40yH%7DR%7DPlBiDiA%7DDZuJjC%7DBp%40mS%60CmEp%40_u%40aD_IuFuFcR%7BIkEQwGwJ%7DAsIaKqAmLiIqCkGiEmBdChA%5BxAZyAuCqA%60%40aKeBITiEnEeU~V_c%40pCiAdJiNCgJ~EkLfCk%40%60Ccb%40tEuHdg%40mJz%40zDpl%40gQaAgJlFwFfg%40cUxBiDtTeJpIi%40le%40y%7B%40zG%7BD%7CReXz%5DdFtJy%40nGmChDwI~YmXzK~JbAwChDwApIvAjAgH%7CHgAhByFKcEnBeCnIbGxFmChDpDnDRzAnDxDsBrAbEhNoAvCpDzGsGhIeCbUlJj%40wCeAkGfiA%7DIvLcElrAqkBnAgEl%40j%40dHqInOcHz%5C%7D%5EnIqQnAcXvT_s%40%7CG%7DK~I_FzS%3F%60IpDPrDbOH%7C%40a%40DsIpCwCvH_AlHvAjLoC%7CEhFTlQtAhD~GvCjFa%40%7CIxJbJyH~DuNhFiD%60eC_OlIsD%7CC%7CBnGOdA%7DDjCj%40cBw%40zBJl%40qBbZlOjJ~BlEw%40nKtJfFQd%5EjIzEvEfAdL%60b%40qAm%40m_%40&format=jpg'

# But the source polyline does not.
SUMMARY_POLYLINE = r'uaneFzjrjVsOb@e@{YqKb@cDiFaC[JuHzCaOiIfGeIcB{IpFaEdHKvJgAzAo~AfFgAeL{EwEe^kIgFPoKuJsFl@yJoC{TcNwFjB{FkD}A`BgCqD{BhGcAsA~BjE_@_AmIrDaeC~NiFhD_EtNcJxH}IyJkOuBuAiDUmQ}EiFkLnCmHwAwH~@qCvCErI}@`@cOIQsDaIqD{S?_J~E}G|KgTjo@cBbZuHdQ_\`^oV|Na_Bj|B}S~Ec]fu@wo@|u@yG`UgHdH|DnHx@tI_BjEpAfHjDeHzB{M|EmAiC|Br@dC}AdC`ChCL`CyBl@yAbEhHeC`AsIdBcB`@bLqHlQpA`K~Nu@jJ`BnIyAnG{EnGTuB|DmKdE}K|SqHb@aC|IbA`D_GxRaGfFoGJuD|EgCpMoRfR}KvE_CvIuBbAcLpRcKdCxGxGxKxBNlGtIbBW`ElIbIuBbQoEfHpAlCwOvNhLu@aApDnBpArCdQbZrK`J`IaIbQkEpAj@fFoFtLpDlGm@pD~LERfBqOnCaCuCaCDgEcHcFDg@eCgEaDkFxAwFeFeDcNaW{HiE{G_@yFaKmGmDcIpAmLcCaG~@mJuP}@gIwNO}BlCeJ|H}N_CoAg@gDsJo@q@sE{DuDhGoJXaRY`RiGnJzDtDp@rErJn@f@fD~BnA}H|NmCdJVpC~HbNtP|@_AlJbC`GqAlLzFbLrHlD^xFpDhGxWlIdDbNvFdF|EaBhFdEd@bGzGdO]pRwGdIeDz\{G{DgHvJkKbE{@|FaMEcHrFoErRgT`e@^nF_JjDsRrP_ZrNaKfXtAfK_AhFoGzRyC`@kCzDqDdAcG_BeD`BfAcCfKuDl@uEbCoAlAeEaAtB}Eb@i@fC_@aAfBkLzAiB[yGyBqBq@{DjCeEnBqKiC{FxCkC|@oE}DeHf@_CeAyFl@yHfGOpEsD{X|B_BwEwC}@~A{DiB}EReG{EyAQqDuBQ}JdHuD{D_NjI_@cGtByFwGNuB{B_A~EsF|BgBbGaDlA}BhHeJhBtCcJFsDgCeEfBgHiEiImEiB{HI{DoCwVhRz@{KsBuCgD]gQjN|AqIxGsKjQqIgAyEyUs@kFlEcIuBuDbI}FeHeG~FpAeHgAaFlEwDr@yH}R}PlBiDiA}DZuJjC}Bp@mS`CmEp@_u@aD_IuFuFcR{IkEQwGwJ}AsIaKqAmLiIqCkGiEmBdChA[xAZyAuCqA`@aKeBITiEnEeU~V_c@pCiAdJiNCgJ~EkLfCk@`Ccb@tEuHdg@mJz@zDpl@gQaAgJlFwFfg@cUxBiDtTeJpIi@le@y{@zG{D|ReXz]dFtJy@nGmChDwI~YmXzK~JbAwChDwApIvAjAgH|HgAhByFKcEnBeCnIbGxFmChDpDnDRzAnDxDsBrAbEhNoAvCpDzGsGhIeCbUlJj@wCeAkGfiA}IvLcElrAqkBnAgEl@j@dHqInOcHz\}^nIqQnAcXvT_s@|G}K~I_FzS?`IpDPrDbOH|@a@DsIpCwCvH_AlHvAjLoC|EhFTlQtAhD~GvCjFa@|IxJbJyH~DuNhFiD`eC_OlIsD|C|BnGOdA}DjCj@cBw@zBJl@qBbZlOjJ~BlEw@nKtJfFQd^jIzEvEfAdL`b@qAm@m_@'
