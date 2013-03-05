from django import test
from .helpers import TestViewHelper
from .views import MessageView, FormMessageView, DeleteMessageView

from braces.views.messages import _MessageWrapper


class FakeMessageApi(object):
    def dummy(self, request, bar):
        return request, bar

"""
__all__ = (
    'add_message', 'get_messages',
    'get_level', 'set_level',
    'debug', 'info', 'success', 'warning', 'error',
)
"""

class TestMessageWrapper(TestViewHelper):
    def test_wrapping(self):
        request = self.build_request()
        wrapper = _MessageWrapper(request, FakeMessageApi())
        res = wrapper.dummy('foo')
        self.assertIs(res[0], request)
        self.assertEqual(res[1], 'foo')


class TestMessageMixin(TestViewHelper):
    view_class = MessageView
    view_url = '/messages/'
    
    def test_message(self):
        resp = self.client.get(self.view_url)
        messages = [m.message for m in resp.context['messages']]
        self.assertEqual(messages[0], 'working')
