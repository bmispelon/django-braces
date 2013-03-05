from . import views
from .compat import patterns, url


urlpatterns = patterns('',
    # LoginRequiredMixin tests
    url(r'^login_required/$', views.LoginRequiredView.as_view()),

    # AjaxResponseMixin tests
    url(r'^ajax_response/$', views.AjaxResponseView.as_view()),

    # CreateAndRedirectToEditView tests
    url(r'^article/create/$', views.CreateArticleView.as_view()),
    url(r'^article/(?P<pk>\d+)/edit/$', views.EditArticleView.as_view(),
        name="edit_article"),

    url(r'^article_list/create/$',
        views.CreateArticleAndRedirectToListView.as_view()),
    url(r'^article_list_bad/create/$',
        views.CreateArticleAndRedirectToListViewBad.as_view()),
    url(r'^article_list/$', views.ArticleListView.as_view(),
        name='article_list'),
    url(r'^user_article_list/$', views.UserArticleListView.as_view(),
        name='user_article_list'),

    # UserFormKwargsMixin tests
    url(r'^form_with_user_kwarg/$', views.FormWithUserKwargView.as_view()),

    # SetHeadlineMixin tests
    url(r'^headline/$', views.HeadlineView.as_view()),
    url(r'^headline/(?P<s>[\w-]+)/$', views.DynamicHeadlineView.as_view()),

    # PermissionRequiredMixin tests
    url(r'^permission_required/$', views.PermissionRequiredView.as_view()),

    # MultiplePermissionsRequiredMixin tests
    url(r'^multiple_permissions_required/$',
        views.MultiplePermissionsRequiredView.as_view()),

    # SuperuserRequiredMixin tests
    url(r'^superuser_required/$', views.SuperuserRequiredView.as_view()),

    # StaffuserRequiredMixin tests
    url(r'^staffuser_required/$', views.StaffuserRequiredView.as_view()),

    # BadCheckUserView tests
    url(r'^bad_checkuserview/$', views.BadCheckUserView.as_view()),

    # CsrfExemptMixin tests
    url(r'^csrf_exempt/$', views.CsrfExemptView.as_view()),

    # SuccessRedirectView tests
    url(r'^success_redirect/$', views.SuccessRedirectView.as_view()),
    # CustomContextNameSuccessRedirectView tests
    url(r'^success_redirect/custom_context/$',
        views.CustomContextNameSuccessRedirectView.as_view()),

    # JSONResponseMixin tests
    url(r'^simple_json/$', views.SimpleJsonView.as_view()),
    url(r'^article_list_json/$', views.ArticleListJsonView.as_view()),

    # MessageMixin tests
    url(r'^messages/$', views.MessageView.as_view()),
    url(r'^messages/form/$', views.FormMessageView.as_view()),
    url(r'^messages/delete/$', views.DeleteMessageView.as_view()),
)

urlpatterns += patterns('django.contrib.auth.views',
    # login page, required by some tests
    url(r'^accounts/login/$', 'login', {'template_name': 'blank.html'}),
)
