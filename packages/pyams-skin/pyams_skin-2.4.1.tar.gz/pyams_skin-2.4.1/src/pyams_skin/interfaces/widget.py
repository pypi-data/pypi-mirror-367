#
# Copyright (c) 2015-2020 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_skin.interfaces.widget module

This module defines interfaces and templates for standard and custom forms widgets and buttons.
"""

from zope.interface import Attribute, Interface
from zope.schema import TextLine
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from pyams_form.interfaces import DISPLAY_MODE, INPUT_MODE
from pyams_form.interfaces.widget import IButtonWidget as IButtonWidgetBase, \
    ICheckBoxWidget, IMultiWidget, IObjectWidget, IOrderedSelectWidget, IPasswordWidget, \
    ISelectWidget, ISequenceWidget, ISubmitWidget as ISubmitWidgetBase, ITextAreaWidget, \
    ITextLinesWidget, ITextWidget, IWidget
from pyams_form.template import override_widget_layout, override_widget_template, \
    widget_template_config
from pyams_layer.interfaces import IPyAMSLayer


__docformat__ = 'restructuredtext'


#
# General widgets layouts
#

override_widget_layout(IWidget,
                       mode=INPUT_MODE,
                       template='templates/widget-layout.pt', layer=IPyAMSLayer)

override_widget_layout(IWidget,
                       mode=DISPLAY_MODE,
                       template='templates/widget-layout.pt', layer=IPyAMSLayer)


#
# Object widgets templates
#

override_widget_layout(IObjectWidget,
                       mode=INPUT_MODE,
                       template='templates/object-layout.pt', layer=IPyAMSLayer)

override_widget_layout(IObjectWidget,
                       mode=DISPLAY_MODE,
                       template='templates/object-layout.pt', layer=IPyAMSLayer)


override_widget_template(IObjectWidget,
                         mode=INPUT_MODE,
                         template='templates/object-input.pt', layer=IPyAMSLayer)

override_widget_template(IObjectWidget,
                         mode=DISPLAY_MODE,
                         template='templates/object-display.pt', layer=IPyAMSLayer)


#
# Buttons interfaces and templates
#

@widget_template_config(mode=INPUT_MODE,
                        template='templates/submit-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/submit-display.pt', layer=IPyAMSLayer)
class ISubmitWidget(ISubmitWidgetBase):
    """Submit button widget interface"""


@widget_template_config(mode=INPUT_MODE,
                        template='templates/button-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/button-display.pt', layer=IPyAMSLayer)
class IActionWidget(IButtonWidgetBase):
    """Secondary button widget interface"""


@widget_template_config(mode=INPUT_MODE,
                        template='templates/reset-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/reset-display.pt', layer=IPyAMSLayer)
class IResetWidget(IButtonWidgetBase):
    """Reset button widget interface"""


@widget_template_config(mode=INPUT_MODE,
                        template='templates/close-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/close-display.pt', layer=IPyAMSLayer)
class ICloseWidget(IButtonWidgetBase):
    """Close button widget interface"""


#
# Standard PyAMS_form widgets templates
#

override_widget_template(ITextWidget,
                         mode=INPUT_MODE,
                         template='templates/text-input.pt', layer=IPyAMSLayer)
override_widget_template(ITextWidget,
                         mode=DISPLAY_MODE,
                         template='templates/text-display.pt', layer=IPyAMSLayer)


@widget_template_config(mode=INPUT_MODE,
                        template='templates/text-copy-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/text-copy-display.pt', layer=IPyAMSLayer)
class ITextCopyWidget(ITextWidget):
    """Text widget with copy button"""


override_widget_template(ITextAreaWidget,
                         mode=INPUT_MODE,
                         template='templates/textarea-input.pt', layer=IPyAMSLayer)
override_widget_template(ITextAreaWidget,
                         mode=DISPLAY_MODE,
                         template='templates/textarea-display.pt', layer=IPyAMSLayer)


override_widget_template(ITextLinesWidget,
                         mode=INPUT_MODE,
                         template='templates/textlines-input.pt', layer=IPyAMSLayer)
override_widget_template(ITextLinesWidget,
                         mode=DISPLAY_MODE,
                         template='templates/textlines-display.pt', layer=IPyAMSLayer)


override_widget_template(IPasswordWidget,
                         mode=INPUT_MODE,
                         template='templates/password-input.pt', layer=IPyAMSLayer)
override_widget_template(IPasswordWidget,
                         mode=DISPLAY_MODE,
                         template='templates/password-display.pt', layer=IPyAMSLayer)


override_widget_template(ICheckBoxWidget,
                         mode=INPUT_MODE,
                         template='templates/checkbox-input.pt', layer=IPyAMSLayer)
override_widget_template(ICheckBoxWidget,
                         mode=DISPLAY_MODE,
                         template='templates/checkbox-display.pt', layer=IPyAMSLayer)


override_widget_template(ISelectWidget,
                         mode=INPUT_MODE,
                         template='templates/select-input.pt', layer=IPyAMSLayer)
override_widget_template(ISelectWidget,
                         mode=DISPLAY_MODE,
                         template='templates/select-display.pt', layer=IPyAMSLayer)


override_widget_template(IOrderedSelectWidget,
                         mode=INPUT_MODE,
                         template='templates/ordered-select-input.pt', layer=IPyAMSLayer)


#
# Date/time widgets interfaces
#

@widget_template_config(mode=INPUT_MODE,
                        template='templates/datetime-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/datetime-display.pt', layer=IPyAMSLayer)
class IDatetimeWidget(ITextWidget):
    """Datetime widget interface"""


@widget_template_config(mode=INPUT_MODE,
                        template='templates/date-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/date-display.pt', layer=IPyAMSLayer)
class IDateWidget(ITextWidget):
    """Date widget interface"""


@widget_template_config(mode=INPUT_MODE,
                        template='templates/time-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/time-display.pt', layer=IPyAMSLayer)
class ITimeWidget(ITextWidget):
    """Time widget interface"""


#
# Colorpicker widget interface
#

@widget_template_config(mode=INPUT_MODE,
                        template='templates/color-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/color-display.pt', layer=IPyAMSLayer)
class IColorWidget(ITextWidget):
    """Color widget interface"""


#
# Custom Dict field widget interface
#

class IDictWidget(ITextAreaWidget):
    """Custom mapping widget interface"""
    
    
#
# Dynamic select widget interface
#

class IDynamicSelectWidget(ISelectWidget):
    """Dynamic select widget interface

    This interface is used to mark select widgets which are used to select values from
    vocabularies which are not defined statically but which are filled dynamically on
    user input.
    """

    term_factory = Attribute("Factory used to create select term from a given value")


#
# HTML editor widget interfaces
#

class IHTMLEditorConfiguration(Interface):
    """HTML editor configuration interface"""


@widget_template_config(mode=INPUT_MODE,
                        template='templates/html-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/html-display.pt', layer=IPyAMSLayer)
class IHTMLWidget(ITextWidget):
    """HTML editor widget interface"""

    editor_data = Attribute("Custom editor data")


#
# HTTP method selector widget interface
#

HTTP_METHODS = ('GET', 'POST', 'PUT', 'PATCH', 'HEAD', 'OPTIONS', 'DELETE')

HTTP_METHODS_VOCABULARY = SimpleVocabulary([
    SimpleTerm(v) for v in HTTP_METHODS
])


@widget_template_config(mode=INPUT_MODE,
                        template='templates/http-method-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/http-method-display.pt', layer=IPyAMSLayer)
class IHTTPMethodWidget(IWidget):
    """HTTP method selector widget interface"""


#
# Ordered list widget interface
#

@widget_template_config(mode=INPUT_MODE,
                        template='templates/ordered-list-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/ordered-list-display.pt', layer=IPyAMSLayer)
class IOrderedListWidget(ISequenceWidget):
    """Ordered list widget marker interface"""

    separator = TextLine(title="Values separator")


#
# Dates and datetimes range widget
#

@widget_template_config(mode=INPUT_MODE,
                        template='templates/dates-range-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/dates-range-display.pt', layer=IPyAMSLayer)
class IDatesRangeWidget(IMultiWidget):
    """Dates range widget marker interface"""


@widget_template_config(mode=INPUT_MODE,
                        template='templates/dates-range-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/dates-range-display.pt', layer=IPyAMSLayer)
class IDatetimesRangeWidget(IMultiWidget):
    """Datetimes range widget marker interface"""


#
# Thumbnails selection widget
#

@widget_template_config(mode=INPUT_MODE,
                        template='templates/bootstrap-selection-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/bootstrap-selection-display.pt', layer=IPyAMSLayer)
class IBootstrapThumbnailsSelectionWidget(IWidget):
    """Bootstrap thumbnails selection widget"""


@widget_template_config(mode=INPUT_MODE,
                        template='templates/bootstrap-devices-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/bootstrap-devices-display.pt', layer=IPyAMSLayer)
class IBootstrapDevicesBooleanWidget(IWidget):
    """Bootstrap devices boolean widget"""
