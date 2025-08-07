#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_skin.widget.datetime module

This module defines widgets which are used to handle date, time and
datetime inputs.
"""

from zope.interface import implementer_only
from zope.schema.interfaces import IDate, IDatetime, ITime

from pyams_form.browser.multi import MultiWidget
from pyams_form.browser.text import TextWidget
from pyams_form.converter import BaseDataConverter
from pyams_form.interfaces import IDataConverter
from pyams_form.interfaces.widget import IFieldWidget
from pyams_form.widget import FieldWidget
from pyams_layer.interfaces import IFormLayer
from pyams_skin.interfaces.widget import IDateWidget, IDatesRangeWidget, IDatetimeWidget, \
    IDatetimesRangeWidget, ITimeWidget
from pyams_utils.adapter import adapter_config
from pyams_utils.date import parse_date, parse_time
from pyams_utils.schema import IDatesRangeField, IDatetimesRangeField
from pyams_utils.timezone import tztime


__docformat__ = 'restructuredtext'


class BaseDatetimeDataConverter(BaseDataConverter):
    """Bse datetime data converter"""

    def to_widget_value(self, value):
        if not value:
            return None
        return tztime(value).isoformat()

    def to_field_value(self, value):
        if not value:
            return None
        return tztime(parse_date(value))


#
# Datetime widget
#

@adapter_config(required=(IDatetime, IDatetimeWidget),
                provides=IDataConverter)
class DatetimeDataConverter(BaseDatetimeDataConverter):
    """Datetime widget data converter"""


@implementer_only(IDatetimeWidget)
class DatetimeWidget(TextWidget):
    """Datetime widget"""


@adapter_config(required=(IDatetime, IFormLayer),
                provides=IFieldWidget)
def DatetimeFieldWidget(field, request):  # pylint: disable=invalid-name
    """Datetime field widget factory"""
    return FieldWidget(field, DatetimeWidget(request))


#
# Date widget
#

@adapter_config(required=(IDate, IDateWidget),
                provides=IDataConverter)
class DateDataConverter(BaseDatetimeDataConverter):
    """Date widget data converter"""

    def to_field_value(self, value):
        if not value:
            return None
        return parse_date(value, to_gmt=False).date()


@implementer_only(IDateWidget)
class DateWidget(TextWidget):
    """Date widget"""


@adapter_config(required=(IDate, IFormLayer),
                provides=IFieldWidget)
def DateFieldWidget(field, request):  # pylint: disable=invalid-name
    """Date field widget factory"""
    return FieldWidget(field, DateWidget(request))


#
# Time widget
#

@adapter_config(required=(ITime, ITimeWidget),
                provides=IDataConverter)
class TimeDataConverter(BaseDatetimeDataConverter):
    """Time widget data converter"""

    def to_field_value(self, value):
        if not value:
            return None
        return parse_time(value)


@implementer_only(ITimeWidget)
class TimeWidget(TextWidget):
    """Time widget"""


@adapter_config(required=(ITime, IFormLayer),
                provides=IFieldWidget)
def TimeFieldWidget(field, request):  # pylint: disable=invalid-name
    """Time field widget factory"""
    return FieldWidget(field, TimeWidget(request))


#
# Dates range widget
#

@implementer_only(IDatesRangeWidget)
class DatesRangeWidget(MultiWidget):
    """Dates range widget"""

    def update(self):
        super(MultiWidget, self).update()  # pylint: disable=bad-super-call


@adapter_config(required=(IDatesRangeField, IFormLayer),
                provides=IFieldWidget)
def DatesRangeFieldWidget(field, request):  # pylint: disable=invalid-name
    """Dates range widget factory"""
    return FieldWidget(field, DatesRangeWidget(request))


#
# Datetimes range widget
#

@implementer_only(IDatetimesRangeWidget)
class DatetimesRangeWidget(MultiWidget):
    """Datetimes range widget"""

    def update(self):
        super(MultiWidget, self).update()  # pylint: disable=bad-super-call


@adapter_config(required=(IDatetimesRangeField, IFormLayer),
                provides=IFieldWidget)
def DatetimesRangeFieldWidget(field, request):  # pylint: disable=invalid-name
    """Datetimes range widget factory"""
    return FieldWidget(field, DatetimesRangeWidget(request))
