🎯 Pipeline thực tế của bạn
YouTube transcript (source)
        ↓
Claude → tách thành:
  ├── [Script] viết lại/customize
  └── [Image prompts] mỗi cảnh 1 prompt
        ↓
ElevenLabs → Audio MP3 (đã có workflow)
        ↓
Leonardo AI → Ảnh 4K (đang build)
        ↓
─────────────────────────────────
Material sẵn sàng để edit thủ công:
  ├── Audio files (MP3)
  └── Image files (PNG 4K)
─────────────────────────────────
        ↓
Bạn tự edit bằng phần mềm

✅ Vậy thứ bạn cần build tiếp là 1 thôi
Claude skill tách transcript thành image prompts — cụ thể là:
Input:  Transcript đã customize
        
Output: JSON array các prompts
[
  {
    "timestamp": "00:00 - 00:45",
    "scene": "Moses standing on Mount Sinai...",
    "prompt": "[scene] + [style block cố định]"
  },
  ...
]
Skill này sẽ:

Đọc transcript theo từng đoạn nội dung
Xác định khi nào cần đổi cảnh (mỗi 30–60 giây hoặc khi nội dung chuyển chủ đề)
Viết scene description bằng tiếng Anh
Tự động append style block cố định vào mỗi prompt
Output JSON để truyền thẳng vào Leonardo API