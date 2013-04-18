"""
Source: http://djangosnippets.org/snippets/2541/

Motivation
==========
There are cases when rendering had already started, but you have to return Your response nevertheless. A good example is when you have a django-cms plugin and a form in it. You want to redirect after the form was processed, but normally you can't do it.

More information here:
https://github.com/divio/django-cms/issues/79
http://groups.google.com/group/django-cms/browse_thread/thread/79ab6080c80bbcb5?pli=1

Usage
=====
1) Add ForceRedirectsMiddleware to MIDDLEWARE_CLASSES in your settings.py
2) throw ForceResponse(HttpResponseRedirect(reverse('your_view_name'))) whenever you want.


Code example (working cms plugin):
==================================
from cv.utils import ForceResponse

class CVPlugin(CMSPluginBase):
    def render(self, context, instance, placeholder):
        request = context['request']
        if request.method == 'POST':
            cv_form = CVForm(request.POST, request.FILES)
        else:
            cv_form = CVForm()

        if not cv_form.is_valid():
            context.update({ 'form' : cv_form })
            return context

        # Saving CV
        cv = cv_form.save(commit=False)
        code = cv.gen_code()
        cv.save()
            
        raise ForceResponse(HttpResponseRedirect(reverse('dashboard',
            kwargs={'code': cv.code})))

plugin_pool.register_plugin(CVPlugin)
"""

class ForceResponse(Exception):
    def __init__(self, response):
        self.response = response

class ForceResponseMiddleware:
    def process_exception(self, request, e):
        """Because django plugins cannot throw raw response
        (redirect is required to user dashboard after form is submitted),
        a solution is to raise an exception, catch it with middleware and
        react.

        This middleware checks for ForceResponse exception and returns it's
        response object.

        In reality, ForceResponse is caught as TemplateSyntaxtError in cms
        plugin. So we have to extract ForceResponse from it.

        Instance of TemplateSyntaxError has exc_info field where it has the
        original exception. exc_info[1] is the exception instance.
        """
        from django.template import TemplateSyntaxError
        if isinstance(e, TemplateSyntaxError) and getattr(e, 'exc_info', 0):
            try:
                e = e.exc_info[1]
            except: # Not iterable or IndexError
                raise e # as if nothing had happened
        if isinstance(e, ForceResponse):
            return e.response
