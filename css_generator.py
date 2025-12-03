#!/usr/bin/env python3
"""
CSS Styling Sub-Agent
Creates modern, clean styling
"""

def generate_css():
    """Generate CSS styling"""

    css = '''
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
      padding: 30px;
      text-align: center;
    }

    header h1 {
      margin-bottom: 15px;
      font-size: 2.5rem;
    }

    .overall-progress {
      margin-top: 10px;
      font-size: 1.2rem;
      font-weight: 500;
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
      header h1 {
        font-size: 1.8rem;
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
    }
    '''

    return css

if __name__ == "__main__":
    print(generate_css())
