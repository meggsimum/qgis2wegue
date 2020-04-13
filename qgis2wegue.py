import re
import os.path

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.core import QgsProject
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .qgis2wegue_dialog import qgis2wegueDialog
from .wegueConf import WegueConfiguration

from .wegue_util import (center2webmercator,
                         scale2zoom,
                         extract_wegue_layer_config)

class qgis2wegue:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            "i18n",
            "qgis2wegue_{}.qm".format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u"&QGIS2Wegue")

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("qgis2wegue", message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ":/plugins/qgis2wegue/logo/logo.png"
        self.add_action(
            icon_path,
            text=self.tr(u"Create a Wegue Configuration"),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u"&QGIS2Wegue"),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the
        # plugin is started
        if self.first_start:
            self.first_start = False
            self.dlg = qgis2wegueDialog()

        # show the dialog
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()

        # See if OK was pressed
        if result:
            # reset Wegue conf
            self.wegue_conf = WegueConfiguration()
            self.store_wegue_conf_to_file()

    def store_wegue_conf_to_file(self):
        """
        Collects all paramters from QGIS and the plugin form
        and creates the Wegue configuration
        """

        canvas = self.iface.mapCanvas()
        qgis_instance = QgsProject.instance()

        scale = canvas.scale()
        center = canvas.center()

        center_3857 = center2webmercator(center, qgis_instance)

        zoom_level = scale2zoom(scale)

        # add configuration from project
        self.wegue_conf.mapZoom = zoom_level
        self.wegue_conf.mapCenter = (center_3857.x(), center_3857.y())

        # get information from all layers
        # loop through checked layers
        root = qgis_instance.layerTreeRoot()
        for layer in root.checkedLayers():

            result_layer = extract_wegue_layer_config(layer)
            if result_layer:
                self.wegue_conf.mapLayers.append(result_layer)

        # optional properties
        self.wegue_conf.title = self.dlg.q2w_title_widget.text()
        self.wegue_conf.footerTextLeft = self.dlg.q2w_footer_left_widget.text()
        self.wegue_conf.footerTextRight = \
            self.dlg.q2w_footer_right_widget.text()

        # add checkbox properties
        self.wegue_conf.showCopyrightYear = \
            self.dlg.q2w_copyright_year.isChecked()

        if self.dlg.q2w_layer_list.isChecked():
            self.wegue_conf.add_layer_list()

        if self.dlg.q2w_info_click.isChecked():
            self.wegue_conf.add_infoclick()

        if self.dlg.q2w_help_window.isChecked():
            self.wegue_conf.add_help_window()

        if self.dlg.q2w_measure_tool.isChecked():
            self.wegue_conf.add_measuretool()

        if self.dlg.q2w_max_extent.isChecked():
            self.wegue_conf.add_button_zoom_to_extent()

        if self.dlg.q2w_geocoder.isChecked():
            self.wegue_conf.add_geocoder()

        # color
        color_rgb = self.dlg.q2w_color_widget.color().getRgb()
        # drop alpha value
        color_rgb = color_rgb[0:3]
        self.wegue_conf.baseColor = "rgb" + str(color_rgb)

        # path for config
        user_input = self.dlg.q2w_file_widget.filePath()
        self.wegue_conf.to_file(user_input)
