from django.test.testcases import SimpleTestCase
from data.utils.clean_name import (
    remove_wrong_spacing, capitalise_generation_suffix, correct_irish_name, correct_suffix_dot,
    correct_suffix_jr_sr, correct_initial, fix_typo_o, correct_title, clean_name)


class CleanNameTestCase(SimpleTestCase):
    def test_remove_wrong_spacing(self):
        name = 'John Hollowell Jr.'
        self.assertEqual(remove_wrong_spacing('John Hollowell  Jr.'), name)
        self.assertEqual(remove_wrong_spacing(name), name)

    def test_capitalise_generation_suffix(self):
        name = 'Mark Loop IV'
        self.assertEqual(capitalise_generation_suffix('Mark Loop Iv'), name)
        self.assertEqual(capitalise_generation_suffix(name), name)

    def test_correct_irish_name(self):
        name = 'Eric O\'Suoji'
        self.assertEqual(correct_irish_name('Eric O suoji'), name)
        self.assertEqual(correct_irish_name(name), name)

        self.assertEqual(correct_irish_name('Eric Obrien'), 'Eric O\'Brien')

    def test_correct_suffix_jr_sr(self):
        name = 'Clarence Pendleton Jr.'
        self.assertEqual(correct_suffix_jr_sr('Clarence Pendleton jr'), name)
        self.assertEqual(correct_suffix_jr_sr(name), name)
        self.assertEqual(clean_name('E. Aaron. JR'), 'E. Aaron Jr.')

    def test_correct_initial(self):
        name = 'C. Pepol'
        self.assertEqual(correct_initial('C Pepol'), name)
        self.assertEqual(correct_initial(name), name)

    def test_fix_typo_o(self):
        name = 'Kimberly Connolly'
        self.assertEqual(fix_typo_o('Kimberly C0nnolly'), name)
        self.assertEqual(fix_typo_o(name), name)

    def test_correct_title(self):
        name = 'Julio Yushu\'a'
        self.assertEqual(correct_title('Julio Yushu\'A'), name)
        self.assertEqual(correct_title(name), name)

    def test_clean_name(self):
        self.assertEqual(clean_name('C 0    Reilly Ii'), 'C. O\'Reilly II')
        self.assertEqual(clean_name('C 0    Reilly sr'), 'C. O\'Reilly Sr.')

    def test_correct_suffix_dot(self):
        self.assertEqual(correct_suffix_dot('Shelton El.'), 'Shelton El')
        self.assertEqual(correct_suffix_dot('Shelton El'), 'Shelton El')

    def test_strip_space(self):
        self.assertEqual(clean_name('   Abc'), 'Abc')
        self.assertEqual(clean_name('Edg '), 'Edg')
