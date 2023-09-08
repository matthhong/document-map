import os
from model.sbmtm import sbmtm
from model.multilayer import sbmmultilayer
from model.Utils.nmi import *
from model.Utils.doc_clustering import *
import graph_tool.all as gt

from collections import defaultdict
import json
import os

import csv
import string
import numpy as np
import pandas as pd
import random

import spacy
sp = spacy.load('en_core_web_sm')

path_data = ''
saliency_dict = {}

SEED_NUM = 32


def run_multilayer(list_codes=[], coded_words=[], iteration=1):
    path_data = './client/public/files/'

    filename = os.path.join(path_data, 'simplyrecipes.csv')

    texts = []
    titles = []
    print("Loading texts")
    with open(filename,'r', encoding = 'utf8') as f:
        reader = csv.reader(f)
        
        next(reader)
        for line in reader:
            titles.append(line[0])

    with open('client/data/clean_texts.json' ,'r') as f:
        texts = json.load(f)

    # sample_range = random.sample(range(0, len(titles)), 1000)
    # titles = [titles[i] for i in sample_range]
    # texts = [texts[i] for i in sample_range]

    print("Running interactive model")
    import time

    t0 = time.time()
    # model = infer_model(texts, None, [], [])
    model = infer_model(texts, None, list_codes, coded_words)
    t1 = time.time()

    print("Took " + str((t1-t0)/60) + "minutes")

    print("Hashing clusters by words")
    
    # find highest non-trivial group
    L = 1000
    for i in range(model.n_levels):
        Bd = model.groups[i]['Bd']
        if Bd <= 1:
            break
        L = i
    model.L = L
    # breakpoint()

    hash_words_and_clusters(model, iteration)
    print("Computing frequencies")
    compute_saliency_dict(model, iteration)
    print("Generating topic tree structure")
    write_topic_tree(model, iteration)
    print("Generating document cluster structure")
    create_hex_map(model, iteration)
    print("Printing p_tw_d")
    save_p_tw_d(model, iteration)
    print("Printing p_d_tw")
    save_p_d_tw(model, iteration)

    command_str = [
        "mv",
        "-t",
        "./client/public/files",
        "p_tw_d_" + str(iteration) + ".json",
        "p_d_tw_" + str(iteration) + ".json",
        "regions_depth_" + str(iteration) + ".topo.json",
        "sbm_topic_tree_" + str(iteration) + ".json",
        "topic_saliency_hashed_" + str(iteration) + ".json",
        "words_to_cluster_" + str(iteration) + ".json"
    ]

    subprocess.run(command_str)


def clean_string(content):
    cleaned = content.lower()
    tokenized = sp(cleaned)

    stop = ['PRON', 'AUX', 'DET', 'ADP', 'CCONJ', 'SCONJ', 'PART', 'NUM', 'X', 'INTJ', 'PUNCT']
    return list(filter(lambda w: w != '', 
                       map(lambda w: w.lemma_ if (
                               (w.pos_ not in stop and len(w.text) > 1 and not w.lex.is_stop)
                                   ) else '', 
                           tokenized)))


def infer_model(texts, titles, list_codes, coded_words):
    ## we create an instance of the sbmtm-class
    model = sbmmultilayer(random_seed=32)

    ## we have to create the word-document network from the corpus
    model.make_graph(texts, titles, list_codes, coded_words)
    # model.make_graph(texts, titles)b
    ## we can also skip the previous step by saving/loading a graph
    # model.save_graph(filename = 'graph.xml.gz')
    # model.load_graph(filename = 'graph.xml.gz')

    ## fit the model
    print("Running model")
    # gt.seed_rng(32) ## seed for graph-tool's random number generator --> same results
    model.fit()

    return model


def hash_words_and_clusters(model, iteration):

    import numpy as np
    from collections import defaultdict

    words_to_cluster = defaultdict(dict)

    for l in range(model.L):
        doc_mem, words_mem = model.group_membership(l);
        words_mem = words_mem.T
        for i, w in enumerate(model.words):
            words_to_cluster[w][l] = int(np.argmax(words_mem[i]))

    with open(os.path.join(path_data,"words_to_cluster_" + str(iteration) + ".json"), "w") as outfile:
        json.dump(dict(words_to_cluster), outfile)
                


def compute_saliency_dict(model, iteration):
    frequencies = model.groups[1]['p_w']
    words = model.words
    frequency_dict = dict((k,v) for k, v in zip(words, frequencies))

    for l in range(model.L):

        dict_topics = model.topics(l=l,n=-1)

        topic_sal_ordering = {}
        for topic_id, topic in dict_topics.items():
            topic_sal_ordering[topic_id] = {"words": list(map(lambda v: v[0], topic)), "frequency": list(map(lambda v: v[1], topic)), "saliency": np.mean([frequency_dict[w] for w in map(lambda v: v[0], topic)])}
        saliency_dict[l] = topic_sal_ordering

    with open(os.path.join(path_data,"topic_saliency_hashed_" + str(iteration) + ".json"), "w") as outfile:
        json.dump(saliency_dict, outfile)


def save_p_tw_d(model, iteration):

    result = {}
    for l in range(model.L):

        p_tw_d = model.groups[l]['p_tw_d']
        result[l] = p_tw_d.tolist()

    with open(os.path.join(path_data,"p_tw_d_" + str(iteration) + ".json"), "w") as outfile:
        json.dump(result, outfile)


def save_p_d_tw(model, iteration):

    result = {}
    for l in range(model.L):

        p_d_tw = model.groups[l]['p_d_tw']
        result[l] = p_d_tw.tolist()

    with open(os.path.join(path_data,"p_d_tw_" + str(iteration) + ".json"), "w") as outfile:
        json.dump(result, outfile)



from scipy.cluster.hierarchy import ClusterNode

class GeneralClusterNode(ClusterNode):
    children = []
    queryed = None
    sampled = 0
    parent = None
    doc_id = None
    docs = []
    level = -1
    level_id = -1
    saliency = 0
    saliency_rank = 0

    def is_leaf(self):
        return True if len(self.children) <= 0 else False

    def get_count(self):
        return len(self.docs)

def construct_tree(model, l, current_index=None):

    # if not current_index: current_index = 0
    dict_clusters = model.clusters(l=l,n=-1)

    # Base Case: lowest level of the hierarchy
    if l == 0:
        ## Create lowest level of dictionary with name as first word in doc and value as number of words in doc
        clusters_formatted = []
        nodes = []
        if not current_index: current_index = len(model.documents)
        for i, val in enumerate(dict_clusters.values()):
            node = GeneralClusterNode(current_index)
            current_index += 1
            node.level_id = i
            
            children = []
            cluster_docs = [v[0] for v in val]
            for doc in cluster_docs:
                leaf_node = GeneralClusterNode(int(doc))
                
                leaf_node.queryed = False
                leaf_node.docs = [doc]
                leaf_node.level_id = int(doc)
                leaf_node.parent = node
                children.append(leaf_node)
                nodes.append(leaf_node)

            node.children = children
            node.docs = cluster_docs
            node.level = l
            nodes.append(node)

            clusters_formatted.append(node)
        return clusters_formatted, nodes, current_index
    # For intermediary levels of hierarchy
    elif l != model.L:
        clusters_children, nodes, current_index = construct_tree(model, l-1, current_index)  # get lower level clusters
        clusters_formatted = []                            # initailize final clusters array
        # iterate through clusters at level l in hierarchy and determine its children
        for i, val in enumerate(dict_clusters.values()):
            node = GeneralClusterNode(current_index)
            current_index += 1
            node.level_id = i
            children = []
            cluster_docs = [v[0] for v in val]
            # iterate through lower level hierarchy clusters and assign children to parent clusters

            for cc in clusters_children:
                if len(set(cc.docs) & set(cluster_docs)):
                    cc.parent = node
                    children.append(cc)
            
            node.children = children
            node.docs = cluster_docs
            node.level = l
            nodes.append(node)

            clusters_formatted.append(node)
        return clusters_formatted, nodes, current_index
    else:
        
        clusters_children, nodes, current_index = construct_tree(model, l-1, current_index)
        
        root = GeneralClusterNode(current_index)
        root.children = clusters_children
        root.level_id = 0
        root.docs = model.documents.copy()
        for c in root.children:
            c.parent = root
        root.level = l
        nodes.append(root)

    return root, nodes

# root, nodes = construct_tree(model, model.L)


def construct_topic_tree(model, l, current_index=None):

    # if not current_index: current_index = 0
    dict_clusters = model.topics(l=l,n=-1)

    # Base Case: lowest level of the hierarchy
    if l == 0:
        ## Create lowest level of dictionary with name as first word in doc and value as number of words in doc
        clusters_formatted = []
        nodes = []
        if not current_index: current_index = len(model.words)

        saliency_ordered = []
        for i, val in enumerate(dict_clusters.values()):
            saliency_ordered.append({"level_id": i, "val": val, "saliency": saliency_dict[l][i]['saliency']})
        saliency_ordered.sort(key=lambda v: v['saliency'], reverse=True)
        for (i, cluster) in enumerate(saliency_ordered):
            cluster["saliency_rank"] = i

        for cluster in saliency_ordered:
            node = GeneralClusterNode(current_index)
            current_index += 1
            node.level_id = cluster["level_id"]
            
            children = []
            cluster_docs = [v[0] for v in cluster["val"]]
            # for i, doc in enumerate(cluster_docs):
            #     leaf_node = GeneralClusterNode(i)
                
            #     leaf_node.queryed = False
            #     leaf_node.docs = [doc]
            #     leaf_node.level_id = int(doc)
            #     leaf_node.parent = node
            #     children.append(leaf_node)
            #     nodes.append(leaf_node)

            node.children = children
            node.docs = cluster_docs
            node.level = l
            node.saliency = cluster["saliency"]
            node.saliency_rank = cluster["saliency_rank"]
            nodes.append(node)

            clusters_formatted.append(node)
        return clusters_formatted, nodes, current_index
    # For intermediary levels of hierarchy
    elif l != model.L:
        clusters_children, nodes, current_index = construct_topic_tree(model, l-1, current_index)  # get lower level clusters
        clusters_formatted = []                            # initailize final clusters array

        saliency_ordered = []
        for i, val in enumerate(dict_clusters.values()):
            saliency_ordered.append({"level_id": i, "val": val, "saliency": saliency_dict[l][i]['saliency']})
        saliency_ordered.sort(key=lambda v: v['saliency'], reverse=True)
        for (i, cluster) in enumerate(saliency_ordered):
            cluster["saliency_rank"] = i

        # iterate through clusters at level l in hierarchy and determine its children
        for cluster in saliency_ordered:
            node = GeneralClusterNode(current_index)
            current_index += 1
            node.level_id = cluster["level_id"]
            children = []
            cluster_docs = [v[0] for v in cluster["val"]]
            # iterate through lower level hierarchy clusters and assign children to parent clusters

            for cc in clusters_children:
                if len(set(cc.docs) & set(cluster_docs)):
                    cc.parent = node
                    children.append(cc)
            
            node.children = children
            node.docs = cluster_docs
            node.level = l
            node.saliency = cluster['saliency']
            node.saliency_rank = cluster['saliency_rank']
            nodes.append(node)

            clusters_formatted.append(node)
        return clusters_formatted, nodes, current_index
    else:
        
        clusters_children, nodes, current_index = construct_topic_tree(model, l-1, current_index)
        
        root = GeneralClusterNode(current_index)
        root.children = clusters_children
        root.level_id = 0
        root.docs = model.words.copy()
        for c in root.children:
            c.parent = root
        root.level = l
        nodes.append(root)

    return root, nodes


# Create a nested dictionary from the ClusterNode's returned by SciPy
def add_node(node, parent ):
    # First create the new node and append it to its parent's children
    newNode = dict( name=str(node.id), size=len(node.docs), level=node.level, level_id=node.level_id, saliency=node.saliency, saliency_rank=node.saliency_rank, children=[] )
    parent["children"].append( newNode )

    # Recursively add the current node's children
    if node.children:
        for child in node.children:
            add_node(child, newNode)
            

def write_topic_tree(model, iteration):
    root, nodes = construct_topic_tree(model, model.L)

    d3Dendro = dict(children=[], name="Root")
    add_node(root, d3Dendro)
    json.dump(d3Dendro['children'][0], open("sbm_topic_tree_" + str(iteration) + ".json", 'w'))


import subprocess

import shapely.wkt
from fiona import collection
from shapely.geometry import mapping
import os

def create_hex_map(model, iteration):
    root, nodes = construct_tree(model, model.L)

    d3Dendro = dict(children=[], name="Root")
    add_node(root, d3Dendro)
    
    num_layers = gosperify(d3Dendro['children'][0], './model/hexes.wkt.csv', './model/hexmap', 'depth.json')

    command_str = [
        "geo2topo",
        "--cartesian",
        "--no-quantization",
        "-p",
        "depth",
        "-p",
        "label",
        "-o",
        "regions_depth_" + str(iteration) + ".topo.json",
        "depth.json",
    ]
    command_str.extend(["model/hexmap/" + str(i) + ".json" for i in range(num_layers)])

    subprocess.run(command_str)

# yield the leaves of the tree, also computing each leaf path
def leafify(node, path=()):
    if len(node['children']) <= 0:
        node['path'] = path + (node,)
        yield node
    else:
        for c in node['children']:
            for l in leafify(c, path + (node,)):
                yield l 
                
def gosperify(tree, hexes_path, output_regions_dir_path, depth_filename):
    leaves_done = 0
    layers = {}
    depth_levels = {}
        
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

    return len(layers)


# def run():


if __name__ == "__main__":

    run_multilayer([["family", "occasions"], ["family", "people"]], [["occasions", "holiday,christmas,thanksgiving,thanksgive,birthday,anniversary"], ["people", "father,mother,daughter,son,grandmother,grandfather,husband,wife,cousin,uncle,aunt"]])