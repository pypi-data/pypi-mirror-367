from __future__ import annotations

import fnmatch
from collections import OrderedDict
from typing import Union
import datetime

from silx.gui import qt

from processview.core.dataset import DatasetIdentifier
from processview.core.manager import DatasetState
from processview.core.manager import ProcessManager as _ProcessManager
from processview.core.sorting import SortType, tooltips
from processview.core.superviseprocess import SuperviseProcess
from processview.gui.DropDownWidget import DropDownWidget
from silx.gui import icons
from processview.gui.messagebox import MessageBox
from processview.utils import docstring

_DATASET_STATE_BACKGROUND = {
    DatasetState.ON_GOING: qt.QColor("#839684"),  # light blue
    DatasetState.SUCCEED: qt.QColor("#068c0c"),  # green
    DatasetState.FAILED: qt.QColor("#f52718"),  # red
    DatasetState.PENDING: qt.QColor("#609ab3"),  # blue gray
    DatasetState.SKIPPED: qt.QColor("#f08e0e"),  # light orange
    DatasetState.WAIT_USER_VALIDATION: qt.QColor("#cb34c1"),  # pink
    DatasetState.CANCELLED: qt.QColor("#a4a8a2"),  # light black
}


class ProcessManagerWindow(qt.QMainWindow):
    """
    Main window of the process manager
    """

    def __init__(self, parent):
        qt.QMainWindow.__init__(self, parent)
        self.setWindowFlags(qt.Qt.Widget)

        self._centralWidget = ProcessManagerWidget(parent=self)
        self.setCentralWidget(self._centralWidget)


class ObservationTable(qt.QTableView):
    """
    Redefinition of QTableView for datasets and processes
    """

    def __init__(self, parent):
        qt.QTableView.__init__(self, parent)
        self.verticalHeader().setSectionsClickable(True)

        # QMenu for the dataset name
        self.dataset_menu = qt.QMenu()
        self._copyAction = qt.QAction("copy")
        self.dataset_menu.addAction(self._copyAction)
        self._removeAction = qt.QAction("remove")
        self.dataset_menu.addAction(self._removeAction)

        # QMenu for cell from on dataset and one process
        self.menu_dataset_vs_process = qt.QMenu()
        self._reprocessAction = qt.QAction("reprocess")
        self.menu_dataset_vs_process.addAction(self._reprocessAction)
        self._cancelAction = qt.QAction("cancel")
        self.menu_dataset_vs_process.addAction(self._cancelAction)
        self._infoAction = qt.QAction("info")
        self.menu_dataset_vs_process.addAction(self._infoAction)
        self.menu_dataset_vs_process.addAction(self._removeAction)

        self._target = (None, None)
        # register target of the last menu (process, DatasetIdentifier)

        # connect signal / slot
        self._copyAction.triggered.connect(self._requestDatasetIdCopy)
        self._removeAction.triggered.connect(self._requestRemoveDataset)
        self._reprocessAction.triggered.connect(self._requestReprocessing)
        self._infoAction.triggered.connect(self._requestInfo)
        self._cancelAction.triggered.connect(self._requestCancelProcessing)

    def _processAt(self, x_pos):
        column = self.columnAt(x_pos)
        if column >= 1:
            processes = self.model()._processes
            process_idx = column - 1
            if process_idx < len(processes):
                return processes[list(processes.keys())[process_idx]]

    def _datasetAt(self, y_pos):
        row = self.rowAt(y_pos)
        if row >= 0:
            datasets = self.model()._sorted_datasets
            if row < len(datasets):
                return datasets[list(datasets.keys())[row]]

    def contextMenuEvent(self, event):
        row = self.columnAt(event.pos().x())
        dataset = self._datasetAt(event.pos().y())
        if row == 0:
            # handle column column
            self._target = (None, dataset)
            self.dataset_menu.exec_(event.globalPos())
        else:
            # handle processes column
            process = self._processAt(event.pos().x())
            if (
                process is not None
                and dataset is not None
                and _ProcessManager().met(process=process, dataset=dataset)
            ):
                self._target = (process, dataset)
                self.menu_dataset_vs_process.exec_(event.globalPos())
            else:
                self._target = (None, None)
        super().contextMenuEvent(event)

    def _requestReprocessing(self, *args, **kwargs):
        process, dataset = self._target

        if process is not None and dataset is not None:
            assert isinstance(process, SuperviseProcess)
            assert isinstance(dataset, DatasetIdentifier)
            process.reprocess(dataset.recreate_dataset())

    def _requestCancelProcessing(self, *args, **kwargs):
        process, dataset = self._target
        if process is not None and dataset is not None:
            assert isinstance(process, SuperviseProcess)
            assert isinstance(dataset, DatasetIdentifier)
            process.cancel(dataset.recreate_dataset())

    def _requestDatasetIdCopy(self, *args, **kwargs):
        _, dataset = self._target
        if dataset is not None:
            clipboard = qt.QGuiApplication.clipboard()
            clipboard.setText(dataset.to_str())

    def _requestRemoveDataset(self, *args, **kwargs):
        def get_dataset_at(row: int):
            datasets = self.model()._sorted_datasets
            return datasets.get(
                list(datasets.keys())[row],
                None,
            )

        datasets = [get_dataset_at(index.row()) for index in self.selectedIndexes()]
        [ProcessManager().remove_dataset(dataset) for dataset in datasets]
        self.model().remove_datasets(datasets)

    def _requestInfo(self, *args, **kwargs):
        process, dataset = self._target
        if process is not None and dataset is not None:
            infos = ProcessManager().get_dataset_details(
                dataset=dataset, process=process
            )
            if infos in (None, ""):
                infos = "No extra information provided"

            msg = MessageBox(self)
            msg.setInfos(infos=infos)
            extra_info = "{} processing {}".format(process.name, dataset)
            msg.setWindowTitle(extra_info)
            msg.setWindowModality(qt.Qt.NonModal)
            msg.show()

    def sizeHintForColumn(self, column):
        if column == 0:
            return 350
        else:
            return super().sizeHintForColumn(column)


class ProcessManagerWidget(qt.QWidget):
    """
    Main widget to display dataset vs process metadata
    """

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())

        self._manager = ProcessManager()

        self._optionsWidget = OptionsWidget(parent=self)
        self._dropDownOptionsWidget = DropDownWidget(parent=self)
        self._dropDownOptionsWidget.setWidget(self._optionsWidget)

        self._dropDownOptionsWidget.setSizePolicy(
            qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum
        )
        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(2)
        self.layout().addWidget(self._dropDownOptionsWidget)

        self.observationTable = ObservationTable(self)

        self.layout().addWidget(self.observationTable)
        self.observationTable.setModel(
            _DatasetProcessModel(parent=self.observationTable, header=tuple())
        )
        self.observationTable.resizeColumnsToContents()
        self.observationTable.setSortingEnabled(True)
        self.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

        # connect signal / slot
        self._manager.sigUpdated.connect(self._updateDatasetStates)
        self._manager.sigNewProcessRegistered.connect(self._updateProcesses)
        self._optionsWidget.filterWidget.sigDatasetPatternEditingFinished.connect(
            self._filterUpdated
        )
        self._optionsWidget.filterWidget.sigProcessPatternEditingFinished.connect(
            self._filterUpdated
        )
        self._manager.sigProcessUnregistered.connect(self._updateProcesses)
        self._optionsWidget._orderingWidget.sigSortTypeChanged.connect(
            self.observationTable.model()._setSorting
        )
        self._manager.sigProcessRenamed.connect(self._renameProcess)
        # update to fit existing processes / datasets
        self._updateProcesses()
        self._updateDatasetStates()

    def _updateDatasetStates(self):
        self.observationTable.model().setDatasets(self._manager.get_datasets())

    def _updateProcesses(self):
        self.observationTable.model().setProcesses(self._manager.get_processes())

    def _renameProcess(self, process: SuperviseProcess):
        self.observationTable.model().headerDataChanged.emit(
            qt.Qt.Horizontal, 0, len(self._manager.get_processes())
        )

    def _filterUpdated(self):
        self.observationTable.model().process_patterns = (
            self._dropDownOptionsWidget.getProcessPatterns()
        )
        self._updateProcesses()
        self.observationTable.model().dataset_patterns = (
            self._dropDownOptionsWidget.getDatasetPatterns()
        )
        self._updateDatasetStates()


class _DatasetProcessModel(qt.QAbstractTableModel):
    def __init__(self, parent, header, *args):
        qt.QAbstractTableModel.__init__(self, parent, *args)
        self.header = header
        self._processes = OrderedDict()
        # processes with order as key and Process as value
        self._sorted_datasets = OrderedDict()
        self._unsorted_datasets = OrderedDict()
        self._processPatterns = tuple()
        # is there some process name pattern to follow ?
        self._datasetPatterns = tuple()
        # is there some dataset id pattern to follow ?
        self._sort_type = SortType.FIRST_APPEARANCE

    def _match_dataset_patterns(self, dataset):
        if len(self._datasetPatterns) == 0:
            return True
        for pattern in self._datasetPatterns:
            if fnmatch.fnmatch(str(dataset), pattern):
                return True
        return False

    def _match_process_patterns(self, process):
        if len(self.process_patterns) == 0:
            return True
        for pattern in self._processPatterns:
            if process.name is None or pattern is None:
                continue
            elif fnmatch.fnmatch(process.name, pattern):
                return True
        return False

    @property
    def process_patterns(self):
        return self._processPatterns

    @process_patterns.setter
    def process_patterns(self, patterns):
        self._processPatterns = patterns

    @property
    def dataset_patterns(self):
        return self._datasetPatterns

    @dataset_patterns.setter
    def dataset_patterns(self, patterns):
        self._datasetPatterns = patterns

    def remove_datasets(self, datasets):
        remaining_datasets = list(self._unsorted_datasets)
        for dataset in datasets:
            if not isinstance(dataset, DatasetIdentifier):
                raise ValueError(
                    f"dataset is expected to be a dataset identifier. Get {type(dataset)} instead"
                )
            try:
                remaining_datasets.remove(dataset)
            except Exception:
                pass

        self.setDatasets(remaining_datasets)
        self.endResetModel()

    def clear(self):
        self._processes = OrderedDict()
        self.endResetModel()

    def rowCount(self, parent=None):
        return len(self._unsorted_datasets)

    def columnCount(self, parent=None):
        return len(self._processes) + 1

    def setProcesses(self, processes):
        assert isinstance(processes, (tuple, list))
        self._processes = {}
        processes = list(filter(self._match_process_patterns, processes))
        for i_process, process in enumerate(processes):
            self._processes[i_process] = process
        self.endResetModel()

    @staticmethod
    def sort_datasets(datasets: list, sort_type):
        if sort_type is SortType.FIRST_APPEARANCE:
            pass
        elif sort_type is SortType.LAST_APPEARANCE:
            datasets.reverse()
        elif sort_type in (SortType.ALPHABETICAL, SortType.REVERSE_ALPHABETICAL):
            datasets = sorted(
                datasets,
                key=lambda x: x.name() or "",
                reverse=sort_type is SortType.REVERSE_ALPHABETICAL,
            )
        elif sort_type in (SortType.CREATION_TIME, SortType.REVERSE_CREATION_TIME):
            datasets = sorted(
                datasets,
                key=lambda x: x.creation_time() or datetime.datetime.fromtimestamp(0),
                reverse=sort_type is SortType.REVERSE_CREATION_TIME,
            )
        elif sort_type in (
            SortType.MODIFICATION_TIME,
            SortType.REVERSE_MODIFICATION_TIME,
        ):
            datasets = sorted(
                datasets,
                key=lambda x: x.modification_time()
                or datetime.datetime.fromtimestamp(0),
                reverse=sort_type is SortType.REVERSE_MODIFICATION_TIME,
            )
        else:
            raise ValueError("sort type not handled")
        return datasets

    def setDatasets(self, datasets):
        assert isinstance(datasets, (tuple, list))
        self._unsorted_datasets = datasets
        # filter datasets
        datasets = list(filter(self._match_dataset_patterns, datasets))
        # sort datasets
        datasets = self.sort_datasets(datasets=datasets, sort_type=self._sort_type)

        self._sorted_datasets.clear()
        for i_dataset, dataset in enumerate(datasets):
            self._sorted_datasets[i_dataset] = dataset
        self.endResetModel()

    def headerData(self, col, orientation, role):
        if orientation == qt.Qt.Horizontal and role == qt.Qt.DisplayRole:
            if col == 0:
                return
            else:
                process_idx = col - 1
            if process_idx < len(self._processes):
                return self._processes[process_idx].name
        return None

    def data(self, index, role):
        if index.isValid() is False:
            return None

        if role not in (qt.Qt.DisplayRole, qt.Qt.ToolTipRole, qt.Qt.BackgroundRole):
            return None

        if index.column() == 0:
            # if dataset name
            if role == qt.Qt.DisplayRole:
                return self._sorted_datasets[index.row()].short_description() or str(
                    self._sorted_datasets[index.row()]
                )
            elif role == qt.Qt.ToolTipRole:
                return self._sorted_datasets[index.row()].long_description()
            elif role == qt.Qt.BackgroundRole:
                return qt.QColor("#dedede")
            else:
                return

        dataset_short_name = self._sorted_datasets[index.row()]
        process_name = self._processes[index.column() - 1]
        dataset_process_state = ProcessManager().get_dataset_state(
            dataset=dataset_short_name, process=process_name
        )
        dataset_process_details = ProcessManager().get_dataset_details(
            dataset=dataset_short_name, process=process_name
        )
        if role == qt.Qt.BackgroundRole:
            if dataset_process_state is None:
                # if "unmet"
                return qt.QColor("#ffffff")
            else:
                return _DATASET_STATE_BACKGROUND[dataset_process_state]
        elif role == qt.Qt.DisplayRole:
            if dataset_process_state is None:
                return ""
            else:
                return dataset_process_state.value
        if role == qt.Qt.ToolTipRole:
            if dataset_process_details is None:
                return ""
            else:
                return dataset_process_details

    def _setSorting(self, sort_type: SortType):
        sort_type = SortType.from_value(sort_type)
        changed = self._sort_type is not sort_type
        if changed:
            self._sort_type = sort_type
            self.setDatasets(datasets=self._unsorted_datasets)
            self.layoutChanged.emit()


class OptionsWidget(qt.QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.setLayout(qt.QGridLayout())

        # dataset ordering
        self._orderingWidget = _OrderingWidget(parent=self)
        self.layout().setContentsMargins(2, 2, 2, 2)
        self.layout().setSpacing(0)
        self.layout().addWidget(self._orderingWidget, 2, 1, 3, 3)

        # filtering
        self._filterWidget = _FilterWidget(parent=self)
        self.layout().setContentsMargins(2, 2, 2, 2)
        self.layout().setSpacing(0)
        self.layout().addWidget(self._filterWidget, 4, 1, 3, 3)

    @property
    def filterWidget(self):
        return self._filterWidget

    # expose API
    def getProcessPatterns(self):
        return self._filterWidget.getProcessPatterns()

    def getDatasetPatterns(self):
        return self._filterWidget.getDatasetPatterns()


class _FilterWidget(qt.QWidget):
    """
    Widget to define some filtering pattern on dataset and / or processes
    """

    sigProcessPatternEditingFinished = qt.Signal()
    """signal emit when the process pattern editing finished"""

    sigDatasetPatternEditingFinished = qt.Signal()
    """signal emit when the dataset pattern editing finished"""

    def __init__(self, parent=None, name=" filter", font_size=12, icon_size=20):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())
        self.layout().setSpacing(2)
        self.layout().setContentsMargins(0, 0, 0, 0)

        font = self.font()
        font.setPixelSize(font_size)
        self.setFont(font)

        icon = icons.getQPixmap("processview:gui/icons/magnifying_glass")
        self._researchLabelIcon = qt.QLabel("", parent=self)
        self._researchLabelIcon.setPixmap(icon)
        self.layout().addWidget(qt.QLabel(name, self), 0, 1, 1, 1)
        self.layout().addWidget(self._researchLabelIcon, 0, 2, 1, 1)

        # filter by dataset id / name
        self._datasetLabel = qt.QLabel("dataset", self)
        self.layout().addWidget(self._datasetLabel, 1, 2, 1, 2)
        self._datasetPatternLE = qt.QLineEdit("", self)
        self.layout().addWidget(self._datasetPatternLE, 1, 4, 1, 1)
        tooltip = (
            "Provide one or several dataset name or pattern to only "
            " display those datasets. Pattern should be separated by a "
            "semi colon. Handle linux wild card. Example: "
            "`pattern1; *suffix; prefix*`"
        )
        for widget in self._datasetLabel, self._datasetPatternLE:
            widget.setToolTip(tooltip)
        self._clearDatasetPatternPB = qt.QPushButton("clear", self)
        self._clearDatasetPatternPB.setAutoDefault(True)
        self.layout().addWidget(self._clearDatasetPatternPB, 1, 5, 1, 1)

        # filter by process name
        self._processLabel = qt.QLabel("process", self)
        self.layout().addWidget(self._processLabel, 2, 2, 1, 2)
        self._processPatternLE = qt.QLineEdit("", self)
        self.layout().addWidget(self._processPatternLE, 2, 4, 1, 1)
        tooltip = (
            "Provide one or several process name or pattern to only "
            " display those datasets. Pattern should be separated by a "
            "semi colon. Handle linux wild card. Example: "
            "`pattern1; *suffix; prefix*`"
        )
        for widget in self._processLabel, self._processPatternLE:
            widget.setToolTip(tooltip)
        self._clearProcessPatternPB = qt.QPushButton("clear", self)
        self._clearProcessPatternPB.setAutoDefault(True)
        self.layout().addWidget(self._clearProcessPatternPB, 2, 5, 1, 1)

        # connect signal / slot
        self._clearProcessPatternPB.released.connect(self._processPatternLE.clear)
        self._clearProcessPatternPB.released.connect(
            self._processPatternEditingFinished
        )
        self._clearDatasetPatternPB.released.connect(self._datasetPatternLE.clear)
        self._clearDatasetPatternPB.released.connect(
            self._datasetPatternEditingFinished
        )
        self._datasetPatternLE.editingFinished.connect(
            self._datasetPatternEditingFinished
        )
        self._processPatternLE.editingFinished.connect(
            self._processPatternEditingFinished
        )

    def getProcessPatterns(self) -> tuple:
        patterns = self._processPatternLE.text().lstrip(" ").rstrip(" ")
        if patterns == "":
            return ("*",)
        res = patterns.replace(" ", "")
        return tuple(res.split(";"))

    def getDatasetPatterns(self) -> tuple:
        patterns = self._datasetPatternLE.text().lstrip(" ").rstrip(" ")
        if patterns == "":
            return ("*",)
        res = patterns.replace(" ", "")
        return tuple(res.split(";"))

    def _datasetPatternEditingFinished(self, *args, **kwargs):
        self.sigDatasetPatternEditingFinished.emit()

    def _processPatternEditingFinished(self, *args, **kwargs):
        self.sigProcessPatternEditingFinished.emit()


class _OrderingWidget(qt.QWidget):
    """Widget to let the user define the ordering of datasets"""

    sigSortTypeChanged = qt.Signal(str)
    """emit when sort type changed. Paramater is the name of the new sorting type"""

    def __init__(self, parent=None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.setLayout(qt.QFormLayout())
        self._sortingTypeCB = qt.QComboBox(self)
        for sort_type in SortType.members():
            self._sortingTypeCB.addItem(sort_type.value)
            self._sortingTypeCB.setItemData(
                self._sortingTypeCB.findText(sort_type.value),
                tooltips[sort_type],
                qt.Qt.ToolTipRole,
            )
        self.layout().addRow("sorting", self._sortingTypeCB)

        # set up
        self._sortingTypeCB.setCurrentIndex(
            self._sortingTypeCB.findText(SortType.FIRST_APPEARANCE.value)
        )

        # connect signal / slot
        self._sortingTypeCB.currentIndexChanged.connect(self._changed)

    def _changed(self, *args, **kwargs):
        self.sigSortTypeChanged.emit(self.getCurrentSort().value)

    def getCurrentSort(self) -> SortType:
        return SortType.from_value(self._sortingTypeCB.currentText())


class ProcessManager(qt.QObject):
    sigUpdated = qt.Signal()
    """Signal emitted when the state of some process / dataset is updated
    """

    sigNewProcessRegistered = qt.Signal()
    """Signal emitted when a new process is registered"""

    sigProcessUnregistered = qt.Signal()
    """Signal emitted when a process is unregistered"""

    sigProcessRenamed = qt.Signal(SuperviseProcess)
    """Emit when the process is renamed"""

    def __init__(self):
        qt.QObject.__init__(self)
        self.manager = _ProcessManager()

        # monkey patch manager updated function
        # TODO: add / remove callback would be simpler
        self.manager.add_update_callback(self.updated)
        self.manager.add_new_process_callback(self.processAdded)
        self.manager.add_process_removed_callback(self.processRemoved)
        self.manager.add_process_name_changed_callback(self.processRenamed)

    def updated(self):
        self.sigUpdated.emit()

    def processAdded(self):
        self.sigNewProcessRegistered.emit()

    def processRemoved(self):
        self.sigProcessUnregistered.emit()

    def processRenamed(self, process):
        self.sigProcessRenamed.emit(process)

    def destroyed(self, object_):
        self.manager.remove_update_callback(self.updated)
        qt.QObject.destroyed(object_)

    # expose some of the original ProcessManager API
    @docstring(_ProcessManager)
    def notify_dataset_state(self, dataset, process, state, details=None) -> None:
        self.manager.notify_dataset_state(
            dataset=dataset, process=process, state=state, details=details
        )

    @docstring(_ProcessManager)
    def get_dataset_state(self, dataset, process) -> Union[None, DatasetState]:
        return self.manager.get_dataset_state(dataset_id=dataset, process=process)

    @docstring(_ProcessManager)
    def get_dataset_details(self, dataset, process) -> Union[None, DatasetState]:
        return self.manager.get_dataset_details(dataset_id=dataset, process=process)

    @docstring(_ProcessManager)
    def get_dataset_stream(self, dataset, time_stamp=False) -> tuple:
        return self.manager.get_dataset_stream(dataset=dataset, time_stamp=time_stamp)

    @docstring(_ProcessManager)
    def get_process_history(self, process, time_stamp=False) -> tuple:
        return self.manager.get_process_history(process=process, time_stamp=time_stamp)

    @docstring(_ProcessManager)
    def get_processes(self):
        return self.manager.get_processes()

    @docstring(_ProcessManager)
    def get_datasets(self):
        return self.manager.get_datasets()

    def remove_dataset(self, *args, **kwargs):
        return self.manager.remove_dataset(*args, **kwargs)
