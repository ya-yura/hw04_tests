from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def check_data(self, response, is_post=False):
        if is_post:
            first_object = response.context.get('post')
        else:
            first_object = response.context.get('page_obj')[0]
        self.assertEqual(first_object.pub_date, self.post.pub_date)
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group, self.post.group)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:index'))
        return self.check_data(response)

    def test_group_posts_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.author_client.get(reverse(
            'posts:group_list',
            args=(self.group.slug,),
        ))
        group_from_context = response.context.get('group')
        self.assertEqual(group_from_context, self.post.group)
        return self.check_data(response)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.author_client.get(reverse(
            'posts:profile',
            args=(self.author.username,),
        ))
        author_from_context = response.context.get('author')
        self.assertEqual(author_from_context, self.post.author)
        return self.check_data(response)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(reverse(
            'posts:post_detail',
            args=(self.post.id,),
        ))
        return self.check_data(response, is_post=True)

    def test_post_not_used_uncorrect_group(self):
        """Пост не попал не в ту группу."""
        new_group = Group.objects.create(
            title='Тестовый измененный заголовок',
            slug='test-slug-fixed',
            description='Тестовое измененное описание',
        )
        response = self.author_client.get(reverse(
            'posts:group_list',
            args=(new_group.slug,),
        ))
        page_obj = response.context.get('page_obj')
        page_obj_count = len(page_obj)
        self.assertEqual(page_obj_count, 0)
        post_have_group = self.post.group
        self.assertTrue(post_have_group)
        self.assertEqual(
            self.group.posts.first(),
            post_have_group.posts.first(),
        )


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post_list = []
        for pryanik in range(settings.TEST_POSTS):
            cls.post_list.append(Post(
                author=cls.author,
                text='Тестовый текст ' + str(pryanik),
                group=cls.group,
            ))
        cls.post = Post.objects.bulk_create(cls.post_list)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_paginator_contains(self):
        """Проверяемм работу паджинатора."""
        pages = (
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.group.slug,)),
            reverse('posts:profile', args=(self.author.username,)),
        )
        data = (
            ('?page=1', settings.NUMBER_OBJECTS),
            ('?page=2', settings.TEST_PAGINATOR),
        )
        for page in pages:
            with self.subTest(page=page):
                for url, number_posts in data:
                    response = self.author_client.get(page + url)
                    context = response.context.get('page_obj')
                    self.assertEqual(len(context), number_posts)
