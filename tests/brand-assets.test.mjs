import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

test('Skillary ships the approved library identity', async () => {
  const [logo, cover, raster, readme] = await Promise.all([
    readFile(new URL('../docs/assets/logo.svg', import.meta.url), 'utf8'),
    readFile(new URL('../docs/assets/cover.svg', import.meta.url), 'utf8'),
    readFile(new URL('../docs/assets/cover.png', import.meta.url)),
    readFile(new URL('../README.md', import.meta.url), 'utf8'),
  ]);
  assert.match(logo, /<title[^>]*>Skillary logo<\/title>/);
  assert.match(cover, /Find and install focused skills for your AI agent\./);
  assert.deepEqual({ width: raster.readUInt32BE(16), height: raster.readUInt32BE(20) }, { width: 1200, height: 630 });
  assert.match(readme, /docs\/assets\/logo\.svg/);
  assert.match(readme, /docs\/assets\/cover\.svg/);
});
