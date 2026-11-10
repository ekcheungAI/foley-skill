# foley: Claude Code gives your video its sound effects

A Claude Code skill by ekcheungAI. Give Claude a video and it:
1. finds every moment that needs a sound;
2. downloads CC0 sounds from Openverse (Freesound, no account, no credit needed);
3. picks and trims them with earshot;
4. places each one on its frame with ffmpeg;
5. listens back with earshot and fixes anything late, buried or clipping until every cue is within 40 ms of the picture.

## Install
1. ffmpeg + uv: `brew install ffmpeg uv` (macOS).
2. earshot, the free "ears" for agents (MIT, CPU only, ~1.1 GB models):
   ```bash
   uv tool install "earshot[mcp] @ git+https://github.com/Leonxlnx/earshot"
   earshot doctor --fetch
   ```
3. This skill:
   ```bash
   git clone https://github.com/ekcheungAI/foley-skill
   mkdir -p ~/.claude/skills && cp -r foley-skill/foley ~/.claude/skills/
   ```

## Use
In the folder with your video, open Claude Code and say:

> 用 foley skill 幫 myclip.mp4 配音效，全部自己做。

or in English: `Use the foley skill to add sound effects to myclip.mp4. Do everything yourself.`

You get `myclip-sfx.mp4` (picture untouched) and `foley/report.md`: every cue, every sound's CC0 source page, and the first and final sync numbers.

## Good to know
- The checks are earshot measurements, not human ears. Listen once before you publish.
- CC0 needs no credit, but Openverse does not guarantee licence accuracy. For commercial work, open each sound's source page (listed in the report).
- Openverse's anonymous limit is about 20 requests a minute and 200 a day.
- A sound-effects-only track is peaky (about −20 LUFS); set the final loudness in your edit.
- Tested 2026-11-10 with Claude Code 2.1 on macOS (headless `claude -p`, earshot via its CLI):
  - a 5 s kung-fu clip: 8 cues, a whoosh 183 ms late and clipping fixed; 46 turns, 9.3 min, about US$2.0 of usage;
  - a fresh install on a 5 s kitchen clip (`potlid.mp4`): 6 cues, a buried footstep and a stray double-clink fixed; 63 turns, 9.3 min, about US$2.4.

## Credits
- earshot by Leon Lin (MIT): https://github.com/Leonxlnx/earshot
- Openverse (WordPress Foundation) and Freesound contributors (CC0)

MIT licence (this skill's text and scripts only).
