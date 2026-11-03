import unittest
from scripts.export_brand_present_handoff import partition


class BrandPresentHandoffTests(unittest.TestCase):
    def test_filters_products_not_entire_video_and_preserves_claim_ownership(self):
        video = dict(video_id='v', products=[dict(product_ref='a', brand_name='Brand'),
            dict(product_ref='b', brand_name=None, manufacturer_name='Known Maker')],
            claims=[dict(claim_id='1', product_ref='a'), dict(claim_id='2', product_ref='b'),
                    dict(claim_id='3', product_ref='unknown')])
        kept, excluded, orphans, allowed = partition([video])
        self.assertEqual(allowed, {('v', 'a')})
        self.assertEqual([c['claim_id'] for c in kept[0]['claims']], ['1'])
        self.assertEqual([c['claim_id'] for c in excluded[0]['claims']], ['2'])
        self.assertEqual([c['claim_id'] for c in orphans[0]['claims']], ['3'])
        self.assertEqual(len(video['products']), 2)

    def test_empty_missing_or_whitespace_brands_do_not_use_manufacturer(self):
        video = dict(video_id='v', products=[dict(product_ref=str(i), brand_name=value, manufacturer_name='Maker')
            for i, value in enumerate([None, '', '  ', '\t'])], claims=[])
        kept, excluded, _, allowed = partition([video])
        self.assertEqual(kept, [])
        self.assertEqual(len(excluded), 4)
        self.assertEqual(allowed, set())
