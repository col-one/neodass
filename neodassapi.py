import os
import time
import filecmp
import py2neo
import neodb
import errors
import hashlib

py2neo.authenticate("192.168.2.250", "neo4j", "tnzpvgeek")
#GRAPH = py2neo.Graph("http://neo4j:tnzpvgeek@192.168.2.250:7474/db/data", bolt=False)

class Graph(py2neo.Graph):
    def __init__(self, bolt=False, secure=False, host='localhost', http_port=7474, user='neo4j', password='neo4j'):
        self.uri = "http://{user}:{pw}@{host}:{port}/db/data".format(user=user, pw=password, host=host, port=http_port)
        super(Graph, self).__init__(self.uri, bolt=False, secure=False)
    
    def push(self, subgraph):
        try:
            subgraph.modification_date = time.time()
        except:
            print "{0} doesn't have modification_date property".format(subgraph)
        super(Graph, self).push(subgraph)


GRAPH = Graph(host='137.74.198.16', password='tamere')

class NeoDassObject(object):
    def __init__(self, asset):
        self.asset = asset

    def create_version(self, comment='no comment', to_current=False, media='', graph=GRAPH, push=True):
        if not os.path.isfile(media):
            raise IOError("Media doesn't exist")
        md5 = hashlib.md5(open(media, 'rb').read()).hexdigest()
        media_asset = neodb.Media()
        versions_nodes = self.asset.version
        print list(versions_nodes)
        if len(versions_nodes) == 0:
            version = neodb.Version()
            version.name = '001'
            version.comment = "first"
            self.asset.version.add(version)
            self.asset.current.add(version)
        else:
            last_version = sorted(list(versions_nodes), key=lambda x: x.name)[-1]
            last_media = list(last_version.use)[-1]
            last_file = last_media.file
            version = neodb.Version()
            version.name = '{v:03d}'.format(v=len(versions_nodes) + 1)
            version.comment = comment
            self.asset.version.add(version)
            if to_current:
                self.asset.relink_current(version)
            if filecmp.cmp(last_file, media):
                media_asset = last_media
                print 'same file, keep last media'
        media_name = os.path.basename(media)
        media_asset.name = media_name
        media_asset.multi_files = 'False'
        media_asset.file = media
        media_asset.hash = md5
        media_asset.type = os.path.splitext(media_name)[-1]
        print version
        version.use.add(media_asset)
        if push is True:
            for a in [media_asset, self.asset, version]:
                graph.push(a)
        return media_asset

    def get_medialib(self, version='current'):
        if version == 'current':
            current_version = list(self.asset.current)[-1]
            current_media = list(current_version.use)[-1]
            return current_media
        else:
            versions_nodes = sorted(list(self.asset.version), key=lambda x: x.name)
            version_dict = {}
            for v in versions_nodes:
                version_dict[v.name] = v
            return list(version_dict[version].use)[-1]

    def get_versionlib(self):
        versions_nodes = sorted(list(self.asset.version), key=lambda x: x.name)
        version_dict = {}
        for v in versions_nodes:
            version_dict[v.name] = v
        return version_dict


def create_assetlib(graph=GRAPH, name='', type='lib', code='', creator='', collection=neodb.Collection,
                    variation='', task=neodb.Task, push=True, match_if=False):
    check = get_assetlib(graph, code=code)
    if len(check) != 0:
        if match_if:
            return check[0]
        raise errors.NotUnique("Asset deja existant {0}".format(check[0].code))
    asset = neodb.AssetLib()
    asset.name = name
    asset.type = type
    asset.code = code
    asset.creator = creator
    asset.collection.add(collection)
    collection.asset_lib.add(asset)
    asset.variation = variation
    asset.date = time.time()
    asset.task.clear()
    asset.task.add(task)
    task.asset_lib.add(asset)
    if push is True:
        graph.push(asset)
    asset.action = NeoDassObject(asset)
    return asset

def get_assetlib(graph=GRAPH, **kwargs):
    if len(kwargs) == 0:
        asset = neodb.AssetLib.select(graph).where("_.type = 'lib'").first()
        asset.extra = NeoDassObject()
        return asset
    else:
        assets = []
        for key, value in kwargs.iteritems():
            value = value.replace('*', '.*')
            assets += list(neodb.AssetLib.select(graph).where("_.{key} =~ '^{value}$'".format(key=key, value=value)))
        for asset in assets:
            asset.action = NeoDassObject(asset)
        return assets

def get_task(task, graph=GRAPH):
    return list(neodb.Task.select(graph).where("_.name = '{0}'".format(task)))[0]

def get_collection(collection, graph=GRAPH):
    return list(neodb.Collection.select(graph).where("_.name = '{0}'".format(collection)))[0]

# # create danael task et collection
task = neodb.Task()
task.name = 'rig'
collection = neodb.Collection()
collection.name = 'chars'
danael = create_assetlib(name="Danael", code='A001', task=task, collection=collection, match_if=True)


t = get_collection('chars')
dd = t.asset_lib
for d in dd:
    print d



#
# danael = get_assetlib(code='A001')[0]
# danaelbave = get_assetlib(code='A001d')[0]
# danaelbave.action.create_version(media="T:\software\Guerilla Render\guerilla.exe")
# GRAPH.push(danael)
