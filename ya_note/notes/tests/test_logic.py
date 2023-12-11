from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.utils import (
    TestBase,
    URL_NOTE_ADD,
    URL_NOTE_DELETE,
    URL_NOTE_EDIT,
    URL_SUCCESS,
)


class TestNoteCreation(TestBase):

    def check_note_creation(self):
        notes = set(Note.objects.all())
        self.assertRedirects(
            self.user_client.post(URL_NOTE_ADD, self.form_data),
            URL_SUCCESS
        )
        notes = set(Note.objects.all()) - notes
        self.assertEqual(len(notes), 1)
        new_note = notes.pop()
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.author, self.user)
        self.assertEqual(
            new_note.slug,
            (
                self.form_data['slug'] if 'slug' in self.form_data
                else slugify(self.form_data['title'])
            )
        )

    def test_anonymous_user_cant_create_note(self):
        notes = set(Note.objects.all())
        self.client.post(URL_NOTE_ADD, self.form_data)
        self.assertEqual(notes, set(Note.objects.all()))

    def test_authenticated_user_can_create_note(self):
        self.check_note_creation()

    def test_user_cant_use_existing_slug(self):
        self.form_data['slug'] = self.note.slug
        notes = set(Note.objects.all())
        self.assertFormError(
            self.user_client.post(URL_NOTE_ADD, self.form_data),
            form='form',
            field='slug',
            errors=self.form_data['slug'] + WARNING
        )
        self.assertEqual(notes, set(Note.objects.all()))

    def test_empty_slug(self):
        self.form_data.pop('slug')
        self.check_note_creation()

    def test_author_can_delete_note(self):
        notes_count = Note.objects.count()
        self.assertRedirects(
            self.author_client.delete(URL_NOTE_DELETE),
            URL_SUCCESS
        )
        notes = Note.objects.all()
        self.assertEqual(notes_count - 1, notes.count())
        self.assertFalse(notes.filter(id=self.note.id).exists())

    def test_user_cant_delete_note_of_another_user(self):
        self.assertEqual(
            self.user_client.delete(URL_NOTE_DELETE).status_code,
            HTTPStatus.NOT_FOUND
        )
        notes = Note.objects.filter(id=self.note.id)
        self.assertTrue(notes.exists())
        note_from_db = notes.get()
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.slug, self.note.slug)
        self.assertEqual(note_from_db.author, self.note.author)

    def test_author_can_edit_note(self):
        self.assertRedirects(
            self.author_client.post(URL_NOTE_EDIT, data=self.form_data),
            URL_SUCCESS
        )
        edited_note = Note.objects.get(id=self.note.id)
        self.assertEqual(edited_note.text, self.form_data['text'])
        self.assertEqual(edited_note.title, self.form_data['title'])
        self.assertEqual(edited_note.slug, self.form_data['slug'])
        self.assertEqual(edited_note.author, self.note.author)

    def test_user_cant_edit_note_of_another_user(self):
        self.assertEqual(
            self.user_client.post(
                URL_NOTE_EDIT, data=self.form_data
            ).status_code,
            HTTPStatus.NOT_FOUND,
        )
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.slug, self.note.slug)
        self.assertEqual(note_from_db.author, self.note.author)
