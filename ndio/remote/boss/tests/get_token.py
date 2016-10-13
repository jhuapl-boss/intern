#!/usr/bin/env python3

# Copyright 2016 The Johns Hopkins University Applied Physics Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A script for logging into Keycloak and getting a Bearer access token.

Because the token is backed by a Keycloak session it will expire after a short
period of time (the lifetime of the session before it expires).

The Keycloak address is discovered by looking in AWS, using the supplied AWS credentials.

The Keycloak token is save to a file called "keycloak.token" in the current directory.

Environmental Variables:
    AWS_CREDENTIALS : File path to a JSON encode file containing the following keys
                      "aws_access_key" and "aws_secret_key"

Author:
    Derek Pryor <Derek.Pryor@jhuapl.edu>
"""

import argparse
import os
import sys
import getpass
import json
import ssl
from boto3.session import Session

from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError

def elb_public_lookup(session, hostname):
    """Lookup the public DNS name for an ELB based on the BOSS hostname.

    Args:
        session (Session) : Active Boto3 session used to lookup ELB
        hostname (string) : Hostname of the desired ELB

    Returns:
        (None|string) : None if the ELB is not located or the public DNS name
    """
    if session is None: return None

    client = session.client('elb')
    responses = client.describe_load_balancers()

    hostname_ = hostname.replace(".", "-")

    for response in responses["LoadBalancerDescriptions"]:
        if response["LoadBalancerName"].startswith(hostname_):
            return response["DNSName"]
    return None

def create_session(cred_fh):
    """Read AWS credentials from the given file object and create a Boto3 session.

        Note: Currently is hardcoded to connect to Region US-East-1

    Args:
        cred_fh (file) : File object of a JSON formated data with the following keys
                         "aws_access_key" and "aws_secret_key"

    Returns:
        (Session) : Boto3 session
    """
    credentials = json.load(cred_fh)

    session = Session(aws_access_key_id = credentials["aws_access_key"],
                      aws_secret_access_key = credentials["aws_secret_key"],
                      region_name = 'us-east-1')
    return session

def request(url, params = None, headers = {}, method = None, convert = urlencode):
    """Make an HTTP(S) query and return the results.

        Note: If the url starts with "https" SSL hostname and cert checking is disabled

    Args:
        url (string) : URL to query
        params : None or an object that will be passed to the convert argument
                 to produce a string
        headers (dict) : Dictionary of HTTP headers
        method (None|string) : HTTP method to use or None for the default method
                               based on the different arguments
        convert : Function to convert params into a string
                  Defaults to urlencode, taking a dict and making a url encoded string

    Returns:
        (string) : Data returned from the request. If an error occured, the error
                   is printed and any data returned by the server is returned.
    """
    rq = Request(
        url,
        data = None if params is None else convert(params).encode("utf-8"),
        headers = headers,
        method = method
    )

    if url.startswith("https"):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        ctx = None

    try:
        response = urlopen(rq, context=ctx).read().decode("utf-8")
        return response
    except HTTPError as e:
        print(e)
        return e.read().decode("utf-8")

if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    parser = argparse.ArgumentParser(description = "Script to get a KeyCloak Bearer Token",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--aws-credentials", "-a",
                        metavar = "<file>",
                        default = os.environ.get("AWS_CREDENTIALS"),
                        type = argparse.FileType('r'),
                        help = "File with credentials to use when connecting to AWS (default: AWS_CREDENTIALS)")
    parser.add_argument("--username", default = None, help = "KeyCloak Username")
    parser.add_argument("--password", default = None, help = "KeyCloak Password")
    parser.add_argument("domain_name", help="Domain in which to execute the configuration (example: integration.boss or auth.integration.theboss.io)")

    args = parser.parse_args()

    if args.aws_credentials is None:
        parser.print_usage()
        print("Error: AWS credentials not provided and AWS_CREDENTIALS is not defined")
        sys.exit(1)

    if args.username is None:
        username = input("Username: ")
    else:
        username = args.username

    if args.password is None:
        password = getpass.getpass()
    else:
        password = args.password

    session = create_session(args.aws_credentials)
    if args.domain_name.endswith(".boss"):
        hostname = elb_public_lookup(session, "auth." + args.domain_name)
    else:
        hostname = args.domain_name

    url = "https://" + hostname + "/auth/realms/BOSS/protocol/openid-connect/token"
    print(url)
    params = {
        "grant_type": "password",
        "client_id": "endpoint",
        "username": username,
        "password": password,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = request(url, params, headers)
    response = json.loads(response)
    print("Response:")
    for key in response:
        val = response[key]
        if type(val) == type(""):
            val = val[:15] + "..."
        print("\t{} -> {}".format(key, val))
    print()

    if "access_token" not in response:
        print("Didn't get a token, exiting...")
        sys.exit(1)

    token = response["access_token"]
    with open("keycloak.token", "w") as fh:
        fh.write(token)
        print("Token writen to keycloak.token")