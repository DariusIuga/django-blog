from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import Post


# Create your views here.


class PostListView(ListView):
    model = Post
    template_name = "blog/home.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"
    ordering = ["-date_posted"]
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = "blog/user_posts.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"
    paginate_by = 5

    def get_queryset(self) -> QuerySet[Any]:
        return Post.objects.filter(
            author=get_object_or_404(User, username=self.kwargs.get("username"))
        ).order_by("-date_posted")


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["title", "content"]

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ["title", "content"]

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self) -> bool | None:
        # Checks that the logged in user is the same as the author of this post
        # If they are different, the current user shouldn't be able to modify or delete the post
        return self.request.user == self.get_object().author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = "/"

    def test_func(self) -> bool | None:
        return self.request.user == self.get_object().author


def about(request):
    return render(request, "blog/about.html", {"title": "About"})
