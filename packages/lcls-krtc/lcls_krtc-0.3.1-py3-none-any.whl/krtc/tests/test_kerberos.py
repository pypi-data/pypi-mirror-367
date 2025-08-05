import kerberos
import pytest

from ..krtc import KerberosTicket


def test_instantiate():
    with pytest.raises(kerberos.GSSError):
        KerberosTicket("HTTP@example.com")
