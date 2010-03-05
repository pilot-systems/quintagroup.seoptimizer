#
# Test product's installation
#
import string
from zope.interface import alsoProvides
from zope.component import queryMultiAdapter
from zope.publisher.browser import TestRequest
from zope.viewlet.interfaces import IViewletManager
from plone.browserlayer import utils
from quintagroup.seoptimizer.browser.interfaces import IPloneSEOLayer

from base import getToolByName, FunctionalTestCase, TestCase, newSecurityManager
from config import *


class TestBeforeInstallation(FunctionalTestCase):

    def afterSetUp(self):
        self.qi = self.portal.portal_quickinstaller
        self.qi.uninstallProducts([PROJECT_NAME])
        self.basic_auth = 'mgr:mgrpw'
        self.portal_path = '/%s' % self.portal.absolute_url(1)

    def testAccessPortalRootAnonymous(self):
        response = self.publish(self.portal_path)
        self.assertEqual(response.getStatus(), 200)

    def testAccessPortalRootAuthenticated(self):
        response = self.publish(self.portal_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200)


class TestInstallation(TestCase):

    def afterSetUp(self):
        self.properties = getToolByName(self.portal, 'portal_properties')

    def testAddingPropertySheet(self):
        """ Test adding property sheet to portal_properties tool """
        self.failUnless(hasattr(self.properties.aq_base, PROPERTY_SHEET))

    def testAddingPropertyFields(self):
        """ Test adding property field to portal_properties.maps_properties sheet """
        map_sheet = self.properties[PROPERTY_SHEET]
        for key, value in PROPS.items():
            self.failUnless(map_sheet.hasProperty(key) and list(map_sheet.getProperty(key)) == value)

    def test_configlet_install(self):
        configTool = getToolByName(self.portal, 'portal_controlpanel', None)
        self.assert_(PROJECT_NAME in [a.getId() for a in configTool.listActions()], 'Configlet not found')

    def test_skins_install(self):
        skinstool=getToolByName(self.portal, 'portal_skins')

        for skin in skinstool.getSkinSelections():
            path = skinstool.getSkinPath(skin)
            path = map( string.strip, string.split( path,',' ) )
            self.assert_(PROJECT_NAME in path, 'qSEOptimizer layer not found in %s' %skin)

    def test_viewlets_install(self):
        VIEWLETS = ['plone.htmlhead.title',
                    'plone.resourceregistries',
                    'quintagroup.seoptimizer.seotags',
                    'quintagroup.seoptimizer.customscript']
        request = self.app.REQUEST
        # mark request with our browser layer
        alsoProvides(request, IPloneSEOLayer)
        view = queryMultiAdapter((self.portal, request), name="plone")
        manager = queryMultiAdapter( (self.portal['front-page'], request, view),
                                     IViewletManager, name='plone.htmlhead')
        for p in VIEWLETS:
            self.assert_(manager.get(p) is not None, "Not registered '%s' viewlet" % p)
        
    def test_browser_layer(self):
        self.assert_(IPloneSEOLayer in utils.registered_layers(),
                     "Not registered 'IPloneSEOLayer' browser layer")
    
    def test_jsregestry_install(self):
        jstool=getToolByName(self.portal, 'portal_javascripts')
        self.assert_(jstool.getResource("++resource++seo_custommetatags.js") is not None,
                     "Not registered '++resource++seo_custommetatags.js' resource")

    def test_action_install(self):
        atool=getToolByName(self.portal, 'portal_actions')
        action_ids = [a.id for a in atool.listActions()]
        self.assert_("SEOProperties" in action_ids,
                     "Not added 'SEOProperties' action")

class TestUninstallation(TestCase):

    def afterSetUp(self):
        self.qi = self.portal.portal_quickinstaller
        self.qi.uninstallProducts([PROJECT_NAME])

    def test_propertysheet_uninstall(self):
        properties = getToolByName(self.portal, 'portal_properties')
        self.assertEqual(hasattr(properties.aq_base, PROPERTY_SHEET), False,
            "'%s' property sheet not uninstalled" % PROPERTY_SHEET)

    def test_configlet_uninstall(self):
        self.assertNotEqual(self.qi.isProductInstalled(PROJECT_NAME), True,
            'qSEOptimizer is already installed')

        configTool = getToolByName(self.portal, 'portal_controlpanel', None)
        self.assertEqual(PROJECT_NAME in [a.getId() for a in configTool.listActions()], False,
            'Configlet found after uninstallation')

    def test_skins_uninstall(self):
        self.assertNotEqual(self.qi.isProductInstalled(PROJECT_NAME), True,
            'qSEOptimizer is already installed')
        skinstool=getToolByName(self.portal, 'portal_skins')

        for skin in skinstool.getSkinSelections():
            path = skinstool.getSkinPath(skin)
            path = map( string.strip, string.split( path,',' ) )
            self.assertEqual(PROJECT_NAME in path, False,
                'qSEOptimizer layer found in %s after uninstallation' %skin)

    def test_viewlets_uninstall(self):
        VIEWLETS = ['quintagroup.seoptimizer.seotags',
                    'quintagroup.seoptimizer.customscript']
        request = self.app.REQUEST
        view = queryMultiAdapter((self.portal, request), name="plone")
        manager = queryMultiAdapter( (self.portal['front-page'], request, view),
                                     IViewletManager, name='plone.htmlhead')
        for p in VIEWLETS:
            self.assertEqual(manager.get(p) is None, True,
                "'%s' viewlet present after uninstallation" % p)

    def test_browserlayer_uninstall(self):
        self.assertEqual(IPloneSEOLayer in utils.registered_layers(), False,
            "Not registered 'IPloneSEOLayer' browser layer")

    def test_jsregestry_uninstall(self):
        jstool=getToolByName(self.portal, 'portal_javascripts')
        self.assertEqual(jstool.getResource("++resource++seo_custommetatags.js") is not None,
            False, "Not registered '++resource++seo_custommetatags.js' resource")

    def test_action_uninstall(self):
        atool=getToolByName(self.portal, 'portal_actions')
        action_ids = [a.id for a in atool.listActions()]
        self.assertEqual("SEOProperties" in action_ids, False,
            "Not added 'SEOProperties' action")

class TestReinstallation(TestCase):

    def afterSetUp(self):
        self.qi = self.portal.portal_quickinstaller
        self.types_tool = getToolByName(self.portal, 'portal_types')
        self.setup_tool = getToolByName(self.portal, 'portal_setup')
        self.pprops_tool = getToolByName(self.portal, 'portal_properties')
        self.seoprops_tool = getToolByName(self.pprops_tool, 'seo_properties', None)
        # Set earlier version profile (2.0.0) for using upgrade steps 
        self.setup_tool.setLastVersionForProfile('%s:default' % PROJECT_NAME, '2.0.0')

    def testChangeDomain(self):
        # Test changed of content type's domain from 'quintagroup.seoptimizer' to 'plone'
        for type in SEO_CONTENT:
            self.types_tool.getTypeInfo(type).i18n_domain = 'quintagroup.seoptimizer'
        self.qi.reinstallProducts([PROJECT_NAME])
        for type in SEO_CONTENT:
            self.assertEqual(self.types_tool.getTypeInfo(type).i18n_domain, 'plone',
                "Not changed of %s content type's domain to 'plone'" % type)

    def testCutItemsMetatagsOrderList(self):
        # Test changed format metatags order list from "metaname accessor" to "metaname"
        value, expect_mto = ['name1 accessor1', 'name2 accessor2'], ['name1','name2']
        self.seoprops_tool.manage_changeProperties(metatags_order=value)
        self.qi.reinstallProducts([PROJECT_NAME])
        mto = list(self.seoprops_tool.getProperty('metatags_order'))
        mto.sort()
        self.assertEqual(mto, expect_mto,
                    "Not changed format metatags order list from \"metaname accessor\" to"\
                    " \"metaname\". %s != %s" %(mto, expect_mto))

    def testAddMetatagsOrderList(self):
        # Test added metatags order list if it was not there before
        self.seoprops_tool.manage_delProperties(['metatags_order'])
        self.qi.reinstallProducts([PROJECT_NAME])
        mto = list(self.seoprops_tool.getProperty('metatags_order'))
        mto.sort()
        self.assertEqual(mto, DEFAULT_METATAGS_ORDER,
                    "Not added metatags order list with default values."\
                    "%s != %s" %(mto, DEFAULT_METATAGS_ORDER))

    def testMigrationActions(self):
        # Test migrated actions from portal_types action to seoproperties tool
        self.seoprops_tool.content_types_with_seoproperties = ()

        # Add seoaction to content type for testing
        for type in CONTENTTYPES_WITH_SEOACTION:
            self.types_tool.getTypeInfo(type).addAction(id='seo_properties',
                                                   name='SEO Properties',
                                                   action=None,
                                                   condition=None,
                                                   permission=(u'Modify portal content',),
                                                   category='object',
                                                   visible=True,
                                                   icon_expr=None,
                                                   link_target=None,
                                                  )
            # Check presence seoaction in content type
            seoaction = [act.id for act in self.types_tool.getTypeInfo(type).listActions()
                                          if act.id == 'seo_properties']
            self.assertEqual(bool(seoaction), True,
                    "Not added seoaction to content type %s for testing" % type)

        self.qi.reinstallProducts([PROJECT_NAME])

        # Check presence seoaction in content type
        for type in CONTENTTYPES_WITH_SEOACTION:
            seoaction = [act.id for act in self.types_tool.getTypeInfo(type).listActions()
                                          if act.id == 'seo_properties']
            self.assertEqual(bool(seoaction), False,
                "Not removed seoaction in content type %s" % type)

        # Check added content type names in seo properties tool if content types have seoaction
        ctws = list(self.seoprops_tool.content_types_with_seoproperties)
        ctws.sort()
        self.assertEqual(ctws, CONTENTTYPES_WITH_SEOACTION,
            "Not added content type names in seo properties tool if content types have seoaction."\
            " %s != %s" %(ctws, CONTENTTYPES_WITH_SEOACTION))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBeforeInstallation))
    suite.addTest(makeSuite(TestInstallation))
    suite.addTest(makeSuite(TestUninstallation))
    suite.addTest(makeSuite(TestReinstallation))
    return suite