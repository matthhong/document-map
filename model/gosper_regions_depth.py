from __future__ import print_function
import csv
import json
from shapely.geometry.polygon import Polygon
import shapely.wkt
from fiona import collection
from shapely.geometry import mapping
import re
import os

# yield the leaves of the tree, also computing each leaf path
def leafify(node, path=()):
    if len(node['children']) <= 0:
        node['path'] = path + (node,)
        yield node
    else:
        for c in node['children']:
            for l in leafify(c, path + (node,)):
                yield l 
                
def gosperify(tree_path, hexes_path, output_regions_dir_path, depth_filename):
    leaves_done = 0
    layers = {}
    depth_levels = {}
    
    print('Reading the tree...')
    
    with open(tree_path, 'rb') as tree_file:
        tree = json.loads(tree_file.read())
        
    print('Reading hexes...')
    
    # iterate over the hexes taken from the file
    with open(hexes_path, 'r') as hexes_file:
        hexes_reader = csv.reader(hexes_file, delimiter=";")
        
        for leaf, hexes_row in zip(leafify(tree), hexes_reader):
            path = leaf['path']
            hex = shapely.wkt.loads(hexes_row[0])
            
            for depth in range(len(path)):
                # add the hex to its political regions
                ancestor_or_self = path[depth]
                
                if depth not in layers:
                    layers[depth] = {}
                    
                if id(ancestor_or_self) not in layers[depth]:
                    layers[depth][id(ancestor_or_self)] = {
                        'geometry': hex,
                        'node': ancestor_or_self
                    }
                else:
                    layers[depth][id(ancestor_or_self)]['geometry'] = layers[depth][id(ancestor_or_self)]['geometry'].union(hex)
                    
                # add the hex to all the depth levels with d <= depth
                if depth not in depth_levels:
                    depth_levels[depth] = hex
                else:
                    depth_levels[depth] = depth_levels[depth].union(hex)
                    
            # logging
            leaves_done += 1
            print('%d leaves done' % leaves_done, end='\r')
    
    print('Writing political regions...')
    
    schema = {'geometry': 'Polygon', 'properties': {'label': 'str'}}
    
    if not os.path.exists(output_regions_dir_path):
        os.makedirs(output_regions_dir_path)
        
    for depth, regions in layers.items():
        with collection(output_regions_dir_path+'/'+str(depth)+'.json', 'w', 'GeoJSON', schema) as output:
            for _, region_obj in regions.items():
                output.write({
                    'properties': {
                        'label': region_obj['node']['name']
                    },
                    'geometry': mapping(region_obj['geometry'])
                })
            
    print('Writing depth_levels...')
    
    schema = {'geometry': 'Polygon', 'properties': {'depth': 'int'}}
    
    with collection(depth_filename, 'w', 'GeoJSON', schema) as output:
        for depth, region in depth_levels.items():
            output.write({
                'properties': {
                    'depth': depth
                },
                'geometry': mapping(region)
            })

if __name__ == '__main__':
    gosperify('./sbm_tree.json', './hexes.wkt.csv', './hexmap', 'depth.json')