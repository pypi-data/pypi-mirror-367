#
# Copyright (c) 2015-2024 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_skin.widget.decimal module

This module provides adapters for custom Decimal fields.
"""

from decimal import Decimal, InvalidOperation

from pyams_form.converter import BaseDataConverter, FormatterValidationError
from pyams_form.interfaces import IDataConverter
from pyams_form.interfaces.widget import IWidget
from pyams_utils.adapter import adapter_config
from pyams_utils.schema import IDottedDecimalField

__docformat__ = 'restructuredtext'

from pyams_skin import _


@adapter_config(required=(IDottedDecimalField, IWidget),
                provides=IDataConverter)
class DottedDecimalDataConverter(BaseDataConverter):
    """Dotted decimal field data converter"""

    error_message = _('The entered value is not a valid decimal literal.')

    def toWidgetValue(self, value):
        if not value:
            return self.field.missing_value
        return value

    def toFieldValue(self, value):
        if value is self.field.missing_value:
            return ''
        if not value:
            return None
        try:
            return Decimal(value)
        except InvalidOperation:
            raise FormatterValidationError(self.error_message, value)
