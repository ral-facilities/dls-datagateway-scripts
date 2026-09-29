#!/usr/bin/env python3
 
import argparse
import json
import requests

from common import VERIFY, add_common_args, get_password, login


def get_size_all_files(base_url: str, session_id: str, input_file: str) -> None:
    """Reads from `input_file` and gets the total volume of all listed files.

    Args:
        base_url (str): URL for DataGateway without path.
        session_id (str): ICAT session id.
        input_file (str):
            File containing newline delimited filepaths for the requested data.
    """
    files = []
    total_count = 0
    total_size = 0
    not_found = []
    with open(input_file) as f:
        line = f.readline()
        while line:
            files.append(line.strip())
            line = f.readline()
            if len(files) >= 10000:
                response = get_size_files(
                    base_url=base_url,
                    session_id=session_id,
                    files=files,
                )
                total_count += response["totalCount"]
                total_size += response["totalSize"]
                not_found.extend(response["notFound"])
                files = []

    if files:
        response = get_size_files(
            base_url=base_url,
            session_id=session_id,
            files=files,
        )
        total_count += response["totalCount"]
        total_size += response["totalSize"]
        not_found.extend(response["notFound"])
        files = []

    size_gb = round(total_size / 1e9)
    print(
        f"{total_count} file(s) with volume {size_gb}GB found\n"
        f"{len(not_found)} file(s) could not be found:{not_found}\n"
    )


def get_size_files(
    base_url: str, session_id: str, files: "list[str]",
) -> "dict[str, int | list[str]]":
    """
    Get the total volume of `files`.

    Args:
        base_url (str): URL for DataGateway without path.
        session_id (str): ICAT session id.
        files (list[str]): List of up to 10,000 of the requested filepaths.

    Raises:
        RuntimeError: If a status code other than 200 is returned.

    Returns:
        dict[str, int | list[str]]:
            Response body with the count, size, and missing locations.
    """
    url = f"{base_url}/topcat/user/getSize/files"
    data = {"sessionId": session_id, "files": files}
    response = requests.post(url=url, data=data, verify=VERIFY)
    if response.status_code != 200:
        raise RuntimeError(response.text)

    return json.loads(response.content)


def get_size_visit(base_url: str, session_id: str, visit_id: str) -> None:
    """
    Get the total volume of all Datafiles within a visit.

    Args:
        base_url (str): URL for DataGateway without path.
        session_id (str): ICAT session id.
        visit_id (str): Visit id in the form AB1234-1.

    Raises:
        RuntimeError: If a status code other than 200 is returned.
    """
    url = f"{base_url}/topcat/user/getSize/visit"
    data = {"sessionId": session_id, "visitId": visit_id}
    response = requests.post(url=url, data=data, verify=VERIFY)
    if response.status_code != 200:
        raise RuntimeError(response.text)

    content = json.loads(response.content)
    size_gb = round(content["totalSize"] / 1e9)
    print(f"{content['totalCount']} file(s) with volume {size_gb}GB found\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="get_size",
        description=(
            "Queries DataGateway Download API for the volume of all Datafiles within a "
            "visit or a list of specific filepaths."
        ),
    )
    subparsers = parser.add_subparsers(help="Target for query.")
    visit_parser = subparsers.add_parser(name="visit")
    visit_parser.add_argument(
        "visit_id", type=str, help="Visit id in the form AB1234-1."
    )
    files_parser = subparsers.add_parser(name="files")
    files_parser.add_argument(
        "input_file",
        type=str,
        help=(
            "File containing the full paths of all files to query for size, "
            "separated by newlines. The path should match the 'location' field "
            "displayed in the DataGateway UI."
        ),
    )
    add_common_args(parser)
    args = parser.parse_args()

    password = get_password(args.password_file)
    session_id = login(
        base_url=args.url,
        authenticator=args.authenticator,
        username=args.username,
        password=password,
    )
    if "input_file" in args:
        get_size_all_files(
            base_url=args.url,
            session_id=session_id,
            input_file=args.input_file,
        )
    else:
        get_size_visit(
            base_url=args.url,
            session_id=session_id,
            visit_id=args.visit_id,
        )
