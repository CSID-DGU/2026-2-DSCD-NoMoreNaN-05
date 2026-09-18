import unittest

from src.collectors import diseases


SUCCESS = b"""<?xml version='1.0' encoding='UTF-8'?>
<response><header><resultCode>00</resultCode><resultMsg>NORMAL SERVICE.</resultMsg></header>
<body><pageNo>1</pageNo><numOfRows>100</numOfRows><totalCount>1</totalCount>
<items><item><sickNm>cholera</sickNm><sickCd>A00</sickCd><sickEngNm>Cholera</sickEngNm></item></items>
</body></response>"""


class DiseaseCollectorTests(unittest.TestCase):
    def test_parses_documented_xml_schema(self):
        page, total, page_size, rows = diseases.parse_xml(SUCCESS)
        self.assertEqual((page, total, page_size), (1, 1, 100))
        self.assertEqual(rows, [{"sickNm": "cholera", "sickCd": "A00", "sickEngNm": "Cholera"}])

    def test_api_error_is_not_treated_as_empty_data(self):
        error = b"<response><header><resultCode>30</resultCode><resultMsg>KEY ERROR</resultMsg></header></response>"
        with self.assertRaisesRegex(RuntimeError, "30"):
            diseases.parse_xml(error)

    def test_query_option_validation(self):
        self.assertEqual(diseases.parse_values("1,2", diseases.SICK_TYPES, "sick-types"), ("1", "2"))
        with self.assertRaises(ValueError):
            diseases.parse_values("3", diseases.SICK_TYPES, "sick-types")


if __name__ == "__main__":
    unittest.main()
