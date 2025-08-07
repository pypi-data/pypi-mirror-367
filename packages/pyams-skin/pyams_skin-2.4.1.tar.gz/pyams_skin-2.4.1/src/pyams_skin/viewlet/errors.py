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

"""PyAMS_skin.viewlet.errors module

This viewlet module displays form errors.
"""

__docformat__ = 'restructuredtext'

from zope.interface import Interface

from pyams_form.interfaces.form import IForm
from pyams_layer.interfaces import IPyAMSLayer
from pyams_template.template import template_config
from pyams_viewlet.viewlet import ViewContentProvider, contentprovider_config, viewlet_config


@contentprovider_config(name='pyams.form_errors',
                        context=Interface, layer=IPyAMSLayer, view=IForm)
@template_config(template='templates/errors.pt',
                 layer=IPyAMSLayer)
class FormErrorsContentProvider(ViewContentProvider):
    """Form errors content provider"""
