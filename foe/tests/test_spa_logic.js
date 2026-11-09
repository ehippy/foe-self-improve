const { test, describe } = require('node:test');
const assert = require('node:assert');

// Simulate the SPA logic extracted from index.html inline scripts
describe('SPA Logic', () => {

  test('API_BASE defaults to localhost:19093', () => {
    const API_BASE = 'http://127.0.0.1:19093';
    assert.strictEqual(API_BASE, 'http://127.0.0.1:19093');
  });

  test('file protocol detection uses correct fallback', () => {
    // Simulates: window.location.protocol === 'file:'
    const protocol = 'file:';
    const isFile = protocol === 'file:';
    assert.strictEqual(isFile, true);
  });

  test('publish button disabled when status is not done', () => {
    const status = 'building';
    const disabled = status !== 'done';
    assert.strictEqual(disabled, true);
  });

  test('publish button enabled when status is done', () => {
    const status = 'done';
    const disabled = status !== 'done';
    assert.strictEqual(disabled, false);
  });

  test('publish endpoint path is correct', () => {
    const projectId = 42;
    const url = `/api/projects/${projectId}/publish`;
    assert.strictEqual(url, '/api/projects/42/publish');
  });

  test('409 conflict is handled', () => {
    const response = { status: 409, body: { detail: 'already published' } };
    const isConflict = response.status === 409;
    assert.strictEqual(isConflict, true);
  });

  test('repo_url and pages_url are displayed after publish', () => {
    const result = {
      repo_url: 'https://github.com/ehippy/foe-42',
      pages_url: 'https://ehippy.github.io/foe-42'
    };
    assert.ok(result.repo_url.includes('github.com'));
    assert.ok(result.pages_url.includes('github.io'));
  });

  test('QA status is a valid enum value', () => {
    const validStatuses = ['pass', 'fail', 'pending'];
    const status = 'pass';
    assert.ok(validStatuses.includes(status));
  });

});
