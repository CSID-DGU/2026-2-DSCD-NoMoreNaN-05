"""Strict output schema from claim_type_db_format.md; never classify claims."""
import copy
import json

TYPE_FIELDS={
    'QUANTITY':['BASE_STANDARD','SRV_USE','DISTB_PD','PRDT_SHAP_CD_NM','BSSH_PRMS_DT','INTAKE_HINT1','RAWMTRL_STD_INFO'],
    'COMPOSITION':['RAWMTRL_NM','INDIV_RAWMTRL_NM','ETC_RAWMTRL_NM','CAP_RAWMTRL_NM','PRDLST_CDNM','BASE_STANDARD','SUNGSANG','RAWMTRL_DICT_INFO'],
    'CERTIFICATION':['STTEMNT_NO','PRMS_DT','INDUTY_CD_NM','MAIN_FNCTN','RAWMTRL_NM','INDIV_RAWMTRL_NM','RAWMTRL_STD_INFO','RAWMTRL_CLASS_INFO'],
    'EFFECT':['MAIN_FNCTN','INTAKE_HINT1','RAWMTRL_STD_INFO']}
ARRAYS={'RAWMTRL_STD_INFO','RAWMTRL_DICT_INFO','RAWMTRL_CLASS_INFO'}
DB_ALIASES={'BASE_STANDARD':'specification','SRV_USE':'intake_method','DISTB_PD':'shelf_life',
    'INTAKE_HINT1':'intake_precautions','SUNGSANG':'appearance','STTEMNT_NO':'manufacturing_report_number','MAIN_FNCTN':'main_functionality'}


def db_sections(product):
    values={}
    for field in {f for fields in TYPE_FIELDS.values() for f in fields}:
        value=product.get(DB_ALIASES.get(field,field))
        if field in ARRAYS:
            if value is None or value=='':value=[]
            elif isinstance(value,str):value=json.loads(value)
            if not isinstance(value,list):raise ValueError('Array field is not an array: '+field)
            values[field]=copy.deepcopy(value)
        else:
            if value is None:value=''
            if not isinstance(value,str):raise ValueError('DB scalar must be raw text: '+field)
            values[field]=value
    return {kind:{field:copy.deepcopy(values[field]) for field in fields} for kind,fields in TYPE_FIELDS.items()}


def build_product(original,mapping,db_product,candidate_count):
    output=copy.deepcopy(original)
    match=mapping.get('product',{}).get('match',{}) if mapping else {}
    status=match.get('status','not_found')
    if status not in {'confirmed','unresolved','not_found'}:raise ValueError('Invalid match status')
    confirmed=status=='confirmed'
    if confirmed and db_product is None:raise ValueError('Confirmed product missing DB row')
    method=match.get('method') if confirmed else None
    if confirmed and method not in {'report_number','name_and_company'}:raise ValueError('Unsupported confirmed method')
    output['match']=dict(status=status,method=method,candidates=candidate_count,
        matched_name=db_product['product_name'] if confirmed else None,
        matched_company=db_product['company_name'] if confirmed else None)
    output['DB']=db_sections(db_product) if confirmed else None
    if confirmed:output['manufacturing_report_number']=db_product['manufacturing_report_number']
    return output
