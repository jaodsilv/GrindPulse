/**
 * Import/Export Functionality Tests
 * Tests serialization, parsing, escape utilities, format detection, and conflict detection
 */

import {
  setMockProblemData,
  getMockProblemData,
  resetMockProblemData,
  MIME_TYPES,
  FILE_EXTENSIONS,
  filterByMode,
  getHeadersForMode,
  fieldFromHeader,
  parseFieldValue,
  detectModeFromFields,
  escapeTSVValue,
  escapeCSVValue,
  parseCSVLines,
  escapeXMLValue,
  escapeXMLAttr,
  formatYAMLValue,
  parseYAMLValue,
  serializeToTSV,
  serializeToCSV,
  serializeToJSON,
  serializeToXML,
  serializeToYAML,
  parseFromTSV,
  parseFromCSV,
  parseFromJSON,
  parseFromXML,
  parseFromYAML,
  detectFormat,
  detectConflicts
} from './import-export.js';

// Sample test data
const sampleProblems = [
  {
    name: 'Two Sum',
    difficulty: 'Easy',
    intermediate_time: '15',
    advanced_time: '10',
    top_time: '5',
    pattern: 'Hash Table',
    solved: true,
    time_to_solve: '12',
    comments: 'Classic problem',
    solved_date: '2024-01-15T10:30:00Z'
  },
  {
    name: 'Valid Parentheses',
    difficulty: 'Easy',
    intermediate_time: '20',
    advanced_time: '15',
    top_time: '8',
    pattern: 'Stack',
    solved: false,
    time_to_solve: '',
    comments: '',
    solved_date: ''
  }
];

beforeEach(() => {
  resetMockProblemData();
});

// ============================================
// MOCK DATA TESTS
// ============================================

describe('Mock Problem Data', () => {
  it('should get and set mock problem data', () => {
    const testData = {
      file_list: ['test'],
      data: { test: [{ name: 'Test Problem' }] }
    };
    setMockProblemData(testData);
    expect(getMockProblemData()).toEqual(testData);
  });

  it('should reset mock problem data', () => {
    setMockProblemData({ file_list: ['test'], data: {} });
    resetMockProblemData();
    const data = getMockProblemData();
    expect(data.file_list).toHaveLength(0);
    expect(data.data).toEqual({});
  });
});

// ============================================
// CONSTANTS TESTS
// ============================================

describe('Constants', () => {
  describe('MIME_TYPES', () => {
    it('should have correct MIME types for all formats', () => {
      expect(MIME_TYPES.tsv).toBe('text/tab-separated-values;charset=utf-8;');
      expect(MIME_TYPES.csv).toBe('text/csv;charset=utf-8;');
      expect(MIME_TYPES.json).toBe('application/json;charset=utf-8;');
      expect(MIME_TYPES.xml).toBe('application/xml;charset=utf-8;');
      expect(MIME_TYPES.yaml).toBe('text/yaml;charset=utf-8;');
    });
  });

  describe('FILE_EXTENSIONS', () => {
    it('should have correct extensions for all formats', () => {
      expect(FILE_EXTENSIONS.tsv).toBe('.tsv');
      expect(FILE_EXTENSIONS.csv).toBe('.csv');
      expect(FILE_EXTENSIONS.json).toBe('.json');
      expect(FILE_EXTENSIONS.xml).toBe('.xml');
      expect(FILE_EXTENSIONS.yaml).toBe('.yaml');
    });
  });
});

// ============================================
// MODE FILTERING TESTS
// ============================================

describe('filterByMode', () => {
  it('should filter to problems mode correctly', () => {
    const filtered = filterByMode(sampleProblems, 'problems');
    expect(filtered[0]).toHaveProperty('name');
    expect(filtered[0]).toHaveProperty('difficulty');
    expect(filtered[0]).toHaveProperty('pattern');
    expect(filtered[0]).not.toHaveProperty('solved');
    expect(filtered[0]).not.toHaveProperty('comments');
  });

  it('should filter to user mode correctly', () => {
    const filtered = filterByMode(sampleProblems, 'user');
    expect(filtered[0]).toHaveProperty('name');
    expect(filtered[0]).toHaveProperty('solved');
    expect(filtered[0]).toHaveProperty('comments');
    expect(filtered[0]).not.toHaveProperty('difficulty');
    expect(filtered[0]).not.toHaveProperty('pattern');
  });

  it('should include all fields in full mode', () => {
    const filtered = filterByMode(sampleProblems, 'full');
    expect(filtered[0]).toHaveProperty('name');
    expect(filtered[0]).toHaveProperty('difficulty');
    expect(filtered[0]).toHaveProperty('solved');
    expect(filtered[0]).toHaveProperty('comments');
  });

  it('should default to full mode for unknown mode', () => {
    const filtered = filterByMode(sampleProblems, 'unknown');
    expect(filtered[0]).toHaveProperty('solved');
    expect(filtered[0]).toHaveProperty('difficulty');
  });
});

// ============================================
// HELPER FUNCTIONS TESTS
// ============================================

describe('getHeadersForMode', () => {
  it('should return problem headers for problems mode', () => {
    const headers = getHeadersForMode('problems');
    expect(headers).toContain('Problem Name');
    expect(headers).toContain('Difficulty');
    expect(headers).toContain('Pattern');
    expect(headers).not.toContain('Solved');
  });

  it('should return user headers for user mode', () => {
    const headers = getHeadersForMode('user');
    expect(headers).toContain('Problem Name');
    expect(headers).toContain('Solved');
    expect(headers).toContain('Comments');
    expect(headers).not.toContain('Difficulty');
  });

  it('should return all headers for full mode', () => {
    const headers = getHeadersForMode('full');
    expect(headers).toContain('Problem Name');
    expect(headers).toContain('Difficulty');
    expect(headers).toContain('Solved');
    expect(headers.length).toBe(10);
  });
});

describe('fieldFromHeader', () => {
  it('should map standard headers correctly', () => {
    expect(fieldFromHeader('Problem Name')).toBe('name');
    expect(fieldFromHeader('Difficulty')).toBe('difficulty');
    expect(fieldFromHeader('Solved')).toBe('solved');
  });

  it('should handle alternate header names', () => {
    expect(fieldFromHeader('Intermediate Max time')).toBe('intermediate_time');
    expect(fieldFromHeader('Advanced Max time')).toBe('advanced_time');
    expect(fieldFromHeader('Problem Pattern')).toBe('pattern');
  });

  it('should convert unknown headers to snake_case', () => {
    expect(fieldFromHeader('Custom Field')).toBe('custom_field');
    expect(fieldFromHeader('Another Header')).toBe('another_header');
  });
});

describe('parseFieldValue', () => {
  it('should parse solved field as boolean', () => {
    expect(parseFieldValue('solved', 'true')).toBe(true);
    expect(parseFieldValue('solved', 'false')).toBe(false);
    expect(parseFieldValue('solved', '1')).toBe(true);
    expect(parseFieldValue('solved', '0')).toBe(false);
  });

  it('should trim string values', () => {
    expect(parseFieldValue('name', '  Two Sum  ')).toBe('Two Sum');
  });

  it('should handle null/undefined', () => {
    expect(parseFieldValue('name', null)).toBe('');
    expect(parseFieldValue('name', undefined)).toBe('');
  });
});

describe('detectModeFromFields', () => {
  it('should detect user mode', () => {
    expect(detectModeFromFields({ name: 'Test', solved: true })).toBe('user');
  });

  it('should detect problems mode', () => {
    expect(detectModeFromFields({ name: 'Test', difficulty: 'Easy' })).toBe('problems');
  });

  it('should detect full mode', () => {
    expect(detectModeFromFields({ name: 'Test', difficulty: 'Easy', solved: true })).toBe('full');
  });

  it('should default to full for null/undefined', () => {
    expect(detectModeFromFields(null)).toBe('full');
    expect(detectModeFromFields(undefined)).toBe('full');
  });
});

// ============================================
// ESCAPE UTILITIES TESTS
// ============================================

describe('escapeTSVValue', () => {
  it('should escape tabs', () => {
    expect(escapeTSVValue('hello\tworld')).toBe('hello world');
  });

  it('should escape newlines', () => {
    expect(escapeTSVValue('hello\nworld')).toBe('hello world');
  });

  it('should handle booleans', () => {
    expect(escapeTSVValue(true)).toBe('true');
    expect(escapeTSVValue(false)).toBe('false');
  });

  it('should handle null/undefined', () => {
    expect(escapeTSVValue(null)).toBe('');
    expect(escapeTSVValue(undefined)).toBe('');
  });
});

describe('escapeCSVValue', () => {
  it('should quote values with commas', () => {
    expect(escapeCSVValue('hello, world')).toBe('"hello, world"');
  });

  it('should double escape quotes', () => {
    expect(escapeCSVValue('say "hello"')).toBe('"say ""hello"""');
  });

  it('should quote values with newlines', () => {
    expect(escapeCSVValue('hello\nworld')).toBe('"hello\nworld"');
  });

  it('should not quote simple values', () => {
    expect(escapeCSVValue('hello')).toBe('hello');
  });

  it('should handle booleans', () => {
    expect(escapeCSVValue(true)).toBe('true');
    expect(escapeCSVValue(false)).toBe('false');
  });
});

describe('parseCSVLines', () => {
  it('should parse simple CSV', () => {
    const lines = parseCSVLines('a,b,c\n1,2,3');
    expect(lines).toEqual([['a', 'b', 'c'], ['1', '2', '3']]);
  });

  it('should handle quoted values', () => {
    const lines = parseCSVLines('a,"b,c",d\n1,2,3');
    expect(lines[0]).toEqual(['a', 'b,c', 'd']);
  });

  it('should handle escaped quotes', () => {
    const lines = parseCSVLines('a,"say ""hello""",c');
    expect(lines[0][1]).toBe('say "hello"');
  });

  it('should handle newlines in quotes', () => {
    const lines = parseCSVLines('a,"hello\nworld",c');
    expect(lines[0][1]).toBe('hello\nworld');
  });
});

describe('escapeXMLValue', () => {
  it('should escape &', () => {
    expect(escapeXMLValue('a & b')).toBe('a &amp; b');
  });

  it('should escape <', () => {
    expect(escapeXMLValue('a < b')).toBe('a &lt; b');
  });

  it('should escape >', () => {
    expect(escapeXMLValue('a > b')).toBe('a &gt; b');
  });

  it('should handle booleans', () => {
    expect(escapeXMLValue(true)).toBe('true');
    expect(escapeXMLValue(false)).toBe('false');
  });
});

describe('escapeXMLAttr', () => {
  it('should escape quotes', () => {
    expect(escapeXMLAttr('say "hello"')).toBe('say &quot;hello&quot;');
  });
});

describe('formatYAMLValue', () => {
  it('should quote strings with colons', () => {
    expect(formatYAMLValue('key: value')).toBe('"key: value"');
  });

  it('should quote strings with special chars', () => {
    expect(formatYAMLValue('hello # comment')).toBe('"hello # comment"');
  });

  it('should handle booleans', () => {
    expect(formatYAMLValue(true)).toBe('true');
    expect(formatYAMLValue(false)).toBe('false');
  });

  it('should handle null/undefined', () => {
    expect(formatYAMLValue(null)).toBe('""');
    expect(formatYAMLValue(undefined)).toBe('""');
  });
});

describe('parseYAMLValue', () => {
  it('should remove double quotes', () => {
    expect(parseYAMLValue('"hello"')).toBe('hello');
  });

  it('should remove single quotes', () => {
    expect(parseYAMLValue("'hello'")).toBe('hello');
  });

  it('should trim whitespace', () => {
    expect(parseYAMLValue('  hello  ')).toBe('hello');
  });
});

// ============================================
// SERIALIZATION TESTS
// ============================================

describe('serializeToTSV', () => {
  it('should create valid TSV', () => {
    const tsv = serializeToTSV(filterByMode(sampleProblems, 'problems'), 'problems');
    const lines = tsv.split('\n');
    expect(lines[0].split('\t')).toContain('Problem Name');
    expect(lines[1]).toContain('Two Sum');
  });

  it('should include correct columns for user mode', () => {
    const tsv = serializeToTSV(filterByMode(sampleProblems, 'user'), 'user');
    expect(tsv).toContain('Solved');
    expect(tsv).not.toContain('Difficulty');
  });
});

describe('serializeToCSV', () => {
  it('should create valid CSV', () => {
    const csv = serializeToCSV(filterByMode(sampleProblems, 'problems'), 'problems');
    const lines = csv.split('\n');
    expect(lines[0]).toContain('Problem Name');
  });

  it('should properly quote values with commas', () => {
    const problems = [{ ...sampleProblems[0], comments: 'hello, world' }];
    const csv = serializeToCSV(filterByMode(problems, 'user'), 'user');
    expect(csv).toContain('"hello, world"');
  });
});

describe('serializeToJSON', () => {
  it('should create valid JSON', () => {
    const json = serializeToJSON(sampleProblems, 'full', 'test');
    const parsed = JSON.parse(json);
    expect(parsed.fileKey).toBe('test');
    expect(parsed.mode).toBe('full');
    expect(parsed.problems).toHaveLength(2);
  });

  it('should include version and exportDate', () => {
    const json = serializeToJSON(sampleProblems, 'full', 'test');
    const parsed = JSON.parse(json);
    expect(parsed.version).toBe('1.0');
    expect(parsed.exportDate).toBeDefined();
  });
});

describe('serializeToXML', () => {
  it('should create valid XML structure', () => {
    const xml = serializeToXML(sampleProblems, 'full', 'test');
    expect(xml).toContain('<?xml version="1.0"');
    expect(xml).toContain('<export fileKey="test"');
    expect(xml).toContain('<problems>');
    expect(xml).toContain('<problem>');
  });

  it('should escape special characters', () => {
    const problems = [{ ...sampleProblems[0], comments: 'a < b & c > d' }];
    const xml = serializeToXML(problems, 'full', 'test');
    expect(xml).toContain('&lt;');
    expect(xml).toContain('&amp;');
    expect(xml).toContain('&gt;');
  });
});

describe('serializeToYAML', () => {
  it('should create valid YAML structure', () => {
    const yaml = serializeToYAML(sampleProblems, 'full', 'test');
    expect(yaml).toContain('fileKey: test');
    expect(yaml).toContain('mode: full');
    expect(yaml).toContain('problems:');
    expect(yaml).toContain('- name:');
  });
});

// ============================================
// PARSING TESTS
// ============================================

describe('parseFromTSV', () => {
  it('should parse valid TSV', () => {
    const tsv = 'Problem Name\tDifficulty\nTwo Sum\tEasy';
    const result = parseFromTSV(tsv);
    expect(result.problems).toHaveLength(1);
    expect(result.problems[0].name).toBe('Two Sum');
    expect(result.problems[0].difficulty).toBe('Easy');
  });

  it('should return empty for invalid TSV', () => {
    const result = parseFromTSV('only one line');
    expect(result.problems).toHaveLength(0);
  });
});

describe('parseFromCSV', () => {
  it('should parse valid CSV', () => {
    const csv = 'Problem Name,Difficulty\nTwo Sum,Easy';
    const result = parseFromCSV(csv);
    expect(result.problems).toHaveLength(1);
    expect(result.problems[0].name).toBe('Two Sum');
  });

  it('should handle quoted values', () => {
    const csv = 'Problem Name,Comments\nTwo Sum,"hello, world"';
    const result = parseFromCSV(csv);
    expect(result.problems[0].comments).toBe('hello, world');
  });
});

describe('parseFromJSON', () => {
  it('should parse object format', () => {
    const json = '{"fileKey":"test","problems":[{"name":"Two Sum"}]}';
    const result = parseFromJSON(json);
    expect(result.fileKey).toBe('test');
    expect(result.problems[0].name).toBe('Two Sum');
  });

  it('should parse array format', () => {
    const json = '[{"name":"Two Sum","difficulty":"Easy"}]';
    const result = parseFromJSON(json);
    expect(result.problems[0].name).toBe('Two Sum');
    expect(result.mode).toBe('problems');
  });

  it('should handle invalid JSON', () => {
    const result = parseFromJSON('invalid json');
    expect(result.problems).toHaveLength(0);
  });
});

// ============================================
// MOCK DOMPARSER FOR XML TESTS
// ============================================

/**
 * Mock DOMParser for Node.js environment
 * Simulates browser DOMParser API for testing XML parsing
 */
class MockDOMParser {
  parseFromString(content, mimeType) {
    // Create mock document object
    const doc = {
      _content: content,
      querySelector: (selector) => {
        if (selector === 'export') {
          // Extract export element attributes
          const exportMatch = content.match(/<export\s+([^>]+)>/);
          if (!exportMatch) return null;

          const attrs = exportMatch[1];
          const fileKeyMatch = attrs.match(/fileKey="([^"]*)"/);
          const modeMatch = attrs.match(/mode="([^"]*)"/);

          return {
            getAttribute: (name) => {
              if (name === 'fileKey' && fileKeyMatch) return fileKeyMatch[1];
              if (name === 'mode' && modeMatch) return modeMatch[1];
              return null;
            }
          };
        }

        if (selector === 'parsererror') {
          // Check for basic XML errors
          if (!content.includes('<export') || !content.includes('</export>')) {
            return { _error: true };
          }
          return null;
        }

        return null;
      },
      querySelectorAll: (selector) => {
        if (selector === 'problem') {
          // Extract all problem elements
          const problemMatches = content.matchAll(/<problem>([\s\S]*?)<\/problem>/g);
          const problems = [];

          for (const match of problemMatches) {
            const problemContent = match[1];
            const element = {
              children: []
            };

            // Extract all child elements
            const childMatches = problemContent.matchAll(/<(\w+)>(.*?)<\/\1>/g);
            for (const childMatch of childMatches) {
              element.children.push({
                tagName: childMatch[1],
                textContent: childMatch[2]
                  .replace(/&lt;/g, '<')
                  .replace(/&gt;/g, '>')
                  .replace(/&quot;/g, '"')
                  .replace(/&amp;/g, '&')
              });
            }

            problems.push(element);
          }

          return problems;
        }

        return [];
      }
    };

    return doc;
  }
}

describe('parseFromXML', () => {
  const mockParser = new MockDOMParser();

  it('should parse valid XML correctly', () => {
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<export fileKey="test" mode="full" exportDate="2024-01-01T00:00:00Z" version="1.0">
  <problems>
    <problem>
      <name>Two Sum</name>
      <difficulty>Easy</difficulty>
      <pattern>Hash Table</pattern>
    </problem>
  </problems>
</export>`;

    const result = parseFromXML(xml, mockParser);
    expect(result.fileKey).toBe('test');
    expect(result.mode).toBe('full');
    expect(result.problems).toHaveLength(1);
    expect(result.problems[0].name).toBe('Two Sum');
    expect(result.problems[0].difficulty).toBe('Easy');
    expect(result.problems[0].pattern).toBe('Hash Table');
  });

  it('should handle XML with multiple problems', () => {
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<export fileKey="test" mode="problems" exportDate="2024-01-01T00:00:00Z" version="1.0">
  <problems>
    <problem>
      <name>Two Sum</name>
      <difficulty>Easy</difficulty>
    </problem>
    <problem>
      <name>Valid Parentheses</name>
      <difficulty>Easy</difficulty>
    </problem>
  </problems>
</export>`;

    const result = parseFromXML(xml, mockParser);
    expect(result.problems).toHaveLength(2);
    expect(result.problems[0].name).toBe('Two Sum');
    expect(result.problems[1].name).toBe('Valid Parentheses');
  });

  it('should extract fileKey and mode attributes', () => {
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<export fileKey="blind75" mode="user" exportDate="2024-01-01T00:00:00Z" version="1.0">
  <problems>
    <problem>
      <name>Two Sum</name>
      <solved>true</solved>
    </problem>
  </problems>
</export>`;

    const result = parseFromXML(xml, mockParser);
    expect(result.fileKey).toBe('blind75');
    expect(result.mode).toBe('user');
  });

  it('should handle XML with escaped characters', () => {
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<export fileKey="test" mode="full" exportDate="2024-01-01T00:00:00Z" version="1.0">
  <problems>
    <problem>
      <name>Test Problem</name>
      <comments>a &lt; b &amp; c &gt; d</comments>
    </problem>
  </problems>
</export>`;

    const result = parseFromXML(xml, mockParser);
    expect(result.problems[0].comments).toBe('a < b & c > d');
  });

  it('should handle XML with missing export element', () => {
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<problems>
  <problem>
    <name>Two Sum</name>
    <difficulty>Easy</difficulty>
  </problem>
</problems>`;

    const result = parseFromXML(xml, mockParser);
    expect(result.fileKey).toBeNull();
    expect(result.mode).toBe('problems'); // Should auto-detect mode
    expect(result.problems).toHaveLength(1);
  });

  it('should handle empty XML content', () => {
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<export fileKey="test" mode="full" exportDate="2024-01-01T00:00:00Z" version="1.0">
  <problems>
  </problems>
</export>`;

    const result = parseFromXML(xml, mockParser);
    expect(result.problems).toHaveLength(0);
    expect(result.fileKey).toBe('test');
  });

  it('should return empty array when DOMParser is not available', () => {
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<export fileKey="test" mode="full">
  <problems>
    <problem>
      <name>Two Sum</name>
    </problem>
  </problems>
</export>`;

    const result = parseFromXML(xml, null);
    expect(result.problems).toHaveLength(0);
    expect(result.fileKey).toBeNull();
    expect(result.mode).toBeNull();
  });

  it('should handle boolean fields correctly', () => {
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<export fileKey="test" mode="user" exportDate="2024-01-01T00:00:00Z" version="1.0">
  <problems>
    <problem>
      <name>Two Sum</name>
      <solved>true</solved>
    </problem>
  </problems>
</export>`;

    const result = parseFromXML(xml, mockParser);
    expect(result.problems[0].solved).toBe(true);
  });

  it('should detect mode from fields when mode attribute is missing', () => {
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<export fileKey="test" exportDate="2024-01-01T00:00:00Z" version="1.0">
  <problems>
    <problem>
      <name>Two Sum</name>
      <difficulty>Easy</difficulty>
      <pattern>Hash Table</pattern>
    </problem>
  </problems>
</export>`;

    const result = parseFromXML(xml, mockParser);
    expect(result.mode).toBe('problems'); // Auto-detected
  });

  it('should handle parsing errors gracefully', () => {
    // Create a mock parser that throws an error
    const errorParser = {
      parseFromString: () => {
        throw new Error('Parse error');
      }
    };

    const xml = `<?xml version="1.0" encoding="UTF-8"?><export></export>`;
    const result = parseFromXML(xml, errorParser);
    expect(result.problems).toHaveLength(0);
    expect(result.fileKey).toBeNull();
    expect(result.mode).toBeNull();
  });
});

describe('parseFromYAML', () => {
  it('should parse valid YAML', () => {
    const yaml = `fileKey: test
mode: full
problems:
  - name: Two Sum
    difficulty: Easy`;
    const result = parseFromYAML(yaml);
    expect(result.fileKey).toBe('test');
    expect(result.problems[0].name).toBe('Two Sum');
  });

  it('should handle inline values', () => {
    const yaml = `problems:
  - name: Two Sum
    difficulty: Easy`;
    const result = parseFromYAML(yaml);
    expect(result.problems[0].difficulty).toBe('Easy');
  });

  it('should handle multiple problems in YAML', () => {
    const yaml = `fileKey: test
mode: problems
problems:
  - name: Two Sum
    difficulty: Easy
  - name: Valid Parentheses
    difficulty: Easy`;
    const result = parseFromYAML(yaml);
    expect(result.problems).toHaveLength(2);
    expect(result.problems[0].name).toBe('Two Sum');
    expect(result.problems[1].name).toBe('Valid Parentheses');
  });

  it('should handle YAML with comments', () => {
    const yaml = `# This is a comment
fileKey: test
# Another comment
problems:
  - name: Two Sum`;
    const result = parseFromYAML(yaml);
    expect(result.fileKey).toBe('test');
    expect(result.problems[0].name).toBe('Two Sum');
  });

  it('should handle dash without value on same line', () => {
    const yaml = `problems:
  - name: Two Sum`;
    const result = parseFromYAML(yaml);
    expect(result.problems).toHaveLength(1);
    expect(result.problems[0].name).toBe('Two Sum');
  });

  it('should handle empty YAML', () => {
    const result = parseFromYAML('');
    expect(result.problems).toHaveLength(0);
  });

  it('should handle YAML with only fileKey', () => {
    const yaml = `fileKey: test
mode: full`;
    const result = parseFromYAML(yaml);
    expect(result.fileKey).toBe('test');
    expect(result.mode).toBe('full');
    expect(result.problems).toHaveLength(0);
  });
});

// ============================================
// FORMAT DETECTION TESTS
// ============================================

describe('detectFormat', () => {
  it('should detect by extension', () => {
    expect(detectFormat('data.tsv', '')).toBe('tsv');
    expect(detectFormat('data.csv', '')).toBe('csv');
    expect(detectFormat('data.json', '')).toBe('json');
    expect(detectFormat('data.xml', '')).toBe('xml');
    expect(detectFormat('data.yaml', '')).toBe('yaml');
    expect(detectFormat('data.yml', '')).toBe('yaml');
  });

  it('should detect JSON by content', () => {
    expect(detectFormat('unknown.txt', '{"key":"value"}')).toBe('json');
    expect(detectFormat('unknown.txt', '[1,2,3]')).toBe('json');
  });

  it('should detect XML by content', () => {
    expect(detectFormat('unknown.txt', '<?xml version="1.0"?><data/>')).toBe('xml');
    expect(detectFormat('unknown.txt', '<export>')).toBe('xml');
  });

  it('should detect TSV by content', () => {
    expect(detectFormat('unknown.txt', 'a\tb\tc')).toBe('tsv');
  });

  it('should detect YAML by content', () => {
    expect(detectFormat('unknown.txt', 'fileKey: test')).toBe('yaml');
    expect(detectFormat('unknown.txt', 'problems:')).toBe('yaml');
  });

  it('should default to CSV', () => {
    expect(detectFormat('unknown.txt', 'a,b,c')).toBe('csv');
  });
});

// ============================================
// CONFLICT DETECTION TESTS
// ============================================

describe('detectConflicts', () => {
  beforeEach(() => {
    setMockProblemData({
      file_list: ['test'],
      data: {
        test: [
          {
            name: 'Two Sum',
            difficulty: 'Easy',
            pattern: 'Hash Table',
            intermediate_time: '15',
            advanced_time: '10',
            top_time: '5',
            solved: false,
            time_to_solve: '',
            comments: '',
            solved_date: ''
          }
        ]
      }
    });
  });

  it('should detect user data conflict', () => {
    const imported = [{ name: 'Two Sum', solved: true }];
    const conflicts = detectConflicts('test', imported, 'user');
    expect(conflicts).toHaveLength(1);
    expect(conflicts[0].name).toBe('Two Sum');
  });

  it('should detect problem data conflict', () => {
    const imported = [{ name: 'Two Sum', difficulty: 'Medium' }];
    const conflicts = detectConflicts('test', imported, 'problems');
    expect(conflicts).toHaveLength(1);
  });

  it('should detect conflict in time_to_solve field', () => {
    const imported = [{ name: 'Two Sum', time_to_solve: '20' }];
    const conflicts = detectConflicts('test', imported, 'user');
    expect(conflicts).toHaveLength(1);
  });

  it('should detect conflict in comments field', () => {
    const imported = [{ name: 'Two Sum', comments: 'New comment' }];
    const conflicts = detectConflicts('test', imported, 'user');
    expect(conflicts).toHaveLength(1);
  });

  it('should detect conflict in solved_date field', () => {
    const imported = [{ name: 'Two Sum', solved_date: '2024-01-15T10:30:00Z' }];
    const conflicts = detectConflicts('test', imported, 'user');
    expect(conflicts).toHaveLength(1);
  });

  it('should detect conflict in pattern field', () => {
    const imported = [{ name: 'Two Sum', pattern: 'Array' }];
    const conflicts = detectConflicts('test', imported, 'problems');
    expect(conflicts).toHaveLength(1);
  });

  it('should detect conflict in intermediate_time field', () => {
    const imported = [{ name: 'Two Sum', intermediate_time: '20' }];
    const conflicts = detectConflicts('test', imported, 'problems');
    expect(conflicts).toHaveLength(1);
  });

  it('should detect conflict in advanced_time field', () => {
    const imported = [{ name: 'Two Sum', advanced_time: '15' }];
    const conflicts = detectConflicts('test', imported, 'problems');
    expect(conflicts).toHaveLength(1);
  });

  it('should detect conflict in top_time field', () => {
    const imported = [{ name: 'Two Sum', top_time: '3' }];
    const conflicts = detectConflicts('test', imported, 'problems');
    expect(conflicts).toHaveLength(1);
  });

  it('should detect conflicts in full mode for user fields', () => {
    const imported = [{ name: 'Two Sum', solved: true, difficulty: 'Easy' }];
    const conflicts = detectConflicts('test', imported, 'full');
    expect(conflicts).toHaveLength(1);
  });

  it('should detect conflicts in full mode for problem fields', () => {
    const imported = [{ name: 'Two Sum', difficulty: 'Medium', solved: false }];
    const conflicts = detectConflicts('test', imported, 'full');
    expect(conflicts).toHaveLength(1);
  });

  it('should not detect conflict for matching data', () => {
    const imported = [{ name: 'Two Sum', difficulty: 'Easy' }];
    const conflicts = detectConflicts('test', imported, 'problems');
    expect(conflicts).toHaveLength(0);
  });

  it('should not detect conflict for new problems', () => {
    const imported = [{ name: 'New Problem', difficulty: 'Hard' }];
    const conflicts = detectConflicts('test', imported, 'problems');
    expect(conflicts).toHaveLength(0);
  });

  it('should return empty for non-existent fileKey', () => {
    const conflicts = detectConflicts('nonexistent', [], 'full');
    expect(conflicts).toHaveLength(0);
  });
});

// ============================================
// ROUND-TRIP TESTS
// ============================================

describe('Round-trip serialization', () => {
  it('should round-trip TSV data', () => {
    const filtered = filterByMode(sampleProblems, 'problems');
    const tsv = serializeToTSV(filtered, 'problems');
    const result = parseFromTSV(tsv);
    expect(result.problems[0].name).toBe(sampleProblems[0].name);
    expect(result.problems[0].difficulty).toBe(sampleProblems[0].difficulty);
  });

  it('should round-trip CSV data', () => {
    const filtered = filterByMode(sampleProblems, 'problems');
    const csv = serializeToCSV(filtered, 'problems');
    const result = parseFromCSV(csv);
    expect(result.problems[0].name).toBe(sampleProblems[0].name);
  });

  it('should round-trip JSON data', () => {
    const json = serializeToJSON(sampleProblems, 'full', 'test');
    const result = parseFromJSON(json);
    expect(result.problems[0].name).toBe(sampleProblems[0].name);
    expect(result.fileKey).toBe('test');
    expect(result.mode).toBe('full');
  });

  it('should round-trip XML data', () => {
    const mockParser = new MockDOMParser();
    const xml = serializeToXML(sampleProblems, 'full', 'test');
    const result = parseFromXML(xml, mockParser);
    expect(result.problems[0].name).toBe(sampleProblems[0].name);
    expect(result.problems[0].difficulty).toBe(sampleProblems[0].difficulty);
    expect(result.fileKey).toBe('test');
    expect(result.mode).toBe('full');
  });

  it('should round-trip YAML data', () => {
    const filtered = filterByMode(sampleProblems, 'full');
    const yaml = serializeToYAML(filtered, 'full', 'test');
    const result = parseFromYAML(yaml);
    expect(result.problems[0].name).toBe(sampleProblems[0].name);
    expect(result.fileKey).toBe('test');
  });
});

// ============================================
// EDGE CASES
// ============================================

describe('Edge cases', () => {
  it('should handle empty problems array', () => {
    const tsv = serializeToTSV([], 'full');
    expect(tsv).toContain('Problem Name'); // Headers still present
    const result = parseFromTSV(tsv);
    expect(result.problems).toHaveLength(0);
  });

  it('should handle special characters in problem names', () => {
    const problems = [{ ...sampleProblems[0], name: 'Problem "with" <special> & chars' }];
    const json = serializeToJSON(problems, 'full', 'test');
    const result = parseFromJSON(json);
    expect(result.problems[0].name).toBe('Problem "with" <special> & chars');
  });

  it('should handle very long comments', () => {
    const longComment = 'a'.repeat(10000);
    const problems = [{ ...sampleProblems[0], comments: longComment }];
    const json = serializeToJSON(problems, 'full', 'test');
    const result = parseFromJSON(json);
    expect(result.problems[0].comments).toBe(longComment);
  });

  it('should handle unicode characters', () => {
    const problems = [{ ...sampleProblems[0], comments: '日本語 emoji: 🎉' }];
    const json = serializeToJSON(problems, 'full', 'test');
    const result = parseFromJSON(json);
    expect(result.problems[0].comments).toBe('日本語 emoji: 🎉');
  });
});
