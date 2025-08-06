from silx.utils.enum import Enum as _Enum


class SortType(_Enum):
    ALPHABETICAL = "alphabetical"
    REVERSE_ALPHABETICAL = "reverse alphabetical"
    CREATION_TIME = "creation time"
    REVERSE_CREATION_TIME = "reverse creation time"
    MODIFICATION_TIME = "modification time"
    REVERSE_MODIFICATION_TIME = "reverse modification time"
    FIRST_APPEARANCE = "first appearance"  # first appearance in the workflow
    LAST_APPEARANCE = "last appearance"  # last appearance in the workflow


tooltips = {
    SortType.ALPHABETICAL: "dataset alphabetical order",
    SortType.REVERSE_ALPHABETICAL: "dataset reverse alphabetical order",
    SortType.CREATION_TIME: "dataset creation time order",
    SortType.REVERSE_CREATION_TIME: "dataset reverse creation time order",
    SortType.MODIFICATION_TIME: "dataset modification time",
    SortType.REVERSE_MODIFICATION_TIME: "dataset reverse modification time",
    SortType.FIRST_APPEARANCE: "dataset first appearance on workflow order",
    SortType.LAST_APPEARANCE: "dataset last appearance on workflow order",
}
