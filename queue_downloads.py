#!/usr/bin/env python3
 
import argparse
from datetime import datetime
from getpass import getpass
import json
from time import sleep
import requests


def login(base_url: str, authenticator: str, username: str, password: str) -> str:
    """
    Args:
        base_url (str): URL for DataGateway without path.
        authenticator (str): Authentication mechanism to use.
        username (str): Username to use.
        password (str): Password to use.

    Raises:
        RuntimeError: If a status code other than 200 is returned.

    Returns:
        str: ICAT session id.
    """
    url = f"{base_url}/topcat/user/session"
    data = {"plugin": authenticator, "username": username, "password": password}
    response = requests.post(url=url, data=data)
    if response.status_code != 200:
        raise RuntimeError(response.text)

    return json.loads(response.content)["sessionId"]


def queue_all_files(
    base_url: str,
    session_id: str,
    input_file: str,
    transport: str,
    file_name: str,
    email: str,
) -> "list[int]":
    """Reads from `file_name` and submits Downloads for every 10,000 listed files.

    Args:
        base_url (str): URL for DataGateway without path.
        session_id (str): ICAT session id.
        input_file (str):
            File containing newline delimited filepaths for the requested data.
        transport (str): Transport mechanism/destination to use.
        file_name (str): Name used for the Download request (without '_part_N').
        email (str): Optional email to send notifications to.

    Returns:
        list[int]: List of download ids for each part.
    """
    i = 1
    files = []
    download_ids = []
    base_file_name = file_name or datetime.now().isoformat()[:19]
    with open(input_file) as f:
        line = f.readline()
        while line:
            files.append(line.strip())
            line = f.readline()
            if len(files) >= 10000:
                download_id = queue_files(
                    base_url=base_url,
                    session_id=session_id,
                    files=files,
                    transport=transport,
                    file_name=f"{base_file_name}_part_{i}",
                    email=email,
                )
                download_ids.append(download_id)
                i += 1
                files = []
    
    if files:
        download_id = queue_files(
            base_url=base_url,
            session_id=session_id,
            files=files,
            transport=transport,
            file_name=f"{base_file_name}_part_{i}",
            email=email,
        )
        download_ids.append(download_id)

    return download_ids


def queue_files(
    base_url: str,
    session_id: str,
    files: "list[int]",
    transport: str,
    file_name: str,
    email: str,
) -> int:
    """
    Submits a part Download of up to 10,000 files, if any filepaths are not found,
    these will be printed to the console.

    Args:
        base_url (str): URL for DataGateway without path.
        session_id (str): ICAT session id.
        files (list[int]): List of up to 10,000 of the requested filepaths.
        transport (str): Transport mechanism/destination to use.
        file_name (str): Name used for the Download request (with '_part_N').
        email (str): Optional email to send notifications to.

        input_file (str):
            File containing newline delimited filepaths for the requested data.

    Raises:
        RuntimeError: If a status code other than 200 is returned.

    Returns:
        int: The Download id.
    """
    data = {
        "sessionId": session_id,
        "transport": transport,
        "fileName": file_name,
        "email": email,
        "files": files,
    }
    response = requests.post(url=base_url + "/topcat/user/queue/files", data=data)
    if response.status_code != 200:
        raise RuntimeError(response.text)

    content = json.loads(response.content)
    download_id = content["downloadId"]
    not_found = content["notFound"]
    print(
        f"Submitted part Download with id {download_id}\n"
        f"{len(not_found)} file(s) could not be found:{not_found}\n"
    )
    return download_id


def monitor(
    base_url: str,
    session_id: str,
    downloads: "list[int]",
    monitor_sleep: int,
) -> None:
    """
    Checks the status of all `downloads` and prints this to the console. Will repeat
    evert `monitor_sleep` seconds until all are complete.

    Args:
        session_id (str): ICAT session id.
        downloads (list[int]): List of download ids for each part.
        monitor_sleep (int): Number of seconds to wait between each check.

    Raises:
        RuntimeError: If a status code other than 200 is returned.
    """
    url = base_url + "/topcat/user/downloads/status"
    params = {"sessionId": session_id, "downloadIds": downloads}
    response = requests.get(url=url, params=params)
    if response.status_code != 200:
        raise RuntimeError(response.text)
    content = json.loads(response.content)
    print(content)

    while any([s in {"QUEUED", "PAUSED", "PREPARING", "RESTORING"} for s in content]):
        headers = {"Authorization": f"Bearer {session_id}"}
        requests.put(url=base_url + "/datagateway-api/sessions", headers=headers)
        if response.status_code != 200:
            raise RuntimeError(response.text)

        sleep(monitor_sleep)
        response = requests.get(url=url, params=params)
        if response.status_code != 200:
            raise RuntimeError(response.text)

        content = json.loads(response.content)
        print(content)
    
    print("All downloads complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="queue_downloads",
        description=(
            "Submits DataGateway Download requests for a list of specific filepaths. "
            "The list will be split into separate parts of up to 10,000 files for "
            "performance reasons. Once submitted Downloads will be visible in the "
            "DataGateway UI as usual."
        ),
    )
    parser.add_argument(
        "input_file",
        type=str,
        help=(
            "File containing the full paths of all files to submit for download, "
            "separated by newlines. The path should match the 'location' field "
            "displayed in the DataGateway UI."
        ),
    )
    parser.add_argument(
        "--url",
        type=str,
        default="https://datagateway.diamond.ac.uk",
        help="The url address of the DataGateway instance to submit requests to.",
    )
    parser.add_argument(
        "-a",
        "--authenticator",
        type=str,
        default="ldap",
        help="The authentication mechanism to use for DataGateway login.",
    )
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        required=True,
        help="The username used for DataGateway login.",
    )
    parser.add_argument(
        "-p",
        "--password-file",
        type=str,
        help=(
            "Location of file containing password for DataGateway login. If not "
            "provided, the password will need to be provided by prompt."
        ),
    )
    parser.add_argument(
        "--download-name",
        type=str,
        help=(
            "Custom file name for the download(s). If not set will default to the "
            "current date and time. '_part_N' will be appended to the each part "
            "Download of up to 10,000 files."
        ),
    )
    parser.add_argument(
        "--access-method",
        type=str,
        default="dls",
        choices=["https", "globus", "dls"],
        help=(
            "The choice of access method for the data. https: download files via your "
            "browser. globus: download the data to Globus Online. dls: restore to the "
            "DLS file system. Data will be available in one of the following directory "
            "structures: /dls/staging/dls/$instrument/data/$year/$visit or "
            "/dls/staging/dls/$village/data/$proposal/$visit. Users will have 15 days "
            "to process and transfer their data. After that period, data will be "
            "deleted from DLS filesystem."
        ),
    )
    parser.add_argument(
        "--email-address",
        type=str,
        help="Optional address to email status messages to.",
    )
    parser.add_argument(
        "-m",
        "--monitor-interval",
        type=float,
        default=0,
        help=(
            "Monitor the submitted downloads to see if they are complete with an "
            "interval of this many seconds. Non-positive values will disable "
            "monitoring."
        ),
    )
    args = parser.parse_args()

    if args.password_file is None:
        password = getpass()
    else:
        with open(args.password_file) as f:
            password = f.readline().strip()

    session_id = login(
        base_url=args.url,
        authenticator=args.authenticator,
        username=args.username,
        password=password,
    )
    download_ids = queue_all_files(
        base_url=args.url,
        session_id=session_id,
        input_file=args.input_file,
        transport=args.access_method,
        file_name=args.download_name,
        email=args.email_address,
    )
    if args.monitor_interval > 0:
        monitor(
            base_url=args.url,
            session_id=session_id,
            downloads=download_ids,
            monitor_sleep=args.monitor_interval,
        )
