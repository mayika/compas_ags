
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.datastructures import Network
from compas.datastructures import FaceNetwork
from compas.topology import network_find_faces
from compas.utilities import geometric_key

import rhinoscriptsyntax as rs


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Networks

guids = rs.ObjectsByLayer('Lines')
lines = [[rs.CurveStartPoint(guid), rs.CurveEndPoint(guid)] for guid in guids]
network = Network.from_lines(lines)
face_network = FaceNetwork.from_data(network.to_data())
network_find_faces(face_network, breakpoints=face_network.leaves())

# Pins

network.update_default_vertex_attributes({'is_fixed': False})
gkey_key = network.gkey_key()
for guid in rs.ObjectsByLayer('Pins'):
    gkey = geometric_key(rs.PointCoordinates(guid))
    network.set_vertex_attributes(gkey_key[gkey], {'is_fixed': True})

# Loads

rs.EnableRedraw(False)
rs.DeleteObjects(rs.ObjectsByLayer('Dots'))
rs.CurrentLayer('Dots')

At = 0
for key in network.vertices():
    A = face_network.vertex_area(key=key)  # fix "bug" for areas at sides
    if network.vertex_degree(key) == 3:  # temp hack
        A = 0.2
#    A = 1.
    At += A
    network.vertex[key]['pz'] = A
    rs.AddTextDot('{0:.1f}'.format(A), network.vertex_coordinates(key)) 
print('Total load: {0}'.format(At))
    
rs.EnableRedraw(True)
rs.CurrentLayer('Lines')

# Save

network.to_json('H:/data/loadpath/arches.json')
