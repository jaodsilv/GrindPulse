#!/usr/bin/env python3
"""
CSS Styling Sub-Agent
Creates modern, clean styling
"""


def generate_css():
    """Generate CSS styling"""

    css = """
    :root {
      /* Awareness color palette */
      --awareness-white: #ffffff;
      --awareness-green: #d1fae5;
      --awareness-yellow: #fef3c7;
      --awareness-red: #fecaca;
      --awareness-dark-red: #f87171;
      --awareness-flashing-primary: #dc2626;
      --awareness-flashing-secondary: #fca5a5;
      --awareness-unsolved: #f3f4f6;
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
    }

    .container {
      max-width: 1600px;
      margin: 0 auto;
      background: white;
      border-radius: 12px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
      overflow: hidden;
    }

    header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 20px 30px;
    }

    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 20px;
      flex-wrap: wrap;
    }

    .header-title {
      flex: 1;
      min-width: 200px;
    }

    header h1 {
      margin-bottom: 8px;
      font-size: 2rem;
    }

    .overall-progress {
      font-size: 1.1rem;
      font-weight: 500;
    }

    .header-controls {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .tab-container {
      display: flex;
      gap: 5px;
      padding: 20px 20px 0 20px;
      background: #f5f5f5;
      border-bottom: 2px solid #e0e0e0;
      overflow-x: auto;
    }

    .tab-button {
      padding: 12px 24px;
      border: none;
      background: #e0e0e0;
      color: #666;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      border-radius: 8px 8px 0 0;
      transition: all 0.3s ease;
      white-space: nowrap;
    }

    .tab-button:hover {
      background: #d0d0d0;
      color: #333;
    }

    .tab-button.active {
      background: white;
      color: #667eea;
      border-bottom: 3px solid #667eea;
    }

    .export-all-section {
      padding: 15px 20px;
      background: #f9f9f9;
      border-bottom: 1px solid #e0e0e0;
      text-align: center;
    }

    .export-all-btn {
      padding: 10px 24px;
      background: #764ba2;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
    }

    .export-all-btn:hover {
      background: #5a3880;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);
    }

    /* ============================================
       HAMBURGER MENU STYLES
       ============================================ */

    /* Wrapper to position menu relative to button */
    .import-export-wrapper {
      position: relative;
      display: inline-block;
      margin-left: auto;
    }

    /* Hamburger button */
    .hamburger-btn {
      background: #667eea;
      border: none;
      color: white;
      width: 44px;
      height: 44px;
      border-radius: 8px;
      font-size: 1.5rem;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .hamburger-btn:hover {
      background: #5568d3;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    .hamburger-btn:focus {
      outline: none;
      box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.4);
    }

    /* Dropdown menu */
    .import-export-menu {
      position: absolute;
      top: calc(100% + 8px);
      right: 0;
      background: white;
      border-radius: 12px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
      min-width: 280px;
      z-index: 1001;
      overflow: hidden;
    }

    .import-export-menu-header {
      padding: 16px 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      font-weight: 600;
      font-size: 1rem;
    }

    .import-export-menu-content {
      padding: 16px 20px;
    }

    .import-export-menu-label {
      display: block;
      font-size: 0.85rem;
      color: #6b7280;
      margin-bottom: 6px;
      margin-top: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .import-export-menu-label:first-child {
      margin-top: 0;
    }

    .import-export-menu-content .filter-dropdown {
      width: 100%;
      margin-bottom: 4px;
    }

    .import-export-menu-divider {
      height: 1px;
      background: #e0e0e0;
      margin: 16px -20px;
      width: calc(100% + 40px);
    }

    .import-export-menu-item {
      display: flex;
      align-items: center;
      gap: 10px;
      width: 100%;
      padding: 12px 0;
      background: none;
      border: none;
      font-size: 1rem;
      color: #374151;
      cursor: pointer;
      text-align: left;
      transition: color 0.2s;
      font-weight: 500;
    }

    .import-export-menu-item:hover {
      color: #667eea;
    }

    .import-export-menu-item span {
      font-size: 1.2rem;
    }

    .import-export-menu-item.export-action span {
      color: #667eea;
    }

    .import-export-menu-item.import-action span {
      color: #10b981;
    }

    /* Responsive adjustments for hamburger menu */
    @media (max-width: 768px) {
      .import-export-menu {
        min-width: 250px;
        right: -10px;
      }

      .hamburger-btn {
        width: 40px;
        height: 40px;
        font-size: 1.3rem;
      }
    }

    .import-btn {
      padding: 12px 24px;
      background: #10b981;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      white-space: nowrap;
    }

    .import-btn:hover {
      background: #059669;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }

    /* Global Import/Export Section */
    .import-export-section {
      padding: 15px 20px;
      background: #f9f9f9;
      border-bottom: 1px solid #e0e0e0;
    }

    .global-import-export {
      display: flex;
      gap: 12px;
      align-items: center;
      justify-content: center;
      flex-wrap: wrap;
    }

    .import-export-label {
      font-weight: 600;
      color: #333;
      font-size: 1rem;
    }

    .import-all-btn {
      padding: 10px 24px;
      background: #10b981;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
    }

    .import-all-btn:hover {
      background: #059669;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }

    /* Conflict Resolution Dialog */
    .conflict-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.6);
      display: none;
      justify-content: center;
      align-items: center;
      z-index: 1100;
      padding: 20px;
    }

    .conflict-panel {
      background: white;
      border-radius: 12px;
      max-width: 800px;
      width: 100%;
      max-height: 90vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }

    .conflict-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px 24px;
      background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
      color: white;
    }

    .conflict-header h2 {
      font-size: 1.3rem;
      margin: 0;
    }

    .conflict-close {
      background: none;
      border: none;
      color: white;
      font-size: 2rem;
      cursor: pointer;
      line-height: 1;
      padding: 0;
      opacity: 0.8;
      transition: opacity 0.2s;
    }

    .conflict-close:hover {
      opacity: 1;
    }

    .conflict-description {
      padding: 16px 24px;
      background: #fef3c7;
      border-bottom: 1px solid #fcd34d;
      font-size: 0.95rem;
      color: #92400e;
    }

    .conflict-description p {
      margin: 0;
    }

    .conflict-global-actions {
      display: flex;
      gap: 10px;
      padding: 16px 24px;
      background: #f9fafb;
      border-bottom: 1px solid #e0e0e0;
      align-items: center;
      flex-wrap: wrap;
    }

    .conflict-global-actions span {
      font-weight: 600;
      color: #333;
      margin-right: 8px;
    }

    .conflict-action-btn {
      padding: 8px 16px;
      background: #e5e7eb;
      color: #374151;
      border: none;
      border-radius: 6px;
      font-size: 0.9rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }

    .conflict-action-btn:hover {
      background: #d1d5db;
    }

    .conflict-list {
      flex: 1;
      overflow-y: auto;
      padding: 16px 24px;
      max-height: 400px;
    }

    .conflict-item {
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      margin-bottom: 16px;
      overflow: hidden;
    }

    .conflict-item:last-child {
      margin-bottom: 0;
    }

    .conflict-problem-name {
      background: #f3f4f6;
      padding: 12px 16px;
      font-weight: 600;
      color: #1f2937;
      border-bottom: 1px solid #e0e0e0;
    }

    .conflict-comparison {
      display: flex;
      gap: 16px;
      padding: 16px;
      align-items: flex-start;
    }

    .conflict-existing,
    .conflict-imported {
      flex: 1;
    }

    .conflict-existing h4,
    .conflict-imported h4 {
      font-size: 0.85rem;
      color: #6b7280;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .conflict-arrow {
      display: flex;
      align-items: center;
      font-size: 1.5rem;
      color: #9ca3af;
      padding-top: 20px;
    }

    .conflict-data {
      background: #f9fafb;
      padding: 12px;
      border-radius: 6px;
      font-size: 0.9rem;
    }

    .conflict-data-list {
      list-style: none;
      margin: 0;
      padding: 0;
    }

    .conflict-data-list li {
      margin-bottom: 4px;
    }

    .conflict-data-list li:last-child {
      margin-bottom: 0;
    }

    .conflict-options {
      display: flex;
      gap: 16px;
      padding: 12px 16px;
      background: #f9fafb;
      border-top: 1px solid #e0e0e0;
    }

    .conflict-option {
      display: flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      font-size: 0.9rem;
    }

    .conflict-option input[type="radio"] {
      width: 16px;
      height: 16px;
      accent-color: #667eea;
    }

    .conflict-footer {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      padding: 16px 24px;
      background: #f9f9f9;
      border-top: 1px solid #e0e0e0;
    }

    .conflict-btn-secondary {
      padding: 12px 24px;
      background: #e0e0e0;
      color: #333;
      border: none;
      border-radius: 6px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .conflict-btn-secondary:hover {
      background: #d0d0d0;
    }

    .conflict-btn-primary {
      padding: 12px 24px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .conflict-btn-primary:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    .tab-content {
      display: none;
      padding: 20px;
    }

    .tab-content.active {
      display: block;
    }

    .progress-section {
      margin-bottom: 20px;
      padding: 20px;
      background: #f9f9f9;
      border-radius: 8px;
    }

    .progress-bar-container {
      width: 100%;
      height: 30px;
      background: #e0e0e0;
      border-radius: 15px;
      overflow: hidden;
      margin-bottom: 10px;
    }

    .progress-bar {
      height: 100%;
      background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
      border-radius: 15px;
      transition: width 0.5s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: 600;
      font-size: 0.9rem;
    }

    .progress-text {
      text-align: center;
      font-size: 1.1rem;
      font-weight: 600;
      color: #333;
    }

    .filter-section {
      display: flex;
      gap: 15px;
      margin-bottom: 20px;
      flex-wrap: wrap;
      align-items: center;
    }

    .search-box {
      flex: 1;
      min-width: 250px;
      padding: 12px 16px;
      border: 2px solid #e0e0e0;
      border-radius: 6px;
      font-size: 1rem;
      transition: all 0.3s ease;
    }

    .search-box:focus {
      outline: none;
      border-color: #667eea;
      box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    .filter-dropdown {
      padding: 12px 16px;
      border: 2px solid #e0e0e0;
      border-radius: 6px;
      font-size: 1rem;
      background: white;
      cursor: pointer;
      transition: all 0.3s ease;
    }

    .filter-dropdown:focus {
      outline: none;
      border-color: #667eea;
    }

    .export-btn {
      padding: 12px 24px;
      background: #667eea;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      white-space: nowrap;
    }

    .export-btn:hover {
      background: #5568d3;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    .table-container {
      overflow-x: auto;
      border-radius: 8px;
      border: 1px solid #e0e0e0;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      background: white;
    }

    thead {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      position: sticky;
      top: 0;
      z-index: 10;
    }

    th {
      padding: 16px 12px;
      text-align: left;
      font-weight: 600;
      font-size: 0.95rem;
      white-space: nowrap;
    }

    td {
      padding: 12px;
      border-bottom: 1px solid #f0f0f0;
      vertical-align: middle;
    }

    tbody tr {
      transition: background 0.2s ease;
    }

    tbody tr:hover {
      background: #f9f9f9;
    }

    .difficulty-badge {
      display: inline-block;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 600;
      text-align: center;
      min-width: 70px;
    }

    .difficulty-Easy {
      background: #10b981;
      color: white;
    }

    .difficulty-Medium {
      background: #f59e0b;
      color: white;
    }

    .difficulty-Hard {
      background: #ef4444;
      color: white;
    }

    .pattern-cell {
      position: relative;
    }

    .pattern-toggle {
      background: #667eea;
      color: white;
      border: none;
      padding: 6px 12px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 600;
      transition: all 0.3s ease;
    }

    .pattern-toggle:hover {
      background: #5568d3;
    }

    .pattern-text {
      display: none;
      margin-top: 8px;
      padding: 8px;
      background: #f0f0f0;
      border-radius: 4px;
      font-size: 0.9rem;
      color: #333;
    }

    .pattern-text.visible {
      display: block;
    }

    .checkbox-input {
      width: 20px;
      height: 20px;
      cursor: pointer;
      accent-color: #667eea;
    }

    .time-input {
      width: 100px;
      padding: 8px;
      border: 2px solid #e0e0e0;
      border-radius: 4px;
      font-size: 0.9rem;
      transition: all 0.3s ease;
    }

    .time-input:focus {
      outline: none;
      border-color: #667eea;
    }

    .comments-input {
      width: 200px;
      min-height: 50px;
      padding: 8px;
      border: 2px solid #e0e0e0;
      border-radius: 4px;
      font-size: 0.9rem;
      font-family: inherit;
      resize: vertical;
      transition: all 0.3s ease;
    }

    .comments-input:focus {
      outline: none;
      border-color: #667eea;
    }

    .solved-date {
      font-size: 0.85rem;
      color: #666;
      font-style: italic;
    }

    .duplicate-badge {
      display: inline-block;
      padding: 4px 8px;
      background: #fbbf24;
      color: #78350f;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 600;
      margin-left: 8px;
      cursor: help;
    }

    .time-col {
      font-size: 0.9rem;
      color: #666;
      text-align: center;
    }

    /* Awareness color classes */
    .awareness-white {
      background-color: var(--awareness-white) !important;
    }

    .awareness-green {
      background-color: var(--awareness-green) !important;
    }

    .awareness-yellow {
      background-color: var(--awareness-yellow) !important;
    }

    .awareness-red {
      background-color: var(--awareness-red) !important;
    }

    .awareness-dark-red {
      background-color: var(--awareness-dark-red) !important;
    }

    .awareness-flashing {
      animation: flash-urgent 0.5s infinite !important;
    }

    @keyframes flash-urgent {
      0%, 50% { background-color: var(--awareness-flashing-primary); }
      51%, 100% { background-color: var(--awareness-flashing-secondary); }
    }

    @media (prefers-reduced-motion: reduce) {
      .awareness-flashing {
        animation: none;
        background-color: var(--awareness-flashing-primary) !important;
      }
    }

    /* Unsolved problem styling */
    .unsolved-problem {
      background-color: var(--awareness-unsolved) !important;
      opacity: 0.85;
    }

    /* Invalid date indicator */
    .invalid-date {
      border-left: 4px solid #ef4444 !important;
    }

    /* Settings button */
    .settings-btn {
      background: rgba(255, 255, 255, 0.2);
      border: 2px solid rgba(255, 255, 255, 0.4);
      color: white;
      width: 44px;
      height: 44px;
      border-radius: 50%;
      font-size: 1.5rem;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .settings-btn:hover {
      background: rgba(255, 255, 255, 0.3);
      border-color: rgba(255, 255, 255, 0.6);
      transform: rotate(45deg);
    }

    /* Refresh button */
    .refresh-btn {
      background: rgba(255, 255, 255, 0.2);
      border: 2px solid rgba(255, 255, 255, 0.4);
      color: white;
      width: 44px;
      height: 44px;
      border-radius: 50%;
      font-size: 1.5rem;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .refresh-btn:hover {
      background: rgba(255, 255, 255, 0.3);
      border-color: rgba(255, 255, 255, 0.6);
    }

    .refresh-btn:active {
      transform: rotate(180deg);
    }

    /* Settings overlay */
    .settings-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      display: none;
      justify-content: center;
      align-items: center;
      z-index: 1000;
      padding: 20px;
    }

    .settings-overlay.visible {
      display: flex;
    }

    /* Settings panel */
    .settings-panel {
      background: white;
      border-radius: 12px;
      max-width: 500px;
      width: 100%;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }

    .settings-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px 24px;
      border-bottom: 1px solid #e0e0e0;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border-radius: 12px 12px 0 0;
    }

    .settings-header h2 {
      font-size: 1.3rem;
      margin: 0;
    }

    .settings-close {
      background: none;
      border: none;
      color: white;
      font-size: 2rem;
      cursor: pointer;
      line-height: 1;
      padding: 0;
      opacity: 0.8;
      transition: opacity 0.2s;
    }

    .settings-close:hover {
      opacity: 1;
    }

    .settings-content {
      padding: 20px 24px;
    }

    .settings-section {
      margin-bottom: 24px;
      padding-bottom: 20px;
      border-bottom: 1px solid #e0e0e0;
    }

    .settings-section:last-child {
      border-bottom: none;
      margin-bottom: 0;
      padding-bottom: 0;
    }

    .settings-section h3 {
      font-size: 1rem;
      color: #333;
      margin-bottom: 12px;
    }

    .settings-hint {
      font-size: 0.85rem;
      color: #666;
      margin-bottom: 12px;
      font-style: italic;
    }

    .settings-section label {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      font-size: 0.95rem;
      color: #444;
    }

    .settings-input {
      width: 80px;
      padding: 8px 10px;
      border: 2px solid #e0e0e0;
      border-radius: 4px;
      font-size: 0.9rem;
      text-align: center;
      transition: border-color 0.2s;
    }

    .settings-input:focus {
      outline: none;
      border-color: #667eea;
    }

    .settings-buttons {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 16px 24px;
      background: #f9f9f9;
      border-top: 1px solid #e0e0e0;
      border-radius: 0 0 12px 12px;
    }

    .settings-btn-secondary {
      padding: 12px 20px;
      background: #e0e0e0;
      color: #333;
      border: none;
      border-radius: 6px;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .settings-btn-secondary:hover {
      background: #d0d0d0;
    }

    .settings-btn-primary {
      padding: 12px 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .settings-btn-primary:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    /* Settings select dropdown */
    .settings-select {
      width: 180px;
      text-align: left;
      padding: 8px 12px;
      background: white;
      cursor: pointer;
    }

    /* Advanced settings toggle */
    .settings-advanced-toggle {
      text-align: center;
      padding: 10px 0;
      border-bottom: none !important;
    }

    .settings-toggle-btn {
      background: none;
      border: 2px solid #e0e0e0;
      border-radius: 6px;
      padding: 10px 20px;
      font-size: 0.9rem;
      color: #666;
      cursor: pointer;
      transition: all 0.2s;
    }

    .settings-toggle-btn:hover {
      border-color: #667eea;
      color: #667eea;
    }

    /* Advanced settings container */
    .settings-advanced {
      background: #f9f9f9;
      border-radius: 8px;
      margin: 0 -24px;
      padding: 20px 24px;
      border-top: 1px solid #e0e0e0;
    }

    .settings-advanced .settings-section:first-child {
      margin-top: 0;
    }

    /* Settings matrix table */
    .settings-matrix {
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
    }

    .settings-matrix th,
    .settings-matrix td {
      padding: 8px;
      text-align: center;
      border: 1px solid #e0e0e0;
    }

    .settings-matrix th {
      background: #f3f4f6;
      font-weight: 600;
      font-size: 0.85rem;
      color: #444;
    }

    .settings-matrix-label {
      font-weight: 600;
      color: #444;
      background: #f9f9f9;
      text-align: left !important;
      padding-left: 12px !important;
    }

    .settings-matrix .settings-input {
      width: 60px;
      padding: 6px;
      font-size: 0.85rem;
    }

    @media (max-width: 1200px) {
      .filter-section {
        flex-direction: column;
        align-items: stretch;
      }

      .search-box, .filter-dropdown, .export-btn {
        width: 100%;
      }

      .comments-input {
        width: 150px;
      }
    }

    @media (max-width: 768px) {
      header {
        padding: 15px 20px;
      }

      .header-content {
        flex-direction: column;
        align-items: stretch;
        gap: 15px;
      }

      .header-title {
        text-align: center;
      }

      header h1 {
        font-size: 1.5rem;
        margin-bottom: 5px;
      }

      .overall-progress {
        font-size: 0.95rem;
      }

      .header-controls {
        justify-content: center;
        gap: 8px;
      }

      .tab-button {
        font-size: 0.9rem;
        padding: 10px 16px;
      }

      th, td {
        padding: 8px;
        font-size: 0.85rem;
      }

      .time-input {
        width: 80px;
      }

      .comments-input {
        width: 120px;
        min-height: 40px;
      }

      .settings-btn,
      .refresh-btn {
        width: 36px;
        height: 36px;
        font-size: 1.2rem;
      }

      .auth-btn {
        padding: 6px 12px;
        font-size: 0.8rem;
        max-width: 140px;
      }

      .auth-avatar {
        width: 20px;
        height: 20px;
      }

      .sync-status {
        font-size: 0.75rem;
      }

      .sync-icon {
        font-size: 12px;
      }

      .sync-now-btn {
        font-size: 12px;
        padding: 3px 6px;
      }
    }

    /* Settings form - remove default styling */
    #settings-form {
      margin: 0;
      padding: 0;
    }

    /* ============================================
       FIREBASE CLOUD SYNC STYLES
       ============================================ */

    /* Auth button */
    .auth-btn {
      background: rgba(255, 255, 255, 0.2);
      border: 2px solid rgba(255, 255, 255, 0.4);
      color: white;
      padding: 8px 16px;
      border-radius: 22px;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      gap: 8px;
      max-width: 180px;
      flex-shrink: 0;
    }

    .auth-btn:hover {
      background: rgba(255, 255, 255, 0.3);
      border-color: rgba(255, 255, 255, 0.6);
    }

    .auth-avatar {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      object-fit: cover;
    }

    #auth-text {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    /* Auth dropdown menu */
    .auth-menu {
      position: absolute;
      top: 70px;
      right: 30px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
      min-width: 250px;
      z-index: 1001;
      overflow: hidden;
    }

    .auth-menu-header {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 16px;
      background: #f9fafb;
      border-bottom: 1px solid #e0e0e0;
    }

    .auth-menu-avatar {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      object-fit: cover;
    }

    .auth-menu-info {
      flex: 1;
      overflow: hidden;
    }

    .auth-menu-name {
      font-weight: 600;
      color: #1f2937;
      font-size: 0.95rem;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .auth-menu-email {
      font-size: 0.85rem;
      color: #6b7280;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .auth-menu-divider {
      height: 1px;
      background: #e0e0e0;
    }

    .auth-menu-item {
      display: flex;
      align-items: center;
      gap: 10px;
      width: 100%;
      padding: 12px 16px;
      background: none;
      border: none;
      font-size: 0.95rem;
      color: #374151;
      cursor: pointer;
      text-align: left;
      transition: background 0.2s;
    }

    .auth-menu-item:hover {
      background: #f3f4f6;
    }

    /* Sync status indicator */
    .sync-status {
      display: flex;
      align-items: center;
      gap: 6px;
      color: white;
      font-size: 0.85rem;
      font-weight: 500;
    }

    .sync-icon {
      width: 14px;
      height: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
    }

    .sync-icon.offline {
      color: rgba(255, 255, 255, 0.6);
    }

    .sync-icon.syncing {
      color: #fbbf24;
      animation: spin 1s linear infinite;
    }

    .sync-icon.synced {
      color: #34d399;
    }

    .sync-icon.error {
      color: #f87171;
    }

    .sync-icon.quota-exceeded {
      color: #fb923c;
    }

    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }

    .sync-text {
      opacity: 0.9;
    }

    /* Toast notifications */
    .sync-toast {
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      padding: 12px 20px;
      border-radius: 8px;
      color: white;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 10px;
      z-index: 10000;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      animation: toast-slide-up 0.3s ease;
    }

    .sync-toast-warning {
      background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    }

    .sync-toast-error {
      background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    }

    .sync-toast-info {
      background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    }

    .sync-toast-success {
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    }

    .sync-toast-fade {
      opacity: 0;
      transition: opacity 0.3s ease;
    }

    .sync-toast-icon {
      font-size: 1.1rem;
    }

    .sync-toast-message {
      font-size: 0.9rem;
    }

    @keyframes toast-slide-up {
      from {
        opacity: 0;
        transform: translateX(-50%) translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
      }
    }

    /* Sync Now button */
    .sync-now-btn {
      background: rgba(255, 255, 255, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      color: white;
      font-size: 14px;
      cursor: pointer;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0;
      transition: all 0.2s ease;
      flex-shrink: 0;
    }

    .sync-now-btn:hover {
      background: rgba(255, 255, 255, 0.25);
      border-color: rgba(255, 255, 255, 0.5);
    }

    .sync-now-btn:active {
      transform: scale(0.95);
    }

    .sync-now-btn.syncing {
      animation: spin 1s linear infinite;
      pointer-events: none;
      opacity: 0.7;
    }

    /* Firebase setup notice */
    .firebase-setup-notice {
      display: flex;
      align-items: center;
      gap: 8px;
      color: rgba(255, 255, 255, 0.8);
      font-size: 0.85rem;
    }

    .firebase-setup-notice a {
      color: #fbbf24;
      text-decoration: underline;
    }

    .firebase-setup-notice a:hover {
      color: #fcd34d;
    }

    /* Sync conflict dialog */
    .sync-conflict-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.6);
      display: none;
      justify-content: center;
      align-items: center;
      z-index: 1100;
      padding: 20px;
    }

    .sync-conflict-panel {
      background: white;
      border-radius: 12px;
      max-width: 700px;
      width: 100%;
      max-height: 90vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }

    .sync-conflict-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px 24px;
      background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
      color: white;
    }

    .sync-conflict-header h2 {
      font-size: 1.3rem;
      margin: 0;
    }

    .sync-conflict-close {
      background: none;
      border: none;
      color: white;
      font-size: 2rem;
      cursor: pointer;
      line-height: 1;
      padding: 0;
      opacity: 0.8;
      transition: opacity 0.2s;
    }

    .sync-conflict-close:hover {
      opacity: 1;
    }

    .sync-conflict-description {
      padding: 16px 24px;
      background: #dbeafe;
      border-bottom: 1px solid #93c5fd;
      font-size: 0.95rem;
      color: #1e40af;
    }

    .sync-conflict-description p {
      margin: 0;
    }

    .sync-conflict-global-actions {
      display: flex;
      gap: 10px;
      padding: 16px 24px;
      background: #f9fafb;
      border-bottom: 1px solid #e0e0e0;
      flex-wrap: wrap;
    }

    .sync-conflict-global-actions button {
      padding: 8px 16px;
      background: #e5e7eb;
      color: #374151;
      border: none;
      border-radius: 6px;
      font-size: 0.9rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }

    .sync-conflict-global-actions button:hover {
      background: #d1d5db;
    }

    .sync-conflict-list {
      flex: 1;
      overflow-y: auto;
      padding: 16px 24px;
      max-height: 400px;
    }

    .sync-conflict-item {
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      margin-bottom: 16px;
      overflow: hidden;
    }

    .sync-conflict-item:last-child {
      margin-bottom: 0;
    }

    .sync-conflict-name {
      background: #f3f4f6;
      padding: 12px 16px;
      font-weight: 600;
      color: #1f2937;
      border-bottom: 1px solid #e0e0e0;
    }

    .sync-conflict-comparison {
      display: flex;
      gap: 16px;
      padding: 16px;
    }

    .sync-conflict-local,
    .sync-conflict-cloud {
      flex: 1;
      background: #f9fafb;
      padding: 12px;
      border-radius: 6px;
      font-size: 0.9rem;
    }

    .sync-conflict-local h4,
    .sync-conflict-cloud h4 {
      font-size: 0.8rem;
      color: #6b7280;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .sync-conflict-local div,
    .sync-conflict-cloud div {
      margin-bottom: 4px;
      color: #374151;
    }

    .sync-conflict-options {
      display: flex;
      gap: 16px;
      padding: 12px 16px;
      background: #f9fafb;
      border-top: 1px solid #e0e0e0;
    }

    .sync-conflict-options label {
      display: flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      font-size: 0.9rem;
    }

    .sync-conflict-options input[type="radio"] {
      width: 16px;
      height: 16px;
      accent-color: #3b82f6;
    }

    .sync-conflict-footer {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      padding: 16px 24px;
      background: #f9f9f9;
      border-top: 1px solid #e0e0e0;
    }

    .sync-conflict-btn-secondary {
      padding: 12px 24px;
      background: #e0e0e0;
      color: #333;
      border: none;
      border-radius: 6px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .sync-conflict-btn-secondary:hover {
      background: #d0d0d0;
    }

    .sync-conflict-btn-primary {
      padding: 12px 24px;
      background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .sync-conflict-btn-primary:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }

    /* Cloud sync section in settings */
    #cloud-sync-section .settings-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 10px;
      font-size: 0.95rem;
    }

    #cloud-sync-section .settings-row span:first-child {
      color: #666;
    }

    #cloud-sync-section .settings-row span:last-child {
      font-weight: 600;
      color: #333;
    }

    #cloud-sync-section button {
      padding: 10px 16px;
      margin-right: 8px;
      margin-top: 12px;
      background: #e5e7eb;
      color: #374151;
      border: none;
      border-radius: 6px;
      font-size: 0.9rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }

    #cloud-sync-section button:hover {
      background: #d1d5db;
    }

    /* Responsive adjustments for Firebase UI */
    @media (max-width: 768px) {
      .auth-menu {
        right: 15px;
        top: auto;
        min-width: 200px;
      }

      .firebase-setup-notice {
        font-size: 0.75rem;
      }

      .sync-conflict-comparison {
        flex-direction: column;
      }

      .sync-conflict-options {
        flex-direction: column;
        gap: 8px;
      }
    }
    """

    return css


if __name__ == "__main__":
    print(generate_css())
