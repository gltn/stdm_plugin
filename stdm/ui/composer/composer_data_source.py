"""
/***************************************************************************
Name                 : Composer Data Source Selector
Description          : Widget for selecting a database table or view that will
                       be used across the composition by the STDM data labels.
Date                 : 14/May/2014
copyright            : (C) 2014 by John Gitau
email                : gkahiu@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QWidget,
    QComboBox
)
from qgis.core import QgsLayout

from stdm.composer.composer_data_source import ComposerDataSource
from stdm.composer.layout_utils import LayoutUtils
from stdm.settings import current_profile
from stdm.ui.gui_utils import GuiUtils
from stdm.utils.util import (
    profile_user_tables,
    profile_entities,
    profile_and_user_views
)

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('composer/ui_composer_data_source.ui'))


class ComposerDataSourceSelector(WIDGET, BASE):
    """
    Widget for selecting a database table or view.
    """

    def __init__(self, layout: QgsLayout, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self._layout = layout

        self.cboDataSource.setInsertPolicy(QComboBox.InsertAlphabetically)
        self.cboReferencedTable.setInsertPolicy(QComboBox.InsertAlphabetically)
        self.curr_profile = current_profile()

        # Load reference tables
        self._ref_tables = profile_entities(
            self.curr_profile
        )

        # Load all tables
        self._tables = profile_user_tables(
            self.curr_profile, False
        )
        # Populate referenced tables
        self._populate_referenced_tables()

        # Flag for synchronizing data source item change to referenced table
        self._sync_data_source = False

        # Force views to be loaded
        self.rbViews.setChecked(True)
        self.onShowViews(True, save_change=False)

        # Connect signal
        self.cboDataSource.currentIndexChanged[str].connect(self.onDataSourceSelected)
        self.cboReferencedTable.currentIndexChanged[str].connect(self.on_referenced_table_selected)

        self.cboReferencedTable.setEnabled(False)

        self.rbTables.toggled.connect(self.onShowTables)
        self.rbViews.toggled.connect(self.onShowViews)

    def set_data_source(self, data_source: ComposerDataSource):
        """
        Sets the data_source to show in the widget
        """
        if not data_source.name():
            return

        self.setCategory(data_source.category())
        self.setSelectedSource(data_source.name())
        self.set_referenced_table(
            data_source.referenced_table_name
        )

    def onDataSourceSelected(self, dataSource):
        """
        Slot raised upon selecting a data source from the items.
        """
        # Enable/disable referenced table combo only if an item is selected
        if self.category() == 'View':
            if not dataSource:
                self.cboReferencedTable.setEnabled(False)
            else:
                self.cboReferencedTable.setEnabled(True)

        if self._sync_data_source:
            GuiUtils.set_combo_current_index_by_text(self.cboReferencedTable, dataSource)

        data_source_name = self.cboDataSource.currentData()
        # this causes the QgsLayout.variablesChanged signal to be emitted -- listening objects should hook to this
        LayoutUtils.set_stdm_data_source_for_layout(self._layout, data_source_name)

    def on_referenced_table_selected(self, _):
        """
        Slot raised upon selecting a referenced table
        """
        # this causes the QgsLayout.variablesChanged signal to be emitted -- listening objects should hook to this
        LayoutUtils.set_stdm_referenced_table_for_layout(self._layout, self.referenced_table_name())

    def _populate_referenced_tables(self):
        # Populate combo box with the list of tables names
        self.cboReferencedTable.addItem('')
        for entity in self._ref_tables:
            # Check if there is supporting document
            self.cboReferencedTable.addItem(
                entity.short_name.lower(), entity.name
            )

    @staticmethod
    def _contains_supporting_document(table):
        # Returns true if the table contains 'supporting_document' text
        res = table.find('supporting_document')
        if res == -1:
            return False

        return True

    def category(self):
        """
        Returns the category (view or table) that the data source belongs to.
        """
        if self.rbTables.isChecked():
            return "Table"

        elif self.rbViews.isChecked():
            return "View"

    def setCategory(self, categoryName: str):
        """
        Set selected radio button.
        """
        if categoryName == "Table":
            self.rbTables.setChecked(True)

        elif categoryName == "View":
            self.rbViews.setChecked(True)

    def setSelectedSource(self, dataSourceName):
        """
        Set the data source name if it exists in the list.
        """
        GuiUtils.set_combo_index_by_data(
            self.cboDataSource,
            dataSourceName
        )

    def set_referenced_table(self, referenced_table: str):
        """
        Selects the specified table in the referenced table combobox.
        :param referenced_table: Name of the referenced table.
        :type: str
        """
        if self.category() == 'View':
            GuiUtils.set_combo_index_by_data(
                self.cboReferencedTable,
                referenced_table
            )

    def referenced_table_name(self) -> str:
        """
        :return: Returns the name of the currently selected referenced table
        name.
        :rtype: str
        """
        return self.cboReferencedTable.itemData(
            self.cboReferencedTable.currentIndex()
        )

    def _reset_referenced_table_combo(self):
        # Resets the referenced table combobox based on the category.
        if self.cboReferencedTable.count() > 0:
            self.cboReferencedTable.setCurrentIndex(0)

        category = self.category()
        if category == 'Table':
            self.cboReferencedTable.setEnabled(False)
            self._sync_data_source = True
        else:
            self.cboReferencedTable.setEnabled(True)
            self._sync_data_source = False

    def onShowTables(self, state, save_change=True):
        """
        Slot raised to show STDM database tables.
        """
        if state:
            self._reset_referenced_table_combo()

            self.cboDataSource.clear()
            self.cboDataSource.addItem('')

            for key, value in self._tables.items():
                if not ComposerDataSourceSelector._contains_supporting_document(key):
                    self.cboDataSource.addItem(value.lower(), key)

        if save_change:
            LayoutUtils.set_stdm_data_category_for_layout(self._layout, self.category())

    def onShowViews(self, state, save_change=True):
        """
        Slot raised to show STDM database views.
        """
        if state:
            self._reset_referenced_table_combo()

            self.cboDataSource.clear()
            self.cboDataSource.addItem('')
            profile_user_views = profile_and_user_views(self.curr_profile, True)
            for view in profile_user_views:
                self.cboDataSource.addItem(view, view)

        if save_change:
            LayoutUtils.set_stdm_data_category_for_layout(self._layout, self.category())
