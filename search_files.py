#!/usr/bin/env python3
 
import argparse
import json
import requests
from typing import Tuple
from urllib.parse import quote

from common import VERIFY, add_common_args, get_password, login


def search_all_files(
    base_url: str,
    session_id: str,
    output_file: str,
    query: str,
    max_results: int,
) -> None:
    """Performs several individual searches to get all results matching `query`.

    Args:
        base_url (str): URL for DataGateway without path.
        session_id (str): ICAT session id.
        output_file (str): File to write founds filepaths to.
        query (str): String in Lucene query syntax.
        max_results (int): The number of results to request in each batch.
    """
    url = f"{base_url}/topcat/user/search/files"
    params = {"sessionId": session_id}
    if max_results is not None:
        params["maxResults"] = max_results

    data = {"query": query}
    batches = 1
    total, search_after = search_files(url, params, data, output_file)
    while search_after is not None:
        data["searchAfter"] = quote(json.dumps(search_after))
        count, search_after = search_files(url, params, data, output_file)
        batches += 1
        total += count

    print(f"{total} file(s) found in {batches} batches")


def search_files(
    url: str,
    params: dict,
    data: dict,
    output_file: str,
) -> "Tuple[int, dict]":
    """Perform a single search, possibly continuing to paginate after a previous search.

    Args:
        url (str): URL with path.
        params (dict): Query parameters.
        data (dict): Request body.
        output_file (str): File to write founds filepaths to.

    Raises:
        RuntimeError: `if response.status_code != 200` 

    Returns:
        Tuple[int, dict]: Number of results, search_after object.
    """
    response = requests.post(url=url, data=data, params=params, verify=VERIFY)
    if response.status_code != 200:
        raise RuntimeError(response.text)

    content = json.loads(response.content)
    results = content["results"]
    with open(output_file, "a") as f:
        for result in results:
            f.write(f"{result['_source']['location']}\n")

    count = len(results)
    print(f"{count} file(s) found")
    if "search_after" in content:
        return count, content["search_after"]
    else:
        return count, None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="search_files",
        description=(
            "Performs DataGateway searches for Datafiles matching the provided query."
            " These paths will be written to file in\nbatches, and can then be "
            "inspected and filtered further if needed before submitting using "
            "queue_file_downloads."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "output_file",
        type=str,
        help=(
            "File to append newline separated paths to.\n"
            "This can then be provided as an input to queue_file_downloads."
        ),
    )
    parser.add_argument(
        "query",
        type=str,
        help=
"""Lucene syntax formatted search query. Full help text and examples can be found
in the DataGateway UI. Note that wildcards can significantly increase the time
taken to perform a search, and the more specific the search query is the more
efficient it will be. Some example searches are:
    'visitId:AB1234'
        Search for all Datafiles in all parts of proposal
    'visitId:\"AB1234-1\"'
        Search for all Datafiles in a (part) visit
    'location.fileName:txt'
        Search for Datafiles with the extension 'txt'
    'location:raw'
        Search for Datafiles with the directory 'raw' somewhere in their path
    'location:(raw processed)'
        Search for Datafiles with either of two directories somewhere in their path
    'location.exact:/dls/i0/data/2000'
        Search for Datafiles in any subdirectory of the provided path (case sensitive)
    'location.exact:/dls/i0/data/202?/*/raw/config.txt'
        Search for a full path with wildcards (case sensitive)
    '+location.exact:/dls/i0/data/202? +location:(raw processed) +location.fileName:txt'
        Search for multiple criteria (all of which are required to match)"""
    )
    add_common_args(parser)
    parser.add_argument(
        "-m",
        "--max-results",
        type=int,
        help=(
            "The maximum number of results to request in a single batch. If unset, the "
            "server default value will be used."
        ),
    )
    args = parser.parse_args()

    password = get_password(args.password_file)
    session_id = login(
        base_url=args.url,
        authenticator=args.authenticator,
        username=args.username,
        password=password,
    )
    search_all_files(
        base_url=args.url,
        session_id=session_id,
        output_file=args.output_file,
        query=args.query,
        max_results=args.max_results,
    )
