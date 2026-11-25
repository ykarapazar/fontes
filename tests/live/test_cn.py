"""Live smoke tests against court.gov.cn (SPC guiding cases). Needs network.
The first search reads the whole guiding-case list (~15 pages at 1 s spacing)."""
import re

from world_legal_mcp import server


async def test_cn_search_by_title_words_and_number():
    out = await server.search_caselaw("cn", "个人信息 纠纷", limit=5)
    assert "指导性案例266号" in out
    one = await server.search_caselaw("cn", "指导案例1号", limit=5)
    assert "居间合同纠纷案" in one and "指导性案例1号" in one
    assert len(re.findall(r"^### \d", one, re.M)) == 1, one


async def test_cn_decision_id_variants():
    for did in ("474491", "指导性案例266号", "GC266",
                "https://www.court.gov.cn/fabu/xiangqing/474491.html"):
        out = await server.get_decision("cn", did, max_chars=4000)
        assert "黄某欢诉某信用管理有限公司个人信息保护纠纷案" in out, did
        assert "## Summary" in out and "先享后付" in out, did


async def test_cn_bad_and_missing_ids():
    bad = await server.get_decision("cn", "not-an-id")
    assert "Bad request" in bad and "not-an-id" in bad, bad
    missing = await server.get_decision("cn", "1")
    assert "Not found" in missing
