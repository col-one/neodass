
import py2neo
from py2neo.ogm import *
import copy


class NeoDb(object):
    @classmethod
    def connect_db(self, host="localhost", login="neo4j", password="admin"):
        """
        use this classmethod for connect cypher to a db different
        than default db. 
        
        :param str host: host name of db
        :param str login: login of the db
        :param str admin: password of the db
        :return: Cypher object
        :rtype: NeoDb
        """
        self.host = host
        self.login = login
        self.password = password
        py2neo.authenticate(self.host, self.login, self.password)
        self.graph = py2neo.Graph("http://{0}:7474/db/data".format(self.host), bolt=False, secure=False)
        self.Node = py2neo.Node
        self.Relationship = py2neo.Relationship
        self.create = self.graph.create
        return NeoDb()


class NodeAddOn(object):
    def __init__(self):
        super(NodeAddOn, self).__init__()

    def add_related(self, relation_class, relation_name, direction=UNDIRECTED, to_node=None):
        """
        Allow to add an empty slot relation dynamically
        :param relation_class: class label for constraint node type
        :param relation_name: name's relationships
        :param direction: direction's relationships, can be UNDIRECTED OUTGOING INCOMMING
        :param to_node: node to connect with
        :return: new attr
        """
        attr = relation_name
        related_instance = Related(relation_class, attr)
        related_instance.direction = direction
        related = Related.__get__(related_instance, self, None)
        setattr(self, attr, related)
        if not to_node is None:
            attr_related = getattr(self, attr)
            attr_related.add(to_node)
        return getattr(self, attr)

    def add_property(self, property_name):
        """
        Doesnt work
        :param property_name:
        :return:
        """
        attr = property_name
        property_instance = Property()
        property = Property()
        setattr(self, attr, property)
        node_property = getattr(self, attr)
        #node_property.update(self)
        print node_property
        return node_property


class Version(GraphObject, NodeAddOn):
    """
    Version node who handle versionning information.
    With property:
        name : 000_000_ETP_v000
        version_id : 0
        comment : first release
        creator : user
        date : 201612120830
    """
    #__primarykey__ = "name"

    #Properties
    name = Property()
    version_id = Property()
    comment = Property()
    creator = Property()
    date = Property()
    flag = Property()

    #Related INCOMING
    asset = RelatedFrom("Asset", "CURRENT")

    #Related OUTGOING
    use = RelatedTo("Media")

class Media(GraphObject, NodeAddOn):
    """
    Media node who handle file information.
    With property:
        name : 000_000_ETP_v001.media
        date : 201612120830
        modification_date : 201612120830
        file : /foo/bar/000_000_ETP_v001.max
        type : max
        multi_files : True
    """
    __primarykey__ = "name"
    #properties
    name = Property()
    date = Property()
    modification_date = Property()
    file = Property()
    type = Property()
    multi_files = Property()

    #related INCOMING
    use = RelatedFrom(Version, "USE")
    cache = RelatedFrom("Asset", "CACHE")

    #related OUTGOING
    movie = RelatedTo("Media")

class User(GraphObject, NodeAddOn):
    """
    User node
    """
    __primarykey__ = "name"

    #properties
    name = Property()
    job = Property()

    #Related OUTGOING
    lock = RelatedTo("Asset")

class Task(GraphObject):
    """
    Task hold the info of various task
    """
    __primarykey__ = "name"
    # add properties
    name = Property()
    # relations INCOMING
    asset_lib = RelatedFrom("AssetLib", "ASSET LIB")
    asset_shot = RelatedFrom("AssetShot", "ASSET SHOT")

class Asset(GraphObject, NodeAddOn):
    """
    Base asset node who handle asset information.
    With property:
        name : 000_000_ETP
        creator : user
        date : 201612120830
        modification_date : 201612120830
        type : LIB / SHOT
        genre : ETP

    """
    __primarykey__ = "name"

    #properties
    name = Property()
    creator = Property()
    modification_date = Property()
    type =  Property()
    date = Property()
    genre = Property()
    code = Property()
    variation = Property()


    #relations OUTGOING
    current = RelatedTo(Version)
    version = RelatedTo(Version)
    cache = RelatedTo(Media)
    task = RelatedTo(Task)

    #relations INCOMING
    locked_by = RelatedFrom("User", "LOCK")

    def relink_current(self, asset):
        self.current.clear()
        self.current.add(asset)

class AssetShot(Asset, NodeAddOn):
    """
    AssetShot derived from Asset
    """
    #add properties
    episode = Property()
    shot = Property()

class AssetLib(Asset, NodeAddOn):
    """
    AssetLib derived from Asset
    """
    #redef primary key to code
    __primarykey__ = "code"
    # add properties
    collection = Property()
    family = Property()



# shot = AssetShot()
# shot.name = "102_148_BLK"
# shot.creator = "FOO"
# shot.episode = "102"
# shot.shot = "148"
# shot.type = "SHOT"
#
# version = Version()
# version.name = "102_148_BLK_v001"
#
# media = Media()
# media.name = "102_148_BLK_v001.media"
#
# version.use.add(media)
#
# user = User()
# user.name = "toto"
#
# user.lock.add(shot)
#
# cache = Media()
# cache.name = "102_148_BLK_v001.cache"
#
# shot.cache.add(cache)
# shot.current.add(version)
# shot.add_related(Version, "V001", direction=OUTGOING, to_node=version)


# graph = NeoDb.connect_db(host="137.74.198.16", password="tamere").graph
#
# props = AssetLib()
# props.name = 'Ecrou'
# props.type = 'LIB'
# props.code = 'H005a'
# props.creator = 'Colin'
# props.collection = 'Props'
# graph.push(props)
