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

"""PyAMS_skin.viewlet.metas module

This module defines standard MyAMS HTML metas headers.
"""

from zope.interface import Interface

from pyams_skin.interfaces.metas import IHTMLContentMetas
from pyams_skin.metas import ContentMeta, HTTPEquivMeta, ValueMeta
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config


__docformat__ = 'restructuredtext'


@adapter_config(name='layout',
                required=(Interface, Interface, Interface),
                provides=IHTMLContentMetas)
class LayoutMetasAdapter(ContextRequestViewAdapter):
    """Basic layout metas adapter"""

    weight = -1

    @staticmethod
    def get_metas():
        """Layout and content metas headers"""
        yield HTTPEquivMeta('X-UA-Compatible', 'IE=edge,chrome=1')
        yield HTTPEquivMeta('Content-Type', 'text/html; charset=utf-8')
        yield ValueMeta('charset', 'utf-8')
        yield ContentMeta('HandheldFriendly', 'True')
        yield ContentMeta('viewport', 'width=device-width, initial-scale=1.0, '
                                      'maximum-scale=1.0, user-scalable=no')
