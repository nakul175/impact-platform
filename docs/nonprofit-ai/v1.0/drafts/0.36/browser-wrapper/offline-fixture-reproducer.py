"""Offline wrapper tests against explicitly synthetic future recipe/assets only.
No application module, package checker, browser, HTTP request or database is run.
"""
from pathlib import Path
import ast, importlib.util, json, tempfile
ROOT = Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform')
WRAPPER = Path('/private/tmp/tola-ai-036-browser-qualification.py')
spec = importlib.util.spec_from_file_location('private_tola_036_wrapper', WRAPPER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory(prefix='tola-036-offline-recipe-assets-', dir='/private/tmp') as name:
    fixture = Path(name)
    recipe = (ROOT / 'Makefile').read_text()
    line = '\tnode --experimental-strip-types tools/browser/ai-procurement-preview-model-check.mjs\n'
    anchor = '\tnode --experimental-strip-types tools/browser/ai-walkthrough-adapter-check.mjs\n'
    assert recipe.count(anchor) == 1
    if line not in recipe:
        recipe = recipe.replace(anchor, anchor + line)
    (fixture / 'Makefile').write_text(recipe)
    (fixture / 'scripts').mkdir()
    runner = (ROOT / 'scripts/run.py').read_text()
    (fixture / 'scripts/run.py').write_text(runner)
    tree = ast.parse(runner)
    registered = next(ast.literal_eval(item.value) for item in tree.body if isinstance(item, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'BROWSER_MODES' for target in item.targets))
    for item in (*module.EXPECTED_PURE, 'tools/browser/prepare.mjs', *['tools/browser/' + item for item in registered.values()]):
        path = fixture / item
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('// synthetic presence-only file: NOT executed\n')
    (fixture / 'VERSION.json').write_text(json.dumps({**module.EXPECTED_VERSION, 'fixture_scope': 'PRIVATE_SYNTHETIC_FUTURE_TUPLE'}))
    dist = fixture / 'apps/web/dist'
    (dist / 'assets').mkdir(parents=True)
    for item in ('index.html', 'ai-walkthrough.html', *[f'assets/synthetic-{i}.js' for i in range(6)]):
        (dist / item).write_text('Private synthetic byte-verification fixture only: ' + item)
    proof_path = fixture / 'docs/evidence/sprint-0.36-web-build-source-proof.json'
    proof_path.parent.mkdir(parents=True)
    proof_path.write_text(json.dumps({'scope': 'PRIVATE_SYNTHETIC_ASSETS_NOT_ACTUAL_BUILD', 'exit_codes': [0,0], 'built_assets_sha256': {str(path.relative_to(dist)): module.digest(path) for path in sorted(dist.rglob('*')) if path.is_file()}}))
    module.self_test(fixture, 'PRIVATE_SYNTHETIC_FUTURE_RECIPE_AND_ASSETS_NOT_0.36_PRODUCT_QUALIFICATION')
    # The plan prerequisite refusal predicates run on the complete proposed module.
    plan = module.make_plan(fixture)
    assert tuple(plan['pure_prerequisites']) == module.EXPECTED_PURE
    for kind in ('missing-pure', 'reordered-pure', 'stale-tuple'):
        original_version = (fixture / 'VERSION.json').read_bytes()
        if kind == 'missing-pure':
            (fixture / 'Makefile').write_text(recipe.replace(line, ''))
        elif kind == 'reordered-pure':
            (fixture / 'Makefile').write_text(recipe.replace(anchor + line, line + anchor))
        else:
            (fixture / 'VERSION.json').write_text(json.dumps({**module.EXPECTED_VERSION, 'build': '0.35.0'}))
        try:
            module.make_plan(fixture)
            raise AssertionError('Invalid proposed recipe accepted: ' + kind)
        except RuntimeError:
            pass
        (fixture / 'Makefile').write_text(recipe)
        (fixture / 'VERSION.json').write_bytes(original_version)
