import unittest
from src.md_db_enrichment import material_key,number,split_materials,EnrichmentSources,numeric
from decimal import Decimal


class MdRulesTests(unittest.TestCase):
    def test_recognition_number_normalization(self):
        self.assertEqual(number('원료(제2023-05호)'),'2023-5')

    def test_thousands_separator_is_not_an_intake_conflict(self):
        self.assertEqual(numeric('2,079 (mg)'),Decimal('2079'))
        self.assertEqual(numeric('1.8'),Decimal('1.8'))
        self.assertIsNone(numeric('1 x 10^9 CFU'))

    def test_split_only_commas_outside_parentheses(self):
        self.assertEqual(split_materials('원료A(가,나), 원료B'),['원료A(가,나)','원료B'])

    def test_name_key_is_only_used_for_exact_comparison(self):
        self.assertEqual(material_key('원료 · A(고시형) 제품',True),'원료a')
        self.assertNotEqual(material_key('원료A'),material_key('원료B'))

    def test_source_precedence_and_original_values(self):
        row=EnrichmentSources.combine_standard('2020-1',dict(PRDCT_NM='I2710 원료',DAY_INTK_LOWLIMIT='1.8',DAY_INTK_HIGHLIMIT='2.5',INTK_UNIT='g',PRIMARY_FNCLTY='조문 참조',IFTKN_ATNT_MATR_CN='std 주의'),
            dict(RAWMTRL_NM=' I0050 원료 ',DAY_INTK_LOWLIMIT='2 (g)',DAY_INTK_HIGHLIMIT='3 (g)',WT_UNIT='g/일',PRIMARY_FNCLTY=' 인정 기능성\n',IFTKN_ATNT_MATR_CN='approved 주의'))
        self.assertEqual(row['DAY_INTK_LOWLIMIT'],'1.8')
        self.assertEqual(row['PRIMARY_FNCLTY'],' 인정 기능성\n')
        self.assertEqual(row['RAWMTRL_NM'],' I0050 원료 ')


if __name__=='__main__':unittest.main()
