import argparse
import getpass
import logging
import os
import re
from urllib.parse import urlparse

import requests
from requests.auth import AuthBase, HTTPBasicAuth

from .krtc import KerberosTicket

logger = logging.getLogger(__name__)


class CompositeAuth(AuthBase):
    """
    Examine the environment and try to use the 'best' possible authentication
    scheme when talking to the LCLS logbook.
    1. Check to see if we are running in the context of an ARP job
    and have a bearer token; if so, use that.
    2. See if we have a Kerberos token and if so, use that.
    Note, we do not validate if the token is valid;
    we just check for presence/absence.
    3. If an operator userid and password are specified; use that.
    4. Finally, if none of these are specified; try to make the call as is.
    Usage:
    r = requests.post(
        ws_url,
        params={"run_num": run},
        json=runtable_data,
        auth=CompositeAuth(operatorid=experiment[:3]+'opr',
        password=answer[:-1]))
    You can use any variant of the
    https://psww.../<ws/ws-auth/ws-kerb/ws-jwt>/lgbk URL
    and the URL will be adjusted according
    to the auth scheme that is finally used.
    """
    def __init__(self, operatorid=None, password=None):
        self.operatorid = operatorid
        self.password = password

    def __call__(self, r):
        uu = "^https://pswww.slac.stanford.edu/ws[^/]*/lgbk/(.*)$"
        theregex = re.compile(uu)
        if not theregex.match(r.url):
            raise Exception("For now, this only applies to eLog URL's")
        # 1. Check to see if we are running in the context of an ARP job
        # and have a bearer token; if so, use that.
        if "Authorization" in os.environ and "Bearer " in os.environ["Authorization"]:
            r.url = "https://pswww.slac.stanford.edu/ws-jwt/lgbk/" \
                + theregex.match(r.url)[1]
            logger.debug(
                "Inside an ARP job, using the JWT endpoint %s",
                r.url)
            r.headers["Authorization"] = os.environ["Authorization"]
            return r
        # See if we have a Kerberos token and if so, use that.
        # Note, we do not validate if the token is valid;
        # we just check for presence/absence.
        # Also skip if we logged in as an operator
        loggedinuser = getpass.getuser()
        amoperator = len(loggedinuser) == 6 and loggedinuser.endswith("opr")
        if not amoperator \
            and "KRB5CCNAME" in os.environ \
                and os.path.exists(urlparse(os.environ["KRB5CCNAME"]).path):
            r.url = "https://pswww.slac.stanford.edu/ws-kerb/lgbk/" \
                + theregex.match(r.url)[1]
            logger.debug(
                "Found a Kerberos ticket;"
                "using the kerberos endpoint %s",
                r.url)
            krbheaders = KerberosTicket(
                "HTTP@" + urlparse(r.url).hostname).getAuthHeaders()
            r.headers.update(krbheaders)
            return r
        # If an operator userid and password are specified; use that.
        if self.operatorid and self.password:
            r.url = "https://pswww.slac.stanford.edu/ws-auth/lgbk/" \
                + theregex.match(r.url)[1]
            logger.debug(
                "Using the operator id %s with the url %s",
                self.operatorid, r.url)
            basic = HTTPBasicAuth(self.operatorid, self.password)
            return basic.__call__(r)

        logger.debug("No authentication found; invoking as is %s", r.url)
        return r


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose",
        action='store_true', help="Turn on verbose logging")
    parser.add_argument(
        "-u", "--userid",
        action='store', help="Optional operator id")
    parser.add_argument(
        "-p", "--password",
        action='store', help="Optional operator password")
    parser.add_argument("url", help="A eLog URL to test")

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if args.userid and args.password:
        theauth = CompositeAuth(
            operatorid=args.userid,
            password=args.password
        )
    else:
        theauth = CompositeAuth()

    resp = requests.get(
        args.url,
        auth=theauth
    )
    resp.raise_for_status()
    print(resp.json())
