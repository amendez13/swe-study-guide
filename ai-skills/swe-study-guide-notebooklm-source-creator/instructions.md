# swe-study-guide NotebookLM Source Creator

Use this skill when the task is to create or refresh NotebookLM upload sources for this study-guide repository.

The output is a text-only bundle under `notebooklm/<TECHNOLOGY>/<TOPIC>/` containing:

- `README.md` with setup instructions, source roles, and starter prompts.
- `sources/` with ordered text files copied from local study-guide material.

NotebookLM bundles are derived from the repository's canonical study content. They should not become a second source of truth.

## Source Rules

Use local study-guide files only:

- topic `concepts.md`
- topic `notes.md` when present
- technology `technology_concepts.md` when present
- technology `research/concepts.md` when present
- technology `research/course_outlines.md` when present

Never include:

- `site/` assets
- screenshots or exported images
- image files such as `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`
- JSON or other media metadata
- generic material from the web

## Workflow

1. Read `AGENTS.md`.
2. Identify the target scope:
   - one topic folder under `content/<TECHNOLOGY>/<TOPIC>/`
   - one technology folder under `content/<TECHNOLOGY>/`
   - existing bundles under `notebooklm/`
   - all topics, only when explicitly requested
3. Prefer the bundled script for deterministic generation:

```bash
python ai-skills/swe-study-guide-notebooklm-source-creator/scripts/build_notebooklm_sources.py --topic content/01_FastAPI/03_Path_Operations_and_Routing
```

4. For bulk refreshes, use the playbook:

```bash
ansible-playbook infra/notebooklm/update_notebooklm_sources.yml
```

5. Verify the generated bundle contains no image or manifest files:

```bash
find notebooklm -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.gif' -o -iname '*.webp' -o -iname '*.json' \) -print
```

## Script Usage

Create or refresh one topic:

```bash
python ai-skills/swe-study-guide-notebooklm-source-creator/scripts/build_notebooklm_sources.py --topic content/<TECHNOLOGY>/<TOPIC>
```

Refresh every existing bundle under `notebooklm/`:

```bash
python ai-skills/swe-study-guide-notebooklm-source-creator/scripts/build_notebooklm_sources.py --all-existing
```

Create or refresh every topic in one technology:

```bash
python ai-skills/swe-study-guide-notebooklm-source-creator/scripts/build_notebooklm_sources.py --technology content/<TECHNOLOGY>
```

Create or refresh every topic in the study guide:

```bash
python ai-skills/swe-study-guide-notebooklm-source-creator/scripts/build_notebooklm_sources.py --all-topics
```

Preview the bundles without writing files:

```bash
python ai-skills/swe-study-guide-notebooklm-source-creator/scripts/build_notebooklm_sources.py --technology content/<TECHNOLOGY> --dry-run
```

## Quality Bar

- Generated bundles must be repeatable.
- Keep source filenames ordered and descriptive.
- README instructions must tell the learner exactly which files to upload.
- Preserve references to canonical study-guide source paths.
- Do not overwrite topic content, technology research, or other canonical files.
- Do not broaden a one-topic request into technology-wide or repository-wide generation without user direction.
