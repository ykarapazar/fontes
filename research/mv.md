# Maldives (mv) — source notes, checked 2026-11-06

## Used: MvLaw — https://mvlaw.gov.mv (Attorney General's Office)
- robots.txt: `User-agent: *` / `Disallow:` (all allowed, no Crawl-delay).
- No terms of use page (`/dv/terms-of-use` is 404); footer "Copy Right 2023 © Atourney generals office".
  The About page (`/dv/mi-vebsaitaagulhey-mauloomaathu`) sets no usage conditions.
- Laravel + Inertia: page JSON is in `<div id="app" data-page="...">`. `/api/v1` needs OAuth (not used).
- Dhivehi only. About 261 instruments (Constitution + historical constitutions, Acts, regulations, other).
- Word search returns the top 10 only; `page` is ignored by the source.

## Not usable (case law)
- judiciary.gov.mv -> dja.gov.mv: Cloudflare "Just a moment" challenge (403).
- highcourt.gov.mv: Cloudflare "Sorry, you have been blocked" (403).
- old.supremecourt.mv: Cloudflare challenge (403). Every Supreme Court judgment PDF is hosted here.
- supremecourt.mv: robots allows public pages; `/case-registry/judgments/{uuid}` gives metadata only
  (citation such as "[2026] SC 41", case no., date, bench) and links the PDF on old.supremecourt.mv.
  Data comes from a Supabase backend whose key lives only in the site JavaScript (off limits).
  Footer: "© 2026 Supreme Court of the Maldives. All rights reserved." No full texts, so no case law.

## Not explored further
- gazette.gov.mv and majlis.gov.mv: robots allow all. Not needed (MvLaw links the gazette PDF per law).
