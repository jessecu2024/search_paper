#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple interactive academic paper finder (detail-abstract enabled)
- Preconfigured top conferences/journals
- Interactive and CLI modes
- If the list page has no abstract, fetch it from the detail page automatically
- Export Markdown + JSON to ./output
- Standard library only
"""

import argparse
import html
import json
import os
import random
import re
import sys
import time
from datetime import datetime
from urllib.parse import quote, urljoin
import urllib.request


class SimpleConferenceScraper:
    def __init__(self):
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

        # Preconfigured venues
        self.conferences = {
            # AI/ML
            'ICML': {
                'name': 'International Conference on Machine Learning',
                'url': 'https://icml.cc/virtual/{year}/papers.html',
                'search_url': 'https://icml.cc/virtual/{year}/papers.html?search={keyword}',
                'base': 'https://icml.cc',
                'years': ['2020', '2021', '2022', '2023', '2024', '2025']
            },
            'NeurIPS': {
                'name': 'Neural Information Processing Systems',
                'url': 'https://nips.cc/virtual/{year}/papers.html',
                'search_url': 'https://nips.cc/virtual/{year}/papers.html?search={keyword}',
                'base': 'https://nips.cc',
                'years': ['2020', '2021', '2022', '2023', '2024']
            },
            'ICLR': {
                'name': 'International Conference on Learning Representations',
                'url': 'https://iclr.cc/virtual/{year}/papers.html',
                'search_url': 'https://iclr.cc/virtual/{year}/papers.html?search={keyword}',
                'base': 'https://iclr.cc',
                'years': ['2020', '2021', '2022', '2023', '2024', '2025']
            },
            'AAAI': {
                'name': 'Association for the Advancement of Artificial Intelligence',
                'url': 'https://aaai.org/{year}/accepted-papers/',
                'search_url': None,
                'base': 'https://aaai.org',
                'years': ['2020', '2021', '2022', '2023', '2024', '2025']
            },
            'IJCAI': {
                'name': 'International Joint Conference on Artificial Intelligence',
                'url': 'https://ijcai-{year}.org/accepted-papers',
                'search_url': None,
                'base': None,
                'years': ['2020', '2021', '2022', '2023', '2024']
            },

            # CV
            'CVPR': {
                'name': 'Conference on Computer Vision and Pattern Recognition',
                'url': 'https://cvpr{year}.thecvf.com/accepted-papers',
                'search_url': None,
                'base': None,
                'years': ['2020', '2021', '2022', '2023', '2024']
            },
            'ICCV': {
                'name': 'International Conference on Computer Vision',
                'url': 'https://iccv{year}.thecvf.com/accepted-papers',
                'search_url': None,
                'base': None,
                'years': ['2021', '2023']
            },
            'ECCV': {
                'name': 'European Conference on Computer Vision',
                'url': 'https://eccv{year}.eu/accepted-papers/',
                'search_url': None,
                'base': 'https://eccv{year}.eu',
                'years': ['2020', '2022', '2024']
            },

            # NLP
            'ACL': {
                'name': 'Association for Computational Linguistics',
                'url': 'https://{year}.aclweb.org/program/accepted/',
                'search_url': None,
                'base': None,
                'years': ['2020', '2021', '2022', '2023', '2024']
            },
            'EMNLP': {
                'name': 'Empirical Methods in Natural Language Processing',
                'url': 'https://{year}.emnlp.org/program/accepted/',
                'search_url': None,
                'base': None,
                'years': ['2020', '2021', '2022', '2023', '2024']
            },
            'NAACL': {
                'name': 'North American Chapter of ACL',
                'url': 'https://{year}.naacl.org/program/accepted/',
                'search_url': None,
                'base': None,
                'years': ['2021', '2022', '2024']
            },

            # DB / DM
            'KDD': {
                'name': 'Knowledge Discovery and Data Mining',
                'url': 'https://kdd.org/kdd{year}/accepted-papers/',
                'search_url': None,
                'base': 'https://kdd.org',
                'years': ['2020', '2021', '2022', '2023', '2024']
            },
            'SIGMOD': {
                'name': 'ACM SIGMOD International Conference on Management of Data',
                'url': 'https://sigmod{year}.org/accepted-papers/',
                'search_url': None,
                'base': None,
                'years': ['2020', '2021', '2022', '2023', '2024']
            },
            'VLDB': {
                'name': 'Very Large Data Bases',
                'url': 'https://vldb.org/{year}/accepted-papers/',
                'search_url': None,
                'base': 'https://vldb.org',
                'years': ['2020', '2021', '2022', '2023', '2024']
            },

            # Systems / Security
            'SOSP': {
                'name': 'Symposium on Operating Systems Principles',
                'url': 'https://sosp{year}.org/accepted-papers/',
                'search_url': None,
                'base': None,
                'years': ['2021', '2023']
            },
            'OSDI': {
                'name': 'Operating Systems Design and Implementation',
                'url': 'https://www.usenix.org/conference/osdi{year}/accepted-papers',
                'search_url': None,
                'base': 'https://www.usenix.org',
                'years': ['2020', '2022', '2024']
            },
            'CCS': {
                'name': 'ACM Conference on Computer and Communications Security',
                'url': 'https://www.sigsac.org/ccs/{year}/accepted-papers/',
                'search_url': None,
                'base': 'https://www.sigsac.org',
                'years': ['2020', '2021', '2022', '2023', '2024']
            },

            # Theory
            'STOC': {
                'name': 'Symposium on Theory of Computing',
                'url': 'https://stoc{year}.org/accepted-papers/',
                'search_url': None,
                'base': None,
                'years': ['2020', '2021', '2022', '2023', '2024']
            },
            'FOCS': {
                'name': 'Foundations of Computer Science',
                'url': 'https://focs{year}.org/accepted-papers/',
                'search_url': None,
                'base': None,
                'years': ['2020', '2021', '2022', '2023', '2024']
            },

            # Journal
            'TPAMI': {
                'name': 'IEEE Transactions on Pattern Analysis and Machine Intelligence',
                'url': 'https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=34',
                'search_url': None,
                'base': 'https://ieeexplore.ieee.org',
                'years': ['2020', '2021', '2022', '2023', '2024', '2025']
            }
        }

        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/123.0 Safari/537.36'
            ),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'close',
        }

    # ---------- interactive UI ----------
    def show_conferences(self):
        print("\n=== Available Conferences & Journals ===")
        categories = {
            'AI/ML': ['ICML', 'NeurIPS', 'ICLR', 'AAAI', 'IJCAI'],
            'Computer Vision': ['CVPR', 'ICCV', 'ECCV'],
            'NLP': ['ACL', 'EMNLP', 'NAACL'],
            'Databases / Data Mining': ['KDD', 'SIGMOD', 'VLDB'],
            'Systems / Security': ['SOSP', 'OSDI', 'CCS'],
            'Theory': ['STOC', 'FOCS'],
            'Top Journal': ['TPAMI']
        }
        all_confs, counter = [], 1
        for category, confs in categories.items():
            print(f"\n{category}:")
            for conf in confs:
                if conf in self.conferences:
                    print(f"  {counter}. {conf} - {self.conferences[conf]['name']}")
                    all_confs.append(conf)
                    counter += 1

        print("\nQuick Picks:")
        print("  'ai'  -> ICML, NeurIPS, ICLR, AAAI, IJCAI")
        print("  'cv'  -> CVPR, ICCV, ECCV")
        print("  'nlp' -> ACL, EMNLP, NAACL")
        print("  'all' -> All above")
        return all_confs

    def get_user_selections(self):
        print("=" * 60)
        print("Simple Paper Finder")
        print("=" * 60)
        all_confs = self.show_conferences()
        print("\nSelect conferences (numbers, comma-separated, e.g., 1,2,3):")
        conf_input = input("Conferences: ").strip()

        selected_conferences = []
        if conf_input.lower() == 'all':
            selected_conferences = all_confs
        elif conf_input.lower() == 'ai':
            selected_conferences = ['ICML', 'NeurIPS', 'ICLR', 'AAAI', 'IJCAI']
        elif conf_input.lower() == 'cv':
            selected_conferences = ['CVPR', 'ICCV', 'ECCV']
        elif conf_input.lower() == 'nlp':
            selected_conferences = ['ACL', 'EMNLP', 'NAACL']
        else:
            try:
                indices = [int(x.strip()) for x in conf_input.split(',')]
                for idx in indices:
                    if 1 <= idx <= len(all_confs):
                        selected_conferences.append(all_confs[idx - 1])
            except Exception:
                print("Invalid input. Falling back to AI/ML.")
                selected_conferences = ['ICML', 'NeurIPS', 'ICLR', 'AAAI', 'IJCAI']

        print("\nAvailable years: 2020, 2021, 2022, 2023, 2024, 2025")
        year_input = input("Years (comma-separated, e.g., 2023,2024): ").strip()
        years = [x.strip() for x in year_input.split(',')] if year_input else ['2024']

        keyword_input = input("\nKeywords (comma-separated, e.g., unlearning,federated learning): ").strip()
        keywords = [x.strip() for x in keyword_input.split(',')] if keyword_input else ['machine learning']
        return selected_conferences, years, keywords

    # ---------- networking ----------
    def get_webpage_content(self, url, max_retry=3):
        last_err = None
        for i in range(max_retry):
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=20) as resp:
                    raw = resp.read()
                    try:
                        return raw.decode('utf-8')
                    except Exception:
                        return raw.decode('utf-8', errors='ignore')
            except Exception as e:
                last_err = e
                delay = 1.2 * (2 ** i) + random.random()
                print(f"  Warning [{i+1}/{max_retry}]: {e} -> retry in {delay:.1f}s: {url}")
                time.sleep(delay)
        print(f"  Error: failed to fetch -> {url} ({last_err})")
        return None

    # ---------- helpers ----------
    def contains_keywords(self, text, keywords):
        if not text or not keywords:
            return False
        low = ' ' + text.lower() + ' '
        for kw in keywords:
            kw = kw.strip().lower()
            if not kw:
                continue
            if ' ' in kw:
                if kw in low:
                    return True
            else:
                if re.search(rf'\b{re.escape(kw)}\b', low):
                    return True
        return False

    def is_valid_title(self, title):
        if not title:
            return False
        t = title.strip()
        if not (5 <= len(t) <= 300):
            return False
        bad = [
            r'^\d+\s*$',
            r'^(abstract|author|paper|download|pdf|view|more|home|about|contact)s?\s*$',
            r'http[s]?://',
            r'^(figure|table|equation|fig|tab|eq)\s+\d+',
            r'^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'^\w{1,2}\s*$',
        ]
        low = t.lower()
        if any(re.search(p, low) for p in bad):
            return False
        positive = [
            'learning', 'algorithm', 'network', 'model', 'method', 'approach',
            'analysis', 'system', 'framework', 'optimization', 'deep', 'neural',
            'machine', 'artificial', 'data', 'unlearning', 'federated'
        ]
        if any(p in low for p in positive):
            return True
        return len(t.split()) >= 3

    def is_valid_author_name(self, name):
        if not name:
            return False
        name = html.unescape(name).strip()
        if not (3 <= len(name) <= 80):
            return False
        invalid_patterns = [
            r'^\d+',
            r'(abstract|paper|download|pdf|view|session|poster|oral)',
            r'^(the|and|or|in|on|at|by|for|with|to|from)\b',
            r'(university|institute|college|department|lab|google|facebook|microsoft|openai|meta|amazon)',
            r'(gmail|email|@)',
            r'^[\W_]+$',
        ]
        low = name.lower()
        if any(re.search(p, low) for p in invalid_patterns):
            return False
        if re.match(r"^[A-Za-z][A-Za-z\.\-']+(?:\s*,\s*|\s+)[A-Za-z][A-Za-z\.\-']+(?:\s+[A-Za-z\.\-']+)*$", name):
            return True
        return len(re.findall(r"[A-Za-z]+", name)) >= 2

    def process_relative_url(self, href, venue):
        if not href:
            return ""
        if href.startswith('http'):
            return href
        base = self.conferences.get(venue, {}).get('base') or ''
        try:
            return urljoin(base, href) if base else href
        except Exception:
            return href

    def is_paper_link(self, url_):
        if not url_:
            return False
        low = url_.lower()
        if any(s in low for s in ['#', 'javascript:', 'mailto:']):
            return False
        if re.search(r'\.(css|js|png|jpg|jpeg|gif|ico)(\?|$)', low):
            return False
        indicators = ['paper', 'poster', 'presentation', 'virtual', 'abstract', 'proceedings', 'publication', 'article', 'pdf']
        return any(ind in low for ind in indicators)

    # ---------- detail page abstract ----------
    def fetch_abstract_from_detail(self, url, venue=None):
        html_text = self.get_webpage_content(url, max_retry=3)
        if not html_text:
            return ""

        # JSON-like fields
        json_pats = [
            r'"abstract"\s*:\s*"([^"]+)"',
            r'"summary"\s*:\s*"([^"]+)"',
            r'"description"\s*:\s*"([^"]+)"',
        ]
        for pat in json_pats:
            m = re.search(pat, html_text, re.IGNORECASE | re.DOTALL)
            if m:
                clean = html.unescape(re.sub(r'\\n', ' ', m.group(1)))
                clean = re.sub(r'\s+', ' ', clean).strip()
                if self.is_valid_abstract(clean):
                    return clean[:1200] + ("..." if len(clean) > 1200 else "")

        # Common class containers
        block_pats = [
            r'<[^>]*class="[^"]*abstract[^"]*"[^>]*>(.*?)</[^>]*>',
            r'<div[^>]*class="[^"]*card-text[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*summary[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*description[^"]*"[^>]*>(.*?)</div>',
            r'<p[^>]*class="[^"]*abstract[^"]*"[^>]*>(.*?)</p>',
        ]
        for pat in block_pats:
            m = re.search(pat, html_text, re.IGNORECASE | re.DOTALL)
            if m:
                clean = html.unescape(re.sub(r'<[^>]+>', ' ', m.group(1)))
                clean = re.sub(r'\s+', ' ', clean).strip()
                if self.is_valid_abstract(clean):
                    return clean[:1200] + ("..." if len(clean) > 1200 else "")

        # Heading "Abstract" followed by a block
        heading_pats = [
            r'(?:<h[1-6][^>]*>\s*Abstract\s*</h[1-6]>\s*)(<[^>]+>.*?</[^>]+>)',
            r'\[\s*Abstract\s*\]\s*</[^>]+>\s*(<[^>]+>.*?</[^>]+>)',
            r'>\s*Abstract\s*<\s*/[^>]+>\s*(<[^>]+>.*?</[^>]+>)',
        ]
        for pat in heading_pats:
            m = re.search(pat, html_text, re.IGNORECASE | re.DOTALL)
            if m:
                block = m.group(1)
                clean = html.unescape(re.sub(r'<[^>]+>', ' ', block))
                clean = re.sub(r'\s+', ' ', clean).strip()
                if self.is_valid_abstract(clean):
                    return clean[:1200] + ("..." if len(clean) > 1200 else "")

        # Fallback: window after "abstract"
        pos = html_text.lower().find('abstract')
        if pos != -1:
            window = html_text[pos: pos + 4000]
            clean = html.unescape(re.sub(r'<[^>]+>', ' ', window))
            clean = re.sub(r'\s+', ' ', clean).strip()
            if len(clean) > 200:
                parts = re.split(r'(?<=[\.!?])\s+', clean)
                joined = ' '.join(parts[:10])
                if self.is_valid_abstract(joined):
                    return joined[:1200] + ("..." if len(joined) > 1200 else "")
        return ""

    # ---------- extraction ----------
    def extract_authors_for_title(self, content, title, line_num):
        authors = []
        try:
            lines = content.split('\n')
            search_range = range(max(0, line_num - 5), min(len(lines), line_num + 15))
            context = '\n'.join(lines[i] for i in search_range)
            patterns = [
                r'<[^>]*class="[^"]*author[^"]*"[^>]*>(.*?)</[^>]*>',
                r'<span[^>]*class="[^"]*presenter[^"]*"[^>]*>(.*?)</span>',
                r'<div[^>]*class="[^"]*card-subtitle[^"]*"[^>]*>(.*?)</div>',
                r'(?:Authors?|By|Presented by)\s*[:\-]\s*(.*?)(?:<|\n|$)',
                r'"authors?"\s*:\s*\[(.*?)\]',
                r'"presenter"\s*:\s*"([^"]+)"',
            ]
            for pat in patterns:
                matches = re.findall(pat, context, re.IGNORECASE | re.DOTALL)
                for m in matches:
                    clean = html.unescape(re.sub(r'<[^>]+>', ' ', m)).strip()
                    clean = re.sub(r'\s+', ' ', clean)
                    if not clean or len(clean) < 3:
                        continue
                    parts = [clean]
                    seps = [r',\s*(?=and\s+)', r'\s+and\s+', r',\s*', r';\s*', r'\|\s*', r'\n\s*']
                    for sp in seps:
                        tmp = []
                        for p in parts:
                            tmp.extend(re.split(sp, p))
                        parts = tmp
                    for a in parts:
                        a = a.strip()
                        if self.is_valid_author_name(a):
                            authors.append(a)
                if authors:
                    break
            if not authors:
                name_pat = r'\b([A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})?)\b'
                for m in re.findall(name_pat, context):
                    if self.is_valid_author_name(m):
                        authors.append(m)
        except Exception as e:
            print(f"      Warning: author extraction failed: {e}")
        uniq, seen = [], set()
        for a in authors:
            k = a.lower()
            if k not in seen:
                seen.add(k)
                uniq.append(a)
            if len(uniq) >= 8:
                break
        return uniq

    def extract_abstract_for_title(self, content, title, line_num):
        abstract = ""
        try:
            lines = content.split('\n')
            search_range = range(max(0, line_num - 5), min(len(lines), line_num + 25))
            context = '\n'.join(lines[i] for i in search_range)
            patterns = [
                r'<[^>]*class="[^"]*abstract[^"]*"[^>]*>(.*?)</[^>]*>',
                r'<div[^>]*class="[^"]*card-text[^"]*"[^>]*>(.*?)</div>',
                r'<div[^>]*class="[^"]*summary[^"]*"[^>]*>(.*?)</div>',
                r'<div[^>]*class="[^"]*description[^"]*"[^>]*>(.*?)</div>',
                r'(?:Abstract|Summary|Description)\s*[:\-]\s*(.*?)(?:<|\n\n|\r\n\r\n|$)',
                r'"abstract"\s*:\s*"([^"]+)"',
                r'"summary"\s*:\s*"([^"]+)"',
                r'"description"\s*:\s*"([^"]+)"',
            ]
            for pat in patterns:
                matches = re.findall(pat, context, re.IGNORECASE | re.DOTALL)
                for m in matches:
                    clean = html.unescape(re.sub(r'<[^>]+>', ' ', m)).strip()
                    clean = re.sub(r'\s+', ' ', clean)
                    if self.is_valid_abstract(clean):
                        abstract = clean[:600] + ("..." if len(clean) > 600 else "")
                        break
                if abstract:
                    break
            if not abstract:
                paras = re.findall(r'([^<>]{80,800})', context)
                for para in paras:
                    clean = html.unescape(para).strip()
                    clean = re.sub(r'\s+', ' ', clean)
                    if self.is_valid_abstract(clean):
                        abstract = clean[:600] + ("..." if len(clean) > 600 else "")
                        break
        except Exception as e:
            print(f"      Warning: abstract extraction failed: {e}")
        return abstract

    def is_valid_abstract(self, text):
        if not text or not (50 <= len(text) <= 2000):
            return False
        invalid = [
            r'^(author|paper|download|pdf|view|session|poster|oral|home|about)\b',
            r'^(figure|table|equation|fig|tab|eq)\s+\d+',
            r'^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'^(copyright|all rights reserved)\b',
            r'^(click|download|view|more)\b',
            r'^\d+\s*(of|/)\s*\d+',
        ]
        low = text.lower()
        if any(re.search(p, low) for p in invalid):
            return False
        positive = [
            'we', 'our', 'this', 'paper', 'propose', 'present', 'show', 'demonstrate',
            'method', 'approach', 'algorithm', 'model', 'framework', 'technique',
            'results', 'experiments', 'evaluation', 'performance', 'learning',
            'problem', 'solution', 'novel', 'new', 'introduce', 'develop'
        ]
        pos_count = sum(1 for p in positive if p in low)
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 10]
        if len(sentences) >= 2 and pos_count >= 3:
            return True
        starters = ['we propose', 'this paper', 'we present', 'we introduce',
                    'in this', 'we develop', 'we show', 'this work']
        return any(st in low for st in starters)

    def extract_url_for_title(self, content, title, venue, year, original_html=""):
        try:
            if original_html:
                url_patterns = [
                    r'href="([^"]+)"',
                    r'data-url="([^"]+)"',
                    r'data-href="([^"]+)"',
                    r'data-link="([^"]+)"',
                ]
                for pat in url_patterns:
                    for href in re.findall(pat, original_html, re.IGNORECASE):
                        if href and not href.startswith('#'):
                            full = self.process_relative_url(href, venue)
                            if full and self.is_paper_link(full):
                                return full

            title_trim = title.strip()
            if title_trim:
                safe = re.escape(title_trim[:80])
                link_pat = rf'<a[^>]*href="([^"]+)"[^>]*>[^<]*{safe}[^<]*</a>'
                m = re.search(link_pat, content, re.IGNORECASE | re.DOTALL)
                if m:
                    href = m.group(1)
                    full = self.process_relative_url(href, venue)
                    if full:
                        return full

            pos = content.lower().find(title.lower())
            if pos != -1:
                start = max(0, pos - 500)
                end = min(len(content), pos + len(title) + 500)
                ctx = content[start:end]
                for href in re.findall(r'href="([^"]+)"', ctx, re.IGNORECASE):
                    full = self.process_relative_url(href, venue)
                    if full and self.is_paper_link(full):
                        return full
            return ""
        except Exception as e:
            print(f"      Warning: URL extraction failed: {e}")
            return ""

    def extract_papers_from_content(self, content, venue, year, keywords):
        if not content:
            return []

        debug_file = os.path.join(self.output_dir, f"debug_{venue}_{year}.html")
        try:
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"    Debug file: {debug_file}")
        except Exception as e:
            print(f"    Warning: cannot write debug file: {e}")

        papers = []
        lines = content.split('\n')
        candidates = []
        for i, line in enumerate(lines):
            clean = re.sub(r'<[^>]+>', ' ', line)
            clean = html.unescape(clean).strip()
            if not clean:
                continue
            if self.contains_keywords(clean, keywords) and self.is_valid_title(clean):
                candidates.append((i, clean, line))

        if not candidates:
            print("    Fallback: HTML tag scanning")
            patterns = [
                r'<h[1-6][^>]*>(.*?)</h[1-6]>',
                r'<[^>]*class="[^"]*title[^"]*"[^>]*>(.*?)</[^>]*>',
                r'<a[^>]*href="[^"]*"[^>]*>(.*?)</a>',
                r'<strong[^>]*>(.*?)</strong>'
            ]
            for pat in patterns:
                for m in re.finditer(pat, content, re.IGNORECASE | re.DOTALL):
                    raw = m.group(0)
                    inner = html.unescape(re.sub(r'<[^>]+>', ' ', m.group(1))).strip()
                    if inner and self.contains_keywords(inner, keywords) and self.is_valid_title(inner):
                        line_num = content[:m.start()].count('\n')
                        candidates.append((line_num, inner, raw))

        print(f"    Candidates: {len(candidates)}")
        seen = set()
        for line_num, title, original_html in candidates:
            key = (title.lower().strip(), venue, year)
            if key in seen:
                continue
            seen.add(key)

            authors = self.extract_authors_for_title(content, title, line_num)
            abstract = self.extract_abstract_for_title(content, title, line_num)
            url = self.extract_url_for_title(content, title, venue, year, original_html)

            if not abstract and url:
                print("       No abstract on list page. Fetching from detail page ...")
                detail_abs = self.fetch_abstract_from_detail(url, venue=venue)
                if detail_abs:
                    abstract = detail_abs
                time.sleep(0.8)

            paper = {
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'venue': venue,
                'year': year,
                'url': url,
                'source': f'{venue} Official Website'
            }
            papers.append(paper)

            print(f"    OK: {title[:80]}{'...' if len(title) > 80 else ''}")
            print(f"       Authors: {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}" if authors else "       Authors: (not found)")
            print(f"       URL: {url}" if url else "       URL: (not found)")
            print(f"       Abstract: {(abstract[:80] + '...') if abstract and len(abstract) > 80 else (abstract or '(not found)')}")

        return papers

    # ---------- search ----------
    def search_single_conference(self, venue, year, keywords):
        results = []
        if venue not in self.conferences:
            print(f"  Error: unknown venue {venue}")
            return results

        conf = self.conferences[venue]
        if year not in conf.get('years', []):
            print(f"  Note: {venue} {year} may not be available (still trying).")

        print(f"  Searching {venue} {year} ...")
        if conf.get('search_url'):
            for kw in keywords:
                try:
                    url = conf['search_url'].format(year=year, keyword=quote(kw))
                    print(f"    Query: {kw} -> {url}")
                    html_text = self.get_webpage_content(url)
                    if html_text:
                        got = self.extract_papers_from_content(html_text, venue, year, [kw])
                        results.extend(got)
                    time.sleep(1.2)
                except Exception as e:
                    print(f"    Error: keyword search failed: {e}")

        if not results:
            try:
                url = conf['url'].format(year=year)
                print(f"    All-papers page: {url}")
                html_text = self.get_webpage_content(url)
                if html_text:
                    got = self.extract_papers_from_content(html_text, venue, year, keywords)
                    results.extend(got)
                time.sleep(1.2)
            except Exception as e:
                print(f"    Error: fetching all-papers page failed: {e}")

        print(f"    Found {len(results)} for {venue} {year}")
        return results

    def remove_duplicates(self, papers):
        seen, uniq = set(), []
        for p in papers:
            key = (p.get('title', '').strip().lower(), p.get('venue'), p.get('year'))
            if key not in seen:
                seen.add(key)
                uniq.append(p)
        return uniq

    def run_search(self, conferences, years, keywords):
        print("\n=== Run Search ===")
        print(f"Venues:   {', '.join(conferences)}")
        print(f"Years:    {', '.join(years)}")
        print(f"Keywords: {', '.join(keywords)}")
        print("=" * 60)

        all_papers = []
        for venue in conferences:
            for year in years:
                all_papers.extend(self.search_single_conference(venue, year, keywords))

        print(f"\nTotal found: {len(all_papers)}")
        unique_papers = self.remove_duplicates(all_papers)
        print(f"After dedup: {len(unique_papers)}")

        if unique_papers:
            self.pretty_print(unique_papers)
            self.generate_report(unique_papers, conferences, years, keywords)
        else:
            print("\nNo results.")
            print("Tips:")
            print("  1) Try broader keywords;")
            print("  2) Expand year range;")
            print("  3) Inspect output/debug_*.html to adapt patterns;")
            print("  4) Manually verify official pages.")
        return unique_papers

    def pretty_print(self, papers):
        print("\n=== Papers ===")
        for i, p in enumerate(papers, 1):
            print(f"\n  {i}. {p['title']}")
            print(f"     Venue: {p['venue']} {p['year']}")
            if p.get('authors'):
                a = ', '.join(p['authors'][:3])
                if len(p['authors']) > 3:
                    a += f" and {len(p['authors']) - 3} more"
                print(f"     Authors: {a}")
            if p.get('url'):
                print(f"     URL: {p['url']}")
            if p.get('abstract'):
                prev = p['abstract'] if len(p['abstract']) <= 100 else p['abstract'][:100] + "..."
                print(f"     Abstract: {prev}")

    # ---------- file naming ----------
    def _safe_token(self, s: str) -> str:
        s = s.strip().replace(' ', '_')
        s = re.sub(r'[,+/\\]+', '-', s)
        s = re.sub(r'[^A-Za-z0-9._\-]+', '_', s)
        s = re.sub(r'_+', '_', s).strip('_')
        return s or 'NA'

    def _build_basename_from_conditions(self, conferences, years, keywords) -> str:
        kw = '-'.join(self._safe_token(k) for k in keywords if k.strip()) or 'NA'
        ven = '-'.join(self._safe_token(v) for v in conferences if v.strip()) or 'NA'
        yrs = '-'.join(self._safe_token(y) for y in years if y.strip()) or 'NA'
        # Format: Keywords+Venues+Years
        base = f"{kw}+{ven}+{yrs}"
        # Add timestamp suffix to avoid accidental overwrite while keeping the requested pattern first
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base}__{ts}"

    # ---------- export ----------
    def generate_report(self, papers, conferences, years, keywords):
        basename = self._build_basename_from_conditions(conferences, years, keywords)
        md_file = os.path.join(self.output_dir, f"{basename}.md")
        json_file = os.path.join(self.output_dir, f"{basename}.json")

        venue_stats, year_stats = {}, {}
        for p in papers:
            v, y = p.get('venue'), p.get('year')
            venue_stats[v] = venue_stats.get(v, 0) + 1
            year_stats[y] = year_stats.get(y, 0) + 1

        lines = [
            "# Paper Search Report",
            "",
            f"**Generated at**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Venues**: {', '.join(conferences)}",
            f"**Years**: {', '.join(years)}",
            f"**Keywords**: {', '.join(keywords)}",
            f"**Total Papers**: {len(papers)}",
            "",
            "## Stats",
            "",
            "### By Venue",
            ""
        ]
        for v in sorted(venue_stats.keys()):
            lines.append(f"- **{v}**: {venue_stats[v]}")

        lines.extend(["", "### By Year", ""])
        for y in sorted(year_stats.keys(), reverse=True):
            lines.append(f"- **{y}**: {year_stats[y]}")

        lines.extend(["", "## Papers", ""])
        for v in sorted(venue_stats.keys()):
            group = [p for p in papers if p.get('venue') == v]
            if not group:
                continue
            lines.append(f"### {v} ({len(group)})")
            lines.append("")
            for i, p in enumerate(group, 1):
                lines.append(f"#### {i}. {p['title']}")
                lines.append("")
                lines.append(f"**Venue**: {p['venue']} {p['year']}")
                if p.get('authors'):
                    lines.append(f"**Authors**: {', '.join(p['authors'])}")
                if p.get('url'):
                    lines.append(f"**URL**: [{p['url']}]({p['url']})")
                if p.get('abstract'):
                    lines.append(f"**Abstract**: {p['abstract']}")
                lines.extend(["", "---", ""])

        try:
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "generated_at": datetime.now().isoformat(),
                    "conferences": conferences,
                    "years": years,
                    "keywords": keywords,
                    "total_papers": len(papers),
                    "venue_stats": venue_stats,
                    "year_stats": year_stats,
                    "papers": papers
                }, f, ensure_ascii=False, indent=2)
            print("\nReport saved:")
            print(f"  Markdown: {md_file}")
            print(f"  JSON:     {json_file}")
        except Exception as e:
            print(f"Error writing report: {e}")

    # ---------- debug ----------
    def analyze_debug_files(self):
        print("\nDebug file analyzer")
        print("=" * 40)
        files = []
        if os.path.exists(self.output_dir):
            for fn in os.listdir(self.output_dir):
                if fn.startswith("debug_") and fn.endswith(".html"):
                    files.append(os.path.join(self.output_dir, fn))
        if not files:
            print("No debug files found.")
            return
        print(f"Found {len(files)} debug files.")
        for fp in files:
            print(f"\n--- {os.path.basename(fp)} ---")
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"Size: {len(content)} chars")
                link_count = content.lower().count('href="')
                author_hits = sum(content.lower().count(tag) for tag in [
                    'class="author"', 'class="presenter"', 'class="name"', 'class="card-subtitle"', '"authors":', '"presenter":'
                ])
                abstract_hits = sum(content.lower().count(tag) for tag in [
                    'class="abstract"', 'class="summary"', 'class="description"', 'class="card-text"', '"abstract":', '"summary":'
                ])
                print(f"Links: {link_count}, author-tags: {author_hits}, abstract-tags: {abstract_hits}")
            except Exception as e:
                print(f"Analyze failed: {e}")


def parse_args():
    ap = argparse.ArgumentParser(description="Simple Paper Finder (detail-abstract enabled)")
    ap.add_argument("--confs", type=str, help="Venues, e.g., ICML,NeurIPS,ICLR")
    ap.add_argument("--years", type=str, help="Years, e.g., 2023,2024")
    ap.add_argument("--keywords", type=str, help="Keywords, e.g., unlearning,federated learning")
    ap.add_argument("--non-interactive", action="store_true", help="Non-interactive mode (requires all of confs/years/keywords)")
    ap.add_argument("--analyze-debug", action="store_true", help="Analyze output/debug_*.html")
    return ap.parse_args()


def main():
    scraper = SimpleConferenceScraper()
    args = parse_args()

    if args.analyze_debug:
        scraper.analyze_debug_files()
        return

    if args.non_interactive:
        if not (args.confs and args.years and args.keywords):
            print("Error: non-interactive mode requires --confs, --years, --keywords.")
            sys.exit(1)
        conferences = [c.strip() for c in args.confs.split(',') if c.strip()]
        years = [y.strip() for y in args.years.split(',') if y.strip()]
        keywords = [k.strip() for k in args.keywords.split(',') if k.strip()]

        print("\nSearch settings (non-interactive):")
        print(f"  Venues:   {', '.join(conferences)}")
        print(f"  Years:    {', '.join(years)}")
        print(f"  Keywords: {', '.join(keywords)}")

        papers = scraper.run_search(conferences, years, keywords)
        print(f"\nDone. Found {len(papers)} papers.")
        return

    try:
        conferences, years, keywords = scraper.get_user_selections()
        print("\nConfirm search:")
        print(f"  Venues:   {', '.join(conferences)}")
        print(f"  Years:    {', '.join(years)}")
        print(f"  Keywords: {', '.join(keywords)}")
        confirm = input("\nStart search? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return

        papers = scraper.run_search(conferences, years, keywords)
        print(f"\nDone. Found {len(papers)} papers.")

        if len(papers) == 0:
            analyze_choice = input("\nRun debug analyzer now? (y/n): ").strip().lower()
            if analyze_choice == 'y':
                scraper.analyze_debug_files()

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
