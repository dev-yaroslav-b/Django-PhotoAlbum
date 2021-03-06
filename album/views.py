from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import generic

from .models import MediaPost
from .forms import MediaPostForm, ShareYoutubeVideoForm
from .get_video import get_video


class IndexView(generic.ListView):
    context_object_name = 'posts'
    template_name = 'album/index.html'

    def get_queryset(self):
        """Return all published posts ordered by creation date."""
        return MediaPost.objects.order_by('-created_date')


class DetailView(LoginRequiredMixin, generic.DetailView):
    model = MediaPost
    context_object_name = 'post'
    template_name = "album/details.html"


@login_required
def new_post(request):
    if request.method == "POST":
        form = MediaPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.created_date = timezone.now()
            post.save()
            return redirect('details', pk=post.pk)
    else:
        form = MediaPostForm()
    return render(request, 'album/new_post.html', {'form': form})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(MediaPost, pk=pk)
    if request.method == "POST":
        form = MediaPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('details', pk=post.pk)
    else:
        form = MediaPostForm(instance=post)
    return render(request, 'album/edit_post.html', {'form': form})


@login_required
def delete_post(request, pk):
    try:
        post = MediaPost.objects.get(pk=pk)
        post.delete()
        return redirect('index')
    except MediaPost.DoesNotExist:
        return redirect('index')


@login_required
def share_video(request):
    if request.method == "POST":
        form = ShareYoutubeVideoForm(request.POST)
        if form.is_valid():
            title, description, media = get_video(
                form.cleaned_data['link'], request.user.id)
            post = MediaPost(user=request.user,
                             title=title,
                             description=description,
                             media=media,
                             created_date=timezone.now())
            post.save()
            return redirect('index')
    else:
        form = ShareYoutubeVideoForm()
    return render(request, 'album/share_video.html', {'form': form})
