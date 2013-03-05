from django import test
from django.core.exceptions import ImproperlyConfigured
from .helpers import TestViewHelper
from .views import SuccessRedirectView


class TestNextMixin(TestViewHelper):
    view_class = SuccessRedirectView
    view_url = '/success_redirect/'
    view_url_custom_context = '/success_redirect/custom_context/'
    default_url = '/'
    
    def _test_redirect(self, expected, data=None, **viewkwargs):
        if data is None:
            data = {}
        req = self.build_request(path=self.view_url, method='POST', data=data)
        resp = self.dispatch_view(req, **viewkwargs)
        self.assertEqual(expected, resp['Location'])
    
    def test_improperly_configured(self):
        with self.assertRaises(ImproperlyConfigured):
            self._test_redirect(self.default_url, default_success_url=None)

    def test_no_parameter_supplied(self):
        self._test_redirect(self.default_url)

    def test_parameter_supplied(self):
        self._test_redirect('/foo/', {'next': '/foo/'})

    def test_custom_parameter_name(self):
        self._test_redirect('/foo/', {'foo': '/foo/'}, success_url_param='foo')
        self._test_redirect(self.default_url, {'next': '/foo/'}, success_url_param='foo')

    def test_with_success_url(self):
        self._test_redirect('/bar/', {'next': '/foo/'}, success_url='/bar/')

    def test_context_without_param(self):
        resp = self.client.get(self.view_url)
        self.assertEqual(resp.context['next'], self.default_url)

    def test_context_with_param(self):
        resp = self.client.get(self.view_url, data={'next': '/foo/'})
        self.assertEqual(resp.context['next'], '/foo/')

    def test_context_custom_name(self):
        resp = self.client.get(self.view_url_custom_context)
        self.assertEqual(resp.context['foo'], self.default_url)

    def test_redirect_method(self):
        req = self.build_request(path=self.view_url)
        view = self.build_view(req)
        resp = view.redirect()
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], self.default_url)
