from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests import utils


class TestNoteCreation(utils.TestBase):

    USE_FORM_DATA = True

    def add_note(self, client):
        return client.post(utils.URL_NOTE_ADD, self.form_data)

    def test_anonymous_user_cant_create_note(self):
        notes_count = Note.objects.count()
        self.add_note(self.client)
        self.assertEqual(notes_count, Note.objects.count())

    def test_authenticated_user_can_create_note(self):
        notes_count = Note.objects.count()
        self.assertRedirects(
            self.add_note(self.user_client),
            utils.URL_SUCCESS
        )
        self.assertEqual((notes_count + 1), Note.objects.count())
        note = Note.objects.all().last()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_user_cant_use_existing_slug(self):
        notes_count = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        self.assertFormError(
            self.add_note(self.user_client),
            form='form',
            field='slug',
            errors=self.form_data['slug'] + WARNING
        )
        self.assertEqual(notes_count, Note.objects.count())

    def test_empty_slug(self):
        notes_count = Note.objects.count()
        self.form_data.pop('slug')
        self.assertRedirects(
            self.add_note(self.user_client),
            utils.URL_SUCCESS
        )
        self.assertEqual((notes_count + 1), Note.objects.count())
        self.assertEqual(
            Note.objects.all().last().slug,
            slugify(self.form_data['title'])
        )

    def test_author_can_delete_note(self):
        notes_count = Note.objects.count()
        self.assertRedirects(
            self.author_client.delete(utils.URL_NOTE_DELETE),
            utils.URL_SUCCESS
        )
        self.assertEqual(notes_count - 1, Note.objects.count())

    def test_user_cant_delete_note_of_another_user(self):
        notes_count = Note.objects.count()
        self.assertEqual(
            self.user_client.delete(utils.URL_NOTE_DELETE).status_code,
            HTTPStatus.NOT_FOUND
        )
        self.assertEqual(notes_count, Note.objects.count())

    def test_author_can_edit_note(self):
        self.assertRedirects(
            self.author_client.post(utils.URL_NOTE_EDIT, data=self.form_data),
            utils.URL_SUCCESS
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.author)

    def test_user_cant_edit_note_of_another_user(self):
        note_title = self.note.title
        note_text = self.note.text
        note_slug = self.note.slug
        note_author = self.note.author
        self.assertEqual(
            self.user_client.post(
                utils.URL_NOTE_EDIT, data=self.form_data
            ).status_code,
            HTTPStatus.NOT_FOUND,
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, note_text)
        self.assertEqual(self.note.title, note_title)
        self.assertEqual(self.note.slug, note_slug)
        self.assertEqual(self.note.author, note_author)
