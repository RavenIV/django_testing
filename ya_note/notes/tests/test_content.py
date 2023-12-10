from notes.forms import NoteForm
from notes.models import Note
from notes.tests.utils import (
    TestBase, URL_NOTE_ADD, URL_NOTE_EDIT, URL_NOTES_LIST
)


class TestNotesListPage(TestBase):

    def test_notes_list_for_author(self):
        notes = self.author_client.get(URL_NOTES_LIST).context['object_list']
        self.assertIn(self.note, notes)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, self.note.title)
        self.assertEqual(notes[0].text, self.note.text)
        self.assertEqual(notes[0].slug, self.note.slug)
        self.assertEqual(notes[0].author, self.note.author)

    def test_notes_list_for_another_user(self):
        self.assertNotIn(
            self.note,
            self.user_client.get(URL_NOTES_LIST).context['object_list']
        )

    def test_notes_pages_contain_form(self):
        for url in (URL_NOTE_ADD, URL_NOTE_EDIT):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIsInstance(response.context.get('form'), NoteForm)
