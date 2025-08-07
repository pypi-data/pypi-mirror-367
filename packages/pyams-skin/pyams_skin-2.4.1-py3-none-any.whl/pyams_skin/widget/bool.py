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

"""PyAMS_skin.widget.bool module

This modules defines SingleCheckboxWidget as default widget for boolean fields.
"""

__docformat__ = 'restructuredtext'

from zope.schema.interfaces import IBool

from pyams_form.browser.checkbox import SingleCheckBoxFieldWidget
from pyams_form.interfaces.widget import IFieldWidget
from pyams_layer.interfaces import IPyAMSLayer
from pyams_utils.adapter import adapter_config


@adapter_config(required=(IBool, IPyAMSLayer),
                provides=IFieldWidget)
def BoolFieldWidget(field, request):  # pylint: disable=invalid-name
    """Bool field widget factory"""
    return SingleCheckBoxFieldWidget(field, request)
