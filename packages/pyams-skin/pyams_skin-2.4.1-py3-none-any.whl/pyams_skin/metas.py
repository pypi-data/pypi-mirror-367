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

"""PyAMS_skin.metas module

Base metas headers classes.
"""

__docformat__ = 'restructuredtext'

from html import escape

from pyramid.interfaces import IRequest
from zope.interface import Interface, implementer

from pyams_skin.interfaces.metas import IHTMLContentMetas, IMetaHeader
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.tales import ITALESExtension


@adapter_config(name='metas',
                required=(Interface, IRequest, Interface),
                provides=ITALESExtension)
class MetasTalesExtension(ContextRequestViewAdapter):
    """tales:metas TALES extension"""

    def render(self, context=None):
        """Extension renderer"""
        if context is None:
            context = self.context
        result = []
        for _name, adapter in sorted(
                self.request.registry.getAdapters((context, self.request, self.view),
                                                  IHTMLContentMetas),
                key=lambda x: getattr(x[1], 'weight', 9999)):
            result.extend([meta.render() for meta in adapter.get_metas()])
        return '\n\t'.join(result)


#
# Custom metas headers
#

def escape_value(value):
    """HTML escaped value"""
    return escape(value) if isinstance(value, str) else value


@implementer(IMetaHeader)
class BaseMeta:
    """Base HTML meta header"""

    def __init__(self, tag='meta', value=None, **attrs):
        self.tag = tag
        self.value = value
        self.attrs = attrs

    def render(self):
        """Render meta header"""
        attributes = ' '.join((f'{k}="{v}"' for k, v in self.attrs.items()))
        if self.value:
            return f'<{self.tag} {attributes}>{self.value}</{self.tag}>'
        return f'<{self.tag} {attributes} />'


class HTMLTagMeta(BaseMeta):
    """HTML tag meta header"""

    def __init__(self, tag, content, **attrs):
        super().__init__(tag, content, **attrs)


class HTTPEquivMeta(BaseMeta):
    """HTTP-Equiv meta header"""

    def __init__(self, http_equiv, value):
        super().__init__(
            **{'http-equiv': http_equiv, 'content': escape_value(value)})


class ValueMeta(BaseMeta):
    """Basic value meta header"""

    def __init__(self, name, value):
        super().__init__(**{name: escape_value(value)})


class ContentMeta(BaseMeta):
    """Content meta header"""

    def __init__(self, name, value):
        super().__init__(name=name, content=escape_value(value))


class PropertyMeta(BaseMeta):
    """Property meta header"""

    def __init__(self, property, value):  # pylint: disable=redefined-builtin
        super().__init__(property=property, content=escape_value(value))


class SchemaMeta(BaseMeta):
    """Schema.org property meta header"""

    def __init__(self, name, value):
        super().__init__(itemprop=name, content=escape_value(value))


class LinkMeta(BaseMeta):
    """Link meta header"""

    def __init__(self, rel, type, href, **kwargs):  # pylint: disable=redefined-builtin
        super().__init__('link', rel=rel, type=type, href=escape_value(href),
                         **kwargs)
