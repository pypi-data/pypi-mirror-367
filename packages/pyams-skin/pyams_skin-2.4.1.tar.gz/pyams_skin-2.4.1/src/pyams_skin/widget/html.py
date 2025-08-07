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

"""PyAMS_skin.widget.html module

This module provides a custom widget which is used to render HTML text fields, using a
TinyMCE editor.
The widget is using an IHTMLEditorConfiguration adapter to build custom editor configurations
easily...
"""

import json

from zope.component import queryMultiAdapter
from zope.interface import implementer_only

from pyams_form.browser.textarea import TextAreaWidget
from pyams_form.interfaces.widget import IFieldWidget
from pyams_form.widget import FieldWidget
from pyams_layer.interfaces import IFormLayer
from pyams_skin.interfaces.widget import IHTMLEditorConfiguration, IHTMLWidget
from pyams_utils.adapter import adapter_config
from pyams_utils.schema import IHTMLField


__docformat__ = 'restructuredtext'


@implementer_only(IHTMLWidget)
class HTMLWidget(TextAreaWidget):
    """HTML editor widget"""

    @property
    def editor_data(self):
        """Extract editor configuration from adapter"""
        configuration = queryMultiAdapter((self.context, self.request, self.form),
                                          IHTMLEditorConfiguration,
                                          name=self.name)
        if (configuration is None) and hasattr(self, 'basename'):  # I18n widget
            configuration = queryMultiAdapter((self.context, self.request, self.form),
                                              IHTMLEditorConfiguration,
                                              name=self.basename)  # pylint:disable=no-member
        if configuration is None:
            configuration = queryMultiAdapter((self.context, self.request, self.form),
                                              IHTMLEditorConfiguration,
                                              name=self.field.getName())
        if configuration is None:
            configuration = queryMultiAdapter((self.context, self.request, self.form),
                                              IHTMLEditorConfiguration)
        if configuration is None:
            configuration = getattr(self, 'editor_configuration', None)
        if configuration is not None:
            return json.dumps(configuration)
        return None


@adapter_config(required=(IHTMLField, IFormLayer), provides=IFieldWidget)
def HTMLFieldWidget(field, request):  # pylint:disable=invalid-name
    """HTML field widget factory"""
    return FieldWidget(field, HTMLWidget(request))
