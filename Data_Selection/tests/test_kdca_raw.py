import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import requests
import collect_kdca_raw as kdca

BODY = '<?xml version="1.0" encoding="UTF-8"?><response><HEAD><CODE>S001</CODE><MESSAGE>OK</MESSAGE></HEAD><svc><CNTNTS_SN><![CDATA[5423]]></CNTNTS_SN><CNTNTSSJ>감기</CNTNTSSJ><CNTNTS_CL_CN><![CDATA[<p>원본 내용</p>]]></CNTNTS_CL_CN></svc></response>'.encode()

def response(body=BODY, status=200, content_type='application/xml; charset=UTF-8'):
    return Mock(content=body, status_code=status, headers={'Content-Type':content_type})

class KdcaTests(unittest.TestCase):
    def test_raw_bytes_and_missing_key(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory=Path(temporary)
            session=Mock()
            session.get.return_value=response()
            item={'content_id':5423,'content_name':'감기/테스트'}
            result=kdca.collect([item],'secret',directory,session=session)
            self.assertEqual(result['success_count'],1)
            self.assertEqual((directory/'5423_감기_테스트.xml').read_bytes(),BODY)
            before=session.get.call_count
            result=kdca.collect([item],'',directory,session=session)
            self.assertEqual(result['items'][0]['error_code'],'MISSING_API_KEY')
            self.assertEqual(session.get.call_count,before)
            self.assertEqual((directory/'5423_감기_테스트.xml').read_bytes(),BODY)
            self.assertEqual(json.loads((directory/'metadata.json').read_text(encoding='utf-8'))['failed_count'],1)

    def test_error_code_mapping_and_rejection(self):
        for code,(label,_) in kdca.ERRORS.items():
            body=f'<HEAD><CODE>{code.zfill(2)}</CODE><MESSAGE>ERROR</MESSAGE></HEAD>'.encode()
            self.assertEqual(kdca.inspect_xml(body,5423)[0],label)
        self.assertEqual(kdca.inspect_xml(b'<broken>',5423)[0],'XML_PARSE_ERROR')
        self.assertEqual(kdca.inspect_xml(BODY,1)[0],'CONTENT_ID_MISMATCH')
        with tempfile.TemporaryDirectory() as temporary:
            session=Mock()
            session.get.return_value=response(b'<HEAD><CODE>30</CODE><MESSAGE>secret</MESSAGE></HEAD>')
            result=kdca.collect([{'content_id':5423,'content_name':'감기'}],'secret',Path(temporary),session=session)
            self.assertEqual(result['failed_count'],1)
            self.assertEqual(list(Path(temporary).glob('*.xml')),[])
            self.assertNotIn('secret',(Path(temporary)/'errors.jsonl').read_text(encoding='utf-8'))

    def test_fragment_example_and_retries(self):
        fragment=b'<HEAD><CODE>S001</CODE><MESSAGE>OK</MESSAGE></HEAD><svc><CNTNTS_SN>5423</CNTNTS_SN></svc>'
        self.assertEqual(kdca.inspect_xml(fragment,5423),(None,None))
        session=Mock()
        session.get.side_effect=[requests.Timeout(),response(status=503),response(status=429),response()]
        with patch.object(kdca.time,'sleep'):
            body,info=kdca.fetch(session,{'content_id':5423},'secret',0.4,120)
        self.assertEqual(body,BODY)
        self.assertEqual(session.get.call_count,4)
        session.get.side_effect=requests.Timeout()
        session.get.reset_mock()
        with patch.object(kdca.time,'sleep'):
            body,info=kdca.fetch(session,{'content_id':5423},'secret',0.4,120)
        self.assertIsNone(body)
        self.assertEqual(info['error_code'],'TIMEOUT')
        self.assertEqual(session.get.call_count,4)

    def test_non_xml_and_encoded_key(self):
        session=Mock()
        session.get.return_value=response(content_type='text/html')
        body,info=kdca.fetch(session,{'content_id':5423},'a%2Fb%3D',0.4,120)
        self.assertIsNone(body)
        self.assertEqual(info['error_code'],'UNEXPECTED_CONTENT_TYPE')
        self.assertEqual(session.get.call_args.kwargs['params']['TOKEN'],'a/b=')

if __name__=='__main__': unittest.main()
