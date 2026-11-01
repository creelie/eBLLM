"""Refresh public Google/quantumlib inventories and incremental creelie source records.

This reads metadata and short attributed excerpts. It never builds or executes
an upstream project and never certifies a mathematical claim.
"""

import base64
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT / 'src/ebllm/research/data/portfolio.json'
WATCH = ROOT / 'src/ebllm/research/data/public-upstream-watch.json'
GROUPS = [('google', 'orgs'), ('google-deepmind', 'orgs'), ('quantumlib', 'orgs'), ('creelie', 'users')]
MANAGED = {'creelie/ebllm', 'creelie/opengluon'}


def api(path, optional=False):
    headers = {'Accept':'application/vnd.github+json','User-Agent':'Anaxia-public-source-refresh','X-GitHub-Api-Version':'2022-11-28'}
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    try:
        with urllib.request.urlopen(urllib.request.Request('https://api.github.com' + path, headers=headers), timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if optional and error.code in (404, 409):
            return None
        raise


def repositories(owner, kind):
    found = []
    page = 1
    while True:
        batch = api(f'/{kind}/{owner}/repos?type=public&per_page=100&page={page}')
        found.extend(item for item in batch if not item['private'])
        if len(batch) < 100:
            break
        page += 1
    if not found:
        raise RuntimeError('Refusing an empty public inventory for ' + owner)
    return found


def write_if_changed(path, text):
    if path.exists() and path.read_text(encoding='utf-8') == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    return True


def write_json(path, data):
    return write_if_changed(path, json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def read_source(repo, previous):
    full_name = repo['full_name']
    if full_name.casefold() in MANAGED and previous:
        # A catalogue commit must not create an endless self-referential update.
        item = dict(previous)
        item['monitoring_note'] = 'Managed workspace: preserve its pinned research snapshot to avoid self-generated catalogue commits causing a refresh loop. OpenGluon separately tracks the live Anaxia source pin.'
        return item
    if previous and previous['pushed_at'] == repo['pushed_at']:
        # A release can be created from an existing tag without a new code push.
        release = api('/repos/' + full_name + '/releases/latest', optional=True)
        latest = None if not release else {'tag':release['tag_name'],'url':release['html_url'],'published_at':release.get('published_at'),'excerpt':re.sub(r'\s+',' ',release.get('body') or '').strip()[:480]}
        item = dict(previous, description=repo.get('description') or '', archived=repo['archived'], latest_release=latest)
        if latest != previous.get('latest_release'):
            item['scope_note_requires_review'] = True
        return item
    route = '/repos/' + full_name
    heads = api(route + '/commits?per_page=1', optional=True)
    commit = heads[0]['sha'] if heads else None
    readme = api(route + '/readme' + ('?ref=' + commit if commit else ''), optional=True)
    release = api(route + '/releases/latest', optional=True)
    text = ''
    if readme and readme.get('encoding') == 'base64':
        text = base64.b64decode(readme['content']).decode('utf-8', errors='replace')
    plain = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', text)).strip()
    item = {
        'name':repo['name'], 'url':repo['html_url'], 'commit':commit,
        'fork':repo['fork'], 'archived':repo['archived'], 'description':repo.get('description') or '',
        'pushed_at':repo['pushed_at'],
        'readme_url':f'{repo["html_url"]}/blob/{commit}/{urllib.parse.quote(readme["path"])}' if readme and commit else None,
        'readme_blob_sha':readme.get('sha') if readme else None, 'readme_excerpt':plain[:300],
        'latest_release':None if not release else {'tag':release['tag_name'],'url':release['html_url'],'published_at':release.get('published_at'),'excerpt':re.sub(r'\s+',' ',release.get('body') or '').strip()[:480]},
        'review_status':'source-recorded-not-independently-audited',
        'scope_note':previous['scope_note'] if previous else 'New public source: metadata and short excerpts recorded. Its mathematical claims require their own proof review.',
        'scope_note_commit':previous.get('scope_note_commit') if previous else None,
    }
    if previous and previous.get('scope_note_commit') != commit:
        item['scope_note_requires_review'] = True
    return item


def portfolio_doc(data):
    lines = ['# Public research portfolio', '', f'Public source snapshot: {data["captured_on"]}. {data["repository_count"]} repositories; {data["readme_count"]} READMEs; {data["release_count"]} stable releases.', '', 'Source claims retain their original authors and hypotheses. No entry is an independent proof audit. A scope note marked for review belongs to an earlier commit.', '', '| Repository | Latest release | Snapshot | Scope |', '| --- | --- | --- | --- |']
    for item in data['repositories']:
        release = item['latest_release']
        tag = '[' + release['tag'] + '](' + release['url'] + ')' if release else 'No stable release'
        sha = '[' + item['commit'][:10] + '](' + item['url'] + '/tree/' + item['commit'] + ')' if item['commit'] else 'Empty repository'
        scope = item['scope_note'].replace('|', '\\|')
        if item.get('scope_note_requires_review'):
            scope = '**Prior scope note; review new commit.** ' + scope
        lines.append(f'| [{item["name"]}]({item["url"]}) | {tag} | {sha} | {scope} |')
    return '\n'.join(lines) + '\n'


def main():
    old_portfolio = json.loads(PORTFOLIO.read_text(encoding='utf-8'))
    previous = {item['name']:item for item in old_portfolio['repositories']}
    all_repos = {}
    for owner, kind in GROUPS:
        found = repositories(owner, kind)
        all_repos[owner] = found
        print(f'{owner}: {len(found)} public repositories', flush=True)
    records = [read_source(repo, previous.get(repo['name'])) for repo in all_repos['creelie']]
    current_names = {item['name'] for item in records}
    for name in set(previous) - current_names:
        retained = dict(previous[name], monitoring_note='Absent from the latest public inventory; previous snapshot retained, not deleted.')
        records.append(retained)
    records.sort(key=lambda item:item['name'].casefold())
    changed = records != old_portfolio['repositories']
    if changed:
        portfolio = dict(old_portfolio, captured_on=datetime.now(timezone.utc).date().isoformat(), repository_count=len(records), readme_count=sum(bool(item['readme_url']) for item in records), release_count=sum(bool(item['latest_release']) for item in records), fork_count=sum(item['fork'] for item in records), repositories=records)
        write_json(PORTFOLIO, portfolio)
        write_if_changed(ROOT/'docs/RESEARCH-PORTFOLIO.md', portfolio_doc(portfolio))
        readme = (ROOT/'README.md').read_text(encoding='utf-8')
        readme = re.sub(r'\*\*\d+\*\* public repository snapshots',f'**{len(records)}** public repository snapshots',readme,count=1)
        write_if_changed(ROOT/'README.md',readme)
    watch_records = []
    for owner, repos in all_repos.items():
        for repo in repos:
            managed = repo['full_name'].casefold() in MANAGED
            watch_records.append({
                'full_name':repo['full_name'], 'owner':owner, 'url':repo['html_url'],
                'description':repo.get('description') or '', 'fork':repo['fork'], 'archived':repo['archived'],
                'default_branch':repo['default_branch'], 'pushed_at':None if managed else repo['pushed_at'],
                'updated_at':None if managed else repo['updated_at'],
                'monitoring':'managed-workspace-no-self-trigger' if managed else 'public-metadata',
            })
    watch_records.sort(key=lambda item:item['full_name'].casefold())
    old_watch = json.loads(WATCH.read_text(encoding='utf-8')) if WATCH.exists() else {}
    if watch_records != old_watch.get('repositories'):
        counts = dict(sorted(Counter(item['owner'] for item in watch_records).items()))
        watch = {'schema':'anaxia-public-upstream-watch-v1','captured_at_utc':datetime.now(timezone.utc).isoformat(),'repository_count':len(watch_records),'owners':counts,'scope':'Public repository metadata is monitored. Only explicitly selected source repositories are cloned or pinned in OpenGluon. Metadata updates do not certify proofs or execute upstream code.','repositories':watch_records}
        write_json(WATCH, watch)
        rows = '\n'.join(f'| [{owner}](https://github.com/{owner}) | {count} |' for owner,count in counts.items())
        write_if_changed(ROOT/'docs/PUBLIC-UPSTREAM-WATCH.md', '# Public upstream watch\n\nThe source-refresh workflow polls these public inventories hourly, including new repositories and changed push/update timestamps. It never executes imported code.\n\n| Owner | Public repositories |\n| --- | --- |\n'+rows+'\n\nAll records are in `src/ebllm/research/data/public-upstream-watch.json`. The creelie research portfolio separately records pinned source excerpts. Managed workspace entries suppress self-generated timestamp loops. A source change is not a mathematical proof verification.\n')
    print('Source refresh complete. Research/source claims remain explicitly unreviewed.', flush=True)


if __name__ == '__main__':
    main()
