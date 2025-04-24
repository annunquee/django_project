from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post

TEST_USERNAME = 'testuser'
TEST_PASSWORD = '12345'


class PostModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username=TEST_USERNAME, password=TEST_PASSWORD)
        cls.post = Post.objects.create(
            author=cls.user,
            title='Test Post',
            content='This is a test post'
        )

    def test_post_content(self):
        post = Post.objects.get(pk=1)
        self.assertEqual(post.author.username, TEST_USERNAME)
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.content, 'This is a test post')

    def test_post_str_method(self):
        post = Post.objects.get(pk=1)
        self.assertEqual(str(post), post.title)

    def test_get_absolute_url(self):
        post = Post.objects.get(pk=1)
        self.assertEqual(post.get_absolute_url(), reverse('post-detail', args=[post.pk]))


class PostViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username=TEST_USERNAME, password=TEST_PASSWORD)
        self.post = Post.objects.create(
            author = self.user,
            title = 'Test Post',
            content = 'This is a test post'
        )

    def test_list_view(self):
        url = reverse('blog-home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This is a test post')
        self.assertTemplateUsed(response, 'blog/home.html')

    def test_detail_view(self):
        url = reverse('post-detail', args=[self.post.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_create_post_view(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        get_response = self.client.get(reverse('post-create'))
        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, 'blog/post_form.html')

        post_response = self.client.post(reverse('post-create'), {
            'title': 'New title',
            'content': 'New text'
        })
        self.assertEqual(post_response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='New title').exists())

    def test_update_post_view(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        url = reverse('post-update', kwargs={'pk': self.post.pk})
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, 'blog/post_form.html')

        self.assertEqual(self.post.title, 'Test Post')  # Check the original

        post_response = self.client.post(url, {
            'title': 'Updated title',
            'content': 'Updated text',
         })

        self.post.refresh_from_db()
        self.assertEqual(post_response.status_code, 302)  # Redirect after POST
        self.assertEqual(self.post.title, 'Updated title')

    def test_delete_post_view(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        url = reverse('post-delete', kwargs={'pk': self.post.pk})
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, 'blog/post_confirm_delete.html')

        post_response = self.client.post(url)
        self.assertEqual(post_response.status_code, 302)  # Redirect after POST
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())
