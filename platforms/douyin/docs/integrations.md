# Production integrations

## Local scope

The workflow keeps task artifacts below `workspace/douyin/<slug>/<version>/`; it does not put generated edits in a skill installation. `sources.md` records source claims and rights context; `assets/` preserves imported material and `assets.json` freezes its hash and rights statement. `review.json` holds substantive review evidence, while `quality.json` and `evidence/` hold repeatable QA output. This makes a version inspectable and lets `revise` preserve its predecessors.

No integration in this document performs account, browser-login, upload, submit, publish, comment, payment, or scheduling actions.

## video-use reference

The project-local reference copy is pinned from [browser-use/video-use](https://github.com/browser-use/video-use) at `43cfc566833548093455c9d4a46bd69913b7e552` (version `0.1.0`, MIT). Its approach is adapted here as production correctness guidance rather than as an account or publishing tool:

- Burn subtitles after overlays so they are not hidden.
- Add 30 ms audio fades at cut boundaries to avoid pops.
- Do not cut speech-source footage until word timings are available. For `speech: true`, the matching `assets/*.json` transcript must carry the source SHA-256 and `words[{start,end,text}]`; every trim keeps at least 30 ms away from a word boundary and mid-word cuts are rejected. `speech: false` accepts a recorded non-dialogue `cut_evidence` instead.
- Verify the rendered output, including duration, visual sampling at cuts, and measurable audio levels.

The workflow does not require external API keys or reuse video-use's hosted transcription path. For designed technical animation, source narration timing and rendered duration provide the synchronization record. Animation needs no API keys.

## Jianying project path

The project-local reference copy is pinned from [luoluoluo22/jianying-editor-skill](https://github.com/luoluoluo22/jianying-editor-skill) at `32c56928ded4f9e2c2b80e099dc7abb793d2c30b` (`VERSION` `1.7.0`, MIT; its bundled `pyJianYingDraft` is Apache-2.0).

Business scripts remain in `platforms/douyin/scripts/`, never inside that skill. The Windows path creates a `JyProject` draft using scene trims of the rendered `base.mp4`, plus one separate voice track and editable subtitle clips. The selected QEMU sample has eight scenes and 18 subtitle clips. It uses Windows-compatible material paths and leaves generated draft evidence in the version's `project/` folder. These are trims of one rendered base asset, not separately rendered scene files.

The local Jianying installation reported by environment inspection is 11.5.0.14471. The upstream skill says its automatic export is most stable on Windows Jianying 5.9 or earlier, even though draft generation supports the newer `draft_info.json` architecture. Therefore draft opening and export on 11.5 remain pending verification; a generated draft or MP4 must be labelled as a local production artifact until the Windows application has opened the draft and its export has been checked.

## Program animation

Remotion `4.0.534` is the installed supplementary engine. It renders horizontal 1920×1080 or portrait 1080×1920 compositions to intermediate assets, then FFmpeg burns subtitles into `final.mp4`. Its relevant official entry points are the [render CLI](https://www.remotion.dev/docs/cli/render) and [API reference](https://www.remotion.dev/docs/api). The pipeline pins all `remotion` and `@remotion/*` packages to the same version and verifies render metadata with `ffprobe`. The bespoke QEMU cinematic composition has a frozen 60-second/eight-beat timeline; changing its scene times requires changing its animation code together with the shot list.

Remotion is source-available under the [Remotion License](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md), rather than an OSI-approved open-source license. Its use must stay within the applicable free/company-license terms; a license decision is outside this production package.

HyperFrames is documented as an optional alternative for a future HTML/CSS/JS composition path, not a required runtime dependency. Its upstream is [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) at `5f9db987c1502c4068bc2a2a279a8a727a44d444`, Apache-2.0. It requires Node.js 22+ and FFmpeg and provides local `init`, `preview`, and `render` commands. It is unavailable in the present implementation, so no deliverable claims to have been rendered with it.

## Earlier camera fixture

The explainer's claims are deliberately bounded to the cited vendor documentation:

- Basler's [stream-grabber parameters](https://docs.baslerweb.com/stream-grabber-parameters) describe GigE packet resend and `FrameRetention`; a missing packet can yield a failed frame without proving a disconnected device.
- Basler's [GigE incomplete-grab diagnosis](https://docs.baslerweb.com/knowledge/troubleshooting-error-code-3774873620-0xe1000014-with-gige-cameras) lists cable, switch, and NIC performance and documents bandwidth-related mitigations.
- Basler's [GigE heartbeat guide](https://zh-tw.docs.baslerweb.com/python-prog-guide) documents a control/heartbeat timeout, including debugger pauses as one cause.
- Basler's [USB3 camera guidance](https://docs.baslerweb.com/daa720-520um) documents bandwidth/component limits that can cause corrupt or dropped frames.

These are Basler/pylon-specific primary sources, useful for the diagnostic model but not a universal conclusion for every industrial camera. The video must say that a real incident requires device logs and interface evidence; it must not describe every dropped frame or timeout as a physical disconnection.

## First selected QEMU video

The first selected video is the horizontal 60-second QEMU explainer. Primary sources are the [QEMU memory API](https://www.qemu.org/docs/master/devel/memory.html), [TCG emulation](https://www.qemu.org/docs/master/about/emulation.html), and the author's [pinned BK7258 diagnostic-machine inventory](https://github.com/Embracecactus/qemu-bk7258/blob/7057f179ad2a31c415053675af72027f1675fb1e/docs/system/arm/bk7258.rst). Its CPU, register, UART and timer displays are original conceptual animations, not captures of a firmware run. Model coverage and physical timing are stated separately; the film makes no complete-chip or board-acceptance claim. See [visual research and topic selection](opus55-research.md).
