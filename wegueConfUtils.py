import uuid
from collections import OrderedDict


def create_wms(name, url,
               layers, **wms_props):

    wms_props['layers'] = layers

    return _make_layer_json(
        "WMS", name, url, wms_props)


def create_xyz(name, url, **xyz_props):

    return _make_layer_json(
        "XYZ", name, url, xyz_props)


def create_vector_layer(name, url, vector_format, **vector_props):

    vector_props['format'] = vector_format

    return _make_layer_json('VECTOR', name, url, vector_props)


def create_wfs(name, url, typename, **wfs_props):

    wfs_props['typename'] = typename

    return _make_layer_json("WFS", name, url, wfs_props)


def _make_layer_json(wegue_layer_type, name, url, props):
    """ Basic function for building a Wegue layer configuration"""

    # convert to OrderedDict
    # because we want to change the order of the properties
    props = OrderedDict(props)

    # add basic properties
    props['name'] = name
    props['url'] = url
    props["type"] = wegue_layer_type

    # lid needs to be created
    if "lid" not in props:
        props["lid"] = _create_layer_id(props["name"])

    # set style for vector layers
    if "geometryTypeName" in props:
        props["style"] = _assign_default_style(
            props["geometryTypeName"])
        del props["geometryTypeName"]

    # move some keys to the beginning of the config
    # makes sure that the user can read it easier
    first_keys = ["type", "name", "url", "lid"]
    if "format" in props:
        first_keys.append("format")
    for key in reversed(first_keys):
        props.move_to_end(key)

    # reverse order of dict
    tmp = OrderedDict()
    for key in reversed(props):
        tmp[key] = props[key]
    props = tmp

    return props


def _create_layer_id(name):
    """Creates a layer id based on the name of the layer"""

    lid = name.strip().lower()

    # replace some special characters
    lid = lid.replace("ä", "ae")
    lid = lid.replace("ö", "oe")
    lid = lid.replace("ü", "ue")
    lid = lid.replace("ß", "ss")
    lid = lid.replace("é", "e")

    # replace whitespace with underscore
    lid = lid.replace(" ", "_")

    # replace other characters with underscore
    lid = lid.replace("-", "_")
    lid = lid.replace(":", "_")

    # only one underscore in a row
    while "__" in lid:
        lid = lid.replace("__", "_")

    # only keep ascii characters
    lid = lid.encode("utf-8").decode("ascii", "ignore")

    # in case all characters have been removed
    if lid == "":
        lid = uuid.uuid1()

    return lid


def _assign_default_style(geometryType):
    """ Create a default OpenLayers style based on the geometry type"""

    style = ""
    if geometryType == "Point":
        style = {
            "radius": 4,
            "strokeColor": "rgb(207, 16, 32)",
            "strokeWidth": 1,
            "fillColor": "rgba(207, 16, 32, 0.6)"
        }
    elif geometryType == "LineString":
        style = {
            "strokeColor": "blue",
            "strokeWidth": 2
        }
    elif geometryType == "Polygon":
        style = {
            "strokeColor": "gray",
            "strokeWidth": 1,
            "fillColor": "rgba(20,20,20,0.1)"
        }
    return style
