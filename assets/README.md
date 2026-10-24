# Profile visual system

The README uses repository-owned SVGs: violet `#8B5CF6`, cyan `#06B6D4`, blue `#2563EB`, and emerald `#10B981`. Light variants use darker text accents for contrast; dark variants use lighter accents. The image backgrounds are explicit, so artwork does not depend on the page background.

## Assets and motion

- `profile/hero-{light,dark}.svg`: gradient fields, slow orbital motion, and traveling circuit accents.
- `profile/typing-{light,dark}.svg`: three coordinated type/delete sequences with a moving cursor. Text remains in the SVG when animation is unavailable.
- `profile/focus-{light,dark}.svg`: traveling signals between learning, evaluation, and building.
- `profile/divider-{light,dark}.svg`: a slow gradient sweep.
- `profile/project-*.svg`, `contact-*.svg`, and `footer-*.svg`: compact project titles, labeled contact links, and a matching closing panel.
- `tech/*.svg`: local technology badges. Brand paths come from [Simple Icons](https://simpleicons.org/) ([CC0 license](https://github.com/simple-icons/simple-icons/blob/develop/LICENSE.md)). Technologies without a retrieved brand mark use a neutral node glyph, not an imitation logo. The badge labels identify every technology.
- `profile/stats-*.svg` and `languages-*.svg`: real, timestamped GitHub snapshots. `snapshot.json` records the source URLs, date, and values. The repository count excludes forks and private repositories. Language bars count public non-fork repositories by their primary language; they do not measure code share, expertise, or time spent. Repositories without a primary language are omitted from the language bars.
- `profile/snake-*.svg`: animated contribution calendars generated with [Platane/snk](https://github.com/Platane/snk), pinned to `d8f6715049803e982ee5ff501b6b9b7d5deeb09b` (v3, Node 24).
- `profile/calendar-*.svg`: static real-data calendars used when reduced motion is requested.

The hero, typing strip, focus graphic, dividers, and snake include `prefers-reduced-motion` handling. The README additionally selects explicit `*-static.svg` variants for the hero, typing strip, focus graphic, and dividers, plus the static calendar, in reduced-motion mode. This avoids relying solely on media queries inside an embedded SVG. SVGs contain no scripts, foreign objects, external fonts, or externally referenced image resources. CSS lives inside the SVG images, not in the README page. GitHub may cache assets, and media selection ultimately depends on the browser/GitHub image renderer.

All initial assets are included: there are no placeholder output-branch URLs, missing generated files, or dependencies on a statistics-card service. The dated snapshots remain usable if a later refresh fails.

## Enable automatic refresh

1. Review and publish the README, `assets/`, `scripts/refresh-profile.py`, and `.github/workflows/profile-visuals.yml` together to the repository’s default branch. No commit or push was performed as part of this redesign.
2. Enable GitHub Actions for the repository. If an action allowlist is enforced, allow the pinned `actions/checkout`, `actions/upload-artifact`, `actions/download-artifact`, and `Platane/snk/svg-only` actions.
3. In **Actions → Refresh profile visuals**, choose **Run workflow** for an initial hosted verification. The schedule runs Mondays at 02:23 UTC (07:53 in Sri Lanka); GitHub may delay scheduled jobs.
4. Repository/organization policy must allow the workflow’s publish job to use `contents: write`. The generation job has only `contents: read`. The workflow uses the built-in `GITHUB_TOKEN`; no personal access token or custom secret is needed.
5. The publish job commits only the generated statistics, calendars, snakes, and snapshot metadata to the default branch. If branch protection blocks that update, retain the protection: download the `profile-visuals` artifact and merge the asset changes through your normal review process. Artifacts are retained for seven days.

The workflow has no pull-request trigger, avoids persisted checkout credentials, pins all actions by commit SHA, and serializes refresh runs. Public API/schema/network failures stop generation rather than publishing made-up or empty statistics. Existing committed images remain in place. GitHub may disable scheduled workflows after prolonged repository inactivity; rerun or re-enable the workflow in Actions if needed.

## Local maintenance

```sh
python3 scripts/refresh-profile.py
```

This standard-library script refreshes the public statistics and static calendar, and adds accessible titles/reduced-motion rules to existing snake files. It does **not** regenerate a snake route; use the workflow for that. Snake dates represent when the snake was generated, independently of the other snapshots. The initial snakes were generated locally using the same pinned action bundle and an existing authenticated GitHub CLI session; no credential is stored in this repository.

The graph includes GitHub’s contribution-calendar data, which may include anonymized private contributions according to profile visibility settings. It is not a count of public commits. The snake is a decorative traversal of calendar intensity, not a live activity indicator.

## Content boundaries

- VenomVerse is credited as a team project and links to the team repository.
- VivoAssist is explicitly separate from the full-stack RAG Chatbot. No public repository/demo for the latter was found during the audit.
- Guruge Cinnamon’s storefront and separate production tracker are described from the portfolio; no private repository URL is guessed.
- Network ML Lab is educational preparation. It is not presented as an implemented or validated encrypted command-and-control detection system.
- LinkedIn is the user-provided URL, but its browser challenge prevented independent destination verification.

## Validation of this redesign

The README was rendered with GitHub’s Markdown API and inspected in Chrome using GitHub-style Markdown CSS. Screenshots and layout checks covered 320, 390, 768, 1024, and 1100px viewports, both color schemes, and reduced motion. All 57 displayed images loaded, with no horizontal overflow. Frame comparisons confirmed embedded animation in the hero, typing strip, focus diagram, and snake; reduced-motion screenshots were stable. The SVG text-color checks passed a 4.5:1 contrast threshold against their designed card backgrounds.

All local image references and SVG XML parsed successfully. Public repository, portfolio, and storefront links responded successfully; LinkedIn returned a browser challenge despite HTTP 200. Snapshot parsing, failure retention, language counts, snake-date preservation, workflow YAML, permission separation, action SHA pins, and `git diff --check` were checked. The hosted GitHub Actions workflow and the published profile page have not been run/viewed with these changes, because nothing was committed or pushed.
