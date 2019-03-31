###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from os import environ
import numpy as np
import pypcd

import asyncio
from autobahn.wamp.types import SubscribeOptions
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner


#TODO import? SPFN

class Component(ApplicationSession):
    """
    An application component that subscribes and receives events of no
    payload and of complex payload, and stops after 5 seconds.
    """

    async def onJoin(self, details):
        self.received = 0

        def on_heartbeat(counter, details=None):
            print("Got heartbeat: {} (publication ID {})".format(counter, details.publication))

        await self.subscribe(on_heartbeat, u'com.myapp.heartbeat', options=SubscribeOptions(details_arg='details'))

        # Calls self.leave after going through event loop five times
        #asyncio.get_event_loop().call_later(5, self.leave)

        def on_pointcloud_received(t, pcd_pointcloud):
            print("[EVENT] Received PointCloud from timestamp: {}".format(t))
            xyz_pointcloud = np.zeros(pcd_pointcloud.dims)
            # Do further stuff with PointCloud

            #TODO Convert PointCloud from `.pcd to .xyz`
            self.publish(u'com.myapp.spfn.input', xyz_pointcloud)

        def on_spfn_input_received(xyz_pointcloud):
            #TODO Do SPFN prediction
            #TODO publish SPFN prediction
            # self.publish(u'com.myapp.spfn.predictions', predicted_geometries)

        await self.subscribe(on_pointcloud_received, u'com.myapp.zenfone.pointclouds')

    def onDisconnect(self):
        print("Disconnecting from crossbar router")
        asyncio.get_event_loop().stop()


if __name__ == '__main__':
    import six
    url = environ.get("AUTOBAHN_DEMO_ROUTER", u"ws://127.0.0.1:8080/ws")
    if six.PY2 and type(url) == six.binary_type:
        url = url.decode('utf8')
    realm = u"crossbardemo"
    runner = ApplicationRunner(url, realm)
    runner.run(Component)
