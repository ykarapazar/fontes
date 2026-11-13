from world_legal_mcp.jurisdictions import tj


def test_decision_date_is_signing_line_not_charter_date():
    text = ("по делу ... утвержденного распоряжением Министерства от 13 февраля 2013 года, № 32\n\n"
            "г. Душанбе 26 сентября 2016 года\n\nКонституционный суд")
    assert tj._text_date(text) == "2016-09-26"


def test_decision_date_fallback_first_date():
    assert tj._text_date("«4» февраля 2016 года") == "2016-02-04"


def test_markdown_headed_articles_are_toc_parts():
    lines = ["#### ГЛАВА 1. ЗАДАЧИ", "### Статья 1. Уголовный закон", "1) текст",
             "###### Статья 11(1). Правила толкования", "текст", "###### Статья 12. Время"]
    parts = tj._parts(lines)
    labels = [p["label"] for p in parts if p["label"]]
    assert labels == ["Статья 1", "Статья 11(1)", "Статья 12"]
    assert tj._find(parts, "Статья 1")["title"] == "Статья 1. Уголовный закон"
    assert tj._find(parts, "Статья 11(1)")["label"] == "Статья 11(1)"
    assert tj._find(parts, "12")["label"] == "Статья 12"
