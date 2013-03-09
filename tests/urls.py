from . import views
from .compat import patterns, url


urlpatterns = patterns('',
    url(r'^access/login_required/$', views.LoginRequiredView.as_view()),
    url(r'^access/permission_required/$',
        views.PermissionRequiredView.as_view()),
    url(r'^access/multiple_permissions_required/$',
        views.MultiplePermissionsRequiredView.as_view()),
    url(r'^access/superuser_required/$', views.SuperuserRequiredView.as_view()),
    url(r'^access/staffuser_required/$', views.StaffuserRequiredView.as_view()),
    url(r'^access/bad_checkuserview/$', views.BadCheckUserView.as_view()),
    
    
    url(r'^ajax/ajax_response/$', views.AjaxResponseView.as_view()),
    url(r'^ajax/simple_json/$', views.SimpleJsonView.as_view()),
    url(r'^ajax/article_list_json/$', views.ArticleListJsonView.as_view()),
    
    
    url(r'context/headline/$', views.HeadlineView.as_view()),
    url(r'context/headline/(?P<s>[\w-]+)/$',
        views.DynamicHeadlineView.as_view()),
    
    
    url(r'form/user_kwargs/$', views.FormWithUserKwargView.as_view()),
    url(r'form/csrf_exempt/$', views.CsrfExemptView.as_view()),
    url(r'form/success_redirect/$', views.SuccessRedirectView.as_view()),
    url(r'form/success_redirect/custom_context/$',
        views.CustomContextNameSuccessRedirectView.as_view()),
    
    
    url(r'legacy/articles/create/$', views.CreateArticleView.as_view()),
    url(r'legacy/articles/(?P<pk>\d+)/edit/$', views.EditArticleView.as_view(),
        name="edit_article"),
    url(r'legacy/article_list/create/$',
        views.CreateArticleAndRedirectToListView.as_view()),
    url(r'legacy/article_list/create/bad/$',
        views.CreateArticleAndRedirectToListViewBad.as_view()),
    
    
    url(r'^messages/$', views.MessageView.as_view()),
    url(r'^messages/form/$', views.FormMessageView.as_view()),
    url(r'^messages/delete/$', views.DeleteMessageView.as_view()),
    
    
    url(r'queryset/article_list/user/$', views.UserArticleListView.as_view()),
    url(r'^article_list/$', views.ArticleListView.as_view(),
        name='article_list'),
)

urlpatterns += patterns('django.contrib.auth.views',
    # login page, required by some tests
    url(r'^accounts/login/$', 'login', {'template_name': 'blank.html'}),
)
