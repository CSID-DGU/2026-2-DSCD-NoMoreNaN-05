import unittest

from scripts.export_candidate_db_handoff import choose_primary, iter_claim_contexts, source_ids


class CandidateHandoffTests(unittest.TestCase):
    def test_keeps_all_sources_not_only_old_selection(self):
        row=dict(candidates=[dict(product_id=1),dict(product_id=2)],
                 selected_product=dict(product_id=1), selected_group_product_ids=[1,3])
        self.assertEqual(source_ids(row), [1,2,3])

    def test_manufacturer_wins_over_brand(self):
        p=dict(product_name='제품',manufacturer_name='제조사',brand_name='브랜드')
        candidates=[dict(product_id=1,product_name='제품',company_name='브랜드'),
                    dict(product_id=2,product_name='제품',company_name='제조사')]
        chosen,reason=choose_primary(p,{},candidates,set())
        self.assertEqual(chosen['product_id'],2)
        self.assertEqual(reason,'manufacturer_priority')

    def test_known_manufacturer_conflict_does_not_pick_brand(self):
        p=dict(product_name='제품',manufacturer_name='다른업체',brand_name='브랜드')
        candidates=[dict(product_id=1,product_name='제품',company_name='브랜드')]
        chosen,_=choose_primary(p,{},candidates,set())
        self.assertIsNone(chosen)

    def test_multiple_formulations_no_arbitrary_primary(self):
        p=dict(product_name='제품',manufacturer_name='제조사')
        candidates=[dict(product_id=i,product_name='제품',company_name='제조사') for i in [1,2]]
        chosen,_=choose_primary(p,{},candidates,set())
        self.assertIsNone(chosen)

    def test_null_top_level_db_still_provides_all_candidate_evidence(self):
        candidates=[dict(product_id=1,DB=dict(EFFECT=dict(MAIN_FNCTN='기능A'))),
                    dict(product_id=2,DB=dict(EFFECT=dict(MAIN_FNCTN='기능B')))]
        claim=dict(claim_id='c1',product_ref='p1',claim_type='EFFECT',effect='원본')
        video=dict(video_id='v1',products=[dict(product_ref='p1',DB=None,candidate_products=candidates)],claims=[claim])
        context=list(iter_claim_contexts([video]))[0]
        self.assertEqual(context['evidence_status'],'linked')
        self.assertEqual(context['candidates'],candidates)
        self.assertEqual(context['claim']['effect'],'원본')

    def test_invalid_ref_never_uses_other_product(self):
        video=dict(video_id='v1',products=[dict(product_ref='p1',candidate_products=[dict(product_id=1)])],
                   claims=[dict(claim_id='c1',product_ref='p2')])
        self.assertEqual(list(iter_claim_contexts([video]))[0]['candidates'],[])


if __name__=='__main__':
    unittest.main()
