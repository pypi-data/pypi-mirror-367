#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.11.21 20:00:00                  #
# ================================================== #

from PySide6 import QtCore
from PySide6.QtGui import QStandardItemModel, Qt, QIcon
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QSplitter, QWidget, QSizePolicy

from pygpt_net.core.types import (
    MODE_AGENT,
    MODE_EXPERT,
)
from pygpt_net.ui.widget.element.labels import HelpLabel, TitleLabel
from pygpt_net.ui.widget.lists.preset import PresetList
from pygpt_net.ui.layout.toolbox.footer import Footer
from pygpt_net.utils import trans
import pygpt_net.icons_rc

class Presets:
    def __init__(self, window=None):
        """
        Toolbox UI

        :param window: Window instance
        """
        self.window = window
        self.footer = Footer(window)
        self.id = 'preset.presets'

    def setup(self) -> QSplitter:
        """
        Setup presets

        :return: QSplitter
        """
        presets = self.setup_presets()

        self.window.ui.models['preset.presets'] = self.create_model(self.window)
        self.window.ui.nodes['preset.presets'].setModel(self.window.ui.models['preset.presets'])

        self.window.ui.nodes['presets.widget'] = QWidget()
        self.window.ui.nodes['presets.widget'].setLayout(presets)
        self.window.ui.nodes['presets.widget'].setMinimumHeight(180)
        self.window.ui.nodes['presets.widget'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return self.window.ui.nodes['presets.widget']

    def setup_presets(self) -> QVBoxLayout:
        """
        Setup list

        :return: QVBoxLayout
        """
        self.window.ui.nodes['preset.presets.new'] = QPushButton(QIcon(":/icons/add.svg"), "")
        self.window.ui.nodes['preset.presets.new'].clicked.connect(
            lambda: self.window.controller.presets.editor.edit()
        )

        self.window.ui.nodes['preset.presets.label'] = TitleLabel(trans("toolbox.presets.label"))
        self.window.ui.nodes['preset.agents.label'] = TitleLabel(trans("toolbox.agents.label"))
        self.window.ui.nodes['preset.experts.label'] = TitleLabel(trans("toolbox.experts.label"))
        self.window.ui.nodes['preset.presets.label'].setVisible(False)
        self.window.ui.nodes['preset.agents.label'].setVisible(False)
        self.window.ui.nodes['preset.experts.label'].setVisible(False)

        header = QHBoxLayout()
        header.addWidget(self.window.ui.nodes['preset.presets.label'])
        header.addWidget(self.window.ui.nodes['preset.agents.label'])
        header.addWidget(self.window.ui.nodes['preset.experts.label'])
        header.addWidget(self.window.ui.nodes['preset.presets.new'], alignment=Qt.AlignRight)
        header.setContentsMargins(5, 0, 0, 0)

        header_widget = QWidget()
        header_widget.setLayout(header)

        self.window.ui.nodes[self.id] = PresetList(self.window, self.id)
        self.window.ui.nodes[self.id].selection_locked = self.window.controller.presets.preset_change_locked
        self.window.ui.nodes[self.id].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.window.ui.nodes['tip.toolbox.presets'] = HelpLabel(trans('tip.toolbox.presets'), self.window)
        self.window.ui.nodes['tip.toolbox.presets'].setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(header_widget)
        layout.addWidget(self.window.ui.nodes[self.id], 1)
        layout.addWidget(self.window.ui.nodes['tip.toolbox.presets'])
        layout.setContentsMargins(2, 5, 5, 5)

        self.window.ui.models[self.id] = self.create_model(self.window)
        self.window.ui.nodes[self.id].setModel(self.window.ui.models[self.id])

        return layout

    def create_model(self, parent) -> QStandardItemModel:
        """
        Create list model
        :param parent: parent widget
        :return: QStandardItemModel
        """
        return QStandardItemModel(0, 1, parent)

    def update_presets(self, data):
        """
        Update presets list

        :param data: Data to update
        """
        mode = self.window.core.config.get('mode')

        # store previous selection
        self.window.ui.nodes[self.id].backup_selection()
        self.window.ui.models[self.id].removeRows(0, self.window.ui.models[self.id].rowCount())
        i = 0
        for n in data:
            self.window.ui.models[self.id].insertRow(i)
            name = data[n].name

            # show disabled in expert mode
            if mode == MODE_EXPERT and not n.startswith("current.") and data[n].enabled:
                name = "[x] " + name
            elif mode == MODE_AGENT:
                num_experts = self.window.core.experts.count_experts(n)
                if num_experts > 0:
                    name = name + " (" + str(num_experts) + " experts)"

            prompt = str(data[n].prompt)
            if len(prompt) > 80:
                prompt = prompt[:80] + '...'  # truncate to max 8 chars
            tooltip = prompt
            index = self.window.ui.models[self.id].index(i, 0)
            self.window.ui.models[self.id].setData(index, tooltip, QtCore.Qt.ToolTipRole)
            self.window.ui.models[self.id].setData(self.window.ui.models[self.id].index(i, 0), name)
            i += 1

        # restore previous selection
        self.window.ui.nodes[self.id].restore_selection()
