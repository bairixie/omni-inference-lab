"""Scan every repository file except Git internals, including untracked files."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, help='Write a JSON record outside the repository')
    args = parser.parse_args()
    root = args.root.resolve()
    files = sorted(p for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts)
    errors, non_ascii, inventory = [], [], []
    forbidden = {'.wav', '.flac', '.mp3', '.mp4', '.safetensors', '.ckpt', '.pt', '.bin', '.log', '.zip', '.pyc'}
    secret_patterns = [r'gh[pousr]_[A-Za-z0-9]{20,}', r'AKIA[0-9A-Z]{16}',
                       r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
    allowed_symbols = set('→←↔≤≥×−–—±≈μ²³°…“”‘’')
    for path in sorted(root.rglob('*')):
        if '.git' in path.relative_to(root).parts:
            continue
        rel = str(path.relative_to(root))
        if not rel.isascii():
            errors.append({'path': rel, 'check': 'non_ascii_path'})
        if path.is_symlink():
            errors.append({'path': rel, 'check': 'symlink_requires_review'})
    for path in files:
        rel = str(path.relative_to(root)); data = path.read_bytes()
        inventory.append({'path': rel, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
        if path.suffix.lower() in forbidden:
            errors.append({'path': rel, 'check': 'runtime_or_archive_asset'})
        try:
            content = data.decode('utf-8')
        except UnicodeDecodeError:
            if path.suffix.lower() != '.png':
                errors.append({'path': rel, 'check': 'unreviewed_binary'})
            continue
        for number, line in enumerate(content.splitlines(), 1):
            unusual = sorted(set(c for c in line if ord(c) > 127 and c not in allowed_symbols))
            if unusual:
                non_ascii.append({'path': rel, 'line': number,
                                  'characters': [{'codepoint': f'U+{ord(c):04X}', 'name': unicodedata.name(c, 'unknown')} for c in unusual]})
            if any(re.search(pattern, line) for pattern in secret_patterns):
                errors.append({'path': rel, 'line': number, 'check': 'possible_secret'})
            if re.search(r'/home/[a-z][a-z0-9_-]*/', line):
                errors.append({'path': rel, 'line': number, 'check': 'hardcoded_user_path'})
        if path.suffix == '.py':
            try:
                ast.parse(content, filename=rel)
            except SyntaxError:
                errors.append({'path': rel, 'check': 'python_syntax'})
        if path.suffix == '.json':
            try:
                decoded = json.dumps(json.loads(content), ensure_ascii=False)
                unusual = sorted(set(c for c in decoded if ord(c) > 127 and c not in allowed_symbols))
                if unusual:
                    non_ascii.append({'path': rel, 'scope': 'decoded_json_strings',
                                      'characters': [f'U+{ord(c):04X}' for c in unusual]})
            except ValueError:
                errors.append({'path': rel, 'check': 'json_syntax'})
        if path.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', content):
                if '://' in target or target.startswith(('#', 'mailto:')):
                    continue
                target = unquote(target.split('#', 1)[0]).strip('<>')
                if target and not (path.parent / target).exists():
                    errors.append({'path': rel, 'target': target, 'check': 'missing_local_link'})
    report = {'scope': 'All files and directories including untracked; .git excluded',
              'file_count': len(files), 'total_bytes': sum(x['bytes'] for x in inventory),
              'files_above_256_KiB': [x for x in inventory if x['bytes'] > 262144],
              'errors': errors, 'unreviewed_non_ascii': non_ascii,
              'inventory': inventory,
              'limits': 'ASCII is not proof of English. Prose, terminology and PNG labels require manual review.'}
    if args.output:
        destination = args.output.resolve()
        if destination == root or root in destination.parents:
            parser.error('Audit output must be outside the audited repository')
        destination.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'inventory'}, indent=2))
    raise SystemExit(bool(errors or non_ascii))


if __name__ == '__main__':
    main()
