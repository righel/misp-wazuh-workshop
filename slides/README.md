# Slides

Workshop slide decks, written in [Marp](https://marp.app/) Markdown. Each
`.md` file in this directory is a self-contained deck (slides separated by
`---`, with a `marp: true` frontmatter block).

## Install the Marp CLI

Requires Node.js (v18+). Install the CLI globally:

```bash
npm install -g @marp-team/marp-cli
```

Verify:

```bash
marp --version
```

> No install? You can run it on demand without installing anything globally:
> `npx @marp-team/marp-cli <file>.md ...` (substitute `npx @marp-team/marp-cli`
> wherever `marp` appears below).

## Render a deck

From the repository root:

```bash
# PDF
marp slides/INTRO.md --pdf

# PowerPoint (.pptx)
marp slides/INTRO.md --pptx

# Self-contained HTML (single file, opens in any browser)
marp slides/INTRO.md --html
```

Output is written next to the source file (e.g. `slides/INTRO.pdf`). Use
`-o <path>` to choose a different output location.

## Render every deck in this directory

```bash
# Convert all decks to PDF
marp slides/*.md --pdf

# ...or into a dedicated output folder
marp slides/*.md --pdf -o dist/
```

## Live preview while editing

```bash
# Watch a single file and rebuild on save
marp -w slides/INTRO.md

# Or serve the whole directory with a live-reloading preview at http://localhost:8080
marp -s slides/
```

The [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode)
extension also gives a live side-by-side preview inside the editor.

## Notes

- PDF/PPTX export uses a headless Chromium bundled with the CLI. On minimal
  Linux installs you may need common libraries (e.g. `libnss3`, `libatk1.0-0`,
  `libgbm1`); install them via your package manager if export fails.
- Themes: decks use Marp's built-in `default` theme unless the frontmatter says
  otherwise. Add `--theme <file.css>` to apply a custom CIRCL-branded theme.
