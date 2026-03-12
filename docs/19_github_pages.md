# 19 Publishing On GitHub Pages

This repository can be published as a proper documentation site instead of relying on raw file browsing.

## What is configured

- `mkdocs.yml` builds a navigation-driven documentation site from the repository's canonical markdown files
- `site-docs/` is a thin build root made of symlinks back to the canonical markdown files, so GitHub Pages gets a proper docs directory without duplicating content
- `.github/workflows/pages.yml` builds and deploys that site on pushes to `main`
- `CNAME` declares the intended public Pages hostname: `wllm.riera.co.uk`
- the site home page is the canonical repository `README.md`, so there is still one canonical introduction

## Why this setup is better

- GitHub repository browsing is good for contributors
- GitHub Pages is better for reading guides in order
- the left-hand navigation makes the numbered guides, knowledge layer, prompt assets, and evaluation docs easier to follow
- Mermaid diagrams and report graphs render directly in the published site

## First-time setup on GitHub

1. push the repository to GitHub
2. open `Settings -> Pages`
3. under `Build and deployment`, select `GitHub Actions`
4. push to `main` or run the `pages` workflow manually

After that, GitHub will publish the generated `site/` artifact automatically.

## Local preview

Install the docs dependencies:

```bash
uv sync --extra docs
```

Run the local preview server:

```bash
uv run mkdocs serve
```

Build a production-style local site:

```bash
uv run mkdocs build
```

## Writing guidelines for Pages-friendly docs

- link to markdown pages or landing pages, not bare folders
- keep command paths as repository-relative paths inside code blocks
- prefer human-readable landing pages like `evaluation/cases/README.md` when a folder contains machine-readable files
- keep diagrams in Mermaid blocks so both GitHub and GitHub Pages can render them

## What to avoid

- absolute local filesystem links
- references that only make sense inside your terminal session
- sending readers to a folder path that has no landing page

## Related files

- `mkdocs.yml`
- `.github/workflows/pages.yml`
- [repository_map.md](repository_map.md)
