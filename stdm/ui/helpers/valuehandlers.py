"""
/***************************************************************************
Name                 : Control Value Handlers
Description          : Classes for getting and setting values for Qt input
                       controls.
Date                 : 27/January/2014
copyright            : (C) 2013 by John Gitau
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

from qgis.PyQt.QtCore import QDate, QDateTime
from qgis.PyQt.QtWidgets import (
    QLineEdit,
    QCheckBox,
    QComboBox,
    QTextEdit,
    QDateEdit,
    QApplication,
    QMessageBox,
    QDateTimeEdit,
    QSpinBox,
    QDoubleSpinBox
)

from stdm.ui.customcontrols.checkable_combo import MultipleChoiceCombo
from stdm.ui.customcontrols.coordinates_editor import CoordinatesWidget
from stdm.ui.customcontrols.multi_select_view import MultipleSelectTreeView
# from stdm.ui.attribute_browser import AttributeBrowser
from stdm.ui.customcontrols.relation_line_edit import (
    AdministrativeUnitLineEdit,
    RelatedEntityLineEdit,
    AutoGeneratedLineEdit,
    ExpressionLineEdit
)
from stdm.ui.foreign_key_mapper import ForeignKeyMapper
from stdm.ui.sourcedocument import SourceDocumentManager
from stdm.utils.util import setComboCurrentIndexWithItemData


class ControlValueHandler(object):
    control = None
    handlers = {}
    '''
    Abstract class that provides a mechanism for subclasses to define how 
    values for specific controls are set and extracted.
    Setter injection of the control.
    '''

    def setControl(self, control):
        self.control = control

    @classmethod
    def register(cls):
        '''
        Used to register control value handler classes for use in the factory.
        '''
        try:
            ctlClassName = cls.controlType.staticMetaObject.className()
            ControlValueHandler.handlers[ctlClassName] = cls
        except AttributeError:
            # Should be logged
            raise AttributeError("Attribute not found")

    def isControlTypeValid(self):
        '''
        Raise type error if the type of control does not match the instance type.
        '''
        if self.control == None or \
                not isinstance(self.control, self.controlType):
            raise TypeError
        else:
            return True

    def value(self):
        raise NotImplementedError

    def setValue(self, value):
        raise NotImplementedError

    def supportsMandatory(self):
        '''
        Indicates whether the control has a default state/value and whether either of these
        states can be used to support mandatory values.
        '''
        raise NotImplementedError

    def clear(self):
        """
        Clears the value.
        """
        raise NotImplementedError

    def default(self):
        '''
        Returns the default value of the control. This complements 'supportsMandatory' method
        for comparison purposes with the current value.
        '''
        raise NotImplementedError


class LineEditValueHandler(ControlValueHandler):
    '''
    QLineEdit text reader.
    '''
    controlType = QLineEdit

    def value(self):
        if self.control.text() == '':
            return self.default()

        return self.control.text()

    def setValue(self, value):
        self.control.setText(value)

    def supportsMandatory(self):
        return True

    def default(self):
        return None

    def clear(self):
        self.control.clear()


LineEditValueHandler.register()


class AdministrativeUnitLineEditValueHandler(LineEditValueHandler):
    """
    Value handler for AdministrativeUnitLineEdit control.
    """
    controlType = AdministrativeUnitLineEdit

    def value(self):
        if not self.control.current_item is None:
            return self.control.current_item.id

        return None

    def setValue(self, value):
        if not value is None:
            self.control.load_current_item_from_id(value)

    def supportsMandatory(self):
        return True

    def default(self):
        return None

    def clear(self):
        self.control.clear()


AdministrativeUnitLineEditValueHandler.register()


class AutoGeneratedLineEditValueHandler(LineEditValueHandler):
    """
    Value handler for AutoGeneratedLineEdit control.
    """
    controlType = AutoGeneratedLineEdit

    def value(self):
        if self.control.text() == '':
            return self.default()

        return self.control.text()

    def setValue(self, value):
        if value is not None:
            self.control.setText(value)

    def supportsMandatory(self):
        return True

    def default(self):
        return None

    def clear(self):
        self.control.clear_line_edit()


AutoGeneratedLineEditValueHandler.register()


class RelatedEntityLineEditValueHandler(AdministrativeUnitLineEditValueHandler):
    """
    Value handler for RelatedEntityLineEdit control.
    """
    controlType = RelatedEntityLineEdit


RelatedEntityLineEditValueHandler.register()


class MultipleSelectTreeViewValueHandler(ControlValueHandler):
    """
    Value handler for MultipleSelectTreeView control.
    """
    controlType = MultipleSelectTreeView

    def value(self):
        return self.control.selection()

    def setValue(self, value):
        if not value is None:
            self.control.set_selection(value)

    def supportsMandatory(self):
        return True

    def default(self):
        return []

    def clear(self):
        self.control.clear_selection()


MultipleSelectTreeViewValueHandler.register()


class CheckBoxValueHandler(ControlValueHandler):
    '''
    QCheckBox state reader.
    '''
    controlType = QCheckBox

    def value(self):
        return self.control.isChecked()

    def setValue(self, value):
        if isinstance(value, str) or \
                isinstance(value, str):
            if value.lower() in ("yes", "true", "t", "1"):
                self.control.setChecked(True)
            else:
                self.control.setChecked(False)
        else:
            if value is None:
                self.control.setChecked(False)
            else:
                self.control.setChecked(value)

    def supportsMandatory(self):
        return False

    def default(self):
        return None

    def clear(self):
        self.control.setChecked(False)


CheckBoxValueHandler.register()


class TextEditValueHandler(LineEditValueHandler):
    '''
    TextEdit value reader.
    '''
    controlType = QTextEdit

    def value(self):
        return self.control.toPlainText()

    def setValue(self, value):
        self.control.setText(value)

    def default(self):
        return None

    def supportsMandatory(self):
        return True

    def clear(self):
        self.control.clear()


TextEditValueHandler.register()


class ComboBoxValueHandler(LineEditValueHandler):
    '''
    Combo box current selection value reader.
    Returns the current displayed string.
    '''
    controlType = QComboBox

    def value(self):
        dataID = self.control.itemData(self.control.currentIndex())

        return dataID

    def setValue(self, value):
        setComboCurrentIndexWithItemData(self.control, value)

    def supportsMandatory(self):
        return True

    def default(self):
        return None

    def clear(self):
        self.control.setCurrentIndex(0)


ComboBoxValueHandler.register()


class DateEditValueHandler(ControlValueHandler):
    '''
    DateEdit value reader.
    '''
    controlType = QDateEdit

    def value(self):
        return self.control.date()

    def setValue(self, value):
        if value is not None:
            try:
                self.control.setDate(value)
            except RuntimeError:
                QMessageBox.warning(
                    None,
                    QApplication.translate(
                        'DateEditValueHandler',
                        "Attribute Table Error"
                    ),
                    'The change is not saved. '
                    'Please use the form to edit data.'
                )
            except TypeError:
                pass

    def default(self):
        return QDate.currentDate()

    def supportsMandatory(self):
        return False

    def clear(self):
        self.control.setDate(QDate.currentDate())


DateEditValueHandler.register()


class DateTimeEditValueHandler(ControlValueHandler):
    '''
    DateTimeEdit value reader.
    '''
    controlType = QDateTimeEdit

    def value(self, for_spatial_unit=False):

        return self.control.dateTime()

    def setValue(self, value, for_spatial_unit=False):

        try:
            self.control.setDateTime(value)
        except RuntimeError:
            QMessageBox.warning(
                None,
                QApplication.translate(
                    'DateTimeEditValueHandler',
                    "Attribute Table Error"
                ),
                'The change is not saved. '
                'Please use the form to edit data.'
            )
        except TypeError:
            pass

    def default(self):
        return QDateTime.currentDateTime()

    def supportsMandatory(self):
        return False

    def clear(self):
        self.control.setDateTime(QDateTime.currentDateTime())


DateTimeEditValueHandler.register()


class SourceDocManagerValueHandler(ControlValueHandler):
    '''
    Source Document Manager value handler.
    '''
    controlType = SourceDocumentManager

    def value(self):
        # Get source document objects
        return self.control.model_objects()

    def setValue(self, value):
        if not value is None:
            self.control.set_source_documents(value)

    def supportsMandatory(self):
        return True

    def default(self):
        return []

    def clear(self):
        self.control.clear()


SourceDocManagerValueHandler.register()


class ForeignKeyMapperValueHandler(ControlValueHandler):
    '''
    ForeignKeyMapper value handler.
    '''
    controlType = ForeignKeyMapper

    def value(self):
        return self.control.entities()

    def setValue(self, value):
        self.control.setEntities(value)

    def default(self):
        return None

    def supportsMandatory(self):
        return True

    def clear(self):
        self.control.remove_rows()


ForeignKeyMapperValueHandler.register()


class SpinBoxValueHandler(ControlValueHandler):
    '''
    QSpinBox value handler.
    '''
    controlType = QSpinBox

    def value(self):
        return self.control.value()

    def setValue(self, value):
        if value != None:
            self.control.setValue(int(value))
        else:
            self.control.setValue(0)

    def supportsMandatory(self):
        return False

    def default(self):
        return None

    def clear(self):
        self.control.clear()


SpinBoxValueHandler.register()


class DoubleSpinBoxValueHandler(ControlValueHandler):
    '''
    QDoubleSpinBox value handler.
    '''
    controlType = QDoubleSpinBox

    def value(self):
        return self.control.value()

    def setValue(self, value):
        if value != None:
            self.control.setValue(float(value))
        else:
            self.control.setValue(0)

    def supportsMandatory(self):
        return False

    def default(self):
        return None

    def clear(self):
        self.control.clear()


DoubleSpinBoxValueHandler.register()


class CoordinatesWidgetValueHandler(ControlValueHandler):
    '''
    Value handler for CoordinatesWidget.
    '''
    controlType = CoordinatesWidget

    def value(self):
        return self.control.toEWKT()

    def setValue(self, value):
        pass

    def supportsMandatory(self):
        return False

    def default(self):
        return None

    def clear(self):
        self.control.clear()


CoordinatesWidgetValueHandler.register()


class MultipleChoiceComboBox(ControlValueHandler):
    controlType = MultipleChoiceCombo

    def value(self):
        ctlValue = self.control.values()
        return ctlValue

    def setValue(self, value):
        if value:
            self.control.set_values(value)

    def default(self):
        return None

    def clear(self):
        self.control.clear()


MultipleChoiceComboBox.register()


class ExpressionLineEditValueHandler(
    LineEditValueHandler, DoubleSpinBoxValueHandler, SpinBoxValueHandler):
    """
    Value handler for AutoGeneratedLineEdit control.
    """
    controlType = ExpressionLineEdit

    def value(self):
        # self.control.on_expression_triggered()
        if self.control.column.output_data_type == 'float':

            if self.control.text() == '':
                return self.default()

            return float(self.control.text())

        if self.control.column.output_data_type == 'int':
            if self.control.text() == '':
                return self.default()

            return int(self.control.text())

        if self.control.column.output_data_type == 'str':
            if self.control.text() == '':
                return self.default()

            return self.control.text()

    def setValue(self, value):

        if value is not None:
            self.control.setText(str(value))

    def supportsMandatory(self):
        return True

    def default(self):
        return None

    def clear(self):

        self.control.clear_line_edit()


ExpressionLineEditValueHandler.register()