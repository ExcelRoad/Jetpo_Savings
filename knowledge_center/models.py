from django.db import models
from django.conf import settings
from django.utils.text import slugify
from anyascii import anyascii
from ckeditor.fields import RichTextField


def generate_unique_slug(title, english_title=None, article_id=None):
    """
    Generate a unique slug for an article using the hybrid approach:
    1. If english_title provided, use it (best SEO)
    2. If not, try transliteration (decent SEO)
    3. If transliteration fails/too short, use article-{id}
    """
    base_slug = None

    # Option 1: Use english_title if provided
    if english_title and english_title.strip():
        base_slug = slugify(english_title.strip())

    # Option 2: Try transliteration
    if not base_slug and title:
        # Transliterate Hebrew/other scripts to Latin
        transliterated = anyascii(title)
        base_slug = slugify(transliterated)

        # If transliteration resulted in too short slug (< 3 chars), reject it
        if base_slug and len(base_slug) < 3:
            base_slug = None

    # Option 3: Fallback to 'article' if nothing worked
    if not base_slug:
        base_slug = 'article'

    # Add ID to ensure uniqueness
    if article_id:
        return f'{base_slug}-{article_id}'

    return base_slug


class Category(models.Model):
    """Category for organizing articles"""
    name = models.CharField(max_length=100, unique=True, verbose_name="שם קטגוריה")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="תיאור")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "קטגוריה"
        verbose_name_plural = "קטגוריות"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tags for articles"""
    name = models.CharField(max_length=50, unique=True, verbose_name="שם תגית")
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    class Meta:
        verbose_name = "תגית"
        verbose_name_plural = "תגיות"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):
    """Article in the knowledge center"""
    title = models.CharField(max_length=200, verbose_name="כותרת")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = RichTextField(verbose_name="תוכן")
    excerpt = models.TextField(max_length=300, blank=True, verbose_name="תקציר")

    # Author and metadata
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='articles', verbose_name="כותב")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles', verbose_name="קטגוריה")
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles', verbose_name="תגיות")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="תאריך יצירה")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="תאריך עדכון")

    # Publishing
    is_published = models.BooleanField(default=True, verbose_name="פורסם")

    # Stats
    views = models.PositiveIntegerField(default=0, verbose_name="צפיות")

    class Meta:
        verbose_name = "מאמר"
        verbose_name_plural = "מאמרים"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Extract english_title from kwargs if provided (used when creating from submission)
        english_title = kwargs.pop('english_title', None)

        if not self.slug:
            # If this is a new object (no pk yet), save first to get ID
            if not self.pk:
                # Temporarily set a placeholder slug
                self.slug = 'temp-placeholder'
                super().save(*args, **kwargs)
                # Now generate the actual slug with ID
                self.slug = generate_unique_slug(self.title, english_title, self.pk)
                super().save(update_fields=['slug'])
                return
            else:
                # For existing objects, generate slug without ID first
                base_slug = generate_unique_slug(self.title, english_title)
                slug = base_slug
                counter = 1
                # Ensure uniqueness
                while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                    slug = f'{base_slug}-{counter}'
                    counter += 1
                self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_comment_count(self):
        return self.comments.filter(is_approved=True).count()


class ArticleSubmission(models.Model):
    """Article submission for review"""

    class ExpertiseType(models.TextChoices):
        AGENT = 'AGENT', 'סוכן פיננסי'
        ADVISOR = 'ADVISOR', 'יועץ פיננסי'
        ACADEMIC = 'ACADEMIC', 'אקדמאי'
        ANALYST = 'ANALYST', 'אנליסט פיננסי'
        INVESTOR = 'INVESTOR', 'משקיע מנוסה'
        OTHER = 'OTHER', 'אחר'

    class ReviewStatus(models.TextChoices):
        PENDING = 'PENDING', 'ממתין לבדיקה'
        APPROVED = 'APPROVED', 'אושר'
        DECLINED = 'DECLINED', 'נדחה'

    class AcademicDegree(models.TextChoices):
        BA = 'BA', 'תואר ראשון (BA/BSc)'
        MA = 'MA', 'תואר שני (MA/MSc)'
        MBA = 'MBA', 'MBA'
        PHD = 'PHD', 'דוקטורט (PhD)'
        MD = 'MD', 'רפואה (MD)'
        EDD = 'EDD', 'חינוך (EdD)'
        JD = 'JD', 'משפטים (JD)'

    # Submitter info
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='article_submissions', verbose_name="מגיש")
    submitter_full_name = models.CharField(max_length=200, verbose_name="שם מלא")
    expertise_type = models.CharField(max_length=20, choices=ExpertiseType.choices, verbose_name="סוג מומחיות")

    # Credentials (optional based on expertise type)
    agent_diploma_id = models.CharField(max_length=100, blank=True, verbose_name="מספר רישיון סוכן")
    advisor_diploma_id = models.CharField(max_length=100, blank=True, verbose_name="מספר רישיון יועץ")
    academic_institution = models.CharField(max_length=200, blank=True, verbose_name="שם מוסד אקדמי")
    academic_degree = models.CharField(max_length=10, choices=AcademicDegree.choices, blank=True, verbose_name="תואר אקדמי")
    company_name = models.CharField(max_length=200, blank=True, verbose_name="שם חברה")
    other_expertise = models.CharField(max_length=200, blank=True, verbose_name="מומחיות אחרת")

    # Article content
    title = models.CharField(max_length=200, verbose_name="כותרת")
    english_title = models.CharField(max_length=200, blank=True, verbose_name="כותרת באנגלית")
    excerpt = models.TextField(max_length=300, verbose_name="תקציר (2 שורות)")
    content = RichTextField(verbose_name="תוכן")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="קטגוריה")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="תגיות")

    # Review status
    review_status = models.CharField(max_length=20, choices=ReviewStatus.choices, default=ReviewStatus.PENDING, verbose_name="סטטוס בדיקה")
    decline_reason = models.TextField(blank=True, verbose_name="סיבת דחייה")

    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="תאריך הגשה")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="תאריך בדיקה")

    # Reference to created article if approved
    approved_article = models.OneToOneField(Article, on_delete=models.SET_NULL, null=True, blank=True, related_name='submission', verbose_name="מאמר שאושר")

    class Meta:
        verbose_name = "הגשת מאמר"
        verbose_name_plural = "הגשות מאמרים"
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.title} - {self.submitter.get_full_name()} ({self.get_review_status_display()})"

    def has_pending_submission(user):
        """Check if user has a pending submission"""
        return ArticleSubmission.objects.filter(submitter=user, review_status=ArticleSubmission.ReviewStatus.PENDING).exists()


class Comment(models.Model):
    """Comments on articles"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments', verbose_name="מאמר")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='article_comments', verbose_name="כותב")
    content = models.TextField(verbose_name="תוכן התגובה")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="תאריך יצירה")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="תאריך עדכון")

    # Moderation
    is_approved = models.BooleanField(default=True, verbose_name="אושר")

    class Meta:
        verbose_name = "תגובה"
        verbose_name_plural = "תגובות"
        ordering = ['created_at']

    def __str__(self):
        return f"תגובה של {self.author.get_full_name()} על {self.article.title}"
