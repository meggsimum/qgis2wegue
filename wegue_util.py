import re
from urllib.parse import parse_qs
from qgis.core import QgsProject, QgsCoordinateTransform
from qgis.core import QgsCoordinateReferenceSystem
from .wegueConfiguration import WegueConfiguration


def create_wegue_conf_from_qgis(canvas):
    """
    Loops through all checked layers in the layer tree
    and converts them to a Wegue configuration
    """

    scale = canvas.scale()
    center = canvas.center()

    qgis_instance = QgsProject.instance()

    center_3857 = center2webmercator(center, qgis_instance)

    zoom_level = scale2zoom(scale)

    # create Wegue configuration
    wc = WegueConfiguration()

    # add configuration from project
    wc.mapZoom = zoom_level
    wc.mapCenter = (center_3857.x(), center_3857.y())

    # loop through checked layers
    root = qgis_instance.layerTreeRoot()
    for layer in root.checkedLayers():

        wegue_layer_type = identify_wegue_layer_type(layer)

        # same for all types
        name = layer.name()
        source = layer.source()

        if wegue_layer_type in ['GeoJSON', 'KML']:
            url = source.split('|')[0]

            wc.add_vector_layer(name=name,
                                format=wegue_layer_type,
                                url=url)

        elif wegue_layer_type == 'WMS':
            layers = re.search(r"layers=(.*?)(?:&|$)", source).groups(0)[0]
            url = get_wms_getmap_url(layer)

            wc.add_wms_layer(name, layers, url)

        elif wegue_layer_type == 'XYZ':

            layer_props = parse_qs(source)
            url = layer_props['url'][0]

            # in case no attribution is available
            attributions = ""  
            if 'referer' in layer_props:
                attributions = layer_props['referer'][0]

            wc.add_xyz_layer(name, url, attributions=attributions)

        elif wegue_layer_type == 'WFS':

            props = get_wfs_properties(source)

            typename = props['typename']
            url = props['url']

            # TODO: add those parameters
            extent = layer.extent()
            crs = layer.crs()

            wc.add_wfs_layer(name=name,
                             url=url,
                             typeName=typename)

    return wc


def center2webmercator(center, qgis_instance):
    """
    Input the center point of the QGIS canvas.
    The QGIS instance object, for computing the source CRS
    and the transformation object.
    Outputs: The Same point in WebMercator(EPSG:3857)
    """

    crs_source = qgis_instance.crs()

    # TODO apparently QgsCoordinateReferenceSystem is deprecated

    # define WebMercator(EPSG:3857)
    crs_destination = QgsCoordinateReferenceSystem(3857)

    # transformation object
    xform = QgsCoordinateTransform(crs_source,
                                   crs_destination,
                                   qgis_instance)

    # forward transformation: src -> dest
    center_3857 = xform.transform(center)
    return center_3857


def scale2zoom(scale):
    """
    Takes the scale from QGIS.
    Computes the zoom level for webmaps.
    Only approximation.
    """

    # Scale to Zoom conversion
    # taken from https://wiki.openstreetmap.org/wiki/Zoom_levels
    scale_dict = {
        500000000: 0,
        250000000: 1,
        150000000: 2,
        70000000: 3,
        35000000: 4,
        15000000: 5,
        10000000: 6,
        4000000	: 7,
        2000000	: 8,
        1000000: 9,
        500000: 10,
        250000: 11,
        150000: 12,
        70000: 13,
        35000: 14,
        15000: 15,
        8000: 16,
        4000: 17,
        2000: 18
    }
    scale_list = scale_dict.keys()

    # get closest scale
    closest_scale = min(scale_list, key=lambda x: abs(x - scale))

    # query respective zoom level
    return scale_dict[closest_scale]


def identify_wegue_layer_type(layer):
    """
    Matches QGIS layer type to Wegue type
    Wegue types:
    - vector
    - wms
    - xyz
    - (osm)
    """

    wegue_layer_type = 'unknown'
    providerType = layer.providerType().lower()
    source = layer.source()

    if providerType == 'wms':
        # Raster layer distinction proudly taken from the great qgis2web
        # project. All creadits to the qgis2web devs
        # https://github.com/tomchadwin/qgis2web
        d = parse_qs(source)
        if "type" in d and d["type"][0] == "xyz":
            wegue_layer_type = 'XYZ'
        elif "tileMatrixSet" in d:
            wegue_layer_type = 'WMTS'  # currently not supported in Wegue
        else:
            wegue_layer_type = 'WMS'

    elif providerType == 'ogr':

        url = source.split('|')[0]

        if(url.endswith('.kml')):
            wegue_layer_type = 'KML'
        elif(url.endswith('.json') | url.endswith('.geojson')):
            wegue_layer_type = 'GeoJSON'

    elif providerType == 'wfs':

        wegue_layer_type = 'WFS'

    return wegue_layer_type


def get_wms_getmap_url(wmsLayer):
    """
    Detects the Get-Map URL for a QGIS WMS layer
    """

    wms_getmap_url = None

    # derive WMS GetMap URL from layer metdata
    htmlMetadata = wmsLayer.htmlMetadata()
    match = re.search(
        r'GetMapUrl<\/td><td>(.*)<\/td><\/tr><tr><td>GetFeatureInfoUrl',
        htmlMetadata)

    if match:
        layersGroup = match.groups(0)
        wms_getmap_url = ''.join(layersGroup)

    else:
        wms_getmap_url = re.search(r"url=(.*?)(?:&|$)",
                                   wmsLayer.source()).groups(0)[0]

    return wms_getmap_url


def get_wfs_properties(source):
    """
    Extracts the WFS properties from the layer source
    """
    # TODO: check if there is a more elegant solution

    # manually converting source into dict
    source = source.strip()
    items = source.split(' ')

    # built property dict
    props = {}
    for i in items:
        # extract keys and values
        spl = i.split('=')
        k, v = spl[0], spl[1]

        # remove single quote
        v = v.replace("'", "")

        # handle keys that appear twice
        if k in props:
            k = k + '_2'

        props[k] = v
    return props
