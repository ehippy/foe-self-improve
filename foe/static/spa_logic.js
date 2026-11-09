'use strict';

/**
 * Core SPA rendering logic extracted from index.html for testability.
 * Exposed as CommonJS module for Node.js testing.
 */

function getStatusClass(status) {
  if (status === 'done') return 'status-done';
  if (status === 'pending') return 'status-pending';
  if (status === 'running') return 'status-running';
  return 'status-unknown';
}

function getQaBadgeClass(qaStatus) {
  if (qaStatus === 'pass') return 'qa-pass';
  if (qaStatus === 'fail') return 'qa-fail';
  return 'qa-unknown';
}

function isPublishEnabled(project) {
  return project.status === 'done';
}

function renderProjectCard(project) {
  const statusClass = getStatusClass(project.status);
  const qaClass = getQaBadgeClass(project.qa_status);
  const isDone = project.status === 'done';

  return {
    id: 'project-' + project.id,
    statusClass: statusClass,
    qaBadgeClass: qaClass,
    iterBtnDisabled: isDone ? 'disabled' : '',
    pubBtnId: 'pub-btn-' + project.id,
    pubBtnDisabled: isDone ? '' : 'disabled',
    qaBadgeClass: qaClass
  };
}

// Export for Node.js testing (no-op in browser)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { getStatusClass, getQaBadgeClass, isPublishEnabled, renderProjectCard };
}
