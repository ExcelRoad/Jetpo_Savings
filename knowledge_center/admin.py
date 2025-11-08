from django.contrib import admin
from django.utils import timezone
from .models import Category, Tag, Article, Comment, ArticleSubmission


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'views', 'created_at']
    list_filter = ['is_published', 'category', 'created_at', 'tags']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['views', 'created_at', 'updated_at']

    fieldsets = (
        ('מידע בסיסי', {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('סיווג', {
            'fields': ('category', 'tags')
        }),
        ('מטא-נתונים', {
            'fields': ('author', 'is_published')
        }),
        ('סטטיסטיקות', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ArticleSubmission)
class ArticleSubmissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'submitter', 'expertise_type', 'review_status', 'submitted_at']
    list_filter = ['review_status', 'expertise_type', 'submitted_at']
    search_fields = ['title', 'content', 'submitter__email', 'submitter__first_name', 'submitter__last_name']
    readonly_fields = ['submitter', 'submitted_at', 'approved_article']
    filter_horizontal = ['tags']
    actions = ['approve_submissions', 'decline_submissions']

    fieldsets = (
        ('מידע מגיש', {
            'fields': ('submitter', 'submitter_full_name', 'expertise_type', 'agent_diploma_id', 'advisor_diploma_id', 'academic_institution', 'academic_degree', 'company_name', 'other_expertise')
        }),
        ('תוכן המאמר', {
            'fields': ('title', 'excerpt', 'content', 'category', 'tags')
        }),
        ('סטטוס בדיקה', {
            'fields': ('review_status', 'decline_reason', 'reviewed_at', 'approved_article')
        }),
        ('תאריכים', {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Override save to automatically create article when status changes to APPROVED"""
        # Check if this is an update (not new submission)
        if change:
            # Get the original object from database
            original = ArticleSubmission.objects.get(pk=obj.pk)

            # Check if status changed from PENDING/DECLINED to APPROVED
            if original.review_status != 'APPROVED' and obj.review_status == 'APPROVED':
                # Create article from submission if it doesn't exist
                if not obj.approved_article:
                    article = Article.objects.create(
                        title=obj.title,
                        content=obj.content,
                        excerpt=obj.excerpt,
                        author=obj.submitter,
                        category=obj.category,
                        is_published=True,
                        english_title=obj.english_title  # Pass english_title for slug generation
                    )
                    article.tags.set(obj.tags.all())
                    obj.approved_article = article
                    obj.reviewed_at = timezone.now()
                    self.message_user(request, f'המאמר "{obj.title}" אושר ופורסם במרכז הידע')

            # If status changed to DECLINED, set reviewed_at
            elif original.review_status != 'DECLINED' and obj.review_status == 'DECLINED':
                obj.reviewed_at = timezone.now()

        super().save_model(request, obj, form, change)

    def approve_submissions(self, request, queryset):
        """Approve selected submissions and create published articles"""
        approved_count = 0
        for submission in queryset.filter(review_status='PENDING'):
            # Create article from submission
            article = Article.objects.create(
                title=submission.title,
                content=submission.content,
                excerpt=submission.excerpt,
                author=submission.submitter,
                category=submission.category,
                is_published=True,
                english_title=submission.english_title  # Pass english_title for slug generation
            )
            article.tags.set(submission.tags.all())

            # Update submission
            submission.review_status = 'APPROVED'
            submission.reviewed_at = timezone.now()
            submission.approved_article = article
            submission.save()

            approved_count += 1

        self.message_user(request, f'{approved_count} מאמרים אושרו ופורסמו בהצלחה')

    approve_submissions.short_description = 'אשר מאמרים שנבחרו'

    def decline_submissions(self, request, queryset):
        """Decline selected submissions"""
        declined_count = queryset.filter(review_status='PENDING').update(
            review_status='DECLINED',
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{declined_count} מאמרים נדחו')

    decline_submissions.short_description = 'דחה מאמרים שנבחרו'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['article', 'author', 'created_at', 'is_approved']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'author__email', 'article__title']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('תגובה', {
            'fields': ('article', 'author', 'content')
        }),
        ('מידע נוסף', {
            'fields': ('is_approved', 'created_at', 'updated_at')
        }),
    )
