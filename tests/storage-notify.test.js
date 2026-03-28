/**
 * Unit Tests for Storage Notification Functions
 */

import {
  showStorageToast,
  saveToLocalStorage,
  loadFromLocalStorage,
  isLocalStorageAvailable,
  TOAST_DISMISS_MS
} from './storage-notify.js';

// --- Minimal DOM mock ---
function makeDocument() {
  const elements = [];
  const byId = {};
  const body = {
    children: elements,
    appendChild(el) {
      el.parentNode = body;
      elements.push(el);
      if (el.id) byId[el.id] = el;
    },
    removeChild(el) {
      const idx = elements.indexOf(el);
      if (idx !== -1) elements.splice(idx, 1);
      if (el.id && byId[el.id] === el) delete byId[el.id];
    }
  };
  return {
    body,
    getElementById(id) { return byId[id] || null; },
    createElement(tag) {
      return {
        tag,
        id: '',
        className: '',
        textContent: '',
        parentNode: null,
        remove() { if (this.parentNode) this.parentNode.removeChild(this); }
      };
    },
    _getToasts() { return elements; }
  };
}

// --- Minimal localStorage mock ---
function makeLocalStorage(throwOnSet = false, throwOnGet = false) {
  const store = {};
  return {
    _store: store,
    setItem(key, val) {
      if (throwOnSet) throw new DOMException('QuotaExceededError', 'QuotaExceededError');
      store[key] = val;
    },
    getItem(key) {
      if (throwOnGet) throw new Error('Storage access denied');
      return Object.prototype.hasOwnProperty.call(store, key) ? store[key] : null;
    },
    removeItem(key) { delete store[key]; }
  };
}

// Synchronous fake setTimeout
function makeFakeTimer() {
  const pending = [];
  const fn = (cb, delay) => pending.push({ cb, delay });
  fn._pending = pending;
  fn.flush = () => { pending.forEach(t => t.cb()); pending.length = 0; };
  return fn;
}

// ─────────────────────────────────────────────
// showStorageToast
// ─────────────────────────────────────────────
describe('showStorageToast', () => {
  let doc;
  let fakeTimer;

  beforeEach(() => {
    doc = makeDocument();
    fakeTimer = makeFakeTimer();
  });

  it('creates element and appends it to document.body', () => {
    const toast = showStorageToast('test message', 'warning', doc, fakeTimer);
    expect(toast).not.toBeNull();
    expect(doc._getToasts()).toContain(toast);
  });

  it('sets id to storage-toast', () => {
    const toast = showStorageToast('msg', 'warning', doc, fakeTimer);
    expect(toast.id).toBe('storage-toast');
  });

  it('sets sync-toast CSS class', () => {
    const toast = showStorageToast('msg', 'warning', doc, fakeTimer);
    expect(toast.className).toContain('sync-toast');
  });

  it('sets sync-toast-warning class for warning type', () => {
    const toast = showStorageToast('msg', 'warning', doc, fakeTimer);
    expect(toast.className).toContain('sync-toast-warning');
  });

  it('sets sync-toast-error class for error type', () => {
    const toast = showStorageToast('msg', 'error', doc, fakeTimer);
    expect(toast.className).toContain('sync-toast-error');
  });

  it('uses warning class for any non-error type', () => {
    const toast = showStorageToast('msg', 'warning', doc, fakeTimer);
    expect(toast.className).not.toContain('sync-toast-error');
  });

  it('sets textContent to the message', () => {
    const toast = showStorageToast('Storage full!', 'warning', doc, fakeTimer);
    expect(toast.textContent).toBe('Storage full!');
  });

  it('auto-dismisses after TOAST_DISMISS_MS', () => {
    const toast = showStorageToast('msg', 'warning', doc, fakeTimer);
    expect(doc._getToasts()).toContain(toast);
    fakeTimer.flush();
    expect(doc._getToasts()).not.toContain(toast);
  });

  it('schedules dismiss with TOAST_DISMISS_MS timeout (5000ms)', () => {
    showStorageToast('msg', 'error', doc, fakeTimer);
    expect(fakeTimer._pending.length).toBe(1);
    expect(fakeTimer._pending[0].delay).toBe(TOAST_DISMISS_MS);
    expect(TOAST_DISMISS_MS).toBe(5000);
  });

  it('removes existing #storage-toast before creating new one', () => {
    showStorageToast('first', 'warning', doc, fakeTimer);
    expect(doc._getToasts().length).toBe(1);
    showStorageToast('second', 'error', doc, fakeTimer);
    const toasts = doc._getToasts();
    expect(toasts.length).toBe(1);
    expect(toasts[0].textContent).toBe('second');
  });

  it('returns null when document is null', () => {
    const result = showStorageToast('msg', 'warning', null, fakeTimer);
    expect(result).toBeNull();
  });

  it('does not throw when document is null', () => {
    expect(() => showStorageToast('msg', 'warning', null, fakeTimer)).not.toThrow();
  });
});

// ─────────────────────────────────────────────
// isLocalStorageAvailable
// ─────────────────────────────────────────────
describe('isLocalStorageAvailable', () => {
  it('returns true when localStorage works', () => {
    const ls = makeLocalStorage();
    expect(isLocalStorageAvailable(ls)).toBe(true);
  });

  it('returns false when localStorage.setItem throws', () => {
    const ls = makeLocalStorage(true);
    expect(isLocalStorageAvailable(ls)).toBe(false);
  });

  it('returns false when localStorage is null', () => {
    expect(isLocalStorageAvailable(null)).toBe(false);
  });

  it('does not leave residue after test write', () => {
    const ls = makeLocalStorage();
    isLocalStorageAvailable(ls);
    expect(ls._store['__storage_test__']).toBeUndefined();
  });

  it('does not show any toast on successful check', () => {
    const doc = makeDocument();
    const ls = makeLocalStorage();
    isLocalStorageAvailable(ls);
    expect(doc._getToasts().length).toBe(0);
  });
});

// ─────────────────────────────────────────────
// saveToLocalStorage
// ─────────────────────────────────────────────
describe('saveToLocalStorage', () => {
  let doc;
  let fakeTimer;

  beforeEach(() => {
    doc = makeDocument();
    fakeTimer = makeFakeTimer();
  });

  it('saves data under tracker_<fileKey> key', () => {
    const ls = makeLocalStorage();
    const data = [{ name: 'Two Sum', solved: true }];
    saveToLocalStorage('blind75', data, ls, doc, fakeTimer);
    expect(ls._store['tracker_blind75']).toBe(JSON.stringify(data));
  });

  it('does not show toast on successful save', () => {
    const ls = makeLocalStorage();
    saveToLocalStorage('blind75', [], ls, doc, fakeTimer);
    expect(doc._getToasts().length).toBe(0);
  });

  it('shows warning toast when localStorage throws', () => {
    const ls = makeLocalStorage(true);
    saveToLocalStorage('blind75', [], ls, doc, fakeTimer);
    expect(doc._getToasts().length).toBe(1);
    expect(doc._getToasts()[0].className).toContain('sync-toast-warning');
  });

  it('warning toast mentions save/export/backup', () => {
    const ls = makeLocalStorage(true);
    saveToLocalStorage('blind75', [], ls, doc, fakeTimer);
    const text = doc._getToasts()[0].textContent.toLowerCase();
    expect(text).toMatch(/save|export|backup/);
  });

  it('does not throw when localStorage is null', () => {
    expect(() => saveToLocalStorage('blind75', [], null, doc, fakeTimer)).not.toThrow();
  });
});

// ─────────────────────────────────────────────
// loadFromLocalStorage
// ─────────────────────────────────────────────
describe('loadFromLocalStorage', () => {
  let doc;
  let fakeTimer;

  beforeEach(() => {
    doc = makeDocument();
    fakeTimer = makeFakeTimer();
  });

  it('returns parsed data when key exists', () => {
    const ls = makeLocalStorage();
    const data = [{ name: 'Two Sum', solved: true }];
    ls._store['tracker_blind75'] = JSON.stringify(data);
    const result = loadFromLocalStorage('blind75', ls, doc, fakeTimer);
    expect(result).toEqual(data);
  });

  it('returns null when key does not exist', () => {
    const ls = makeLocalStorage();
    const result = loadFromLocalStorage('blind75', ls, doc, fakeTimer);
    expect(result).toBeNull();
  });

  it('does not show toast on successful load', () => {
    const ls = makeLocalStorage();
    ls._store['tracker_blind75'] = JSON.stringify([]);
    loadFromLocalStorage('blind75', ls, doc, fakeTimer);
    expect(doc._getToasts().length).toBe(0);
  });

  it('shows error toast when stored value is invalid JSON', () => {
    const ls = makeLocalStorage();
    ls._store['tracker_blind75'] = 'not-valid-json{{{';
    loadFromLocalStorage('blind75', ls, doc, fakeTimer);
    expect(doc._getToasts().length).toBe(1);
    expect(doc._getToasts()[0].className).toContain('sync-toast-error');
  });

  it('returns null on JSON parse error', () => {
    const ls = makeLocalStorage();
    ls._store['tracker_blind75'] = '{bad json';
    const result = loadFromLocalStorage('blind75', ls, doc, fakeTimer);
    expect(result).toBeNull();
  });

  it('error toast message mentions load/corrupted/progress', () => {
    const ls = makeLocalStorage();
    ls._store['tracker_blind75'] = 'bad json';
    loadFromLocalStorage('blind75', ls, doc, fakeTimer);
    const text = doc._getToasts()[0].textContent.toLowerCase();
    expect(text).toMatch(/load|corrupt|progress/);
  });

  it('does not throw when localStorage is null', () => {
    expect(() => loadFromLocalStorage('blind75', null, doc, fakeTimer)).not.toThrow();
  });

  it('returns null when localStorage is null', () => {
    expect(loadFromLocalStorage('blind75', null, doc, fakeTimer)).toBeNull();
  });
});

// ─────────────────────────────────────────────
// Integration: no toast on normal successful operations
// ─────────────────────────────────────────────
describe('Integration: no toast on normal operations', () => {
  it('completes full save-then-load cycle without any toasts', () => {
    const doc = makeDocument();
    const fakeTimer = makeFakeTimer();
    const ls = makeLocalStorage();
    const data = [{ name: 'Valid Parentheses', solved: false }];

    saveToLocalStorage('neetcode', data, ls, doc, fakeTimer);
    const loaded = loadFromLocalStorage('neetcode', ls, doc, fakeTimer);

    expect(loaded).toEqual(data);
    expect(doc._getToasts().length).toBe(0);
  });
});
