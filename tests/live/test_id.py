"""Live smoke tests against JDIH Setneg (jdih.setneg.go.id). Needs network."""
from world_legal_mcp import server


async def test_id_search_filters():
    out = await server.search_legislation("id", "", limit=3, filters={"type": "PP", "year": "2021"})
    assert "Peraturan Pemerintah Nomor" in out and "Tahun 2021" in out and '"PP ' in out, out
    out = await server.search_legislation("id", "27 tahun 2022", limit=5)
    assert 'get_legislation_toc("id", "UU 27/2022")' in out, out
    assert "Bad request" in await server.search_legislation("id", "x", filters={"type": "XYZ"})
    assert "Bad request" in await server.search_legislation("id", "x", filters={"year": "22"})


async def test_id_id_variants_and_provision_labels():
    for law in ("Undang-Undang Nomor 27 Tahun 2022", "UU No. 27 Tahun 2022",
                "https://jdih.setneg.go.id/detailperaturan?jns=UU&no=27&thn=2022"):
        out = await server.get_legislation_provision("id", law, "Pasal 4")
        assert "- Law: UU 27/2022" in out and "**Pasal 4**" in out and "Data Pribadi" in out, out
    out = await server.get_legislation_provision("id", "UU 27/2022", "1")   # OCR'd "Pasal I" in the PDF
    assert "**Pasal 1**" in out and "Data Pribadi adalah" in out, out
    out = await server.get_legislation_provision("id", "UU 27/2022", "Penjelasan")
    assert "Cukup jelas" in out, out


async def test_id_errors():
    assert "Not found" in await server.get_legislation_toc("id", "UU 9999/2022")
    assert "UU 27/2022" in await server.get_legislation_toc("id", "Pasal 5")   # bad id -> format hint
    assert "Not found" in await server.get_legislation_provision("id", "UU 27/2022", "999")


async def test_id_constitution_from_mpr():
    out = await server.search_legislation("id", "", limit=5, filters={"type": "UUD"})
    assert 'get_legislation_toc("id", "UUD 1945")' in out, out
    toc = await server.get_legislation_toc("id", "Undang-Undang Dasar 1945")
    for lab in ('"28I"', '"22B"', '"Peralihan I"', '"Tambahan II"', '"Pembukaan"'):
        assert lab in toc, lab
    out = await server.get_legislation_provision("id", "UUD 1945", "Pasal 28I")
    assert "(2) Setiap orang berhak bebas dari perlakuan" in out and "2002-08-10" in out, out
