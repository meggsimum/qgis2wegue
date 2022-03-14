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
                         extract_wegue_layer_config,
                         rgb2hex
                         )


class qgis2wegue:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):

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

        if self.first_start:
            self.first_start = False
            self.dlg = qgis2wegueDialog(parent=self.iface.mainWindow())
            self.dlg = qgis2wegueDialog()
            self.dlg.q2w_file_widget.fileChanged.connect(
                self.check_path_and_handle_submit_button)
            self.dlg.finished.connect(self.final_task)

        self.dlg.open()

    def final_task(self, result):

        if result:
            # reset Wegue conf
            self.wegue_conf = WegueConfiguration()
            self.store_wegue_conf_to_file()

    def check_path_and_handle_submit_button(self, path):
        """Checks if output path is valid"""

        base_dir, file = os.path.split(path)

        dir_exists = os.path.exists(base_dir)

        enabled = False
        if (file != "") & dir_exists & file.endswith('.json'):
            # output path valid
            enabled = True

        self.dlg.button_box.setEnabled(enabled)

    def store_wegue_conf_to_file(self):
        """
        Collects all parameters from QGIS and the plugin form
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

        if self.dlg.q2w_geodata_drag_drop.isChecked():
            self.wegue_conf.add_map_geodata_drag_drop()

        if self.dlg.q2w_permalink.isChecked():
            self.wegue_conf.add_permalink()

        if self.dlg.q2w_geolocator.isChecked():
            self.wegue_conf.add_geolocator()

        if self.dlg.q2w_overview_map.isChecked():
            self.wegue_conf.add_overview_map()

        if self.dlg.q2w_view_animation.isChecked():
            self.wegue_conf.add_view_animation()

        if self.dlg.q2w_map_recorder.isChecked():
            self.wegue_conf.add_maprecorder()

        if self.dlg.q2w_attribute_table.isChecked():
            self.wegue_conf.add_attribute_table()

        # color
        qt_color = self.dlg.q2w_color_widget.color()
        hex_color = rgb2hex(qt_color.red(), qt_color.green(), qt_color.blue())
        self.wegue_conf.colorTheme = {
            "themes": {
                "light": {
                    "primary": hex_color
                }
            }
        }

        # path for config
        user_input = self.dlg.q2w_file_widget.filePath()
        self.wegue_conf.to_file(user_input)
