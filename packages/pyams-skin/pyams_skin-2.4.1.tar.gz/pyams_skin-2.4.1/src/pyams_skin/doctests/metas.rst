==================
HTML metas headers
==================

HTML headers are included in rendered pages using a custom "metas" TALES extension, which relies
on adapters providing *IHTMLContentMetas* interface:

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)
    >>> from pyams_viewlet import includeme as include_viewlet
    >>> include_viewlet(config)
    >>> from pyams_form import includeme as include_form
    >>> include_form(config)
    >>> from pyams_skin import includeme as include_skin
    >>> include_skin(config)

    >>> from pyams_skin.metas import MetasTalesExtension

    >>> context = object()
    >>> request = DummyRequest(context=context, registry=config.registry)

    >>> metas = MetasTalesExtension(context, request, None)
    >>> print(metas.render())
    <meta ...http-equiv="X-UA-Compatible"... />
    <meta ...http-equiv="Content-Type"... />
    <meta charset="utf-8" />
    <meta ...name="HandheldFriendly"... />
    <meta ...name="viewport"... />

Several kinds of metas tags are available:

    >>> from pyams_skin.metas import *

    >>> HTMLTagMeta('tag', 'content', attr='value').render()
    '<tag attr="value">content</tag>'

    >>> meta = HTTPEquivMeta('equiv', 'value')
    >>> meta.render()
    '<meta ...http-equiv="equiv"... />'
    >>> meta.render()
    '<meta ...content="value"... />'

    >>> ValueMeta('name', 'value').render()
    '<meta name="value" />'

    >>> meta = ContentMeta('name', 'value')
    >>> meta.render()
    '<meta ...content="value"... />'
    >>> meta.render()
    '<meta ...name="name"... />'

    >>> meta = PropertyMeta('property', 'value')
    >>> meta.render()
    '<meta ...property="property"... />'
    >>> meta.render()
    '<meta ...content="value"... />'

    >>> meta = SchemaMeta('name', 'value')
    >>> meta.render()
    '<meta ...content="value"... />'
    >>> meta.render()
    '<meta ...itemprop="name"... />'

    >>> meta = LinkMeta('rel', 'type', 'href', arg="value")
    >>> meta.render()
    '<link ...rel="rel"... />'
    >>> meta.render()
    '<link ...type="type"... />'
    >>> meta.render()
    '<link ...href="href"... />'
    >>> meta.render()
    '<link ...arg="value"... />'


Tests cleanup:

    >>> tearDown()
