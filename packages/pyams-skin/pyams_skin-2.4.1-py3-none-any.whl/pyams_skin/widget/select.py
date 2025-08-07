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

"""PyAMS_skin.widget.select module

This module provides a "dynamic" terms adapter for "dynamic" select widgets.

These select widgets are not based on a static pre-loaded vocabulary, but on remote
elements like an SQL database or a remote users database whose elements are only loaded
on demand; they must provide a "term_factory" attribute, which is called to create terms
based on widget values.

A widget example can be found in pyams_security_views principals widgets.
"""

from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.schema.interfaces import IField
from zope.schema.vocabulary import SimpleVocabulary

from pyams_form.interfaces import ITerms
from pyams_form.interfaces.form import IForm
from pyams_layer.interfaces import IFormLayer
from pyams_skin.interfaces.widget import IDynamicSelectWidget
from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces.form import IDataManager, NO_VALUE


__docformat__ = 'restructuredtext'


@adapter_config(required=(Interface, IFormLayer, IForm, IField, IDynamicSelectWidget),
                provides=ITerms)
class DynamicSelectWidgetTermsFactory(SimpleVocabulary):
    """Dynamic select widget terms factory"""

    def __init__(self, context, request, form, field, widget):  # pylint:disable=too-many-arguments
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        super().__init__(self.getTerms())

    def getTerms(self):  # pylint:disable=invalid-name
        """Get terms from factory"""
        value = NO_VALUE
        result = []
        if (not self.widget.ignore_request) and (self.widget.name in self.request.params):
            try:
                value = self.request.params.getall(self.widget.name)
            except AttributeError:
                value = self.request.params.get(self.widget.name)
        if (value is NO_VALUE) and (not self.widget.ignore_context):
            value = getMultiAdapter((self.context, self.field), IDataManager).query()
        if value and (value is not NO_VALUE):
            values = []
            if not isinstance(value, (list, dict, set)):
                value = (value,)
            for val in value:
                if isinstance(val, str):
                    values.extend(val.split(self.widget.separator))
                else:
                    values.append(val)
            value = tuple(values)
            for token in value:
                if not token:
                    continue
                term = self.widget.term_factory(token)
                if term is not None:
                    result.append(term)
        return result

    def getValue(self, value):  # pylint:disable=invalid-name
        """Get value from internal value"""
        return self.getTerm(value).value
