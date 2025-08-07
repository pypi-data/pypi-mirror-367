#
# Copyright (c) 2015-2022 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_content_es.component.paragraph module

This module defines the adapters which are used to handle paragraphs indexation.
"""

__docformat__ = 'restructuredtext'

from pyams_content.component.paragraph.interfaces import IBaseParagraph, IParagraphContainer, \
    IParagraphContainerTarget
from pyams_content.component.paragraph.interfaces.group import IParagraphsGroup
from pyams_content.component.paragraph.interfaces.html import IHTMLParagraph, IRawParagraph
from pyams_content_es.component import get_index_values, html_to_index
from pyams_content_es.interfaces import IDocumentIndexInfo
from pyams_utils.adapter import adapter_config


@adapter_config(name='paragraphs',
                required=IParagraphContainerTarget,
                provides=IDocumentIndexInfo)
def paragraph_container_index_info(context):
    """Paragraph container index info"""
    body = {}
    for paragraph in IParagraphContainer(context).get_visible_paragraphs():
        info = IDocumentIndexInfo(paragraph, None)
        if info is not None:
            for lang, body_info in info.items():
                body[lang] = f"{body.get(lang, '')}\n{body_info}"
    return {
        'body': body
    }


@adapter_config(required=IBaseParagraph,
                provides=IDocumentIndexInfo)
def base_paragraph_index_info(context):
    """Base paragraph index info"""
    info = {}
    get_index_values(context, info,
                     i18n_fields=('title',))
    return info


@adapter_config(required=IParagraphsGroup,
                provides=IDocumentIndexInfo)
def paragraphs_group_index_info(context):
    """Paragraphs group index info"""
    info = base_paragraph_index_info(context)
    paragraphs_info = paragraph_container_index_info(context)
    for lang, body in paragraphs_info.get('body', {}).items():
        info[lang] += f"\n{body}"
    return info


@adapter_config(required=IRawParagraph,
                provides=IDocumentIndexInfo)
@adapter_config(required=IHTMLParagraph,
                provides=IDocumentIndexInfo)
def html_paragraph_index_info(context):
    """HTML paragraph index info"""
    info = base_paragraph_index_info(context)
    get_index_values(context, info,
                     i18n_fields=(('body', html_to_index),))
    return info
