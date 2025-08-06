#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Mustache v1.4 implementation with lambdas.

Usable both in code and as CLI.
To render a mustache template use `combustache.render`.
Processed templates are cached; to clear cache use `combustache.cache_clear`.

Typical usage in code: ::

    >>> import combustache
    >>> template = 'Hello my name is {{>fancy_name}}!'
    >>> partials = {'fancy_name': '-> {{name}} <-'}
    >>> data = {'name': 'Anahit'}
    >>> combustache.render(template, data, partials)
    'Hello my name is -> Anahit <-!'

Typical usage as CLI: ::

    $ curl https://end.point/v1/api | combustache template.txt -o out.txt
    $ cat out.txt
    Hello world!
"""

from mystace.exceptions import (
    DelimiterError,
    MissingClosingTagError,
    MystaceError,
    StrayClosingTagError,
)
from mystace.mustache_tree import (
    MustacheRenderer,
    create_mustache_tree,
    render_from_template,
)
from mystace.tokenize import mustache_tokenizer

__all__ = [
    "MystaceError",
    "DelimiterError",
    "MissingClosingTagError",
    "StrayClosingTagError",
    "create_mustache_tree",
    "render_from_template",
    "MustacheRenderer",
    "mustache_tokenizer",
]
