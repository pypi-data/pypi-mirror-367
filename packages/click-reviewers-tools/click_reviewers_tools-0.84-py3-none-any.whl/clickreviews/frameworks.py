#
#  Copyright (C) 2014 Canonical Ltd.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 3 of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

FRAMEWORKS = {
    "ubuntu-sdk-13.10": "obsolete",
    "ubuntu-sdk-14.04": "obsolete",
    "ubuntu-sdk-14.04-dev1": "obsolete",
    "ubuntu-sdk-14.04-html-dev1": "obsolete",
    "ubuntu-sdk-14.04-html": "obsolete",
    "ubuntu-sdk-14.04-papi-dev1": "obsolete",
    "ubuntu-sdk-14.04-papi": "obsolete",
    "ubuntu-sdk-14.04-qml-dev1": "obsolete",
    "ubuntu-sdk-14.04-qml": "obsolete",
    "ubuntu-sdk-14.10": "obsolete",
    "ubuntu-sdk-14.10-dev1": "obsolete",
    "ubuntu-sdk-14.10-dev2": "obsolete",
    "ubuntu-sdk-14.10-dev3": "obsolete",
    "ubuntu-sdk-14.10-html-dev1": "obsolete",
    "ubuntu-sdk-14.10-html-dev2": "obsolete",
    "ubuntu-sdk-14.10-html-dev3": "obsolete",
    "ubuntu-sdk-14.10-html": "obsolete",
    "ubuntu-sdk-14.10-papi-dev1": "obsolete",
    "ubuntu-sdk-14.10-papi-dev2": "obsolete",
    "ubuntu-sdk-14.10-papi-dev3": "obsolete",
    "ubuntu-sdk-14.10-papi": "obsolete",
    "ubuntu-sdk-14.10-qml-dev1": "obsolete",
    "ubuntu-sdk-14.10-qml-dev2": "obsolete",
    "ubuntu-sdk-14.10-qml-dev3": "obsolete",
    "ubuntu-sdk-14.10-qml": "obsolete",
    "ubuntu-sdk-15.04": "obsolete",
    "ubuntu-sdk-15.04-html": "obsolete",
    "ubuntu-sdk-15.04-papi": "obsolete",
    "ubuntu-sdk-15.04-qml": "obsolete",
    "ubuntu-sdk-15.04.1-html": "obsolete",
    "ubuntu-sdk-15.04.1-papi": "obsolete",
    "ubuntu-sdk-15.04.1-qml": "obsolete",
    "ubuntu-sdk-15.04.1": "obsolete",
    "ubuntu-sdk-15.04.2-html": "obsolete",
    "ubuntu-sdk-15.04.2-papi": "obsolete",
    "ubuntu-sdk-15.04.2-qml": "obsolete",
    "ubuntu-sdk-15.04.2": "obsolete",
    "ubuntu-sdk-15.04.3-html": "obsolete",
    "ubuntu-sdk-15.04.3-papi": "obsolete",
    "ubuntu-sdk-15.04.3-qml": "obsolete",
    "ubuntu-sdk-15.04.3": "obsolete",
    "ubuntu-sdk-15.04.4-html": "obsolete",
    "ubuntu-sdk-15.04.4-papi": "obsolete",
    "ubuntu-sdk-15.04.4-qml": "obsolete",
    "ubuntu-sdk-15.04.4": "obsolete",
    "ubuntu-sdk-15.04.5-html": "obsolete",
    "ubuntu-sdk-15.04.5-papi": "obsolete",
    "ubuntu-sdk-15.04.5-qml": "obsolete",
    "ubuntu-sdk-15.04.5": "obsolete",
    "ubuntu-sdk-15.04.6-html": "obsolete",
    "ubuntu-sdk-15.04.6-papi": "obsolete",
    "ubuntu-sdk-15.04.6-qml": "obsolete",
    "ubuntu-sdk-15.04.6": "obsolete",
    "ubuntu-sdk-15.04.7-html": "obsolete",
    "ubuntu-sdk-15.04.7-papi": "obsolete",
    "ubuntu-sdk-15.04.7-qml": "obsolete",
    "ubuntu-sdk-15.04.7": "obsolete",
    "ubuntu-sdk-16.04": "deprecated",
    "ubuntu-sdk-16.04-html": "deprecated",
    "ubuntu-sdk-16.04-papi": "deprecated",
    "ubuntu-sdk-16.04-qml": "deprecated",
    "ubuntu-sdk-16.04.1": "deprecated",
    "ubuntu-sdk-16.04.1-html": "deprecated",
    "ubuntu-sdk-16.04.1-papi": "deprecated",
    "ubuntu-sdk-16.04.1-qml": "deprecated",
    "ubuntu-sdk-16.04.2": "deprecated",
    "ubuntu-sdk-16.04.2-html": "deprecated",
    "ubuntu-sdk-16.04.2-papi": "deprecated",
    "ubuntu-sdk-16.04.2-qml": "deprecated",
    "ubuntu-sdk-16.04.3": "deprecated",
    "ubuntu-sdk-16.04.3-html": "deprecated",
    "ubuntu-sdk-16.04.3-papi": "deprecated",
    "ubuntu-sdk-16.04.3-qml": "deprecated",
    "ubuntu-sdk-16.04.4": "deprecated",
    "ubuntu-sdk-16.04.4-html": "deprecated",
    "ubuntu-sdk-16.04.4-papi": "deprecated",
    "ubuntu-sdk-16.04.4-qml": "deprecated",
    "ubuntu-sdk-16.04.5": "deprecated",
    "ubuntu-sdk-16.04.5-html": "deprecated",
    "ubuntu-sdk-16.04.5-papi": "deprecated",
    "ubuntu-sdk-16.04.5-qml": "deprecated",
    "ubuntu-sdk-16.04.6": "deprecated",
    "ubuntu-sdk-16.04.6-html": "deprecated",
    "ubuntu-sdk-16.04.6-papi": "deprecated",
    "ubuntu-sdk-16.04.6-qml": "deprecated",
    "ubuntu-sdk-16.04.7": "deprecated",
    "ubuntu-sdk-16.04.7-html": "deprecated",
    "ubuntu-sdk-16.04.7-papi": "deprecated",
    "ubuntu-sdk-16.04.7-qml": "deprecated",
    "ubuntu-sdk-16.04.8": "deprecated",
    "ubuntu-sdk-16.04.8-html": "deprecated",
    "ubuntu-sdk-16.04.8-papi": "deprecated",
    "ubuntu-sdk-16.04.8-qml": "deprecated",
    "ubuntu-sdk-20.04": "available",
    "ubuntu-sdk-20.04-qml": "available",
    "ubuntu-sdk-20.04.1": "available",
    "ubuntu-sdk-20.04.1-qml": "available",
    "ubuntu-touch-24.04-1.x": "available",
    "ubuntu-touch-24.04-1.x-papi": "available",
    "ubuntu-touch-24.04-1.x-qml": "available",
    "ubuntu-touch-next-internal": "prereleased",
}


class Frameworks(object):
    DEPRECATED_FRAMEWORKS = []
    OBSOLETE_FRAMEWORKS = []
    AVAILABLE_FRAMEWORKS = []
    PRERELEASED_FRAMEWORKS = []

    def __init__(self, overrides=None):
        self.FRAMEWORKS = FRAMEWORKS
        if overrides is not None:
            self.FRAMEWORKS.update(overrides)

        for name, data in self.FRAMEWORKS.items():
            if type(data) is dict:
                state = data.get('state')
            else:
                state = data

            if state == 'deprecated':
                self.DEPRECATED_FRAMEWORKS.append(name)
            elif state == 'obsolete':
                self.OBSOLETE_FRAMEWORKS.append(name)
            elif state == 'available':
                self.AVAILABLE_FRAMEWORKS.append(name)
            elif state == 'prereleased':
                self.PRERELEASED_FRAMEWORKS.append(name)
