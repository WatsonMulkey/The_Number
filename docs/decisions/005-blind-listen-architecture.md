# ADR 005: Blind Listen — Blind Mix Comparison Tool

**Status**: Accepted (2026-03-24, post skeptic review)
**Date**: 2026-03-24
**Author**: Watson Mulkey + Claude (with senior-dev-skeptic and socratic-architect review)

## Context

When comparing multiple mixes of the same song, knowing which file is playing introduces confirmation bias — you favor the mix you *think* should be better (the latest revision, the one with the name you remember tweaking). Professional mix engineers use blind listening tests to make objective decisions, but setting one up manually (renaming files, having someone else randomize) is tedious enough that most people skip it.

The tool should live at `foil.engineering/blindlisten` as a product under the FOIL Engineering brand, starting as a free client-side tool and scaling to a collaborative paid product if demand proves out.

### Requirements (from FOI-27)

**Core (Free Tier)**:
- Web-based at `foil.engineering/blindlisten`
- Up to 5 audio files
- Visual confirmation when each file is successfully loaded
- Blind switching between mixes with synced playback position
- Loop sections with custom start/end locators
- Randomized looping by song section and length (minimum 5-second loops)
- Waveform display with hide/unhide toggle
- 10-minute session timer as a forcing function
- Per-mix notes fields
- Reveal button to unmask filenames

**Paid Tier (deferred until demand proven)**:
- Larger file uploads
- Open-ended sessions (no 10-minute limit)
- Re-shuffle with lock-in favorites (lock a choice, reshuffle, see if you pick the same one again)
- Volume (dB), LUFS, and other metrics per mix

**Session Mode (deferred until paying customers request it)**:
- Shareable link for up to 5 participants with session tokens
- Single streamlined playback controlled by session creator (can pass control)
- Private voting — "planning poker for which mix is the best"

## Decision

Build **Blind Listen** as a **static-first web application** deployed to Vercel, proxied under the Foil Engineering domain via `vercel.json` rewrite. The free tier is 100% client-side (zero backend, zero cost). Backend infrastructure is introduced only when paid features or collaborative sessions require it.

### Deployment Architecture

**Standalone Vercel project with domain rewrite** — the same pattern used by TheNumber.

Blind Listen gets its own repo (`WatsonMulkey/blind-listen`), its own Vercel project (`blindlisten`), and is proxied from the Foil Engineering site via rewrite rules in `foil-industries-v2/vercel.json`:

```json
{
  "source": "/blindlisten",
  "destination": "https://blindlisten.vercel.app/"
},
{
  "source": "/blindlisten/",
  "destination": "https://blindlisten.vercel.app/"
},
{
  "source": "/blindlisten/:path*",
  "destination": "https://blindlisten.vercel.app/:path*"
}
```

**Naming convention**: Repo = `blind-listen` (hyphenated, matches directory), Vercel project = `blindlisten`, URL path = `/blindlisten`. Three rewrite rules (no slash, trailing slash, wildcard) matching the TheNumber pattern.

**Why not an Astro page inside `foil-industries-v2`?**
- The Foil site is a static marketing site (Astro 5). Blind Listen needs its own deploy cycle and will iterate independently.
- Coupling them means every Blind Listen deploy rebuilds the entire Foil site.
- Scoped styles in Astro break when components cross boundaries (lesson from foil-industries, 2026-02-16). Blind Listen's interactive UI is better served by a standalone app.

**Why a path (`/blindlisten`) over a subdomain (`blindlisten.foil.engineering`)?**
- Path preserves SEO link equity flowing to the root domain.
- TheNumber already established this pattern. Consistency matters.

**Lesson applied** (Vercel deployment confusion, 2026-02-03): Always verify `.vercel/project.json` contains the correct projectId before deploying. Never assume the project name — verify with `vercel ls`.

### Audio Engine

**Web Audio API** (`AudioContext`, `AudioBufferSourceNode`, `GainNode`, `AnalyserNode`)

Why Web Audio API over `<audio>` elements:
- Sample-accurate playback position tracking
- Instant switching without re-buffering (all files decoded into `AudioBuffer` upfront)
- Shared `GainNode` for consistent volume across switches
- `AnalyserNode` for waveform rendering and future LUFS metering
- `loopStart`/`loopEnd` properties on `BufferSourceNode` for native loop support
- No network requests in free tier — files decoded from local `FileReader` → `ArrayBuffer` → `decodeAudioData`

**Core playback mechanism**:

```
User drops files → FileReader → decodeAudioData → AudioBuffer[]
                                                      ↓
Shuffle: Fisher-Yates permutation maps button indices → file indices
                                                      ↓
Switch: stop current source → new BufferSource → start(0, currentTime)
```

When switching from Mix X to Mix Y:
1. Record current playback position: `audioCtx.currentTime - startedAt`
2. Stop current `BufferSourceNode`
3. Create new `BufferSourceNode` with the target buffer
4. Start from the same position: `source.start(0, savedPosition)`

**Critical**: `AudioContext` must be created on first user interaction (click/keypress), not on page load. Browsers enforce autoplay policy — creating an AudioContext without user gesture results in a suspended context. This is a common Web Audio gotcha.

**File validation** (lesson from BEST_PRACTICES.md, Section 5.1 — arbitrary file upload is CRITICAL severity):
- Client-side: whitelist extensions (`.mp3`, `.wav`, `.flac`, `.aiff`, `.ogg`, `.m4a`, `.aac`)
- Client-side: validate MIME type starts with `audio/`
- Client-side: validate `decodeAudioData` succeeds before accepting the file
- Size limit: 200MB per file free tier (client-enforced), raised for paid tier

### Looping Architecture

Two looping modes:

**Manual loop** — user sets custom start/end locators:
- Two draggable markers on the seek bar / waveform
- `BufferSourceNode.loopStart` and `BufferSourceNode.loopEnd` for native browser-level looping
- `BufferSourceNode.loop = true`
- Minimum loop duration: 5 seconds (enforced in UI — snap markers apart)

**Randomized loop** — system picks a random section:
- Random start point within the file, random length between 5 seconds and a user-defined max
- The random start/length stays the same across all mixes in the session (critical for fair comparison)
- Random start is clamped to the shortest file's duration minus loop length — prevents selecting a region that doesn't exist in shorter files. If files differ by >10% in duration, warn the user (may not be the same song).
- User can "re-roll" for a new random section
- Does NOT require beat detection — this is random timestamp selection, not musical analysis

### Waveform Visualization

Canvas-rendered from `AudioBuffer` PCM data:

1. On decode, downsample each `AudioBuffer` to ~2000 peak amplitude points
2. Draw waveform to `<canvas>` with playback position indicator
3. Loop markers rendered as draggable overlays on the canvas
4. Toggle visibility via hide/unhide button

The waveform does NOT reveal which file is playing — all mixes show the same generic waveform display (the active mix's waveform). This is a potential bias vector: experienced engineers can identify mixes by waveform shape. The hide/unhide toggle mitigates this — default to hidden for maximum blindness, show when loop markers need precise placement.

### Randomization

Fisher-Yates shuffle creates a mapping array `shuffleMap[buttonIndex] → fileIndex`. The mapping is never exposed in the UI, DOM, console, or network tab until reveal.

**Re-shuffle with lock-in (paid tier)**: User marks a favorite, hits reshuffle. The system generates a new permutation for all mixes (including the locked one — it gets a new label). The locked choice is tracked internally but the user must identify it again by ear. This tests whether their preference is consistent. Implementation: maintain a `lockedFileIndex` that persists across shuffles; after reveal, show whether they picked the same file both times.

### State Management

**Lesson applied** (race condition prevention, BEST_PRACTICES.md Section 6.2): Use per-operation loading states, not a single global flag:

```javascript
const state = {
  decoding: [false, false, false, false, false], // per-file decode status
  playing: false,
  seeking: false,
  activeIndex: -1,
  revealed: false,
  loopEnabled: false,
  loopStart: 0,
  loopEnd: 0,
};
```

**Lesson applied** (silent catch is a code smell, skeptic review): All `try/catch` blocks in audio operations must log errors, not swallow them silently. Show user-facing error messages for decode failures, playback failures, and unsupported formats.

### UI Design

Dark theme, minimal layout. Distraction-free — less visual noise means more focus on audio.

| Element | Purpose |
|---------|---------|
| Upload zone | Drag & drop or click to load 2–5 audio files |
| File list | Per-file confirmation: name (truncated), size, decode status (spinner → checkmark) |
| Mix buttons (X/Y/Z/W/V) | Switch between mixes, active state highlighted |
| Play/pause | Transport control |
| Seek bar + waveform | Scrub to any position, loop markers overlaid |
| Loop controls | Enable/disable loop, set start/end, randomize section |
| Volume slider | Shared gain control |
| Session timer | Countdown from 10:00 (free tier), warning at 2:00 remaining |
| Notes section | Per-mix text fields for jotting impressions before reveal |
| Reveal button | Unmasks filenames on the mix buttons |
| Reshuffle button | Re-randomize assignment for another round |

Keyboard shortcuts: `1-5` switch mixes, `Space` play/pause, `R` reveal, `L` toggle loop.

**Seek bar behavior with different-length files**: The seek bar range dynamically adjusts to show the **active buffer's duration**, not the longest file. When switching to a shorter file, the bar contracts. This prevents seeking past the end of a shorter file and avoids confusion about why a 3-minute file has a 5-minute seek bar. If the current playback position exceeds the new active buffer's duration, clamp to the end.

**Accessibility**: All interactive elements require ARIA labels (`aria-pressed` on mix buttons, `aria-valuetext` on seek/volume sliders with human-readable time, `<label>` elements on note inputs — not just placeholder text). Focus management: after reveal, focus returns to the first mix button. Keyboard navigation must reach all controls. Color contrast: WCAG AA minimum throughout, AAA for primary text. `prefers-reduced-motion` respected for animations.

**Client-side tier gate bypass (accepted risk)**: Paid features are client-side gated. A technically savvy user could modify JavaScript to bypass gates. This is explicitly accepted because: (1) bypassed features cost the server nothing (all computation is local), (2) the effort to bypass exceeds the cost of subscribing, (3) server-side enforcement would require moving audio processing to the server, defeating the architecture. Only Session Mode (Phase 3) has server-enforced limits because it uses server resources.

**Session timer behavior**: Timer counts down from 10:00. At 2:00 remaining, the timer turns amber as a warning. At 0:00, playback stops and a "Session ended" message appears. The user CAN restart by clicking play again (soft stop, not force-close). This preserves the forcing-function intent while not being punitive. Paid tier removes the timer entirely.

### Privacy and Security

**Free tier (client-side only)**:
- No data leaves the browser — files loaded via `FileReader`, decoded locally, never uploaded
- No cookies, no analytics, no external requests
- No server, no database, no auth
- Works offline after initial page load

**Session Mode (when implemented)**:
- Unreleased mixes are sensitive intellectual property. Audio files getting leaked would be a career-ending trust violation for users.
- Files stored in Cloudflare R2 with **1-hour TTL auto-expiry** — no persistent storage of anyone's music
- Presigned URLs for upload/download — URLs expire, cannot be reused or shared
- Session isolation — users in session A cannot access session B's files
- File URLs never exposed in client-side JavaScript or network inspector (presigned URLs generated server-side, used once)
- No file indexing, no content analysis, no metadata extraction beyond what's needed for playback

## Progressive Backend Architecture

The most important architectural decision: **when to introduce a backend**. The answer: only when money or multi-user coordination requires it.

### Phase 1 — Free Tier (Client-Side Only, $0/month)

Static site on Vercel free tier (100GB bandwidth/month). All audio processing happens in the browser. No server, no database, no auth. This is the same as opening a local HTML file, but hosted.

**Cost**: $0 until ~100,000 monthly visits.

### Phase 2 — Paid Tier (Minimal Backend)

When adding paid features, introduce:

| Layer | Technology | Why |
|-------|-----------|-----|
| Auth | Supabase Auth (free to 50K MAU) | Bundles Postgres + Realtime. Watson has Neon experience from Buyer Mode, but Supabase bundles more for this use case. |
| Payments | Stripe Checkout | No custom payment UI. Redirect to Stripe, webhook confirms, flip a flag. |
| Backend | Vercel serverless functions (TypeScript) | Thin: verify subscriptions, generate presigned URLs, handle webhooks. Not heavy enough for Fly.io. |
| Database | Supabase Postgres (free tier: 500MB, unlimited API) | Auth + subscription status + session metadata. |

**Paid features are client-side gated**: the backend tells the client the user's tier, and the client unlocks features. No server-side audio processing.

- Larger file uploads: raise client-side validation limit when `user.tier === 'paid'`
- Open-ended sessions: remove 10-minute countdown
- Re-shuffle with lock-in: client-side logic, gated by tier
- LUFS metering: client-side computation from AudioBuffer data (ITU-R BS.1770-4, ~200 lines of JS)

**Lesson applied** (env-var feature gating, 2026-02-16): Mark all gating code with searchable comments (`// PAID_GATE`) so tier logic can be found and updated cleanly. When a gate is removed, all code paths should be searchable.

**Cost**: $0 until 50K MAU. At 100 subscribers × $8-10/month = $800-1,000/month revenue against $0 infrastructure.

### Phase 3 — Session Mode (Real-Time Collaboration)

**The hard problem**: Audio files cannot be streamed from a server (too expensive, latency kills the experience). Every participant must have the files locally in their browser.

**Solution: Cloudflare R2 with auto-expiring objects**.

| Decision | Choice | Why |
|----------|--------|-----|
| File distribution | Cloudflare R2 (presigned URLs, 1-hr TTL) | Zero egress fees (vs S3 at $0.09/GB). Free tier: 10GB storage, 10M reads/month. |
| Playback sync | Supabase Realtime | Already in the stack from Phase 2. Syncing play/pause/switch/seek — not streaming audio. 100ms latency is imperceptible for control signals. |
| Voting | REST API (Vercel serverless) | No real-time needed for votes. Creator reveals when ready. |
| Session auth | Anonymous session tokens (no account for participants) | Creator needs an account; participants just need a link + token. |

**Session flow**:
1. Creator uploads files → presigned R2 upload URLs → browser uploads directly to R2
2. Creator gets shareable link: `foil.engineering/blindlisten/session/abc123`
3. Participants open link, get anonymous session token, download files from R2
4. All participants decode files locally in browser
5. Creator controls playback — state syncs via Supabase Realtime channel
6. Participants vote privately — votes stored in Supabase, visible only to creator after reveal
7. After 1 hour, R2 objects auto-expire. Session records soft-delete after 24 hours.

**Lesson applied** (synchronized playback is genuinely hard): We are NOT streaming audio. Every client plays from local buffers. The server only syncs control signals (which mix, what timestamp, play/pause). This sidesteps the distributed audio sync problem entirely. Latency in control signals is acceptable — a 100-200ms delay when the creator hits "switch to Mix Y" is imperceptible.

**Cost at moderate traction (500 sessions/month, avg 3 participants, avg 150MB files/session)**:
- R2 storage: peak ~5GB concurrent (1-hr TTL). Free tier.
- R2 egress: 500 × 3 × 150MB = 225GB. **R2 egress is free.** $0.
- Supabase Realtime: ~20 peak concurrent connections. Free tier.
- Total: **$0/month** until ~200+ concurrent sessions.

## Cost Analysis

Watson asked: "If this catches traction, it could churn through site data fast. Can you do some math on breakpoints where it starts to cost us money or performance."

### Audio File Sizes (reference)
| Format | 5-min stereo | Per session (3 files avg) |
|--------|-------------|--------------------------|
| MP3 320kbps | ~12MB | ~36MB |
| WAV 44.1/16-bit | ~50MB | ~150MB |
| WAV 48/24-bit | ~86MB | ~258MB |

### Breakpoints by Phase

**Phase 1 (Static, client-side only)**:

| Resource | Free Limit | Break Point | Cost When Exceeded |
|----------|-----------|-------------|-------------------|
| Vercel static hosting | 100GB bandwidth/month | ~3,300 daily users loading ~1MB | $20/month (Vercel Pro) |

**Phase 1 stays at $0 until ~100K monthly visits.** Audio files never touch the server.

**Phase 2 (Paid tier)**:

| Resource | Free Limit | Break Point | Monthly Cost |
|----------|-----------|-------------|-------------|
| Supabase Auth + DB | 50K MAU, 500MB | 50K users | $25/month (Pro) |
| Vercel serverless | 100GB-hrs, 100K invocations | ~3K daily paid users | $20/month (Pro) |
| Stripe | No monthly fee | Per transaction | 2.9% + $0.30/txn |

At $8/month subscription, Stripe takes $0.53 (6.6%). At $10/month, Stripe takes $0.59 (5.9%). **Price at $8-10/month minimum** for healthy margins.

**Phase 3 (Session Mode)**:

| Resource | Free Limit | Break Point | Monthly Cost |
|----------|-----------|-------------|-------------|
| Cloudflare R2 storage | 10GB | ~20 concurrent sessions | $0.015/GB-month |
| Cloudflare R2 reads | 10M reads/month | ~2M reads per 1K participants | Free to 10M |
| Supabase Realtime | Included free | 200 concurrent connections | $25/month (Pro) |

**Critical cost insight**: The real danger is NOT compute or storage — it is **bandwidth if using S3 instead of R2**, and **storage if files don't auto-delete**. One user uploading 500MB/day without cleanup costs more than 100 users with proper TTLs. R2's zero egress fee is the key architectural choice.

### Summary Breakpoints

| Monthly Usage | Infrastructure Cost | Revenue Needed |
|---------------|-------------------|----------------|
| Up to 100K visits (static only) | **$0** | None |
| Up to 50K MAU with paid features | **$0** | Subscriptions covering Stripe fees |
| 50K+ MAU | **$25-45/month** (Supabase + Vercel Pro) | ~5 subscribers covers it |
| 200+ concurrent sessions | **$50-70/month** | ~8 subscribers covers it |
| 1,000+ concurrent sessions | **$100-150/month** | ~15 subscribers covers it |

**The tool pays for itself with ~5-15 paying subscribers at any scale up to 1,000+ concurrent sessions.**

## Phases

### Phase 1A — Deploy MVP (1 day)
- Push `blind-listen` to GitHub (`WatsonMulkey/blind-listen`, public)
- Create Vercel project `blindlisten`, connect repo
- Add rewrite rules to `foil-industries-v2/vercel.json`
- Verify `foil.engineering/blindlisten` returns 200 and loads correctly
- Update file limit from 4 to 5 (add `V` label)

### Phase 1B — Enhanced Free Tier (1 week)
- Visual file upload confirmation: file list with name (truncated), size, decode status (spinner → checkmark → error)
- Waveform display (Canvas from AudioBuffer PCM) with hide/toggle
- Loop section with custom start/end locators (draggable markers on waveform)
- Randomized loop sections (random start, random 5-60s length, re-roll button)
- 10-minute session countdown (warning at 2:00, stops playback at 0:00)
- Keyboard shortcut `5` for fifth mix, `L` for loop toggle
- Error handling: clear messages for decode failures, unsupported formats
- Loading states: per-file decode progress, disabled controls until ready

### Phase 2 — Paid Tier (1-2 weeks, only after Phase 1 proves demand)
- Supabase Auth integration (Google sign-in or magic link — no passwords)
- Stripe Checkout (single "Pro" tier, $8-10/month)
- Webhook handler on Vercel serverless to confirm payment and update Supabase
- Client-side feature gates: check tier, unlock larger files, remove timer, enable LUFS, enable lock-in reshuffle
- LUFS metering: client-side ITU-R BS.1770-4 implementation from AudioBuffer data
- dB peak and RMS display per mix

### Phase 3 — Session Mode (2-3 weeks, only if paying customers ask for it)
- Cloudflare R2 integration: presigned upload/download URLs, 1-hour object TTL
- Session creation: creator uploads files, gets shareable link
- Anonymous session tokens for participants (no account required)
- Playback sync via Supabase Realtime (creator broadcasts play/pause/switch/seek)
- Private voting UI: each participant ranks mixes, votes stored server-side
- Creator reveal: aggregated votes shown alongside filename reveal
- Session cleanup: R2 objects auto-expire, session records soft-delete after 24 hours

### Phase 4 — Polish (ongoing, driven by user feedback)
- Level matching: RMS-based loudness normalization across mixes (prevents "louder = better")
- Spectrogram view (FFT via `AnalyserNode` + Canvas)
- Reference track support (separate "Ref" button outside the blind rotation)
- Session history for paid users
- Export results as text/PDF (notes + ratings + revealed mapping)

## Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| Single HTML file (no hosting) | Original approach. Doesn't support the `foil.engineering/blindlisten` requirement, paid tiers, or collaboration. The local-file approach is preserved in the free tier — all audio stays client-side. |
| Desktop app (Python/Tkinter) | Browser handles audio natively, is cross-platform with zero install, and enables web-based collaboration. Desktop limits distribution. |
| Electron app | Adds 200MB runtime for something a browser page does. |
| Astro page inside `foil-industries-v2` | Couples the marketing site to a fast-iterating tool. Different deploy cycles. Astro scoped styles break across component boundaries (lesson: 2026-02-16). |
| Subdomain (`blindlisten.foil.engineering`) | Splits SEO authority. Path rewrite preserves link equity. TheNumber already established this pattern. |
| Fly.io for backend | Overkill. The backend is thin (verify subscriptions, generate presigned URLs, handle webhooks). Vercel serverless is cheaper and simpler for this workload. |
| AWS S3 for session file storage | S3 charges $0.09/GB egress. For 225GB/month at moderate traction, that is $20/month for something R2 does for free. R2 is the obvious choice. |
| WebRTC peer-to-peer for session file transfer | NAT traversal issues, creator must stay connected, transfer speed depends on creator's upload. R2 presigned URLs are more reliable. |
| Server-side audio streaming | Too expensive, latency kills the experience. Every client should decode and play locally from downloaded buffers. Server only syncs control signals. |
| Server-side LUFS analysis | Requires FFmpeg or dedicated compute. Client-side BS.1770-4 from AudioBuffer data avoids all server-side audio processing. |

## Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Scope creep — tool becomes unshipped platform | **Critical** | Phase 1 is 100% client-side, ships in days. Backend only introduced with proven demand. Each phase has a gate: "do users want this?" |
| Audio IP leakage — unreleased mixes on a server | **Critical** | Free tier: files never leave browser. Session mode: R2 with 1-hr TTL auto-expiry, presigned URLs, session isolation. No persistent storage of user audio. |
| Loudness bias — louder mix sounds "better" | **High** | Phase 4 adds level matching. Phase 1 documents the limitation. Waveform hidden by default to reduce visual loudness cues. |
| Browser memory with large files | **Medium** | 5 stereo WAVs at 5 min each ≈ 500MB decoded. Modern browsers handle this. Warn if total exceeds 500MB. Consider `OfflineAudioContext` for peak-only decode to reduce memory for waveform rendering. |
| `AudioContext` suspended by autoplay policy | **Medium** | Create AudioContext on first user click, not on page load. Show "Click to begin" prompt if context is suspended. |
| Vercel project confusion on deploy | **Medium** | Lesson applied (2026-02-03): always verify `.vercel/project.json` before deploying. Document the correct projectId in CLAUDE.md. |
| `decodeAudioData` fails for uncommon formats | **Low** | Show per-file error with clear message. WAV/MP3 universally supported. Validate files before accepting. |
| Seek bar confusion with different-length files | **Low** | Display duration of active buffer. Clamp seek to shortest buffer. Warn if files differ by >10% in duration (may not be the same song). |
| Session Mode sync latency | **Low** | Not streaming audio — syncing control signals only. 100-200ms latency is imperceptible for play/pause/switch. |
| Waveform reveals mix identity to experienced engineers | **Low** | Default to waveform hidden. Toggle is explicit opt-in. |
| 10-minute timer feels punitive | **Low** | Timer is a soft limit — warns but doesn't force-close. Paid tier removes it. Adjust duration based on user feedback. |

## Development Environment

- **Requires**: Any modern browser (Chrome, Firefox, Edge, Safari)
- **Editor**: Any text editor (VS Code + Claude Code)
- **Testing**: Manual testing with representative audio files (MP3, WAV, FLAC at various lengths and sample rates)
- **Deployment**: Vercel (auto-deploy on push to main)
- **Pre-deploy checklist**: verify `.vercel/project.json`, check `git status` for untracked assets, spot-check production URL after deploy

## Open Questions

1. **Pricing model**: $8-10/month subscription vs. one-time payment ($30-50) for lifetime access? Subscription makes sense if features keep expanding. One-time makes sense if the feature set stabilizes.

2. **Session Mode pricing**: Include in the single paid tier, or a separate higher tier? Recommendation: single paid tier for simplicity — one free, one paid, no confusion.

3. **Mobile UX**: Drag-and-drop doesn't work well on iOS/Android. The file picker fallback handles loading, but waveform and loop controls need touch-friendly design from the start.

4. **"Randomize by song section"** clarification: This is random timestamp selection (pick a start point, loop for N seconds), NOT beat detection or musical analysis. If Watson wants musical-section-aware randomization, that requires a beat detection library and is a Phase 4+ feature.

## References

- [Web Audio API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [AudioBufferSourceNode.loopStart/loopEnd (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/AudioBufferSourceNode/loopStart)
- [ITU-R BS.1770-4 (LUFS measurement standard)](https://www.itu.int/rec/R-REC-BS.1770)
- [Cloudflare R2 Pricing](https://developers.cloudflare.com/r2/pricing/)
- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [Supabase Realtime Documentation](https://supabase.com/docs/guides/realtime)
- [Vercel Rewrites Documentation](https://vercel.com/docs/edge-network/rewrites)
- [Stripe Checkout Documentation](https://docs.stripe.com/payments/checkout)

## Review Notes

### Architect Review (2026-03-24)
- Recommended static-first, backend-later approach
- Proposed Vercel rewrite pattern (matching TheNumber)
- Identified Cloudflare R2 as key cost differentiator (zero egress vs S3)
- Recommended Supabase over custom Neon + auth for bundled functionality
- Recommended Vercel serverless over Fly.io for thin backend
- Provided detailed cost breakpoint analysis

### Skeptic Review — Round 1 (2026-03-24)
- Flagged scope creep as the primary risk (local tool → collaborative platform in one ticket)
- Identified 6 missing technical domains in original ADR (file storage, real-time sync, auth, LUFS, deployment, security)
- Called out audio IP security as underspecified — critical for user trust
- Recommended deferring Session Mode until 50+ paying users
- Recommended deferring paid tiers until free version proves demand
- Found bugs in current MVP: silent catch, duration mismatch, missing loading indicator, 4-file limit vs 5-file requirement
- Validated current `index.html` audio engine as solid, reusable foundation

### Skeptic Review — Round 2: Formal Approval (2026-03-24)
**Verdict: Accept with Notes.** All issues non-blocking. Addressed in this revision:
- Fixed Vercel rewrite to three rules (matching TheNumber's actual `vercel.json` pattern)
- Specified seek bar behavior for different-length files (active buffer governs range)
- Acknowledged client-side tier gate bypass as an accepted risk with rationale
- Defined random loop clamping to shortest file's duration
- Resolved timer contradiction: soft stop at 0:00 (playback stops, can restart)
- Added accessibility section (ARIA, focus management, contrast, reduced motion)
- Added naming convention note (repo vs Vercel project vs URL path)

### UX Review (2026-03-24)
- Produced full Phase 1B HTML mockup with 6 states (empty, loading, loaded, playing, looping, revealed)
- Design pushed to Figma: https://www.figma.com/design/TEbC950BK1H9Ga6ZB6nIbu
- Accent color changed from `#5b5bff` to `#6366f1` (indigo) — more professional, better contrast ratios
- Mix buttons reduced from 100px to 80px for 5-across layout without wrapping
- Loop controls collapsed by default, expand on enable
- Loudness warning banner added as persistent `role="note"`
- Waveform hidden by default, loop inputs accessible via keyboard even without waveform
- Identified accessibility issues in current MVP: missing ARIA labels, silent catch, AudioContext timing, placeholder-only labels
