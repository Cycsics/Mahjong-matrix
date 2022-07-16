from django.test import TestCase

import datetime
from django.utils import timezone
from mental.models import MentalPost
from django.contrib.auth.models import User

from time import sleep
from django.urls import reverse


class MentalPostModelTests(TestCase):

    def test_was_created_recently_with_future_mental(self):
        # 若文章创建时间为未来，返回 False
        author = User(username='user', password='test_password')
        author.save()

        future_mental = MentalPost(
            author=author,
            title='test',
            body='test',
            created=timezone.now() + datetime.timedelta(days=30)
            )
        self.assertIs(future_mental.was_created_recently(), False)

    def test_was_created_recently_with_seconds_before_mental(self):
        # 若文章创建时间为 1 分钟内，返回 True
        author = User(username='user1', password='test_password')
        author.save()
        seconds_before_mental = MentalPost(
            author=author,
            title='test1',
            body='test1',
            created=timezone.now() - datetime.timedelta(seconds=45)
            )
        self.assertIs(seconds_before_mental.was_created_recently(), True)

    def test_was_created_recently_with_hours_before_mental(self):
        # 若文章创建时间为几小时前，返回 False
        author = User(username='user2', password='test_password')
        author.save()
        hours_before_mental = MentalPost(
            author=author,
            title='test2',
            body='test2',
            created=timezone.now() - datetime.timedelta(hours=3)
            )
        self.assertIs(hours_before_mental.was_created_recently(), False)

    def test_was_created_recently_with_days_before_mental(self):
        # 若文章创建时间为几天前，返回 False
        author = User(username='user3', password='test_password')
        author.save()
        months_before_mental = MentalPost(
            author=author,
            title='test3',
            body='test3',
            created=timezone.now() - datetime.timedelta(days=5)
            )
        self.assertIs(months_before_mental.was_created_recently(), False)


class MentalPostViewTests(TestCase):

    def test_increase_views(self):
        # 请求详情视图时，阅读量 +1
        author = User(username='user4', password='test_password')
        author.save()
        mental = MentalPost(
            author=author,
            title='test4',
            body='test4',
            )
        mental.save()
        self.assertIs(mental.total_views, 0)

        url = reverse('mental:mental_detail', args=(mental.id,))
        response = self.client.get(url)

        viewed_mental = MentalPost.objects.get(id=mental.id)
        self.assertIs(viewed_mental.total_views, 1)

    def test_increase_views_but_not_change_updated_field(self):
        # 请求详情视图时，不改变 updated 字段
        author = User(username='user5', password='test_password')
        author.save()
        mental = MentalPost(
            author=author,
            title='test5',
            body='test5',
            )
        mental.save()

        sleep(0.5)

        url = reverse('mental:mental_detail', args=(mental.id,))
        response = self.client.get(url)

        viewed_mental = MentalPost.objects.get(id=mental.id)
        self.assertIs(viewed_mental.updated - viewed_mental.created < timezone.timedelta(seconds=0.1), True)