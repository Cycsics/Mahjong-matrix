from django.db import models
from django.contrib.auth.models import User
from mental.models import MentalPost
# django-ckeditor
from ckeditor.fields import RichTextField
# django-mptt
from mptt.models import MPTTModel, TreeForeignKey

# 博文的评论
class Comment_mental(MPTTModel):
    mental = models.ForeignKey(
        MentalPost,
        on_delete=models.CASCADE,
        related_name='comments_mental'
    )

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='comments_mental'
    )

    # mptt树形结构
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    # 记录二级评论回复给谁, str
    reply_to = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replyers_mental'
    )

    body = RichTextField()
    created = models.DateTimeField(auto_now_add=True)

    class MPTTMeta:
        order_insertion_by = ['created']

    def __str__(self):
        return self.body[:20]
