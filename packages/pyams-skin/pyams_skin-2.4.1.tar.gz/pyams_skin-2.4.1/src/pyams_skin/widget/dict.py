# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from zope.interface import implementer_only
from zope.schema.interfaces import IDict

from pyams_form.browser.textarea import TextAreaWidget
from pyams_form.converter import BaseDataConverter
from pyams_form.interfaces import IDataConverter
from pyams_form.widget import FieldWidget
from pyams_skin.interfaces.widget import IDictWidget
from pyams_utils.adapter import adapter_config

__docformat__ = 'restructuredtext'


@implementer_only(IDictWidget)
class DictWidget(TextAreaWidget):
    """Custom dict widget"""
    
    
@adapter_config(required=(IDict, IDictWidget),
                provides=IDataConverter)
class DictWidgetDataConverter(BaseDataConverter):
    """Dict field data converter"""
    
    def to_widget_value(self, value):
        """See `pyams_form.interfaces.IDataConverter`"""
        if not value:
            return ''
        return '\n'.join((
            f'{key}={val}'
            for key, val in value.items()
        ))
    
    def to_field_value(self, value):
        """See `pyams_form.interfaces.IDataConverter`"""
        if not value:
            return None
        return dict(val.split('=') for val in value.split('\n') if val)

    
def DictFieldWidget(field, request):
    """Dict field widget factory"""
    return FieldWidget(field, DictWidget(request))
