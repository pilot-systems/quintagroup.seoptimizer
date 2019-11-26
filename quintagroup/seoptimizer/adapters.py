from collections import OrderedDict

from quintagroup.seoptimizer.browser.seo_configlet import ISEOConfigletSchema
from quintagroup.seoptimizer.interfaces import IMappingMetaTags, IMetaKeywords
from zope.component import queryAdapter, queryMultiAdapter
from zope.interface import implementer
from plone import api

METADATA_MAPS = dict([
    ("DC.publisher", "Publisher"),
    ("DC.description", "Description"),
    ("DC.contributors", "Contributors"),
    ("DC.creator", "Creator"),
    ("DC.format", "Format"),
    ("DC.rights", "Rights"),
    ("DC.language", "Language"),
    ("DC.date.modified", "ModificationDate"),
    ("DC.date.created", "CreationDate"),
    ("DC.type", "Type"),
    ("DC.subject", "Subject"),
    ("DC.distribution", "seo_distribution"),
    ("description", "seo_description"),
    ("keywords", "meta_keywords"),
    ("robots", "seo_robots"),
    ("distribution", "seo_distribution")])


@implementer(IMetaKeywords)
class MetaKeywordsAdapter(object):

    def __init__(self, context):
        self.context = context

    def getMetaKeywords(self):
        """ See interface.
        """
        meta_keywords = []
        seo_context = queryMultiAdapter((self.context, self.context.REQUEST),
                                        name='seo_context')
        if seo_context:
            meta_keywords = list(seo_context['meta_keywords'])
        return ', '.join(meta_keywords)


implementer(IMappingMetaTags)
class MappingMetaTags(object):

    def __init__(self, context):
        self.context = context

    def getMappingMetaTags(self):
        """ See interface.
        """
        metadata_name = OrderedDict()
        metatags_order = api.portal.get_registry_record(
            name='quintagroup.seoptimizer.metatags_order')
        for mt in metatags_order:
            if mt in METADATA_MAPS:
                metadata_name[mt] = METADATA_MAPS[mt]
        return metadata_name
