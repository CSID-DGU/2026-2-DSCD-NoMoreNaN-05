"""Extract explicit, product-scoped identity declarations without an LLM."""
import re
from src.claim_evidence_experiment import name_key
from scripts.recover_product_candidates import same_numbers, notation_key
from scripts.evaluate_relaxed_product_mapping import strip_brand

LABEL = re.compile(
    r'(?P<label>품목\s*제조\s*(?:신고|보고)\s*번호|제조\s*(?:신고|보고)\s*번호|'
    r'유통\s*전문\s*판매원|수입\s*판매원|수입원|판매업소명[·ㆍ/]제조업소명|'
    r'제조\s*(?:업소명|업체명|업소|업체|원|사)|판매\s*(?:업소명|원|사)|'
    r'브랜드(?:명)?|제품명)(?:\s*[:：]\s*|\s+(?=\(?주\)?|[A-Za-z가-힣]))')


def declarations(claims, product_ref):
    observations = []
    for claim in claims:
        if claim.get('product_ref') != product_ref:
            continue
        text = claim.get('text') or ''
        matches = list(LABEL.finditer(text))
        for index, match in enumerate(matches):
            label = re.sub(r'\s+', '', match['label'])
            if label in ('브랜드','브랜드명','제품명') and not re.search(r'[:：]',match[0]):
                continue
            prefix = text[max(0, match.start()-12):match.start()]
            if re.search(r'원료\s*$|원재료\s*$|예시\s*$|예를\s*들어\s*$', prefix):
                continue
            end = matches[index+1].start() if index+1 < len(matches) else len(text)
            value = text[match.end():end]
            value = re.split(r'[\r\n;|]|(?:소재지|주소|고객센터|소비자상담실)\s*[:：]', value)[0]
            value = value.strip(' \t.,/·ㆍ-')
            if not value or re.search(r'미확인|알\s*수\s*없|불명|아님|아닌|예시', value):
                continue
            if '번호' in label:
                digits = re.match(r'[\d\s-]+', value)
                value = re.sub(r'\D', '', digits[0]) if digits else ''
                if not 11 <= len(value) <= 20:
                    continue
                role = 'report_number'
            elif label == '제품명':
                role = 'product_name'
            elif label.startswith('브랜드'):
                role = 'brand_name'
            elif label.startswith('제조') or label == '판매업소명·제조업소명':
                role = 'manufacturer_name'
            else:
                role = 'seller_name'
            observations.append(dict(role=role, value=value, claim_id=claim.get('claim_id'),
                product_ref=product_ref, text=text, start=match.end(), end=match.end()+len(text[match.end():end])))
    return observations


def resolve_claim_identity(row, claims, index, grouping):
    """Narrow candidates only from this product's explicit claim observations.

    The original input manufacturer_name never participates. Sellers are retained
    as provenance, not treated as manufacturers. No generic efficacy inference.
    """
    observations = declarations(claims, row['product_ref'])
    own_claims = [c for c in claims if c.get('product_ref') == row['product_ref']]
    pool = {c['product_id']:grouping.products[c['product_id']] for c in row.get('candidates', [])}
    name_hits = {}
    explicit_names = [o for o in observations if o['role'] == 'product_name']
    if explicit_names:
        for observation in explicit_names:
            hits = index.notation.get(notation_key(observation['value']), [])
            for hit in hits:
                name_hits[hit['product_id']] = hit
    else:
        raw_variants={notation_key(row.get('product_name') or ''),notation_key(strip_brand(row.get('product_name'),row.get('brand_name')))}
        brand_key=notation_key(row.get('brand_name') or '')
        for claim in own_claims:
            text = claim.get('text') or ''
            if re.search(r'아닌|다른\s*제품|예를\s*들어|원료\s*제조', text):
                continue
            context_hits=index.context_products(text)
            if len({name_key(p['product_name']) for p in context_hits})>1 and re.search(r'[,/]|제품\s*중',text):
                continue
            for hit in context_hits:
                # Unlabelled text can only narrow existing product candidates.
                # Never turn an ingredient mention (Magnesium, omega-3, etc.)
                # into a new product, or shorten an observed product variant.
                hit_key=notation_key(hit['product_name'])
                if hit['product_id'] not in pool or not any(v and v in hit_key for v in raw_variants):
                    continue
                if hit_key not in raw_variants and (not brand_key or brand_key not in hit_key):
                    continue
                name_hits[hit['product_id']] = hit
                observations.append(dict(role='db_product_name_in_claim', value=hit['product_name'],
                    claim_id=claim.get('claim_id'), product_ref=row['product_ref'], text=text))
    # Ignore a bare base name embedded in an explicitly observed longer variant.
    names = {name_key(p['product_name']) for p in name_hits.values()}
    maximal = {n for n in names if not any(n != other and other.startswith(n) for other in names)}
    name_hits = {pid:p for pid,p in name_hits.items() if name_key(p['product_name']) in maximal}
    if name_hits:
        common = set(pool) & set(name_hits)
        # A full explicit product-name declaration can supply candidates that
        # were absent from the structured product field.
        if common:
            pool = {pid:pool[pid] for pid in common}
        elif explicit_names:
            pool = dict(name_hits)
        else:
            return None, observations, 'claim_product_name_conflicts_with_existing_candidates'
    reports = {name_key(o['value']) for o in observations if o['role'] == 'report_number'}
    makers = {grouping.company(o['value']) for o in observations if o['role'] == 'manufacturer_name'}
    if len(reports) > 1 or len(makers) > 1:
        return None, observations, 'conflicting_claim_identity_declarations'
    if makers:
        maker = next(iter(makers))
        narrowed = [p for p in pool.values() if grouping.company(p['company_name']) == maker]
        # Input numeric variants are protected unless a labelled full product
        # name explicitly supplies the corrected variant.
        if not explicit_names:
            narrowed = [p for p in narrowed if same_numbers(row.get('product_name') or '', p['product_name'])]
        keys = {grouping.key(p) for p in narrowed}
        if len(keys) == 1:
            return grouping.group(next(iter(keys))), observations, 'claim_manufacturer_and_product_name'
    elif name_hits and pool:
        # Brand remains a separate comparison field; do not substitute seller.
        keys = {grouping.key(p) for p in pool.values()}
        if len(keys) == 1:
            return grouping.group(next(iter(keys))), observations, 'claim_full_product_name_unique_group'
        brand = grouping.company(row.get('brand_name'))
        matching = [key for key in keys if key[1] == brand]
        if len(matching) == 1:
            return grouping.group(matching[0]), observations, 'claim_full_product_name_and_brand'
    # A report explicitly declared in claims is an independent fallback.
    if reports:
        report = next(iter(reports))
        keys = {grouping.key(p) for p in grouping.reports.get(report, [])}
        if makers and any(key[1] not in makers for key in keys):
            return None, observations, 'claim_report_and_manufacturer_conflict'
        if len(keys) == 1:
            return grouping.group(next(iter(keys)), report=report), observations, 'claim_report_number_fallback'
    return None, observations, 'no_unique_product_from_claims'
