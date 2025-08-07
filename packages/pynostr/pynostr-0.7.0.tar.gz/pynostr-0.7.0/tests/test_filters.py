"""Forked from https://github.com/jeffthibault/python-nostr.git."""

import unittest

from pynostr.encrypted_dm import EncryptedDirectMessage
from pynostr.event import Event, EventKind
from pynostr.filters import Filters, FiltersList
from pynostr.key import PrivateKey


class TestFilters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pk1 = PrivateKey()
        cls.pk2 = PrivateKey()

        """ pk1 kicks off a thread and interacts with pk2 """
        cls.pk1_thread = [
            # Note posted by pk1
            Event(pubkey=cls.pk1.public_key.hex(), content="pk1's first note!"),
        ]
        cls.pk1_thread.append(
            # Note posted by pk2 in response to pk1's note
            Event(
                pubkey=cls.pk2.public_key.hex(),
                content="Nice to see you here, pk1!",
                tags=[
                    [
                        "e",
                        cls.pk1_thread[0].id,
                    ],  # Replies reference which note they're directly responding to
                    [
                        "p",
                        cls.pk1.public_key.hex(),
                    ],  # Replies reference who they're responding to
                ],
            )
        )
        cls.pk1_thread.append(
            # Next response note by pk1 continuing thread with pk2
            Event(
                pubkey=cls.pk1.public_key.hex(),
                content="Thanks! Glad you're here, too, pk2!",
                tags=[
                    ["e", cls.pk1_thread[0].id],  # Threads reference the original note
                    [
                        "e",
                        cls.pk1_thread[-1].id,
                    ],  # Replies reference which note they're directly responding to
                    [
                        "p",
                        cls.pk2.public_key.hex(),
                    ],  # Replies reference who they're responding to
                ],
            )
        )

        """ pk2 starts a new thread but no one responds """
        cls.pk2_thread = [
            # Note posted by pk2
            Event(pubkey=cls.pk2.public_key.hex(), content="pk2's first note!")
        ]
        cls.pk2_thread.append(
            # pk2's self-reply
            Event(
                pubkey=cls.pk2.public_key.hex(),
                content="So... I guess no one's following me.",
                tags=[["e", cls.pk2_thread[0].id]],
            )
        )

        """ pk1 DMs pk2 """
        cls.pk1_pk2_dms = [
            # DM sent by pk1 to pk2
            Event(
                pubkey=cls.pk1.public_key.hex(),
                kind=EventKind.ENCRYPTED_DIRECT_MESSAGE,
            ),
            Event(
                pubkey=cls.pk2.public_key.hex(),
                kind=EventKind.ENCRYPTED_DIRECT_MESSAGE,
            ),
        ]
        dm1 = EncryptedDirectMessage()
        dm1.encrypt(
            cls.pk1.hex(),
            recipient_pubkey=cls.pk2.public_key.hex(),
            cleartext_content="Hey pk2, here's a secret",
        )
        cls.pk1_pk2_dms[0] = dm1.to_event()

        dm2 = EncryptedDirectMessage()
        dm2.encrypt(
            cls.pk2.hex(),
            recipient_pubkey=cls.pk1.public_key.hex(),
            cleartext_content="Thanks! I'll keep it secure.",
        )
        cls.pk1_pk2_dms[1] = dm2.to_event()

    def test_match_by_event_id(self):
        """Should match Events by event_id."""
        filters = Filters(
            ids=[self.pk1_thread[0].id],
        )
        self.assertTrue(filters.matches(self.pk1_thread[0]))
        self.assertEqual(filters, self.pk1_thread[0])

        # None of the others should match
        for event in self.pk1_thread[1:] + self.pk2_thread + self.pk1_pk2_dms[1:]:
            self.assertFalse(filters.matches(event))
            self.assertNotEqual(filters, event)
        filter_copy = Filters.from_dict(filters.to_dict())
        self.assertEqual(filter_copy.ids, filters.ids)

    def test_multiple_values_in_same_tag(self):
        """Should treat multiple tag values as OR searches."""
        filters = Filters(
            ids=[
                self.pk1_thread[0].id,
                self.pk1_pk2_dms[0].id,
                "some_other_event_id",
            ],
        )
        self.assertTrue(filters.matches(self.pk1_thread[0]))
        self.assertTrue(filters.matches(self.pk1_pk2_dms[0]))

        # None of the others should match
        for event in self.pk1_thread[1:] + self.pk2_thread + self.pk1_pk2_dms[1:]:
            self.assertFalse(filters.matches(event))

    def test_match_by_kinds(self):
        """Should match Events by kind."""
        filters = Filters(
            kinds=[EventKind.TEXT_NOTE],
        )

        # Both threads should match
        for event in self.pk1_thread + self.pk2_thread:
            self.assertTrue(filters.matches(event))

        # DMs should not match
        for event in self.pk1_pk2_dms:
            self.assertFalse(filters.matches(event))

        # Now allow either kind
        filters = Filters(
            kinds=[EventKind.TEXT_NOTE, EventKind.ENCRYPTED_DIRECT_MESSAGE],
        )

        # Now everything should match
        for event in self.pk1_thread + self.pk2_thread + self.pk1_pk2_dms:
            self.assertTrue(filters.matches(event))

        filter_copy = Filters.from_dict(filters.to_dict())
        self.assertEqual(filter_copy.kinds, filters.kinds)

    def test_match_by_authors(self):
        """Should match Events by author."""
        filters = Filters(authors=[self.pk1.public_key.hex()])

        # Everything sent by pk1 should match
        for event in [
            event
            for event in (self.pk1_thread + self.pk2_thread + self.pk1_pk2_dms)
            if event.pubkey == self.pk1.public_key.hex()
        ]:
            self.assertTrue(filters.matches(event))

        # None of pk2's should match
        for event in [
            event
            for event in (self.pk1_thread + self.pk2_thread + self.pk1_pk2_dms)
            if event.pubkey == self.pk2.public_key.hex()
        ]:
            self.assertFalse(filters.matches(event))

        filter_copy = Filters.from_dict(filters.to_dict())
        self.assertEqual(filter_copy.authors, filters.authors)

    def test_match_by_event_refs(self):
        """Should match Events by event_ref 'e' tags."""
        filters = Filters(
            event_refs=[self.pk1_thread[0].id],
        )

        # All replies to pk1's initial note should match (even pk1's reply at the end)
        self.assertTrue(filters.matches(self.pk1_thread[1]))
        self.assertTrue(filters.matches(self.pk1_thread[2]))

        # Everything else should not match
        for event in [self.pk1_thread[0]] + self.pk2_thread + self.pk1_pk2_dms:
            self.assertFalse(filters.matches(event))

        filter_copy = Filters.from_dict(filters.to_dict())
        self.assertEqual(filter_copy.event_refs, filters.event_refs)

    def test_match_by_pubkey_refs(self):
        """Should match Events by pubkey_ref 'p' tags."""
        filters = Filters(
            pubkey_refs=[self.pk1_thread[0].pubkey],
        )

        # pk2's reply in pk1's thread should match
        self.assertTrue(filters.matches(self.pk1_thread[1]))

        # pk2's DM reply to pk1 should match
        self.assertTrue(filters.matches(self.pk1_pk2_dms[1]))

        # Everything else should not match
        for event in (
            [self.pk1_thread[0], self.pk1_thread[2]]
            + self.pk2_thread
            + [self.pk1_pk2_dms[0]]
        ):
            self.assertFalse(filters.matches(event))

        filter_copy = Filters.from_dict(filters.to_dict())
        self.assertEqual(filter_copy.pubkey_refs, filters.pubkey_refs)

    def test_match_by_arbitrary_single_letter_tag(self):
        """Should match NIP-12 arbitrary single-letter tags."""
        filters = Filters()
        filters.add_arbitrary_tag("x", ["oranges"])

        # None of our Events match
        for event in self.pk1_thread + self.pk2_thread + self.pk1_pk2_dms:
            self.assertFalse(filters.matches(event))

        # A new Event that has the target tag but the wrong value should not match
        event = Event(
            pubkey=self.pk1.public_key.hex(),
            content="Additional event to test with",
            tags=[["x", "bananas"]],
        )
        self.assertFalse(filters.matches(event))

        # But a new Event that includes the target should match
        event = Event(
            pubkey=self.pk1.public_key.hex(),
            content="Additional event to test with",
            tags=[["x", "oranges"]],
        )
        self.assertTrue(filters.matches(event))

        # Filter shouldn't care if there are other extraneous values
        event.tags.append(["x", "pizza"])
        self.assertTrue(filters.matches(event))

        event.tags.append(["y", "honey badger"])
        self.assertTrue(filters.matches(event))

    def test_match_by_arbitrary_multi_letter_tag(self):
        """Should match any arbitrary multi-letter tag."""
        filters = Filters()
        filters.add_arbitrary_tag("favorites", ["bitcoin"])

        # None of our Events match
        for event in self.pk1_thread + self.pk2_thread + self.pk1_pk2_dms:
            self.assertFalse(filters.matches(event))

        # A new Event that has the target tag but the wrong value should not match
        event = Event(
            pubkey=self.pk1.public_key.hex(),
            content="Additional event to test with",
            tags=[["favorites", "shitcoin"]],
        )
        self.assertFalse(filters.matches(event))

        # But a new Event that includes the target should match
        event = Event(
            pubkey=self.pk1.public_key.hex(),
            content="Additional event to test with",
            tags=[["favorites", "bitcoin"]],
        )
        self.assertTrue(filters.matches(event))

        # Filter shouldn't care if there are other extraneous values
        event.tags.append(["favorites", "sats"])
        self.assertTrue(filters.matches(event))

        event.tags.append(["foo", "bar"])
        self.assertTrue(filters.matches(event))

    def test_match_by_delegation_tag(self):
        """should match on delegation tag.

        Note: this is to demonstrate that it works w/out special handling, but
        arguably Delegation filtering should have its own explicit Filter support.
        """
        filters = Filters()

        # Search just for the delegator's pubkey (only aspect of delegation search
        # that is supported this way)
        filters.add_arbitrary_tag(
            "delegation",
            ["8e0d3d3eb2881ec137a11debe736a9086715a8c8beeeda615780064d68bc25dd"],
        )

        # None of our Events match
        for event in self.pk1_thread + self.pk2_thread + self.pk1_pk2_dms:
            self.assertFalse(filters.matches(event))

        # A new Event that has the target tag but the wrong value should not match
        event = Event(
            pubkey=self.pk1.public_key.hex(),
            content="Additional event to test with",
            tags=[
                [
                    "delegation",
                    "some_other_delegators_pubkey",
                    "kind=1&created_at<1675721813",
                    "cbc49c65fe04a3181d72fb5a9f1c627e329d5f45d300a2dfed1c3e788b7834dad4"
                    "8a6d27d8e244af39c77381334ede97d4fd15abe80f35fda695fd9bd732aa1e",
                ]
            ],
        )
        self.assertFalse(filters.matches(event))

        # But a new Event that includes the target should match
        event = Event(
            pubkey=self.pk1.public_key.hex(),
            content="Additional event to test with",
            tags=[
                [
                    "delegation",
                    "8e0d3d3eb2881ec137a11debe736a9086715a8c8beeeda615780064d68bc25dd",
                    "kind=1&created_at<1675721813",
                    "cbc49c65fe04a3181d72fb5a9f1c627e329d5f45d300a2dfed1c3e788b7834dad4"
                    "8a6d27d8e244af39c77381334ede97d4fd15abe80f35fda695fd9bd732aa1e",
                ]
            ],
        )
        self.assertTrue(filters.matches(event))

        # Filter shouldn't care if there are other extraneous values
        event.tags.append(["favorites", "sats"])
        self.assertTrue(filters.matches(event))

        event.tags.append(["foo", "bar"])
        self.assertTrue(filters.matches(event))

    def test_match_by_authors_and_kinds(self):
        """Should match Events by authors AND kinds."""
        filters = Filters(
            authors=[self.pk1.public_key.hex()],
            kinds=[EventKind.TEXT_NOTE],
        )

        # Should match pk1's notes but not pk2's reply
        self.assertTrue(filters.matches(self.pk1_thread[0]))
        self.assertFalse(filters.matches(self.pk1_thread[1]))
        self.assertTrue(filters.matches(self.pk1_thread[2]))

        # Should not match anything else
        for event in self.pk2_thread + self.pk1_pk2_dms:
            self.assertFalse(filters.matches(event))

        # Typical search to get all Events sent by a pubkey
        filters = Filters(
            authors=[self.pk1.public_key.hex()],
            kinds=[EventKind.TEXT_NOTE, EventKind.ENCRYPTED_DIRECT_MESSAGE],
        )

        # Should still match pk1's notes but not pk2's reply
        self.assertTrue(filters.matches(self.pk1_thread[0]))
        self.assertFalse(filters.matches(self.pk1_thread[1]))
        self.assertTrue(filters.matches(self.pk1_thread[2]))

        # Should not match any of pk2's solo thread
        self.assertFalse(filters.matches(self.pk2_thread[0]))
        self.assertFalse(filters.matches(self.pk2_thread[1]))

        # Should match pk1's DM but not pk2's DM reply
        self.assertTrue(filters.matches(self.pk1_pk2_dms[0]))
        self.assertFalse(filters.matches(self.pk1_pk2_dms[1]))

    def test_match_by_kinds_and_pubkey_refs(self):
        """Should match Events by kind AND pubkey_ref 'p' tags."""
        filters = Filters(
            kinds=[EventKind.TEXT_NOTE],
            pubkey_refs=[self.pk2.public_key.hex()],
        )

        # Only pk1's reply to pk2 should match
        self.assertTrue(filters.matches(self.pk1_thread[2]))

        # Should not match anything else
        for event in self.pk1_thread[:1] + self.pk2_thread + self.pk1_pk2_dms:
            self.assertFalse(filters.matches(event))

        # Typical search to get all Events sent to a pubkey
        filters = Filters(
            kinds=[EventKind.TEXT_NOTE, EventKind.ENCRYPTED_DIRECT_MESSAGE],
            pubkey_refs=[self.pk2.public_key.hex()],
        )

        # pk1's reply to pk2 should match
        self.assertTrue(filters.matches(self.pk1_thread[2]))

        # pk2's DM to pk1 should match
        self.assertTrue(filters.matches(self.pk1_pk2_dms[0]))

        # Should not match anything else
        for event in self.pk1_thread[:1] + self.pk2_thread + self.pk1_pk2_dms[1:]:
            self.assertFalse(filters.matches(event))

    def test_event_refs_json(self):
        """Should insert event_refs as "#e" in json."""
        filters = Filters(event_refs=["some_event_id"])
        self.assertIn("#e", filters.to_dict().keys())
        self.assertNotIn("e", filters.to_dict().keys())

    def test_pubkey_refs_json(self):
        """Should insert pubkey_refs as "#p" in json."""
        filters = Filters(pubkey_refs=["some_pubkey"])
        self.assertIn("#p", filters.to_dict().keys())
        self.assertNotIn("p", filters.to_dict().keys())

    def test_arbitrary_single_letter_json(self):
        """Should prefix NIP-12 arbitrary single-letter tags with "#" in json."""
        filters = Filters()
        filters.add_arbitrary_tag("x", ["oranges"])
        self.assertIn("#x", filters.to_dict().keys())
        self.assertNotIn("x", filters.to_dict().keys())

    def test_arbitrary_multi_letter_json(self):
        """Should include arbitrary multi-letter tags as-is in json."""
        filters = Filters()
        filters.add_arbitrary_tag("foo", ["bar"])
        self.assertIn("foo", filters.to_dict().keys())


# Inherit from TestFilter to get all the same test data
class TestFiltersList(TestFilters):
    def test_match_by_authors_or_pubkey_refs(self):
        """Should match on authors or pubkey_refs."""
        # Typical filters for anything sent by or to a pubkey
        filter1 = Filters(
            authors=[self.pk1.public_key.hex()],
        )
        filter2 = Filters(
            pubkey_refs=[self.pk1.public_key.hex()],
        )
        filtersList = FiltersList([filter1, filter2])

        # Should match the entire pk1 thread and the DM exchange
        for event in self.pk1_thread + self.pk1_pk2_dms:
            self.assertTrue(filtersList.match(event))

        # Should not match anything in pk2's solo thread
        self.assertFalse(filtersList.match(self.pk2_thread[0]))
        self.assertFalse(filtersList.match(self.pk2_thread[1]))

        filtersList_copy = FiltersList.from_json_array(filtersList.to_json_array())
        self.assertEqual(filtersList_copy[0].authors, filter1.authors)
        self.assertEqual(filtersList_copy[1].pubkey_refs, filter2.pubkey_refs)
