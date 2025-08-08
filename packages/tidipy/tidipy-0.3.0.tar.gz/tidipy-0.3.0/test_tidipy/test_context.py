from unittest import TestCase

from test_tidipy import context_composition
from test_tidipy.context_composition import StringGenerator, HelloGenerator, TimberGenerator, App
from tidipy import scan, get_resolver, reset, ensure_scope, ensure_root_scope


class TestContext(TestCase):
    def setUp(self) -> None:
        scan(context_composition)

    def tearDown(self) -> None:
        reset()

    def test_production(self):
        ensure_root_scope(context={'environment': 'prod'})
        result = get_resolver()(StringGenerator)

        self.assertEqual(result.generate(), 'Timber')

    def test_specific_type(self):
        ensure_root_scope(context={'environment': 'test'})
        result = get_resolver()(HelloGenerator)

        self.assertEqual(result.generate(), 'Hello')

    def test_resolves_with_additional_values(self):
        ensure_root_scope(context={'environment': 'test', 'extra_key': 'iets'})
        result = get_resolver()(HelloGenerator)

        self.assertEqual(result.generate(), 'Hello')

    def test_cannot_resolve_with_multiple_candidates(self):
        with self.assertRaises(Exception):
            get_resolver()(StringGenerator)

    def test_can_resolve_specific(self):
        result = get_resolver()(TimberGenerator)

        self.assertEqual(result.generate(), 'Timber')

    def test_resolve_app(self):
        ensure_root_scope(context={'environment': 'test'})
        app = get_resolver()(App)

        self.assertEqual(app.generate(), 'Hello')

    def test_cannot_change_context(self):
        ensure_root_scope(context={'environment': 'test'})

        with self.assertRaises(Exception):
            ensure_root_scope(context={'environment': 'prod'})

    def test_cannot_add_to_context(self):
        ensure_root_scope(context={'environment': 'test'})

        with self.assertRaises(Exception):
            ensure_root_scope(context={'new': 'iets'})

    def test_cannot_change_empty_context(self):
        ensure_root_scope()

        with self.assertRaises(Exception):
            ensure_root_scope(context={'a': 'b'})

    def test_cannot_change_context_in_child(self):
        ensure_root_scope(context={'environment': 'test'})

        with self.assertRaises(Exception):
            ensure_scope('child', scope_type='child', context={'environment': 'prod'})

    def test_adding_context_to_child_scope_does_not_influence_root(self):
        ensure_scope(scope_id='child', scope_type='child', context={'environment': 'test'})

        root_resolver = get_resolver()
        child_resolver = get_resolver('child')

        with self.assertRaises(Exception):
            root_resolver(StringGenerator)
        with self.assertRaises(Exception):
            child_resolver(StringGenerator)
