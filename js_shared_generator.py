#!/usr/bin/env python3
"""
Shared Utility Functions Generator
Contains utility functions used across multiple JavaScript modules.
"""

def generate_js_shared():
    """Generate shared utility functions used across multiple generators."""
    return '''
// === Shared Utility Functions ===

function escapeHTML(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
'''
