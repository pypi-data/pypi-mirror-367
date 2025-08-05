__author__ = "Christian Heider Lindbjerg"
__doc__ = r"""

           Created on 02-12-2020
           """

import time
from typing import Any

# noinspection PyUnresolvedReferences
from qgis.PyQt import QtGui

# noinspection PyUnresolvedReferences
from qgis.PyQt.QtCore import Qt
from warg import Triple

__all__ = ["qt_draw_timestamp"]


def qt_draw_timestamp(
    image: Any,  # QtImage
    font_size: int = 10,
    font_color: Triple = (255, 255, 255),
    font_family: str = "Arial",
    font_style: int = QtGui.QFont.StyleNormal,
    font_weight: int = QtGui.QFont.Normal,
) -> None:
    """

    :param image:
    :param font_size:
    :param font_color:
    :param font_family:
    :param font_style:
    :param font_weight:
    :return:
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    font = QtGui.QFont(font_family, font_size, font_style, font_weight)
    font.setPixelSize(font_size)
    font.setBold(True)

    painter = QtGui.QPainter(image)

    painter.setFont(font)
    painter.setPen(QtGui.QColor(*font_color))
    painter.drawText(
        0,
        0,
        image.width(),
        image.height(),
        Qt.AlignCenter,
        timestamp,
    )

    painter.end()
