import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.gui import QgsFileWidget

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'qgis2wegue_dialog_base.ui'))


class qgis2wegueDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(qgis2wegueDialog, self).__init__(parent)
        self.setupUi(self)
