import unittest
import eliza


class ElizaTest(unittest.TestCase):
    def test_decomp_1(self):
        el = eliza.Eliza()
        self.assertEqual([], el._match_decomp(['a'], ['a']))
        self.assertEqual([], el._match_decomp(['a', 'b'], ['a', 'b']))

    def test_decomp_2(self):
        el = eliza.Eliza()
        self.assertIsNone(el._match_decomp(['a'], ['b']))
        self.assertIsNone(el._match_decomp(['a'], ['a', 'b']))
        self.assertIsNone(el._match_decomp(['a', 'b'], ['a']))
        self.assertIsNone(el._match_decomp(['a', 'b'], ['b', 'a']))

    def test_decomp_3(self):
        el = eliza.Eliza()
        self.assertEqual([['a']], el._match_decomp(['*'], ['a']))
        self.assertEqual([['a', 'b']], el._match_decomp(['*'], ['a', 'b']))
        self.assertEqual([['a', 'b', 'c']],
                         el._match_decomp(['*'], ['a', 'b', 'c']))

    def test_decomp_4(self):
        el = eliza.Eliza()
        self.assertEqual([], el._match_decomp([], []))
        self.assertEqual([[]], el._match_decomp(['*'], []))

    def test_decomp_5(self):
        el = eliza.Eliza()
        self.assertIsNone(el._match_decomp(['a'], []))
        self.assertIsNone(el._match_decomp([], ['a']))

    def test_decomp_6(self):
        el = eliza.Eliza()
        self.assertEqual([['0']], el._match_decomp(['*', 'a'], ['0', 'a']))
        self.assertEqual([['0', 'a']],
                         el._match_decomp(['*', 'a'], ['0', 'a', 'a']))
        self.assertEqual([['0', 'a', 'b']],
                         el._match_decomp(['*', 'a'], ['0', 'a', 'b', 'a']))
        self.assertEqual([['0', '1']],
                         el._match_decomp(['*', 'a'], ['0', '1', 'a']))

    def test_decomp_7(self):
        el = eliza.Eliza()
        self.assertEqual([[]], el._match_decomp(['*', 'a'], ['a']))

    def test_decomp_8(self):
        el = eliza.Eliza()
        self.assertIsNone(el._match_decomp(['*', 'a'], ['a', 'b']))
        self.assertIsNone(el._match_decomp(['*', 'a'], ['0', 'a', 'b']))
        self.assertIsNone(el._match_decomp(['*', 'a'], ['0', '1', 'a', 'b']))

    def test_decomp_9(self):
        el = eliza.Eliza()
        self.assertEqual([['0'], ['b']],
                         el._match_decomp(['*', 'a', '*'], ['0', 'a', 'b']))
        self.assertEqual([['0'], ['b', 'c']],
                         el._match_decomp(['*', 'a', '*'],
                                          ['0', 'a', 'b', 'c']))

    def test_decomp_10(self):
        el = eliza.Eliza()
        self.assertEqual([['0'], []],
                         el._match_decomp(['*', 'a', '*'], ['0', 'a']))
        self.assertEqual([[], []], el._match_decomp(['*', 'a', '*'], ['a']))
        self.assertEqual([[], ['b']],
                         el._match_decomp(['*', 'a', '*'], ['a', 'b']))

    def test_syn_1(self):
        el = eliza.Eliza()
        el.load('doctor.txt')
        self.assertEqual([['am']], el._match_decomp(['@be'], ['am']))
        self.assertEqual([['am']], el._match_decomp(['@be', 'a'], ['am', 'a']))
        self.assertEqual([['am']],
                         el._match_decomp(['a', '@be', 'b'], ['a', 'am', 'b']))

    def test_syn_2(self):
        el = eliza.Eliza()
        el.load('doctor.txt')
        self.assertIsNone(el._match_decomp(['@be'], ['a']))

    def test_syn_3(self):
        el = eliza.Eliza()
        el.load('doctor.txt')
        self.assertIsNotNone(
            el._match_decomp(['*', 'i', 'am', '@sad', '*'],
                             ['its', 'true', 'i', 'am', 'unhappy']))

    def test_response_1(self):
        el = eliza.Eliza()
        el.load('doctor.txt')
        self.assertEqual('In what way ?', el.respond('Men are all alike.'))
        self.assertEqual(
            'Can you think of a specific example ?',
            el.respond('They\'re always bugging us about something or other.'))
        self.assertEqual('Your boyfriend made you come here ?',
                         el.respond('Well, my boyfriend made me come here.'))
        self.assertEqual(
            'I am sorry to hear that you are depressed .',
            el.respond('He says I\'m depressed much of the time.'))
        self.assertEqual(
            'Do you think that coming here will help you not to be unhappy ?',
            el.respond('It\'s true. I am unhappy.'))
        self.assertEqual(
            'What would it mean to you if you got some help ?',
            el.respond('I need some help, that much seems certain.'))
        self.assertEqual(
            'Tell me more about your family.',
            el.respond('Perhaps I could learn to get along with my mother.'))
        self.assertEqual('Who else in your family takes care of you ?',
                         el.respond('My mother takes care of me.'))
        self.assertEqual('Your father ?', el.respond('My father.'))
        self.assertEqual('What resemblence do you see ?',
                         el.respond('You are like my father in some ways.'))
        self.assertEqual(
            'What makes you think I am not very aggressive ?',
            el.respond(
                'You are not very aggressive, but I think you don\'t want me to notice that.'
            ))
        self.assertEqual('Why do you think I don\'t argue with you ?',
                         el.respond('You don\'t argue with me.'))
        self.assertEqual('Does it please you to believe I am afraid of you ?',
                         el.respond('You are afraid of me.'))
        self.assertEqual(
            'What else comes to mind when you think of your father ?',
            el.respond('My father is afraid of everybody.'))
        self.assertIn(
            el.respond('Bullies.'), [
                'Lets discuss further why your boyfriend made you come here .',
                'Earlier you said your mother .',
                'But your mother takes care of you .',
                'Does that have anything to do with the fact that your boyfriend made you come here ?',
                'Does that have anything to do with the fact that your father ?',
                'Lets discuss further why your father is afraid of everybody .',
            ])

    def test_response_2(self):
        el = eliza.Eliza()
        el.load('doctor.txt')
        self.assertEqual(el.initial(), 'How do you do.  Please tell me your problem.')
        self.assertIn(el.respond('Hello'), [
            'How do you do. Please state your problem.',
            'Hi. What seems to be your problem ?'])
        self.assertEqual(el.final(), 'Goodbye.  Thank you for talking to me.')


if __name__ == '__main__':
    unittest.main()
