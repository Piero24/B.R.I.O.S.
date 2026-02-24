#!/usr/bin/env node
/**
 * sync-changelog.js
 *
 * Copies the root CHANGELOG.md content into the docs/changelog.md file,
 * preserving the frontmatter header. New entries in the root CHANGELOG.md
 * automatically appear at the top of the documentation changelog.
 *
 * Usage: node scripts/sync-changelog.js
 * Called automatically via the "prebuild" npm script.
 */

const fs = require('fs');
const path = require('path');

const ROOT_CHANGELOG = path.resolve(__dirname, '..', '..', 'CHANGELOG.md');
const DOCS_CHANGELOG = path.resolve(__dirname, '..', 'docs', 'changelog.md');

const FRONTMATTER = `---
id: changelog
title: Changelog
sidebar_position: 7
---

`;

try {
  const rootContent = fs.readFileSync(ROOT_CHANGELOG, 'utf-8');

  // Strip the "# Changelog" title from root (the docs page has its own)
  const contentWithoutTitle = rootContent.replace(/^#\s+Changelog\s*\n*/m, '');

  const output = FRONTMATTER + '# Changelog\n\n' + contentWithoutTitle.trim() + '\n';

  fs.writeFileSync(DOCS_CHANGELOG, output, 'utf-8');
  console.log('✅ Synced CHANGELOG.md → docs/changelog.md');
} catch (err) {
  console.error('❌ Failed to sync changelog:', err.message);
  process.exit(1);
}
