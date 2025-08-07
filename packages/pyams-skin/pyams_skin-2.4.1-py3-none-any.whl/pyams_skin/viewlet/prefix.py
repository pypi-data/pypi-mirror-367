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

"""PyAMS_skin.viewlet.prefix module

This module provides "pyams.prefix" and "pyams.suffix" content providers, which are both
viewlets managers which can be used to insert additional contents at the top or at the end of
elements, including forms and widgets.
"""

from zope.interface import Interface

from pyams_layer.interfaces import IPyAMSLayer
from pyams_skin.interfaces.viewlet import IContentPrefixViewletManager, \
    IContentSuffixViewletManager
from pyams_viewlet.manager import WeightOrderedViewletManager, viewletmanager_config


__docformat__ = 'restructuredtext'


@viewletmanager_config(name='pyams.prefix', layer=IPyAMSLayer, view=Interface,
                       provides=IContentPrefixViewletManager)
class PrefixViewletManager(WeightOrderedViewletManager):
    """Content prefix viewlet manager"""


@viewletmanager_config(name='pyams.suffix', layer=IPyAMSLayer, view=Interface,
                       provides=IContentSuffixViewletManager)
class SuffixViewletManager(WeightOrderedViewletManager):
    """Content suffix viewlet manager"""
