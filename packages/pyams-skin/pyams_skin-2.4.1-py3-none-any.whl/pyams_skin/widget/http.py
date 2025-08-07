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

"""PyAMS_skin.widget.http module

This module defines a custom widget which can be used to select HTTP REST API
methods, made of a verb and an URI.
"""

__docformat__ = 'restructuredtext'

from zope.interface import implementer_only

from pyams_form.browser.widget import HTMLFormElement
from pyams_form.converter import BaseDataConverter
from pyams_form.interfaces import IDataConverter
from pyams_form.interfaces.widget import IFieldWidget
from pyams_form.widget import FieldWidget, Widget
from pyams_layer.interfaces import IFormLayer
from pyams_skin.interfaces.widget import HTTP_METHODS, IHTTPMethodWidget
from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces.form import NO_VALUE
from pyams_utils.schema import IHTTPMethodField


@adapter_config(required=(IHTTPMethodField, IHTTPMethodWidget),
                provides=IDataConverter)
class HTTPMethodDataConverter(BaseDataConverter):
    """HTTP method field data converter"""

    def to_widget_value(self, value):
        return value

    def to_field_value(self, value):
        return value


@implementer_only(IHTTPMethodWidget)
class HTTPMethodWidget(HTMLFormElement, Widget):
    """HTTP method getter widget"""

    @property
    def display_value(self):
        """Display value getter"""
        return self.value or (None, None)

    def extract(self, default=NO_VALUE):
        params = self.request.params
        marker = params.get(f'{self.name}-empty-marker', default)
        if marker is not default:
            verb = params.get(f'{self.name}-verb')
            url = params.get(f'{self.name}-url')
            return (verb, url) if verb and url else None
        return default

    @property
    def http_methods(self):
        """HTTP methods getter"""
        return HTTP_METHODS


@adapter_config(required=(IHTTPMethodField, IFormLayer),
                provides=IFieldWidget)
def HTTPMethodFieldWidget(field, request):  # pylint: disable=invalid-name
    """HTTP method getter widget factory"""
    return FieldWidget(field, HTTPMethodWidget(request))
