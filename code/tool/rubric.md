# Test value rubric (written 2026-10-18 for this benchmark)

Grade how much the suite would lose if this one test were deleted.

5  Checks behaviour a user of the code relies on, with assertions on concrete results, and would fail on a realistic bug that other tests are unlikely to catch.
4  Checks meaningful behaviour with concrete assertions; other tests probably cover part of it.
3  Checks real behaviour but weakly (one loose assertion, only the happy path), or mostly repeats what nearby tests check.
2  Runs code but checks little: asserts only that no exception is raised, that a value is not None, or a type; or asserts mostly on mocks.
1  Could not fail on a realistic bug: tautological, tests the language or a library, or only checks a mock it set up itself.

Typed questions (answer each with one of the listed values):
- assertions: exact_value | structure_or_type | no_exception | none
- exercises: public_api | internal_helper | mostly_mocks
- expected_from: literal_in_test | computed_by_product | mock_return | none
- error_path: yes | no   (does it check an error, edge or boundary case)
