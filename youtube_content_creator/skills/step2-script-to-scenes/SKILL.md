# SKILL: Script → Scene JSON

## TRIGGER
Use this skill when the user has a finished English script and wants to:
- Break it into visual scenes for image generation
- Generate structured JSON for the n8n pipeline (Steps 3–6)
- Create a scene plan for Leonardo AI image prompts

Keywords that trigger this skill:
"break this into scenes", "generate scene JSON", "create image prompts from script",
"tách scene", "tạo prompt ảnh từ kịch bản"

---

## INPUT FORMAT

```
STYLE_PRESET: [bible_cinematic | bible_classical | storytelling_dark | storytelling_mystery]
SCRIPT:
[paste the full script here OR specify a file path, e.g., "read from output/script.txt"]
```

---

## RULES

### Scene Splitting — Hybrid Logic
Split scenes by SEMANTIC MEANING first:
- New location or setting = new scene
- New character enters or exits = new scene
- Major action or event changes = new scene
- Emotional beat shifts (joy → grief, calm → terror) = new scene

Then apply TIME CAP:
- Hard cap: **max 30 seconds per scene** (~65 words at 130 wpm for bible, ~72 words at 145 wpm for dark/mystery)
- If a passage exceeds 30s without a semantic shift, split into sub-scenes by varying:
  - Camera angle: wide → medium → close-up → detail shot
  - Subject focus: from group to individual, from face to hands, from sky to ground
  - Temporal shift: "earlier that morning...", "as the sun set..."

### character_registry — Auto-Detection
Scan the entire script before writing any scenes. Identify:
- All named human characters (Moses, Noah, David, etc.)
- Divine entities or presences (God, angels, the Holy Spirit)
- Key symbolic objects that recur (the Ark, the staff, the burning bush)

For each, write a **fixed physical description** that will be reused consistently:
- Age, build, skin tone
- Hair and beard
- Clothing (specific fabric, color, style — period-accurate)
- Distinguishing features or objects they carry

### scene_prompt Rules
Each `scene_prompt` must:
- Be written in English, purely visual/descriptive
- Describe: SUBJECT + ACTION + ENVIRONMENT + LIGHTING + CAMERA SHOT
- NOT include: style keywords (those come from config.style_block)
- NOT include: character physical descriptions (those are injected from character_registry at assembly time)
- NOT include: text, logos, watermarks, modern objects
- NOT use abstract concepts ("hope", "faith") — translate to concrete visuals ("a man kneeling with hands raised toward a beam of light breaking through storm clouds")

### camera_shot Vocabulary
Use these standardized shot types to create diverse, dynamic visual sequences:
- `extreme wide shot` — landscape, establishing, God's-eye view
- `wide shot` — full scene, multiple characters
- `medium shot` — waist-up, character interaction
- `close-up` — face, emotion, reaction
- `extreme close-up` — hands, eyes, symbolic object detail
- `low angle` — looking up, making subject or environment appear powerful
- `high angle` — looking down, showing vulnerability or vast scale
- `over-the-shoulder` — POV, intimacy
- `dutch angle` — tilted horizon, used to evoke tension, chaos, or divine awe
- `macro shot` — extreme focus on textures (e.g., embers of fire, water droplets, wood grain)
- `profile view` (or `side profile`) — side-facing angle, great for dramatic, reflective moments
- `back view` (or `rear view`) — camera behind the character looking out at the scene they see

### Output Format Rules
- Return ONLY valid JSON — no explanation, no markdown fences, no preamble
- `voiceover_segment`: copy the exact script text that plays during this scene
- `timestamp_est`: cumulative, based on reading speed of the niche
- `character_refs`: list only character NAMES (not descriptions) — descriptions live in character_registry
- `scene_prompt`: self-contained visual description, ready for Leonardo AI

---

## OUTPUT FORMAT

```json
{
  "config": {
    "style_preset": "bible_cinematic",
    "style_block": "[from style-presets/presets.json — copy matching preset's style_block here]",
    "negative_prompt": "[from style-presets/presets.json — copy matching preset's negative_prompt here]",
    "aspect_ratio": "16:9",
    "character_registry": {
      "CharacterName": "full physical description...",
      "AnotherCharacter": "full physical description..."
    }
  },
  "scenes": [
    {
      "scene_index": 1,
      "timestamp_est": "00:00 - 00:22",
      "voiceover_segment": "exact script text for this scene",
      "visual_concept": "one sentence — what do we SEE in this scene",
      "camera_shot": "shot type and angle",
      "character_refs": ["CharacterName"],
      "scene_prompt": "full visual description without style keywords or character physical desc"
    }
  ]
}
```

---

## ASSEMBLY NOTE (for n8n Step 4)

The `final_prompt` for Leonardo AI is assembled OUTSIDE this skill, in the n8n Code node:

```javascript
final_prompt = scene.scene_prompt
  + ". " + character_refs.map(name => config.character_registry[name]).join(', ')
  + ". " + config.style_block
```

Do NOT pre-assemble `final_prompt` inside this skill output. Keep `scene_prompt` clean and separate.

---

## EXAMPLE

### Input
```
STYLE_PRESET: bible_cinematic
SCRIPT:
[00:00]
Imagine walking through a vast, silent desert — nothing but sand, stone, and sky stretching endlessly in every direction. Then something catches your eye. A bush. On fire. But it isn't burning.

[00:22]
Moses moved closer. He was just a shepherd that day, tending his flock on the slopes of Mount Horeb. And then — from the heart of that impossible fire — a voice called his name.
```

### Output
```json
{
  "config": {
    "style_preset": "bible_cinematic",
    "style_block": "cinematic still, epic volumetric lighting, ancient Near East setting, atmospheric haze, dramatic chiaroscuro, photorealistic, anamorphic 35mm lens, warm golden color grading, ultra-detailed",
    "negative_prompt": "cartoon, anime, flat illustration, modern clothing, text, watermark, blurry, low quality, duplicate, deformed hands, ugly",
    "aspect_ratio": "16:9",
    "character_registry": {
      "Moses": "an elderly man in his 80s, long white beard and white hair, deeply weathered olive skin, wearing a simple undyed linen robe tied with a rope belt, carrying a long wooden shepherd's staff"
    }
  },
  "scenes": [
    {
      "scene_index": 1,
      "timestamp_est": "00:00 - 00:12",
      "voiceover_segment": "Imagine walking through a vast, silent desert — nothing but sand, stone, and sky stretching endlessly in every direction.",
      "visual_concept": "Vast empty desert landscape stretching to the horizon under a blazing sun",
      "camera_shot": "extreme wide shot, high angle, God's-eye view",
      "character_refs": [],
      "scene_prompt": "Extreme wide shot from high above. Vast ancient desert, endless golden sand dunes stretching to the horizon, scattered limestone rocks, a single narrow winding path barely visible below, heat shimmer rising from the ground, blazing midday sun casting deep shadows."
    },
    {
      "scene_index": 2,
      "timestamp_est": "00:12 - 00:22",
      "voiceover_segment": "Then something catches your eye. A bush. On fire. But it isn't burning.",
      "visual_concept": "A thornbush burning with supernatural fire that does not consume it",
      "camera_shot": "medium shot, slight low angle",
      "character_refs": [],
      "scene_prompt": "Medium shot, slight low angle. A desert thornbush engulfed in brilliant golden-white fire, flames reaching upward dramatically, yet the branches and leaves completely intact and unburned, supernatural divine light emanating from within the fire, rocky desert ground, dusk light in the background sky."
    },
    {
      "scene_index": 3,
      "timestamp_est": "00:22 - 00:38",
      "voiceover_segment": "Moses moved closer. He was just a shepherd that day, tending his flock on the slopes of Mount Horeb. And then — from the heart of that impossible fire — a voice called his name.",
      "visual_concept": "Moses approaching the burning bush with awe and reverence",
      "camera_shot": "medium shot, eye level, slight over-the-shoulder",
      "character_refs": ["Moses"],
      "scene_prompt": "Medium shot at eye level. A lone figure slowly approaching a burning thornbush on a rocky desert hillside, sheep visible in the distant background, dramatic fire light illuminating his face from ahead, one hand slightly raised in wonder and caution, Mount Horeb slopes behind him under a golden dusk sky."
    }
  ]
}
```

---

## NOTES
- **Local Preset Reading:** As an AI assistant, you MUST read the exact configuration values (`style_block`, `negative_prompt`, `aspect_ratio`) dynamically from `skills/style-presets/presets.json` matching the requested `STYLE_PRESET`. Do not make up these configurations.
- **Local Saving:** After outputting the JSON in the chat, you MUST write/save the valid JSON directly to `output/scenes.json` in the workspace to prevent chat truncation and make it ready to be read by automated image/audio generators.
- Always process the ENTIRE script — do not truncate or summarize.
- If the script has 50+ scenes, still output all of them in one JSON.
- character_registry entries must be detailed enough that Leonardo AI can render the same person consistently across scenes.
- When in doubt about scene count: more scenes = more visual variety = better retention.
