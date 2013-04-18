from form_designer.contrib.cms_plugins.form_designer_form.models import CMSFormDefinition
from form_designer.contrib.force_response import ForceResponse
from form_designer.views import process_form
from form_designer import settings

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _


class FormDesignerPlugin(CMSPluginBase):
    model = CMSFormDefinition
    module = _('Form Designer')
    name = _('Form')
    admin_preview = False

    def render(self, context, instance, placeholder):
        request = context['request']
               
        if instance.form_definition.form_template_name:
            self.render_template = instance.form_definition.form_template_name
        else:
            self.render_template = settings.DEFAULT_FORM_TEMPLATE

        # Redirection does not work with CMS plugin, hence disable:
        result = process_form(request, instance.form_definition, context)
        if isinstance(result, HttpResponseRedirect):
            raise ForceResponse(result)
        else:
            return result


plugin_pool.register_plugin(FormDesignerPlugin)
