from notes.forms import NoteForm
from notes.tests import utils


class TestNotesListPage(utils.TestBase):

    def test_notes_list_for_author(self):
        note_title = self.note.title
        note_text = self.note.text
        note_slug = self.note.slug
        note_author = self.note.author
        self.assertIn(
            self.note,
            self.author_client.get(utils.URL_NOTES_LIST).context['object_list']
        )
        self.assertEqual(self.note.title, note_title)
        self.assertEqual(self.note.text, note_text)
        self.assertEqual(self.note.slug, note_slug)
        self.assertEqual(self.note.author, note_author)

    def test_notes_list_for_another_user(self):
        self.assertNotIn(
            self.note,
            self.user_client.get(utils.URL_NOTES_LIST).context['object_list']
        )

    def test_notes_pages_contain_form(self):
        for url in (
            utils.URL_NOTE_ADD,
            utils.URL_NOTE_EDIT
        ):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
