"""Re-run established product retrieval and identity rules on a new input.

Candidate diagnostics are sidecars; the transport keeps the agreed statuses
and DB fields. Source claims (including effect and claim_type) are untouched.
"""
import copy
import json
from collections import Counter, defaultdict
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from .scripts.evaluate_relaxed_product_mapping import search
from .scripts.export_restored_claim_handoff import select_product
from .scripts.recover_product_candidates import RecoveryIndex
from .src.claim_evidence_experiment import name_key
from .src.claim_type_db_format import ARRAYS, TYPE_FIELDS, build_product
from .src.product_identity_filtered import FilteredProductCatalog, company_core
from .src.product_name_groups import ProductGroups


def remap(videos, dsn, pairs_path, threshold, db_version, input_path=None):
    pairs_path = Path(pairs_path)
    originals = videos
    with psycopg.connect(dsn, autocommit=True, row_factory=dict_row) as db:
        database = db.execute(
            "SELECT current_database() AS dbname, "
            "(SELECT n.nspname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace"
            " WHERE c.oid = to_regclass('products')) AS products, "
            "(SELECT n.nspname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace"
            " WHERE c.oid = to_regclass('ingredients')) AS ingredients").fetchone()
        catalog = FilteredProductCatalog(db)
        choices = [name_key(p['product_name']) for p in catalog.products]
        pairs = {frozenset(company_core(v) for v in pair) for pair in json.loads(
            pairs_path.read_text(encoding='utf-8'))['pairs']}
        grouping = ProductGroups(catalog.products, pairs)
        cache, results, audits = {}, [], []
        ingredients = [r['ingredient_name'] for r in db.execute('SELECT ingredient_name FROM ingredients ORDER BY ingredient_id')]
        recovery = RecoveryIndex(catalog.products, ingredients)
        for vi, video in enumerate(originals):
            result = {'video_id': video['video_id'], 'url': video.get('url'), 'title': video.get('title'),
                          'db_version': db_version,
                          'products': [], 'claims': copy.deepcopy(video.get('claims', []))}
            for product in video.get('products', []):
                key = tuple(product.get(k) for k in ('product_name', 'brand_name', 'manufacturing_report_number'))
                if key not in cache:
                    cache[key] = search(catalog, product, {'status':'not_found'}, choices,
                                        threshold=threshold, brand_recombine=True, report_fallback_only=True)
                candidates, route, score = cache[key]
                observations = []
                # Existing exact-notation recovery overrides fuzzy candidates;
                # whole-phrase/context recovery runs only when retrieval failed.
                if route.startswith('full_name_distance_'):
                    exact = recovery.exact_notation(product)
                    if exact:
                        candidates, route, score = exact, 'exact_notation_over_fuzzy', None
                if not candidates:
                    candidates, recovered_route, observations = recovery.search(
                        product, video, {'title':video.get('title') or ''})
                    if candidates:
                        route, score = recovered_route, None
                row = {'candidates': candidates}
                chosen, method, reason, ids, company_source = select_product(
                    product, row, video.get('claims', []), grouping)
                status = 'confirmed' if chosen else 'unresolved' if ids else 'not_found'
                full = db.execute('SELECT * FROM products WHERE product_id = %s',
                                  (chosen['product_id'],)).fetchone() if chosen else None
                exported = build_product(product, {'product':{'match':{'status': status, 'method': method}}}, full, len(ids))
                result['products'].append(exported)
                audits.append(dict(video_id=video['video_id'], url=video.get('url'), **product,
                    status=status, reason=reason, route=route, top_name_score=score,
                    company_source=company_source, observations=observations,
                    selected_product_id=chosen['product_id'] if chosen else None,
                    candidate_ids=ids,
                    candidates=[grouping.products[i] for i in ids]))
            results.append(result)
            if (vi+1) % 50 == 0:
                print(f'Processed {vi+1}/{len(originals)} videos', flush=True)

    # Verify round-trip original claims and scalar/array transport contracts.
    for original, result in zip(originals, results):
        assert original.get('claims', []) == result['claims']
        assert len(original.get('products', [])) == len(result['products'])
        for before, after in zip(original['products'], result['products']):
            for field in before:
                if field != 'manufacturing_report_number' or after['match']['status'] != 'confirmed':
                    assert before[field] == after[field]
            if after['match']['status'] == 'confirmed':
                assert after['match']['method'] in ('report_number', 'name_and_company')
                assert set(after['DB']) == set(TYPE_FIELDS)
                for kind, fields in TYPE_FIELDS.items():
                    assert list(after['DB'][kind]) == fields
                    for field in fields:
                        assert isinstance(after['DB'][kind][field], list if field in ARRAYS else str)
            else:
                assert after['DB'] is None and after['match']['method'] is None

    def aggregate(rows):
        n = len(rows)
        counts = Counter(r['status'] for r in rows)
        candidate = sum(bool(r['candidate_ids']) for r in rows)
        return {'total': n, 'candidate_found': candidate,
                    'candidate_rate': round(100*candidate/n, 2) if n else 0,
                    'confirmed': counts['confirmed'],
                    'confirmed_rate': round(100*counts['confirmed']/n, 2) if n else 0,
                    'unresolved': counts['unresolved'], 'not_found': counts['not_found']}

    groups = defaultdict(list)
    for row in audits:
        if name_key(row.get('product_name')):
            groups[(name_key(row['product_name']), name_key(row.get('brand_name')))].append(row)
    unique = []
    for rows in groups.values():
        # Coverage across occurrences, not a new confirmed product identity.
        order = {'confirmed':0, 'unresolved':1, 'not_found':2}
        unique.append(min(rows, key=lambda r:order[r['status']]))
    summary = {'input_file': str(input_path) if input_path else None, 'database': database,
        'videos': len(originals), 'unique_video_ids': len({v['video_id'] for v in originals}),
        'unique_urls': len({v.get('url') for v in originals if v.get('url')}),
        'claims': sum(len(v.get('claims', [])) for v in originals),
        'product_entries': aggregate(audits), 'deduplicated_product_name_brand': aggregate(unique),
        'missing_product_name': sum(not name_key(r.get('product_name')) for r in audits),
        'unresolved_reasons': dict(Counter(r['reason'] for r in audits if r['status']=='unresolved')),
        'retrieval_routes': dict(Counter(r['route'] for r in audits)),
        'database_products': len(catalog.products), 'threshold': threshold,
        'original_claims_preserved': True, 'original_files_changed': False,
        'accuracy_measured': False, 'A_B_runtime_tested': False,
        'policy': f'Existing {threshold:g}-point full-name candidate retrieval, exact notation recovery, manufacturer/approved-pair grouping, explicit same-product claim manufacturer, brand fallback, report fallback. No new match statuses; DB only confirmed.'}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return results, audits, summary
