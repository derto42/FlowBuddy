from __future__ import annotations

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel

from addon import AddOnBase
from addons.shortcuts.dialog import GroupDialog, REJECTED
from ui.utils import get_font

from . import shortcuts_save as Data

from ui import (
    BaseWindow,
    GrnButton,
    REJECTED,
)

from .nodes import (
    GroupNode,
    SubNodeManager,
    TaskNode
)

from settings import apply_ui_scale as scaled


add_on_base = AddOnBase()
add_on_base.set_icon_path("icon.png")
add_on_base.set_name("Shortcuts")


class MainWindow(BaseWindow):
    def __init__(self) -> None:
        super().__init__(hide_title_bar = False)
        
        self._edit_mode: bool = False
        
        self.toggle_window = lambda: window.show() if window.isHidden() else window.hide()

        self.setContentsMargins(x := scaled(15), x, x, x)
        self.setMinimumSize(scaled(110), scaled(76))
        
        self.setLayout(layout := QVBoxLayout())
        layout.addLayout(nodes_layout := QVBoxLayout())
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        nodes_layout.setContentsMargins(0, 0, 0, 0)
        nodes_layout.setSpacing(0)
        self._nodes_layout = nodes_layout

        self._group_nodes_manager = SubNodeManager(nodes_layout, self)
        
        layout.addLayout(add_new_group_layout := QHBoxLayout())
        self._setup_add_new_group_button(add_new_group_layout)
        
        
        for group_id in Data.load_groups():
            group_class = Data.get_group_by_id(group_id)
            self._add_group_node(group_class)
                
        self.yel_button.clicked.connect(self._toggle_edit_mode)
        self.red_button.clicked.connect(self.hide)
        

    def _setup_add_new_group_button(self, add_new_group_layout: QHBoxLayout):
        """Creates 'Add New Group' label and green button and places that on add_new_group_layout."""
        add_new_group_layout.setContentsMargins(0, scaled(25), 0, 0)
        add_new_group_layout.setSpacing(0)
        
        add_group_label = QLabel("Add New Group", self)
        add_group_label.setFont(get_font(size=scaled(24), weight="semibold"))
        add_group_label.setStyleSheet("color: #ABABAB")

        add_group_button = GrnButton(self, "radial")
        add_group_button.clicked.connect(self._on_add_group_button)
        add_group_button.setToolTip("Add Group")

        add_new_group_layout.addWidget(add_group_label)
        add_new_group_layout.addSpacing(scaled(13))
        add_new_group_layout.addWidget(add_group_button)
        add_new_group_layout.addStretch()
        
        self._add_new_group_label = add_group_label
        self._add_new_group_button = add_group_button
        self._add_new_group_layout = add_new_group_layout
        
        self._update_edit_mode()

    def _add_group_node(self, group_class: Data.GroupClass) -> None:
        group_node = GroupNode(group_class, self)
        self._group_nodes_manager.add_node(group_node)
        self._update_edit_mode()
        group_node.task_node_departed_signal.connect(self._on_task_node_departed)
        
    def _on_add_group_button(self) -> None:
        dialog = GroupDialog(self)
        if dialog.exec() != REJECTED:
            res = dialog.result()
            self._add_group_node(Data.GroupClass(res))
        
    def _update_edit_mode(self) -> None:
        self._group_nodes_manager.set_edit_mode(self._edit_mode)
        self._add_new_group_label.setHidden(not self._edit_mode)
        self._add_new_group_button.setHidden(not self._edit_mode)
        self._add_new_group_layout.setContentsMargins(0, scaled(25) if self._edit_mode else 0, 0, 0)
        self.adjustSize()
        
    def _toggle_edit_mode(self) -> None:
        self._edit_mode = not self._edit_mode
        self._update_edit_mode()
        
    def _on_task_node_departed(self, task_node: TaskNode) -> None:
        print(f"{self._nodes[task_node.task_class.task_id]} is departed from {self._nodes[Data.get_group_id_of_task(task_node.task_class.task_id)]}.")
        # XXX: Should be implemented
        
        
    def get_first_node(self) -> GroupNode:
        return self.layout().itemAt(0).layout().itemAt(0).widget()

    @property
    def _nodes(self) -> dict[str, GroupNode | TaskNode]:
        """This property is used to keep all the nodes accessible via its save data id."""
        return {**GroupNode.nodes, **TaskNode.nodes}


window = MainWindow()
add_on_base.activate = window.toggle_window