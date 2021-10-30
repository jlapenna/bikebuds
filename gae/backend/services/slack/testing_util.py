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
import mock

from google.cloud.datastore.entity import Entity

from stravalib.model import Athlete, Map, Route

from shared import ds_util


def track_finished_for_test() -> Entity:
    track = Entity(ds_util.client.key('Track', 10285651))
    track.update(
        {
            "info": {
                "gcAvatar": "https://s3.amazonaws.com/garmin-connect-prod/profile_images/avatar.png",
                "session": {
                    "end": "2021-04-11T20:28:36.000Z",
                    "position": {
                        "lat": 37.77,
                        "locationName": "San Francisco",
                        "lon": -122.44,
                    },
                    "publisher": {
                        "connectUserProfileId": 123456,
                        "identifier": "PUBLISHERIDPUBLISHERID",
                        "nickname": "Joe LaPenna",
                        "trackerId": "UA69B7XL",
                        "type": "WEARABLE",
                    },
                    "publisherState": "ACTIVE",
                    "sessionId": "session-session",
                    "sessionName": "04/11/21",
                    "start": "2021-04-11T15:00:09.000Z",
                    "subscriber": {
                        "identifier": "jlapenna.test.1@gmail.com",
                        "type": "EMAIL",
                    },
                    "subscriberState": "ACTIVE",
                    "token": "1618153228",
                    "url": "https://livetrack.garmin.com/session/session-session/token/TOKENTOKEN",
                    "userDisplayName": "Joe LaPenna",
                    "viewable": "2021-04-11T20:28:36.000Z",
                },
                "shortened": False,
                "unitId": 3996815102,
                "viewable": False,
            },
            "start": datetime.datetime(
                2021, 4, 11, 15, 00, tzinfo=datetime.timezone.utc
            ),
            "end": datetime.datetime(2021, 4, 11, 20, 28, tzinfo=datetime.timezone.utc),
            "status": 4,  # FINISHED
            "url": "https://livetrack.garmin.com/session/session-session/token/TOKENTOKEN",
            "url_info": {"session": "session-session", "token": "TOKENTOKEN"},
        }
    )
    return track


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


def set_mockurlopen(mock_urlopen):
    cm = mock.MagicMock()
    cm.getcode.return_value = 200
    cm.read.return_value = MOCK_STRAVA_ACTIVITY_LINK_CONTENTS
    cm.__enter__.return_value = cm
    mock_urlopen.return_value = cm


# The generated url will be quoted, we remove the key= param here so we don't
# have to deal with it when running unittests with a dev or prod config.
EXPECTED_URL = r'https://maps.googleapis.com/maps/api/staticmap?size=512x512&maptype=roadmap&format=jpg&path=enc%3AuaneFzjrjVsOb%40e%40%7BYqKb%40cDiFaC%5BJuHzCaOiIfGeIcB%7BIpFaEdHKvJgAzAo~AfFgAeL%7BEwEe%5EkIgFPoKuJsFl%40yJoC%7BTcNwFjB%7BFkD%7DA%60BgCqD%7BBhGcAsA~BjE_%40_AmIrDaeC~NiFhD_EtNcJxH%7DIyJkOuBuAiDUmQ%7DEiFkLnCmHwAwH~%40qCvCErI%7D%40%60%40cOIQsDaIqD%7BS%3F_J~E%7DG%7CKgTjo%40cBbZuHdQ_%5C%60%5EoV%7CNa_Bj%7CB%7DS~Ec%5Dfu%40wo%40%7Cu%40yG%60UgHdH%7CDnHx%40tI_BjEpAfHjDeHzB%7BM%7CEmAiC%7CBr%40dC%7DAdC%60ChCL%60CyBl%40yAbEhHeC%60AsIdBcB%60%40bLqHlQpA%60K~Nu%40jJ%60BnIyAnG%7BEnGTuB%7CDmKdE%7DK%7CSqHb%40aC%7CIbA%60D_GxRaGfFoGJuD%7CEgCpMoRfR%7DKvE_CvIuBbAcLpRcKdCxGxGxKxBNlGtIbBW%60ElIbIuBbQoEfHpAlCwOvNhLu%40aApDnBpArCdQbZrK%60J%60IaIbQkEpAj%40fFoFtLpDlGm%40pD~LERfBqOnCaCuCaCDgEcHcFDg%40eCgEaDkFxAwFeFeDcNaW%7BHiE%7BG_%40yFaKmGmDcIpAmLcCaG~%40mJuP%7D%40gIwNO%7DBlCeJ%7CH%7DN_CoAg%40gDsJo%40q%40sE%7BDuDhGoJXaRY%60RiGnJzDtDp%40rErJn%40f%40fD~BnA%7DH%7CNmCdJVpC~HbNtP%7C%40_AlJbC%60GqAlLzFbLrHlD%5ExFpDhGxWlIdDbNvFdF%7CEaBhFdEd%40bGzGdO%5DpRwGdIeDz%5C%7BG%7BDgHvJkKbE%7B%40%7CFaMEcHrFoErRgT%60e%40%5EnF_JjDsRrP_ZrNaKfXtAfK_AhFoGzRyC%60%40kCzDqDdAcG_BeD%60BfAcCfKuDl%40uEbCoAlAeEaAtB%7DEb%40i%40fC_%40aAfBkLzAiB%5ByGyBqBq%40%7BDjCeEnBqKiC%7BFxCkC%7C%40oE%7DDeHf%40_CeAyFl%40yHfGOpEsD%7BX%7CB_BwEwC%7D%40~A%7BDiB%7DEReG%7BEyAQqDuBQ%7DJdHuD%7BD_NjI_%40cGtByFwGNuB%7BB_A~EsF%7CBgBbGaDlA%7DBhHeJhBtCcJFsDgCeEfBgHiEiImEiB%7BHI%7BDoCwVhRz%40%7BKsBuCgD%5DgQjN%7CAqIxGsKjQqIgAyEyUs%40kFlEcIuBuDbI%7DFeHeG~FpAeHgAaFlEwDr%40yH%7DR%7DPlBiDiA%7DDZuJjC%7DBp%40mS%60CmEp%40_u%40aD_IuFuFcR%7BIkEQwGwJ%7DAsIaKqAmLiIqCkGiEmBdChA%5BxAZyAuCqA%60%40aKeBITiEnEeU~V_c%40pCiAdJiNCgJ~EkLfCk%40%60Ccb%40tEuHdg%40mJz%40zDpl%40gQaAgJlFwFfg%40cUxBiDtTeJpIi%40le%40y%7B%40zG%7BD%7CReXz%5DdFtJy%40nGmChDwI~YmXzK~JbAwChDwApIvAjAgH%7CHgAhByFKcEnBeCnIbGxFmChDpDnDRzAnDxDsBrAbEhNoAvCpDzGsGhIeCbUlJj%40wCeAkGfiA%7DIvLcElrAqkBnAgEl%40j%40dHqInOcHz%5C%7D%5EnIqQnAcXvT_s%40%7CG%7DK~I_FzS%3F%60IpDPrDbOH%7C%40a%40DsIpCwCvH_AlHvAjLoC%7CEhFTlQtAhD~GvCjFa%40%7CIxJbJyH~DuNhFiD%60eC_OlIsD%7CC%7CBnGOdA%7DDjCj%40cBw%40zBJl%40qBbZlOjJ~BlEw%40nKtJfFQd%5EjIzEvEfAdL%60b%40qAm%40m_%40'

# But the source polyline does not.
SUMMARY_POLYLINE = r'uaneFzjrjVsOb@e@{YqKb@cDiFaC[JuHzCaOiIfGeIcB{IpFaEdHKvJgAzAo~AfFgAeL{EwEe^kIgFPoKuJsFl@yJoC{TcNwFjB{FkD}A`BgCqD{BhGcAsA~BjE_@_AmIrDaeC~NiFhD_EtNcJxH}IyJkOuBuAiDUmQ}EiFkLnCmHwAwH~@qCvCErI}@`@cOIQsDaIqD{S?_J~E}G|KgTjo@cBbZuHdQ_\`^oV|Na_Bj|B}S~Ec]fu@wo@|u@yG`UgHdH|DnHx@tI_BjEpAfHjDeHzB{M|EmAiC|Br@dC}AdC`ChCL`CyBl@yAbEhHeC`AsIdBcB`@bLqHlQpA`K~Nu@jJ`BnIyAnG{EnGTuB|DmKdE}K|SqHb@aC|IbA`D_GxRaGfFoGJuD|EgCpMoRfR}KvE_CvIuBbAcLpRcKdCxGxGxKxBNlGtIbBW`ElIbIuBbQoEfHpAlCwOvNhLu@aApDnBpArCdQbZrK`J`IaIbQkEpAj@fFoFtLpDlGm@pD~LERfBqOnCaCuCaCDgEcHcFDg@eCgEaDkFxAwFeFeDcNaW{HiE{G_@yFaKmGmDcIpAmLcCaG~@mJuP}@gIwNO}BlCeJ|H}N_CoAg@gDsJo@q@sE{DuDhGoJXaRY`RiGnJzDtDp@rErJn@f@fD~BnA}H|NmCdJVpC~HbNtP|@_AlJbC`GqAlLzFbLrHlD^xFpDhGxWlIdDbNvFdF|EaBhFdEd@bGzGdO]pRwGdIeDz\{G{DgHvJkKbE{@|FaMEcHrFoErRgT`e@^nF_JjDsRrP_ZrNaKfXtAfK_AhFoGzRyC`@kCzDqDdAcG_BeD`BfAcCfKuDl@uEbCoAlAeEaAtB}Eb@i@fC_@aAfBkLzAiB[yGyBqBq@{DjCeEnBqKiC{FxCkC|@oE}DeHf@_CeAyFl@yHfGOpEsD{X|B_BwEwC}@~A{DiB}EReG{EyAQqDuBQ}JdHuD{D_NjI_@cGtByFwGNuB{B_A~EsF|BgBbGaDlA}BhHeJhBtCcJFsDgCeEfBgHiEiImEiB{HI{DoCwVhRz@{KsBuCgD]gQjN|AqIxGsKjQqIgAyEyUs@kFlEcIuBuDbI}FeHeG~FpAeHgAaFlEwDr@yH}R}PlBiDiA}DZuJjC}Bp@mS`CmEp@_u@aD_IuFuFcR{IkEQwGwJ}AsIaKqAmLiIqCkGiEmBdChA[xAZyAuCqA`@aKeBITiEnEeU~V_c@pCiAdJiNCgJ~EkLfCk@`Ccb@tEuHdg@mJz@zDpl@gQaAgJlFwFfg@cUxBiDtTeJpIi@le@y{@zG{D|ReXz]dFtJy@nGmChDwI~YmXzK~JbAwChDwApIvAjAgH|HgAhByFKcEnBeCnIbGxFmChDpDnDRzAnDxDsBrAbEhNoAvCpDzGsGhIeCbUlJj@wCeAkGfiA}IvLcElrAqkBnAgEl@j@dHqInOcHz\}^nIqQnAcXvT_s@|G}K~I_FzS?`IpDPrDbOH|@a@DsIpCwCvH_AlHvAjLoC|EhFTlQtAhD~GvCjFa@|IxJbJyH~DuNhFiD`eC_OlIsD|C|BnGOdA}DjCj@cBw@zBJl@qBbZlOjJ~BlEw@nKtJfFQd^jIzEvEfAdL`b@qAm@m_@'

MOCK_STRAVA_APP_LINK_CONTENTS = """
<!DOCTYPE html>
<html>
    <body>
        <script type="text/javascript">
        function unescapeHtml(escaped_str) {
...
            window.onload = function() {
                document.getElementById("l").src = validate("nullopen?link_click_id=link-759892900544534247");
                window.setTimeout(function() {
                    if (!hasURI) {
                        window.top.location = validate("https://www.strava.com/activities/3123195350/shareable_images/image?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOm51bGwsInR5cGUiOiJtYXAiLCJ0b2tlbiI6IjIyZGNlNGY5MmM2ZTYzY2MwMjg2NzA0MGMyNmM0NTA1MzcxZTdkN2UiLCJ3aWR0aCI6MTA4MCwiaGVpZ2h0IjoyMjM2LCJpbWFnZV93aWR0aCI6bnVsbCwiaW1hZ2VfaGVpZ2h0IjpudWxsLCJ1bmlxdWVfaWQiOm51bGx9.LUnrspUpHFkz72yBMtZ5tu3VhQ8KTKSYEXuq-Elb2w4&amp;hl=en-US&amp;utm_source=UNKNOWN&amp;utm_source=android_share&amp;utm_medium=referral&amp;utm_medium=social&amp;share_sig=AQZ23XKT1582410811&amp;_branch_match_id=link-759892900544534247");
...
    </body>
</html>
"""

MOCK_STRAVA_ACTIVITY_LINK_CONTENTS = """
<!-- Orion-App Layout -->
<!DOCTYPE html>
<html class='logged-out responsive feed3p0 old-login strava-orion responsive' dir='ltr' lang='en-US' xmlns:fb='http://www.facebook.com/2008/fbml' xmlns:og='http://opengraphprotocol.org/schema/' xmlns='http://www.w3.org/TR/html5'>
<!--
layout orion app
-->
<head>
<meta charset='UTF-8'>
<meta content='width = device-width, initial-scale = 1, maximum-scale = 1' name='viewport'>

<link href='https://www.strava.com/activities/3123195350' rel='canonical'>

<title>48.3 mi Ride Activity on February 22, 2020 by Joe L. on Strava</title>
<link href='https://www.strava.com/activities/3123195350' rel='canonical'>
<meta content='284597785309' property='fb:app_id'>
<meta content='Strava' property='og:site_name'>
<meta content='strava://activities/3123195350' property='al:ios:url'>
<meta content='Strava' property='al:ios:app_name'>
<meta content='426826309' property='al:ios:app_store_id'>
<meta content='strava://activities/3123195350' property='al:android:url'>
<meta content='Strava' property='al:android:app_name'>
<meta content='com.strava' property='al:android:package'>
<meta content='fitness.course' property='og:type'>
<meta content='Choo choo - Joe LaPenna&#39;s 48.3 mi bike ride' property='og:title'>
<meta content='' property='og:description'>
<meta content='https://www.strava.com/activities/3123195350' property='og:url'>
<meta content='https://dgtzuqphqg23d.cloudfront.net/q1ixMRMczt82TG8EZDC1bvQioVWD8a-pJsadS0C14Ro-768x575.jpg' property='og:image'>
<meta content='575' property='og:image:height'>
<meta content='768' property='og:image:width'>
<meta content='4084' property='fitness:custom_unit_energy:value'>
<meta content='https://www.strava.com/activities/facebook_open_graph_unit_elevation_gain' property='fitness:custom_unit_energy:units'>
<meta content='48.3' property='fitness:distance:value'>
<meta content='mi' property='fitness:distance:units'>
<meta content='13545' property='fitness:duration:value'>
<meta content='s' property='fitness:duration:units'>
<meta content='5.742746' property='fitness:speed:value'>
<meta content='m/s' property='fitness:speed:units'>
<link href='https://www.strava.com/activities/3123195350/facebook_open_graph_metadata' rel='opengraph'>

<meta content='summary_large_image' property='twitter:card'>
<meta content='@Strava' property='twitter:site'>
<meta content='strava.com' property='twitter:domain'>
<meta content='Choo choo' property='twitter:title'>
<meta content='Strava' property='twitter:app:name:googleplay'>
<meta content='com.strava' property='twitter:app:id:googleplay'>
<meta content='https://www.strava.com/activities/3123195350' property='twitter:app:url:googleplay'>
<meta content='Strava' property='twitter:app:name:iphone'>
<meta content='426826309' property='twitter:app:id:iphone'>
<meta content='strava://activities/3123195350' property='twitter:app:url:iphone'>
<meta content='Joe L. rode 48.3 mi on Feb 22, 2020.' property='twitter:description'>
<meta content='https://dgtzuqphqg23d.cloudfront.net/q1ixMRMczt82TG8EZDC1bvQioVWD8a-pJsadS0C14Ro-768x575.jpg' property='twitter:image'>
</head>
</body>
</html>
"""


MOCK_CRAWLED_ACTIVITY = {
    'fb:app_id': '284597785309',
    'og:site_name': 'Strava',
    'al:ios:url': 'strava://activities/538',
    'al:ios:app_name': 'Strava',
    'al:ios:app_store_id': '426826309',
    'al:android:url': 'strava://activities/538',
    'al:android:app_name': 'Strava',
    'al:android:package': 'com.strava',
    'og:type': 'fitness.course',
    'og:title': "Morning Ride - Bob Stover's 58.0 mi bike ride",
    'og:url': 'https://www.strava.com/activities/538',
    'og:image': 'http://d3nn82uaxijpm6.cloudfront.net/assets/sharing/summary_activity_generic-ec8c36660493881ac5fb7b7.png',
    'og:image:height': '200',
    'og:image:width': '200',
    'fitness:custom_unit_energy:value': '5219',
    'fitness:custom_unit_energy:units': 'https://www.strava.com/activities/facebook_open_graph_unit_elevation_gain',
    'fitness:distance:value': '58.1',
    'fitness:distance:units': 'mi',
    'fitness:duration:value': '14175',
    'fitness:duration:units': 's',
    'fitness:speed:value': '6.594554',
    'fitness:speed:units': 'm/s',
    'twitter:card': 'summary',
    'twitter:site': '@Strava',
    'twitter:domain': 'strava.com',
    'twitter:title': 'Morning Ride',
    'twitter:app:name:googleplay': 'Strava',
    'twitter:app:id:googleplay': 'com.strava',
    'twitter:app:url:googleplay': 'https://www.strava.com/activities/538',
    'twitter:app:name:iphone': 'Strava',
    'twitter:app:id:iphone': '426826309',
    'twitter:app:url:iphone': 'strava://activities/538',
    'twitter:description': 'Bob S. rode 58.0 mi on Apr 24, 2021.',
    'twitter:image': 'http://d3nn82uaxijpm6.cloudfront.net/assets/sharing/summary_activity_generic-ec8c36660493881ac5fb7b7.png',
}
