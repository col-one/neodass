import os
import filecmp
import neodb

def create_assetlib(graph, name='', type='lib', code='', creator='', collection='', variation=''):
    asset = neodb.AssetLib()
    asset.name = name
    asset.type = type
    asset.code = code
    asset.creator = creator
    asset.collection = collection
    asset.variation = variation
    return asset

def get_assetlib(graph, type='lib', **kwargs):
    if len(kwargs) == 0:
        return list(neodb.AssetLib.select(graph).where("_.type = 'lib'"))
    else:
        assets = []
        for key, value in kwargs.iteritems():
            assets += list(neodb.AssetLib.select(graph).where("_.{key} =~ '^.*{value}.*$'".format(key=key, value=value)))
        return assets

def create_version(asset, comment='no comment', to_current=False, media=''):
    if not os.path.isfile(media):
        raise IOError("Media doesn't exist")
    media_asset = neodb.Media()
    versions_nodes = asset.version
    if len(versions_nodes) == 0:
        version = neodb.Version()
        version.name = '001'
        version.comment = "first"
        asset.version.add(version)
        asset.current.add(version)
    else:
        last_version = sorted(list(versions_nodes), key=lambda x:x.name)[-1]
        last_media = list(last_version.use)[-1]
        last_file = last_media.file
        version = neodb.Version()
        version.name = '{v:03d}'.format(v=len(versions_nodes)+1)
        version.comment = comment
        asset.version.add(version)
        if to_current:
            asset.relink_current(version)
        if filecmp.cmp(last_file, media):
            media_asset = last_media
            print 'same file, keep last media'
    media_name = os.path.basename(media)
    media_asset.name = media_name
    media_asset.multi_files = 'False'
    media_asset.file = media
    media_asset.type = os.path.splitext(media_name)[-1]
    version.use.add(media_asset)
    return asset

def get_medialib(asset, version='current'):
    if version == 'current':
        current_version = list(asset.current)[-1]
        current_media = list(current_version.use)[-1]
        return current_media
    else:
        versions_nodes = sorted(list(asset.version), key=lambda x: x.name)
        version_dict = {}
        for v in versions_nodes:
            version_dict[v.name]=v
        return list(version_dict[version].use)[-1]

def get_versionlib(asset):
    versions_nodes = sorted(list(asset.version), key=lambda x: x.name)
    version_dict = {}
    for v in versions_nodes:
        version_dict[v.name] = v
    return version_dict

graph = neodb.NeoDb.connect_db(host="137.74.198.16", password="tamere").graph
asset = get_assetlib(graph)[0]
print get_versionlib(asset)['004'].comment