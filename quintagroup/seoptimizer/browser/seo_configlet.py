from zope.interface import Interface

from zope.schema import Bool, Choice, Tuple, List
from zope.schema import SourceText
from plone.app.registry.browser import controlpanel
from z3c.form import field
from z3c.form import group

from quintagroup.seoptimizer import SeoptimizerMessageFactory as _


# Configlet schemas
class ISEOConfigletBaseSchema(Interface):

    exposeDCMetaTags = Bool(
        title=_("label_exposeDCMetaTags",
                default='Expose <abbr title="Dublin Core">DC</abbr> '
                'meta tags'),
        description=_("description_seo_dc_metatags",
                      default='Controls if <abbr title="Dublin Core">DC</abbr>'
                      ' metatags are exposed to page header. They include '
                      'DC.description, DC.type, DC.format, DC.creator and '
                      'others.'),
        default=True,
        required=False)

    metatags_order = List(
        title=_("label_metatags_order",
                default='Meta tags order in the page.'),
        description=_("help_metatags_order",
                      default='Fill in meta tags (one per line) in the order '
                      'in which they will appear on site source pages. '
                      'Example: "metaname accessor".'),
        required=False)

    types_seo_enabled = Tuple(
        title=_("label_content_type_title", default='Content Types'),
        description=_("description_seo_content_types",
                      default='Select content types that will have SEO '
                      'properties enabled.'),
        required=False,
        missing_value=tuple(),
        value_type=Choice(
            vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes"))

    default_custom_metatags = List(
        title=_("label_default_custom_metatags",
                default='Default custom metatags.'),
        description=_("help_default_custom_metatags",
                      default='Fill in custom metatag names (one per line) '
                      'which will appear on qseo_properties edit tab. '
                      'Example: "metaname|metacontent" or "metaname".'),
        required=False)


class ISEOConfigletAdvancedSchema(Interface):
    custom_script = SourceText(
        title=_("label_custom_script", default=u'Header JavaScript'),
        description=_("help_custom_script",
                      default=u"This JavaScript code will be included in "
                      "the rendered HTML as entered in the page header."),
        default=u'',
        required=False)

    fields = List(
        title=_("label_fields", default='Fields for keywords statistic '
                'calculation.'),
        description=_("help_fields", default='Fill in filds (one per line)'
                      'which statistics of keywords usage should '
                      'be calculated for.'),
        required=False)

    stop_words = List(
        title=_("label_stop_words", default='Stop words.'),
        description=_("help_stop_words", default='Fill in stop words '
                      '(one per line) which will be excluded from kewords '
                      'statistics calculation.'),
        required=False)

    external_keywords_test = Bool(
        title=_("label_external_keywords_test",
                default='External keywords check'),
        description=_("description_external_keywords_test",
                      default='Make keywords test by opening context url as '
                      'external resource with urllib2.openurl(). This is '
                      'useful when xdv/Deliverance transformation is used '
                      'on the site.'),
        default=False,
        required=False)


class SEOConfigletBaseForm(group.GroupForm):
    label = _(u'label_seobase', default=u'Base')
    fields = field.Fields(ISEOConfigletBaseSchema)


class SEOConfigletAdvancedForm(group.GroupForm):
    label = _(u'label_seoadvanced', default=u'Advanced')
    fields = field.Fields(ISEOConfigletAdvancedSchema)


class ISEOConfigletSchema(ISEOConfigletBaseSchema,
                          ISEOConfigletAdvancedSchema):
    """Combined schema for the adapter lookup.
    """


class SEOConfigletForm(controlpanel.RegistryEditForm):

    id = "SEOConfiglet"


    schema = ISEOConfigletSchema
    label = _("Search Engine Optimizer configuration")
    description = _("seo_configlet_description", default="You can select what "
                    "content types are qSEOptimizer-enabled, and control if "
                    "Dublin Core metatags are exposed in the header of content"
                    " pages.")
    groups = (SEOConfigletBaseForm, SEOConfigletAdvancedForm)

class SEOConfiglet(controlpanel.ControlPanelFormWrapper):
    form = SEOConfigletForm
