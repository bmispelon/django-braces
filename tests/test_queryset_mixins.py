from django import test

from .factories import make_user, make_article

class TestUserQuerysetMixin(test.TestCase):
    """Tests for UserQuerysetMixin."""
    
    def test_queryset_is_filtered(self):
        alice = make_user(username='alice')
        article_alice = make_article(author=alice, title="Alice's article")
        bob = make_user(username='bob')
        make_article(author=bob, title="Bob's article")

        self.client.login(username='alice', password='asdf1234')

        resp = self.client.get('/user_article_list/')
        self.assertQuerysetEqual(
            resp.context['object_list'],
            [article_alice.pk],
            ordered=False,
            transform=lambda a: a.pk,
        )
