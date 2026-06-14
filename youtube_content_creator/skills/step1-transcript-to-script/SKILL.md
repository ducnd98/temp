# SKILL: Transcript / Idea → English Script

## TRIGGER
Use this skill when the user wants to:
- Convert a raw YouTube transcript (any language) into a polished English narration script
- Write a script from scratch given a topic/idea (no transcript needed)
- Rewrite or adapt existing script content for a specific niche voice

Keywords that trigger this skill:
"write me a script", "convert this transcript", "turn this into a script",
"viết kịch bản", "chuyển transcript này thành script"

---

## INPUT FORMAT

### Option A — From Transcript
```
NICHE: [bible | storytelling_dark | storytelling_mystery | other]
SOURCE_LANGUAGE: [vi | en | other]
TRANSCRIPT:
[paste raw transcript here OR specify a file path, e.g., "read from input/transcript.txt"]
```

### Option B — From Idea (no transcript)
```
NICHE: [bible | storytelling_dark | storytelling_mystery | other]
TOPIC: [e.g. "The story of Moses and the burning bush"]
TARGET_DURATION: [e.g. "8 minutes"]
REFERENCE_STYLE: [optional — describe tone, pacing, inspiration]
```

---

## RULES

### Language & Voice
- Output is ALWAYS in American English (US spelling, natural conversational rhythm).
- Use standard punctuation (commas, periods, ellipses `...`, or em-dashes `—`) to guide speech pacing and natural pauses in ElevenLabs. Avoid brackets, inline formatting, or phonetic spellings that the TTS engine might mispronounce.
- Write flowing narration prose — no bullet points or dialogue indicators in the script body.
- Use present tense for narration where possible ("Moses stands...", not "Moses stood...")
- Sentence length: vary between short punchy (5-8 words) and longer flowing (15-20 words) — never monotone.
- Write for the ear, not the eye: use active verbs, clear visual nouns, and maintain a consistent storytelling cadence.

### Niche Voice Guide
| Niche | Tone | Pacing | Vocabulary |
|---|---|---|---|
| `bible` | Epic, reverent, awe-inspiring | Slow and deliberate | Elevated but accessible |
| `storytelling_dark` | Suspenseful, ominous, gripping | Builds tension gradually | Vivid, sensory, foreboding |
| `storytelling_mystery` | Curious, investigative, tense | Measured, with sudden reveals | Precise, journalistic |

### Script Structure
1. **Hook (first 15 seconds)** — Open with a question, shocking fact, or vivid scene. No "Hello everyone" or channel intros.
2. **Body** — Tell the story in clear paragraph blocks. Each paragraph = one coherent idea or narrative beat.
3. **Outro (last 10-15 seconds)** — Reflection, call-to-action, or cliffhanger. Keep it brief.

### Paragraph Formatting
- Each paragraph should take approximately 20-40 seconds to read aloud (~45-90 words)
- Separate paragraphs with a blank line
- Add estimated timestamp at the start of each paragraph in brackets: `[00:00]`, `[00:35]`, etc.
- Estimate reading speed at ~130 words/minute for epic/bible style, ~145 words/minute for mystery/dark

### From Transcript Rules
- Do NOT translate word-for-word — rewrite completely in natural English storytelling style
- Preserve all factual content and story beats from the original
- Remove filler words, repetition, and source-language sentence structure artifacts
- Elevate the language to match the niche voice

### From Idea Rules
- Research accuracy: for bible content, align with canonical scripture (KJV/NIV)
- Include vivid sensory details to enable image prompting in Step 2
- Structure the story with clear rising action, climax, and resolution

---

## OUTPUT FORMAT

```
SCRIPT: [Title of the video]
NICHE: [detected/specified niche]
ESTIMATED_DURATION: [X minutes Y seconds]
WORD_COUNT: [total words]

---

[00:00]
[Opening hook paragraph...]

[00:35]
[Next story beat...]

[01:10]
[Continue narration...]

[...]

[07:45]
[Outro paragraph...]
```

---

## EXAMPLE

### Input (Option A)
```
NICHE: bible
SOURCE_LANGUAGE: vi
TRANSCRIPT:
Xin chào các bạn, hôm nay chúng ta sẽ tìm hiểu về câu chuyện của Moses và bụi gai bốc lửa. 
Moses đang chăn chiên ở vùng hoang mạc thì bỗng nhiên ông thấy một bụi gai đang bốc lửa 
nhưng không bị thiêu rụi. Ông đến gần xem thì nghe tiếng Đức Chúa Trời gọi tên mình...
```

### Output
```
SCRIPT: The Burning Bush — When God Spoke Moses's Name
NICHE: bible
ESTIMATED_DURATION: 0 minutes 45 seconds
WORD_COUNT: 98

---

[00:00]
Imagine walking through a vast, silent desert — nothing but sand, stone, and sky stretching endlessly in every direction. Then something catches your eye. A bush. On fire. But it isn't burning. The flames dance, the branches glow — yet nothing is consumed. This is the moment that changed everything.

[00:22]
Moses moved closer. He was just a shepherd that day, tending his flock on the slopes of Mount Horeb. Nothing remarkable. Nothing holy. And then — from the heart of that impossible fire — a voice called his name. "Moses. Moses." And he answered: "Here I am."
```

---

## NOTES
- **Local Agent Execution:** When executing this skill as a local AI assistant, after displaying the script in the chat, you MUST write/save the full script content to a file at `output/script.txt` (or a location requested by the user) in the workspace to facilitate easy manual editing. Create the `output` directory if it does not exist.
- Always output the complete script — never truncate.
- If the transcript is very long (10+ minutes of content), process in full without summarizing.
- For bible niche: avoid anachronistic language — no slang, no internet-speak.
- The output of this skill feeds directly into Step 2 (Script → Scene JSON).
