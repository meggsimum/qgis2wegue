# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    from .qgis2wegue import qgis2wegue
    return qgis2wegue(iface)
