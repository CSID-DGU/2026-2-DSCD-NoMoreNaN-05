import copy
import unittest
from scripts.map_claim_products import map_video, identity_cache_key
from src.claim_evidence_experiment import name_key
from tests.test_claim_evidence_experiment import catalog,product


class NewInputMappingTests(unittest.TestCase):
    def run_video(self, video, rows):
        db=catalog(rows)
        sources={r['product_id']:dict(r,main_functionality='DB 원문\n기능성') for r in rows}
        return map_video(video,db,[name_key(r['product_name']) for r in rows],set(),sources,'version',{})

    def test_new_video_preserves_original_claims_url_and_functionality(self):
        video=dict(video_id='new',url='https://example.com/v',products=[dict(product_ref='p1',product_name='올인원 멀티비타민 유산균',manufacturer_name='제조사 2공장')],
                   claims=[dict(claim_id='c1',product_ref='p1',text='원문',extra='보존')])
        before=copy.deepcopy(video)
        audit,records=self.run_video(video,[product()])
        self.assertEqual(records[0]['product']['evi_product']['main_functionality'],'DB 원문\n기능성')
        self.assertEqual(records[0]['claims'],video['claims'])
        self.assertEqual(records[0]['url'],video['url'])
        self.assertEqual(video,before)

    def test_manufacturer_disambiguates_new_input(self):
        video=dict(video_id='new',products=[dict(product_ref='p1',product_name='올인원 멀티비타민 유산균',manufacturer_name='회사B')],claims=[])
        audit,records=self.run_video(video,[product(company='회사A'),product(2,company='회사B',report='456')])
        self.assertEqual(audit[0]['selection_status'],'selected_by_manufacturer')
        self.assertEqual(records[0]['product']['evi_product']['product_id'],2)

    def test_orphan_claim_is_not_lost(self):
        video=dict(video_id='new',products=[],claims=[dict(claim_id='c1',product_ref='missing',text='원문')])
        _,records=self.run_video(video,[product()])
        self.assertEqual(records[0]['claims'],video['claims'])
        self.assertIsNone(records[0]['product']['evi_product'])

    def test_brand_is_part_of_cache_identity(self):
        self.assertNotEqual(identity_cache_key(dict(product_name='브랜드 제품',brand_name='브랜드')),
                            identity_cache_key(dict(product_name='브랜드 제품',brand_name='다른브랜드')))

    def test_70_point_search_uses_separate_cache_and_keeps_claim(self):
        db=catalog([product(name='abcdefghij')])
        sources={1:dict(db.products[0],main_functionality='원문')}
        video=dict(video_id='new',products=[dict(product_ref='p1',product_name='abcdefgxyz')],
                   claims=[dict(claim_id='c1',product_ref='p1',text='원문')])
        cache={}
        old,_=map_video(video,db,['abcdefghij'],set(),sources,'version',cache,threshold=80)
        new,export=map_video(video,db,['abcdefghij'],set(),sources,'version',cache,threshold=70)
        self.assertEqual(old[0]['candidate_count'],0)
        self.assertEqual(new[0]['candidate_count'],1)
        self.assertEqual(new[0]['route'],'full_name_distance_70_candidates')
        self.assertEqual(export[0]['claims'],video['claims'])
