# Douyin Flow

Douyin Flow adds a local, production-first short-video workflow to this workspace. Its production CLI produces a reviewable package; it does not log into a platform, upload media, submit a draft, publish, reply to comments, or manage an account.

For technical hand-drawn explainers, use the project-local [technical-handdraw-video Skill](../../skills/technical-handdraw-video/SKILL.md) and [production SOP](../../docs/technical-handdraw-video.md). This route reuses the installed `sweety-handdraw-video` engine, accepts accurate Jianying voice exports, and covers native landscape 4K layout, audio-driven timing and final-file review. Its native job layout differs from the Remotion CLI below; inspect `production_engine` before choosing build or revision commands. The locally installed engine lives under ignored `.local/skills/` and is not included by cloning this repository.

For an already approved video and an explicit single-post web-publication request, use the project-local [multi-platform-publish Skill](../../skills/multi-platform-publish/SKILL.md) and [web publication SOP](../../docs/douyin-web-publishing.md). That workflow operates the official page within the user's scope and records upload, moderation and publication evidence separately. It adds no platform API or unattended publishing command to this CLI. Invocation example: “按 multi-platform-publish，发布当前已确认版本；保留我指定的话题，其余按本篇内容补充。” Existing authorization remains valid on resume; uncertain submissions are checked in content management before any further action.

Each task moves through these states:

`idea` → `script` → `shooting` → `editing` → `review` → `ready_publish` → `published` → `reviewed`

The supported forms are `A` 真人口播, `B` 技术动画解释, and `C` 实拍素材剪辑. **The reference video is a production-quality benchmark, not a content brief to copy.** The user explicitly corrected the Agent's mistaken switch to a PCB topic. Keep the user's own knowledge-base/GitHub subject; do not transplant the reference's board, characters, chapter structure or simulations.

The current local review film is **《没插开发板，固件为什么也能跑？》**, in `workspace/douyin/qemu-without-board/v008/`: [watch](../../workspace/douyin/qemu-without-board/v008/preview.html), [reference analysis](../../workspace/douyin/qemu-without-board/v008/reference-analysis.md), [script](../../workspace/douyin/qemu-without-board/v008/script.md), and [handoff](../../workspace/douyin/qemu-without-board/handoff.md). It is a complete 70-second, 1920×1080, 30fps original animation with Chinese captions, a locally synthesized score, a cover and editable Three.js/Remotion sources. It follows the preserved real Cortex-M3 / MPS2 AN385 experiment: file analysis, matching environment, reset and RAM initialization, disabled UART TX, source revision, rebuild, fresh reset and 42-byte output. Current status is `review`; author approval and subjective audio listening are still pending. No platform operation occurred. v005 preparation and v006/v007 intermediate exports remain preserved. The earlier requirement for author-recorded narration does not apply.

**PCB v001/v002 are preserved off-scope technical experiments, not fulfillment of the user's request.** Their [technical production record](docs/pcb-acceptance.md) remains, but machine checks and a locally reviewed DEMO do not prove task alignment or reference-level aesthetics. Earlier QEMU deliveries and their [separate acceptance record](docs/acceptance.md) also remain untouched; no prior QA or approval transfers to v005. See [earlier visual research](docs/opus55-research.md). Industrial-camera exports remain fixtures.

## Workflow

Run commands from the repository root. The command interface is intentionally local and file-based:

```bash
npm ci --prefix platforms/douyin --ignore-scripts --no-audit --no-fund
python3 platforms/douyin/scripts/sample.py
python3 platforms/douyin/scripts/flow.py new <slug> --kind A|B|C --title <title> [--demo]
python3 platforms/douyin/scripts/flow.py asset <slug> <source> --rights <text>
python3 platforms/douyin/scripts/flow.py build <slug>
python3 platforms/douyin/scripts/flow.py audit <slug>
python3 platforms/douyin/scripts/flow.py review <slug> <review-json> [--author-note <note>]
python3 platforms/douyin/scripts/flow.py revise <slug>
python3 platforms/douyin/scripts/flow.py status <slug>
python3 platforms/douyin/scripts/flow.py package <slug>
```

The workspace already provides PyYAML, Pillow, and NumPy; this flow does not install all upstream Windows/Jianying dependencies. `sample.py` prepares the first local fixture. `asset` records the supplied source and its rights statement before it can be used. `build` creates the current version's edit assets and production package. `audit` writes measurable quality evidence. `review` records an Agent substantive review from the supplied JSON. `--author-note` is the only command input that records formal author approval for a non-demo task. `revise` creates a new version rather than overwriting the reviewed one.

## Project and version records

A task is rooted at `workspace/douyin/<slug>/`. Its `state.json` points to the current version, for example `v001`. Each version records sources in `sources.md`, registered material in `assets.json` and `assets/`, substantive review in `review.json`, and automated QA in `quality.json` plus `evidence/`. It retains these required delivery artifacts:

```text
script.md
shotlist.yaml
subtitle.srt
thumbnail.png
project/
final.mp4
publish.json
```

Versions are immutable after review. Revisions create `v002`, `v003`, and so on; earlier assets, scripts, audits, review decisions, and exports remain available for comparison.

`package` creates `publish-vNNN.zip` after production review. It copies manifest-pinned production files and the QA/review preview, excludes private Windows draft-index backups, checks the archive contents against the output hashes, and preserves an existing archive. It does not upload the package.

`ready_publish` means production QA and the Agent substantive review are complete. A demo task may enter that state with a visible `demo` marker, but it is not formal approval. A non-demo task additionally requires an explicit author note. The state name `published` exists for externally confirmed outcomes only; this workflow has no platform-operation command and does not set that state by itself.

## Evidence standard

Production QA checks the opening hook (first three seconds), information density, subtitle readability, audio measurements, pacing, thumbnail, and title. It distinguishes generated/synthetic checks from an Agent substantive review and from formal author approval. A rendered MP4, draft project, or passing script check is evidence of production output only; it is not evidence of a platform upload, moderation result, public availability, or real viewing performance.

For technical topics, script claims must name their primary source and respect its scope. The current v008 film binds the original MPS2 AN385 experiment session `20261012T090234263613Z` and this turn's independent no-debugger output reruns (0 / 42 bytes). Internal register states are reconstructed from the preserved session checkpoints; animation seconds are editorial timing. The older BK7258 document pin applies only to earlier drafts and is not evidence for the MPS2 film. No animation or partial diagnostic establishes arbitrary-firmware compatibility, whole-chip support or physical-board acceptance.

See [integration notes](docs/integrations.md) for engine and editing boundaries.
