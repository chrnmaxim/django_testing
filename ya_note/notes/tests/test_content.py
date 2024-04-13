from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.notes = Note.objects.create(
            title='slug',
            text='Текст',
            slug='note-slug',
            author=cls.author
        )

    def test_notes_list_for_different_users(self):
        """Проверка передачи отдельной заметки в списке."""
        users_note_statutes = (
            (self.author, True,),
            (self.reader, False),
        )
        url = reverse('notes:list')
        for user, note_in_list in users_note_statutes:
            self.client.force_login(user)
            with self.subTest(user=user, note_in_list=note_in_list):
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertEqual((self.notes in object_list), note_in_list)

    def test_pages_contains_form(self):
        """Проверка передачи формы  при создании и редактировании заметки."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.notes.slug,)),
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIsInstance(response.context['form'], NoteForm)
