#!/usr/bin/env python3
"""
Cross-File Sync Engine Sub-Agent
Synchronizes edits across duplicate problems
"""


def generate_js_sync():
    """Generate JavaScript sync logic"""

    js = """
    // Sync duplicate problems across all files
    function syncDuplicates(problemName, field, value) {
      // Check if this problem appears in multiple files
      if (!DUPLICATE_MAP[problemName] || DUPLICATE_MAP[problemName].length <= 1) {
        return; // Not a duplicate, no sync needed
      }

      // Update all instances across all files
      DUPLICATE_MAP[problemName].forEach(fileKey => {
        const problems = PROBLEM_DATA.data[fileKey];
        const problemIdx = problems.findIndex(p => p.name === problemName);

        if (problemIdx !== -1) {
          // Update the data
          problems[problemIdx][field] = value;

          // Update the DOM
          updateDOMField(fileKey, problemIdx, field, value);

          // Save to localStorage
          saveToLocalStorage(fileKey);

          // Update awareness color for this row
          updateRowAwareness(fileKey, problemIdx);
        }
      });

      // Update progress bars
      DUPLICATE_MAP[problemName].forEach(fileKey => {
        updateProgress(fileKey);
      });
      updateOverallProgress();
    }

    // Update DOM field for a specific problem
    function updateDOMField(fileKey, problemIdx, field, value) {
      const tbody = document.getElementById(`tbody-${fileKey}`);
      if (!tbody) return;

      const row = tbody.querySelector(`tr[data-index="${problemIdx}"]`);
      if (!row) return;

      switch (field) {
        case 'solved':
          const checkbox = row.querySelector('.checkbox-input');
          if (checkbox) {
            checkbox.checked = value;
          }
          break;

        case 'time_to_solve':
          const timeInput = row.querySelector('.time-input');
          if (timeInput) {
            timeInput.value = value;
          }
          break;

        case 'comments':
          const commentsInput = row.querySelector('.comments-input');
          if (commentsInput) {
            commentsInput.value = value;
          }
          break;

        case 'solved_date':
          updateSolvedDateDisplay(fileKey, problemIdx);
          break;
      }
    }
    """

    return js


if __name__ == "__main__":
    print(generate_js_sync())
