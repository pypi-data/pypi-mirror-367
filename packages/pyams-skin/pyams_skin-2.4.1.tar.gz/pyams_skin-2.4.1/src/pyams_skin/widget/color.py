#
# Copyright (c) 2015-2023 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_skin.widget.color module

This module defines the widget which is used to handle color input.
"""

from zope.interface import implementer_only

from pyams_form.browser.text import TextWidget
from pyams_form.interfaces.widget import IFieldWidget
from pyams_form.widget import FieldWidget
from pyams_layer.interfaces import IFormLayer
from pyams_skin.interfaces.widget import IColorWidget
from pyams_utils.adapter import adapter_config
from pyams_utils.schema import IColorField

__docformat__ = 'restructuredtext'


@implementer_only(IColorWidget)
class ColorWidget(TextWidget):
    """Color widget"""


@adapter_config(required=(IColorField, IFormLayer),
                provides=IFieldWidget)
def ColorFieldWidget(field, request):
    """Color field widget factory"""
    return FieldWidget(field, ColorWidget(request))
