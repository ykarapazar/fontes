"""The bundled intermediates (loaded on Linux by _http) parse, are CAs and are not expired."""
import datetime
import ssl

from cryptography import x509

from world_legal_mcp import _http


def test_intermediates_are_valid_cas():
    pem = open(_http.INTERMEDIATES, "rb").read()
    certs = x509.load_pem_x509_certificates(pem)
    assert certs
    now = datetime.datetime.now(datetime.UTC)
    for c in certs:
        assert c.extensions.get_extension_for_class(x509.BasicConstraints).value.ca
        assert c.not_valid_after_utc > now + datetime.timedelta(days=60), c.subject
        assert c.subject != c.issuer   # an intermediate, never a self-signed root
    ssl.create_default_context().load_verify_locations(_http.INTERMEDIATES)
