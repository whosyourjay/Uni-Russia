#!/usr/bin/env python3
"""Download the public СПО monitoring records for each institution.

The 2023 edition is the latest one whose institution pages publish separate
budget and paid certificate-grade averages.  Pages are compressed locally:
the site emits a large amount of presentation markup around a small table.
"""

import concurrent.futures
import gzip
import os
import re
import sys
import time

from lib import html, net
from lib.paths import source_path

DEFAULT_YEAR = 2023
BASE = "https://monitoring.miccedu.ru"
INDEX = (BASE + "/iam/set_SearchVuzList.php?m=spo&year={year}"
         "&search_text=%D0%B0")
LINK = re.compile(r"iam/(?P<year>\d{4})/_spo/inst\.php\?id=(?P<id>\d+)")


def index_path(year):
    return source_path("spo", str(year), "index.html")


def page_path(year, institution_id):
    return source_path("spo", str(year), f"{institution_id}.html.gz")


def institutions(page, year):
    """Unique ``(id, name)`` pairs from the monitoring's search result."""
    found = {}
    for href, name in html.links(page):
        match = LINK.search(href)
        if match and int(match.group("year")) == year:
            found.setdefault(match.group("id"), name)
    return sorted(found.items(), key=lambda pair: int(pair[0]))


def _download_page(year, institution_id, force=False):
    target = page_path(year, institution_id)
    if os.path.exists(target) and not force:
        return False
    url = f"{BASE}/iam/{year}/_spo/inst.php?id={institution_id}"
    for attempt in range(3):
        try:
            body = net.get(url, timeout=90)
            if b"inst_name" not in body:
                raise ValueError(f"not an institution page: {url}")
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with gzip.open(target, "wb", compresslevel=6) as output:
                output.write(body)
            return True
        except Exception as error:
            if getattr(error, "code", None) in (429, 468):
                raise
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def main(year=DEFAULT_YEAR, force=False, index_only=False, workers=6, limit=None):
    target = index_path(year)
    net.download(INDEX.format(year=year), target, force=force)
    schools = institutions(net.text(target), year)
    if index_only:
        print(f"indexed {len(schools):,} СПО institutions for {year}")
        return
    missing = [(school_id, name) for school_id, name in schools
               if force or not os.path.exists(page_path(year, school_id))]
    retained = len(schools) - len(missing)
    pending = missing
    if limit is not None:
        pending = pending[:limit]
    print(f"indexed {len(schools):,}; retained {retained:,}; "
          f"missing {len(missing):,}; downloading {len(pending):,}", flush=True)
    fetched = 0
    failures = []
    throttled = None
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        jobs = {pool.submit(_download_page, year, school_id, force): school_id
                for school_id, _ in pending}
        for number, job in enumerate(concurrent.futures.as_completed(jobs), 1):
            try:
                fetched += bool(job.result())
            except Exception as error:
                failures.append((jobs[job], str(error)))
                if getattr(error, "code", None) in (429, 468):
                    throttled = error
                    for pending_job in jobs:
                        pending_job.cancel()
                    break
            if number % 250 == 0:
                print(f"finished {number:,}/{len(jobs):,} downloads",
                      flush=True)
    print(f"downloaded {fetched:,}; retained {retained:,}; "
          f"failed {len(failures):,}")
    if throttled:
        raise RuntimeError(f"server rate limited the download: {throttled}")
    if failures:
        sample = "; ".join(f"{school_id}: {error}"
                           for school_id, error in failures[:3])
        raise RuntimeError(f"failed to download {len(failures):,} pages: {sample}")


if __name__ == "__main__":
    args = sys.argv[1:]
    selected = next((int(arg) for arg in args if arg.isdigit()), DEFAULT_YEAR)
    workers = next((int(arg.split("=", 1)[1]) for arg in args
                    if arg.startswith("--workers=")), 6)
    limit = next((int(arg.split("=", 1)[1]) for arg in args
                  if arg.startswith("--limit=")), None)
    main(selected, force="--force" in args,
         index_only="--index-only" in args, workers=workers, limit=limit)
