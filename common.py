from argparse import ArgumentParser
from getpass import getpass
import json
from urllib.parse import quote

import requests


VERIFY = True  # If False then ssl certs won't be checked, useful for development


def add_common_args(parser: ArgumentParser) -> None:
    """
    Add the common arguments url, authenticator, username and password-file to `parser`.

    Args:
        parser (ArgumentParser): ArgumentParser for the program.
    """
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


def get_password(password_file: "str | None") -> str:
    """
    Load the user's password from `password_file` if provided, otherwise prompt for it.

    Args:
        password_file (str): Optional path of file containing the user's password.

    Returns:
        str: The user's password
    """
    if password_file is None:
        return getpass()
    else:
        with open(password_file) as f:
            return f.readline().strip()


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
    encoded_password = quote(json.dumps(password)[1:-1])
    data = {"plugin": authenticator, "username": username, "password": encoded_password}
    response = requests.post(url=url, data=data, verify=VERIFY)
    if response.status_code != 200:
        raise RuntimeError(response.text)

    return json.loads(response.content)["sessionId"]
