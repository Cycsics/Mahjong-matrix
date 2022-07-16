from django.test import TestCase

import datetime
from django.utils import timezone
from addiction.models import AddictionPost
from django.contrib.auth.models import User

from time import sleep
from django.urls import reverse


class AddictionPostModelTests(TestCase):

    def test_was_created_recently_with_future_addiction(self):
        # 若文章创建时间为未来，返回 False
        author = User(username='user', password='test_password')
        author.save()

        future_addiction = AddictionPost(
            author=author,
            title='test',
            body='test',
            created=timezone.now() + datetime.timedelta(days=30)
            )
        self.assertIs(future_addiction.was_created_recently(), False)

    def test_was_created_recently_with_seconds_before_addiction(self):
        # 若文章创建时间为 1 分钟内，返回 True
        author = User(username='user1', password='test_password')
        author.save()
        seconds_before_addiction = AddictionPost(
            author=author,
            title='test1',
            body='test1',
            created=timezone.now() - datetime.timedelta(seconds=45)
            )
        self.assertIs(seconds_before_addiction.was_created_recently(), True)

    def test_was_created_recently_with_hours_before_addiction(self):
        # 若文章创建时间为几小时前，返回 False
        author = User(username='user2', password='test_password')
        author.save()
        hours_before_addiction = AddictionPost(
            author=author,
            title='test2',
            body='test2',
            created=timezone.now() - datetime.timedelta(hours=3)
            )
        self.assertIs(hours_before_addiction.was_created_recently(), False)

    def test_was_created_recently_with_days_before_addiction(self):
        # 若文章创建时间为几天前，返回 False
        author = User(username='user3', password='test_password')
        author.save()
        months_before_addiction = AddictionPost(
            author=author,
            title='test3',
            body='test3',
            created=timezone.now() - datetime.timedelta(days=5)
            )
        self.assertIs(months_before_addiction.was_created_recently(), False)


class AddictionPostViewTests(TestCase):

    def test_increase_views(self):
        # 请求详情视图时，阅读量 +1
        author = User(username='user4', password='test_password')
        author.save()
        addiction = AddictionPost(
            author=author,
            title='test4',
            body='test4',
            )
        addiction.save()
        self.assertIs(addiction.total_views, 0)

        url = reverse('addiction:addiction_detail', args=(addiction.id,))
        response = self.client.get(url)

        viewed_addiction = AddictionPost.objects.get(id=addiction.id)
        self.assertIs(viewed_addiction.total_views, 1)

    def test_increase_views_but_not_change_updated_field(self):
        # 请求详情视图时，不改变 updated 字段
        author = User(username='user5', password='test_password')
        author.save()
        addiction = AddictionPost(
            author=author,
            title='test5',
            body='test5',
            )
        addiction.save()

        sleep(0.5)

        url = reverse('addiction:addiction_detail', args=(addiction.id,))
        response = self.client.get(url)

        viewed_addiction = AddictionPost.objects.get(id=addiction.id)
        self.assertIs(viewed_addiction.updated - viewed_addiction.created < timezone.timedelta(seconds=0.1), True)