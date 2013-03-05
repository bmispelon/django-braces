from django import test
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from .compat import force_text
from .factories import make_user
from .helpers import TestViewHelper
from .views import (PermissionRequiredView, MultiplePermissionsRequiredView,
                    SuperuserRequiredView, StaffuserRequiredView,
                    LoginRequiredView)


class _TestAccessBasicsMixin(TestViewHelper):
    """
    A set of basic tests for access mixins.
    """
    view_url = None

    def build_authorized_user(self):
        """
        Returns user authorized to access view.
        """
        raise NotImplementedError

    def build_unauthorized_user(self):
        """
        Returns user not authorized to access view.
        """
        raise NotImplementedError

    def test_success(self):
        """
        If user is authorized then view should return normal response.
        """
        user = self.build_authorized_user()
        self.client.login(username=user.username, password='asdf1234')
        resp = self.client.get(self.view_url)
        self.assertEqual(200, resp.status_code)
        self.assertEqual('OK', force_text(resp.content))

    def test_redirects_to_login(self):
        """
        Browser should be redirected to login page if user is not authorized
        to view this page.
        """
        user = self.build_unauthorized_user()
        self.client.login(username=user.username, password='asdf1234')
        resp = self.client.get(self.view_url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % self.view_url)

    def test_raise_permission_denied(self):
        """
        PermissionDenied should be raised if user is not authorized and
        raise_exception attribute is set to True.
        """
        user = self.build_unauthorized_user()
        req = self.build_request(user=user, path=self.view_url)

        with self.assertRaises(PermissionDenied):
            self.dispatch_view(req, raise_exception=True)

    def test_custom_login_url(self):
        """
        Login url should be customizable.
        """
        user = self.build_unauthorized_user()
        req = self.build_request(user=user, path=self.view_url)
        resp = self.dispatch_view(req, login_url='/login/')
        self.assertEqual('/login/?next=%s' % self.view_url, resp['Location'])

    def test_custom_redirect_field_name(self):
        """
        Redirect field name should be customizable.
        """
        user = self.build_unauthorized_user()
        req = self.build_request(user=user, path=self.view_url)
        resp = self.dispatch_view(req, redirect_field_name='foo')
        expected_url = '/accounts/login/?foo=%s' % self.view_url
        self.assertEqual(expected_url, resp['Location'])

    def test_get_login_url_raises_exception(self):
        """
        Test that get_login_url from AccessMixin raises
        ImproperlyConfigured.
        """
        with self.assertRaises(ImproperlyConfigured):
            self.dispatch_view(self.build_request(path=self.view_url),
                login_url=None)

    def test_get_redirect_field_name_raises_exception(self):
        """
        Test that get_redirect_field_name from AccessMixin raises
        ImproperlyConfigured.
        """
        with self.assertRaises(ImproperlyConfigured):
            self.dispatch_view(self.build_request(path=self.view_url),
                redirect_field_name=None)


class TestCheckUserMixin(test.TestCase):
    view_url = '/bad_checkuserview/'
    
    def test_improperly_configured(self):
        with self.assertRaises(ImproperlyConfigured):
            self.client.get(self.view_url)


class TestLoginRequiredMixin(TestViewHelper):
    """
    Tests for LoginRequiredMixin.
    """
    view_class = LoginRequiredView
    view_url = '/login_required/'

    def test_anonymous(self):
        resp = self.client.get(self.view_url)
        self.assertRedirects(resp, '/accounts/login/?next=/login_required/')

    def test_anonymous_raises_exception(self):
        with self.assertRaises(PermissionDenied):
            self.dispatch_view(self.build_request(path=self.view_url),
                raise_exception=True)

    def test_authenticated(self):
        user = make_user()
        self.client.login(username=user.username, password='asdf1234')
        resp = self.client.get(self.view_url)
        assert resp.status_code == 200
        assert force_text(resp.content) == 'OK'


class TestPermissionRequiredMixin(_TestAccessBasicsMixin, test.TestCase):
    """
    Tests for PermissionRequiredMixin.
    """
    view_class = PermissionRequiredView
    view_url = '/permission_required/'

    def build_authorized_user(self):
        return make_user(permissions=['auth.add_user'])

    def build_unauthorized_user(self):
        return make_user()

    def test_invalid_permission(self):
        """
        ImproperlyConfigured exception should be raised in two situations:
        if permission is None or if permission has invalid name.
        """
        with self.assertRaises(ImproperlyConfigured):
            self.dispatch_view(self.build_request(), permission_required=None)


class TestMultiplePermissionsRequiredMixin(
        _TestAccessBasicsMixin, test.TestCase):
    view_class = MultiplePermissionsRequiredView
    view_url = '/multiple_permissions_required/'

    def build_authorized_user(self):
        return make_user(permissions=[
            'tests.add_article', 'tests.change_article', 'auth.change_user'])

    def build_unauthorized_user(self):
        return make_user(permissions=['tests.add_article'])

    def test_redirects_to_login(self):
        """
        User should be redirected to login page if he or she does not have
        sufficient permissions.
        """
        url = '/multiple_permissions_required/'
        test_cases = (
            # missing one permission from 'any'
            ['tests.add_article', 'tests.change_article'],
            # missing one permission from 'all'
            ['tests.add_article', 'auth.add_user'],
            # no permissions at all
            [],
        )

        for permissions in test_cases:
            user = make_user(permissions=permissions)
            self.client.login(username=user.username, password='asdf1234')
            resp = self.client.get(url)
            self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

    def test_invalid_permissions(self):
        """
        ImproperlyConfigured exception should be raised if permissions
        attribute is set incorrectly.
        """
        permissions = (
            None,  # permissions must be set
            (),  # and they must be a dict
            {},  # at least one of 'all', 'any' keys must be present
            {'all': None},  # both all and any must be list or a tuple
            {'all': {'a': 1}},
            {'any': None},
            {'any': {'a': 1}},
        )

        for attr in permissions:
            with self.assertRaises(ImproperlyConfigured):
                self.dispatch_view(self.build_request(), permissions=attr)

    def test_raise_permission_denied(self):
        """
        PermissionDenied should be raised if user does not have sufficient
        permissions and raise_exception is set to True.
        """
        test_cases = (
            # missing one permission from 'any'
            ['tests.add_article', 'tests.change_article'],
            # missing one permission from 'all'
            ['tests.add_article', 'auth.add_user'],
            # no permissions at all
            [],
        )

        for permissions in test_cases:
            user = make_user(permissions=permissions)
            req = self.build_request(user=user)
            with self.assertRaises(PermissionDenied):
                self.dispatch_view(req, raise_exception=True)

    def test_all_permissions_key(self):
        """
        Tests if everything works if only 'all' permissions has been set.
        """
        permissions = {'all': ['auth.add_user', 'tests.add_article']}
        user = make_user(permissions=permissions['all'])
        req = self.build_request(user=user)

        resp = self.dispatch_view(req, permissions=permissions)
        self.assertEqual('OK', force_text(resp.content))

        user = make_user(permissions=['auth.add_user'])
        with self.assertRaises(PermissionDenied):
            self.dispatch_view(
                self.build_request(user=user), raise_exception=True,
                permissions=permissions)

    def test_any_permissions_key(self):
        """
        Tests if everything works if only 'any' permissions has been set.
        """
        permissions = {'any': ['auth.add_user', 'tests.add_article']}
        user = make_user(permissions=['tests.add_article'])
        req = self.build_request(user=user)

        resp = self.dispatch_view(req, permissions=permissions)
        self.assertEqual('OK', force_text(resp.content))

        user = make_user(permissions=[])
        with self.assertRaises(PermissionDenied):
            self.dispatch_view(
                self.build_request(user=user), raise_exception=True,
                permissions=permissions)


class TestSuperuserRequiredMixin(_TestAccessBasicsMixin, test.TestCase):
    view_class = SuperuserRequiredView
    view_url = '/superuser_required/'

    def build_authorized_user(self):
        return make_user(is_superuser=True, is_staff=True)

    def build_unauthorized_user(self):
        return make_user()


class TestStaffuserRequiredMixin(_TestAccessBasicsMixin, test.TestCase):
    view_class = StaffuserRequiredView
    view_url = '/staffuser_required/'

    def build_authorized_user(self):
        return make_user(is_staff=True)

    def build_unauthorized_user(self):
        return make_user()
