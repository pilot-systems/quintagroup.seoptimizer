import re
import sys

import six
import six.moves.urllib.error
import six.moves.urllib.parse
import six.moves.urllib.request
from quintagroup.seoptimizer.browser.interfaces import IValidateSEOKeywordsView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.PortalTransforms.interfaces import IPortalTransformsTool
from quintagroup.seoptimizer import SeoptimizerMessageFactory as _
from zope.component import getUtility, queryAdapter
from zope.interface import implementer

implementer(IValidateSEOKeywordsView)
class ValidateSEOKeywordsView(BrowserView):

    def validateKeywords(self):
        """ see interface """
        text = self.request.get('text')
        ts = getToolByName(self.context, 'translation_service')
        transforms = getUtility(IPortalTransformsTool)
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        isExternal = api.portal.get_registry_record('quintagroup.seoptimizer.external_keywords_test')
        # extract keywords from text
        enc = 'utf-8'
        if text.lower().strip():
            keywords = [_f for _f in [safe_unicode(x.strip(), enc) for x in text.lower().strip().split('\n')] if _f]
        else:
            return ts.utranslate(domain='quintagroup.seoptimizer',
                                 msgid=_(u'Keywords list is empty!'),
                                 context=self.context)
        # Get html page internally or with external request
        error_url = ""
        if isExternal:
            # Not pass timeout option because:
            # 1. its value get from the global default timeout settings.
            # 2. timeout option added in python 2.6
            #    (so acceptable only in plone4+)
            try:
                resp = six.moves.urllib.request.urlopen(self.context.absolute_url())
                try:
                    html = resp.read()
                finally:
                    resp.close()
            except (six.moves.urllib.error.URLError, six.moves.urllib.error.HTTPError):
                # In case of exceed timeout period or
                # other URL connection errors.
                # Get nearest to context error_log object
                # (stolen from Zope2/App/startup.py)
                html = None
                info = sys.exc_info()
                elog = getToolByName(self.context, "error_log")
                error_url = elog.raising(info)
        else:
            html = six.text_type(self.context()).encode(enc)

        # If no html - information about problem with page retrieval
        # should be returned
        result = []
        if html is None:
            result.append("Problem with page retrieval.")
            if error_url:
                result.append("Details at %s." % error_url)
        else:
            page_text = transforms.convert("html_to_text", html).getData()
            # check every keyword on appearing in body of html page
            for keyword in keywords:
                keyword_on_page = six.text_type(len(re.findall(u'\\b%s\\b' % keyword,
                                              page_text, re.I | re.U)))
                result.append(' - '.join((keyword, keyword_on_page)))

        return ts.utranslate(domain='quintagroup.seoptimizer',
                             msgid=_(u'number_keywords',
                                     default=u'Number of keywords at page:\n'
                                     '${result}',
                                     mapping={'result': '\n'.join(result)}),
                             context=self.context)
