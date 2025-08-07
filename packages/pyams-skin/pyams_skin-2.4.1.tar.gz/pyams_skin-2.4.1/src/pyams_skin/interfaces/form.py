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

"""PyAMS_skin.interfaces.form module

This module is providing interfaces for a small set of custom widgets.
It also overrides default form templates defined into PyAMS_form package.
"""

from pyams_form.interfaces.button import IButton
from pyams_form.interfaces.form import IDisplayForm, IForm, IGroup, IInnerSubForm, IInnerTabForm
from pyams_layer.interfaces import IPyAMSLayer
from pyams_template.template import override_template


__docformat__ = 'restructuredtext'


override_template(IForm, template='templates/form.pt', layer=IPyAMSLayer)
override_template(IDisplayForm, template='templates/form-display.pt', layer=IPyAMSLayer)

override_template(IGroup, template='templates/form-group.pt', layer=IPyAMSLayer)

override_template(IInnerSubForm, template='templates/form-group.pt', layer=IPyAMSLayer)

override_template(IInnerTabForm, template='templates/form-tabform.pt', layer=IPyAMSLayer)


class ISubmitButton(IButton):
    """Submit button interface"""


class IActionButton(IButton):
    """Secondary button interface"""


class IResetButton(IButton):
    """Reset button interface"""


class ICloseButton(IButton):
    """Close button interface"""
