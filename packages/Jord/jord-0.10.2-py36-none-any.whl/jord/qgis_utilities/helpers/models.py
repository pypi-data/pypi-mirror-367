__author__ = "Christian Heider Lindbjerg"
__doc__ = r"""

           Created on 02-12-2020
           """

from typing import Any, Optional, Tuple

# noinspection PyUnresolvedReferences
from qgis.PyQt import QtCore

__all__ = ["MyTableModel"]


# noinspection PyPep8Naming
class MyTableModel(QtCore.QAbstractTableModel):
    """
    A model that can be used to display a table of data.

    :param data: The data to display.
    :param parent: The parent object.

    """

    def __init__(self, data: Tuple = (()), parent: Any = None):
        super().__init__(parent)
        self.data = data

    # noinspection PyMethodMayBeStatic
    def headerData(
        self, section: int, orientation: QtCore.Qt.Orientation, role: int
    ) -> str:  # Do not rename
        """

        :param section:
        :param orientation:
        :param role:
        :return:
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return f"Column {str(section)}"
            else:
                return f"Row {str(section)}"

    def columnCount(self, parent: Any = None) -> int:  # Do not rename
        """

        :param parent:
        :return:
        """
        if self.rowCount():
            return len(self.data[0])
        return 0

    def rowCount(self, parent: Any = None) -> int:
        """

        :param parent:
        :return:
        """
        return len(self.data)

    def data(self, index: QtCore.QModelIndex, role: int) -> Optional[str]:
        """

        :param index:
        :param role:
        :return:
        """
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()
            return str(self.data[row][col])
