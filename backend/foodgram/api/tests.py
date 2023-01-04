from django.test import Client, TestCase
from users.models import User


class URLTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(
            username='HasNoName',
            password='123456',
            email='test@mail.ru',
            first_name='Иван',
            last_name='Иванов')

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='HasNoName')
        self.authorized = Client()
        self.authorized.force_login(self.user)

    def test_urls_responses(self):
        urls = (
            '/api/recipes/', '/api/ingredients/',
            '/api/tags/', '/api/users/subscriptions/')

        for address in urls:
            with self.subTest(address=address):
                response = self.authorized.get(address)
                self.assertEqual(response.status_code, 200)
