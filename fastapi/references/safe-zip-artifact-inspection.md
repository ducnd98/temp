# Safe Zip Artifact Inspection & Streaming in FastAPI

This guide documents the architecture and security standards for inspecting and retrieving files from packaged zip archives in FastAPI applications.

---

## 1. In-Memory Archive Inspection (Zero Full Disk Extraction)

When users or clients request a directory tree or file list of an uploaded artifact package:
- **Never** extract the entire zip archive to temporary directories on disk just to read filenames or sizes. Disk extraction causes massive disk I/O, creates race conditions, and exposes the filesystem to uncleaned temp directories.
- **Always** inspect the archive in-memory using `zipfile.ZipFile(artifact_path, "r")` and `zf.infolist()`:
  ```python
  with zipfile.ZipFile(artifact_path, "r") as zf:
      for member in zf.infolist():
          name = member.filename.replace("\\", "/")
          # 1. Filter out system and hidden OS noise
          if name.startswith("__MACOSX/") or name.endswith((".DS_Store", "Thumbs.db")):
              continue

          is_dir = member.is_dir() or name.endswith("/")
          clean_path = name.rstrip("/")
          if not clean_path:
              continue

          results.append({
              "path": clean_path,
              "name": Path(clean_path).name,
              "size_bytes": member.file_size,
              "is_dir": is_dir,
          })
  ```
- **Sorting Rule**: Sort directories before files, then alphabetically:
  `results.sort(key=lambda x: (not x["is_dir"], x["path"].lower()))`

---

## 2. ZipSlip Directory Traversal Prevention

When fetching the content of a specific file inside a zip archive via API query parameters (e.g. `GET /files/content?path=...`):
- **Path Sanitization**:
  ```python
  clean_path = file_path.replace("\\", "/").strip("/")
  parts = Path(clean_path).parts
  if ".." in parts or clean_path.startswith(("/", "\\")):
      raise ValueError("Forbidden path traversal sequence detected.")
  ```
- Any presence of `..` or leading slashes must immediately raise a validation error (`400 Bad Request`).

---

## 3. Single-Root Folder Resolution Fallback

Artifact archives downloaded from GitHub or created on certain OS tools often wrap all files inside a top-level directory (e.g. `confluence-skill/...`).
When a client requests `path="SKILL.md"` or `path="scripts/audit.py"`:
- Check for exact match first.
- If not found, check if the file is inside the single root directory:
  ```python
  target_name = None
  for name in zf.namelist():
      normalized = name.replace("\\", "/").rstrip("/")
      if normalized == clean_path:
          target_name = name
          break

  if target_name is None:
      for name in zf.namelist():
          normalized = name.replace("\\", "/").rstrip("/")
          if normalized.endswith(f"/{clean_path}"):
              target_name = name
              break
  ```
- This ensures that clients requesting either the relative path or the full internal archive path succeed without error.

---

## 4. Binary File Detection & Memory Guard

To prevent reading huge binary assets (e.g. `.png`, `.pdf`, `.mp4`, `.zip`, `.wasm`) into memory and attempting to serialize them as UTF-8 text strings:
1. **Extension Blacklist**:
   ```python
   BINARY_EXTENSIONS = {
       ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico",
       ".pdf", ".zip", ".tar", ".gz", ".mp4", ".mov",
       ".wasm", ".bin", ".pyc", ".woff", ".woff2", ".ttf"
   }
   ```
2. **Null-Byte Sniffing**:
   Check for null bytes in the first 1024 bytes of raw data:
   `is_binary = ext in BINARY_EXTENSIONS or (b"\x00" in raw_bytes[:1024])`
3. **Response Payload**:
   If binary, return:
   `{"path": clean_path, "name": name, "size_bytes": size, "is_binary": True, "content": ""}`
   If text, safely decode with `raw_bytes.decode("utf-8", errors="replace")`.

---

## 5. Automatic Orphan Zip Artifact Pruning on Update/Rename

When a skill is updated or re-ingested with a new name (e.g. "Alpha Skill" -> "Beta Skill"):
- The filename changes from `alpha-skill.zip` to `beta-skill.zip`.
- If unhandled, `alpha-skill.zip` remains on disk as an orphan file, wasting storage and causing `get_artifact_path` fallback logic to potentially pick the wrong/outdated archive.
- **The Pruning Invariant**: In `StorageService.save_artifact`:
  Before writing the new file, iterate over all existing files in `skill_dir`:
  ```python
  for f in skill_dir.iterdir():
      if f.is_file() and f.name.endswith(".zip") and f.resolve() != artifact_file:
          f.unlink(missing_ok=True)
  ```
  Also purge any stale standalone cached markdown `(skill_dir / "skill.md").unlink(missing_ok=True)`.
- **Result**: Guarantees that `{skill_id}/` contains strictly **one single `.zip` file** corresponding to the active skill version.

