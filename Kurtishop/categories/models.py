from django.db import models
from django.utils.text import slugify
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=False, blank=True)

    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )

    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
    )

    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=["is_active", "is_deleted"]),
        ]
        constraints = [
            # Allow same name if one is soft deleted
            UniqueConstraint(
                fields=['name'],
                condition=Q(is_deleted=False),
                name='unique_category_name_active',
            ),
            # Same for slug
            UniqueConstraint(
                fields=['slug'],
                condition=Q(is_deleted=False),
                name='unique_category_slug_active',
            )
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Category.objects.filter(slug=slug, is_deleted=False).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug

        super().save(*args, **kwargs)
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    @property
    def is_root(self):
        return self.parent is None