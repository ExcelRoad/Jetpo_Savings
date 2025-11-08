from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import Article, Category, Tag, Comment, ArticleSubmission
from .forms import ArticleSubmissionForm


def knowledge_center_list(request):
    """List all published articles with filtering options"""
    articles = Article.objects.filter(is_published=True).select_related('author', 'category').prefetch_related('tags').order_by('-views', '-created_at')

    # Get filter parameters
    category_slug = request.GET.get('category')
    tag_slug = request.GET.get('tag')
    search_query = request.GET.get('q')

    # Apply filters
    if category_slug:
        articles = articles.filter(category__slug=category_slug)

    if tag_slug:
        articles = articles.filter(tags__slug=tag_slug)

    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )

    # Get all categories and tags for the filter sidebar
    categories = Category.objects.annotate(article_count=Count('articles')).filter(article_count__gt=0)
    tags = Tag.objects.annotate(article_count=Count('articles')).filter(article_count__gt=0)

    # Get selected category and tag for highlighting
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)

    selected_tag = None
    if tag_slug:
        selected_tag = get_object_or_404(Tag, slug=tag_slug)

    context = {
        'articles': articles,
        'categories': categories,
        'tags': tags,
        'selected_category': selected_category,
        'selected_tag': selected_tag,
        'search_query': search_query,
    }

    return render(request, 'knowledge_center/article_list.html', context)


def article_detail(request, slug):
    """Display article detail with comments"""
    article = get_object_or_404(
        Article.objects.select_related('author', 'category').prefetch_related('tags'),
        slug=slug,
        is_published=True
    )

    # Increment view count
    article.views += 1
    article.save(update_fields=['views'])

    # Get approved comments
    comments = article.comments.filter(is_approved=True).select_related('author').order_by('-created_at')

    context = {
        'article': article,
        'comments': comments,
    }

    return render(request, 'knowledge_center/article_detail.html', context)


@login_required
def add_comment(request, slug):
    """Add a comment to an article"""
    article = get_object_or_404(Article, slug=slug, is_published=True)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()

        if content:
            Comment.objects.create(
                article=article,
                author=request.user,
                content=content
            )
            messages.success(request, 'התגובה שלך נוספה בהצלחה!')
        else:
            messages.error(request, 'אנא הזן תוכן לתגובה')

    return redirect('article_detail', slug=slug)


@login_required
def submit_article(request):
    """Submit an article for review"""
    # Check if user already has a pending submission
    if ArticleSubmission.has_pending_submission(request.user):
        messages.warning(request, 'יש לך כבר מאמר ממתין לבדיקה. תוכל להגיש מאמר נוסף לאחר שהמאמר הנוכחי יבדק.')
        return redirect('knowledge_center')

    if request.method == 'POST':
        form = ArticleSubmissionForm(request.POST, user=request.user)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.submitter = request.user
            submission.save()
            form.save_m2m()  # Save many-to-many relationships (tags)

            messages.success(request, 'המאמר הוגש בהצלחה! תוכל לעקוב אחר סטטוס המאמר בעמוד הפרופיל שלך.')
            return redirect('knowledge_center')
    else:
        form = ArticleSubmissionForm(user=request.user)

    context = {
        'form': form,
    }
    return render(request, 'knowledge_center/submit_article.html', context)


@login_required
def view_submission(request, submission_id):
    """View a submitted article (only accessible by the submitter)"""
    submission = get_object_or_404(
        ArticleSubmission.objects.select_related('submitter', 'category').prefetch_related('tags'),
        id=submission_id,
        submitter=request.user
    )

    context = {
        'submission': submission,
    }
    return render(request, 'knowledge_center/submission_detail.html', context)


@login_required
def delete_comment(request, comment_id):
    """Delete a comment (only the author can delete their own comment)"""
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    article_slug = comment.article.slug

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'התגובה נמחקה בהצלחה')

    return redirect('article_detail', slug=article_slug)
