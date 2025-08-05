# -*- coding: utf-8 -*-
from design.plone.ctgeneric import _
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


@provider(IFormFieldProvider)
class IDocumentoV2(model.Schema):
    tipologia_documento = schema.Choice(
        title=_("tipologia_documento_label", default="Tipologia del documento"),
        description=_(
            "tipologia_documento_help",
            default="Seleziona la tipologia del documento.",
        ),
        required=True,
        vocabulary="design.plone.vocabularies.tipologie_documento",
    )

    # custom order
    form.order_after(tipologia_documento="identificativo")


@implementer(IDocumentoV2)
@adapter(IDexterityContent)
class DocumentoV2(object):
    """ """

    def __init__(self, context):
        self.context = context
