from silx.gui import qt


class DropDownWidget(qt.QWidget):
    """Simple 'dropdown' widget"""

    _BUTTON_ICON = qt.QStyle.SP_ToolBarVerticalExtensionButton  # noqa

    def __init__(self, parent, direction=qt.Qt.LeftToRight):
        super().__init__(parent)

        self.setLayout(qt.QGridLayout())
        # toggable button
        self._toggleButton = qt.QPushButton("", self)
        self._toggleButton.setCheckable(True)
        self._toggleButton.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        spacer = qt.QWidget()
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)

        if direction == qt.Qt.LeftToRight:
            self.layout().addWidget(self._toggleButton, 0, 0, 1, 1)
            self.layout().addWidget(spacer, 0, 1, 1, 1)
        else:
            self.layout().addWidget(spacer, 0, 0, 1, 1)
            self.layout().addWidget(self._toggleButton, 0, 1, 1, 1)

        self._mainWidget = None

        # set up interface
        self.layout().setContentsMargins(2, 2, 2, 2)
        self.layout().setSpacing(0)

        self._setButtonIcon(show=True)
        self._toggleButton.setChecked(True)

        # connect signal / slot
        self._toggleButton.toggled.connect(self._toggleVisibility)

    def setWidget(self, widget: qt.QWidget):
        if self._mainWidget is not None:
            self.layout().removeWidget(self._mainWidget)

        self._mainWidget = widget
        self.layout().addWidget(self._mainWidget, 1, 0, 2, 2)

    def _setButtonIcon(self, show):
        style = qt.QApplication.instance().style()
        # return a QIcon
        icon = style.standardIcon(self._BUTTON_ICON)
        if show is True:
            pixmap = icon.pixmap(32, 32).transformed(qt.QTransform().scale(1, -1))
            icon = qt.QIcon(pixmap)
        self._toggleButton.setIcon(icon)

    def _toggleVisibility(self, visible):
        self._setButtonIcon(show=visible)
        self._mainWidget.setVisible(visible)

    def setChecked(self, checked: bool):
        self._toggleButton.setChecked(checked)
