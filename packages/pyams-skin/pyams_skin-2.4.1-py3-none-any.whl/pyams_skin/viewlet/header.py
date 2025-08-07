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

"""PyAMS_skin.viewlet.header module

This module provides a single "pyams.header" viewlet manager used to handle internal page header.
"""

from zope.interface import Interface

from pyams_layer.interfaces import IPyAMSLayer
from pyams_skin.interfaces.viewlet import IFormHeaderViewletManager, IHeaderViewletManager
from pyams_viewlet.manager import WeightOrderedViewletManager, viewletmanager_config


__docformat__ = 'restructuredtext'


@viewletmanager_config(name='pyams.header', layer=IPyAMSLayer, view=Interface,
                       provides=IHeaderViewletManager)
class HeaderViewletManager(WeightOrderedViewletManager):
    """Internal header viewlet manager"""


@viewletmanager_config(name='pyams.form_header', layer=IPyAMSLayer, view=Interface,
                       provides=IFormHeaderViewletManager)
class FormHeaderViewletManager(WeightOrderedViewletManager):
    """Form header viewlet manager"""
