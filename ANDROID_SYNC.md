# Android Sync Compatibility Documentation

Technical specification for building an Android counterpart that syncs with the web tracker.

## 1. Firebase Project Configuration

> **Note**: Firebase configuration values are stored in `firebase_config.json` (gitignored).
> Get your config from the [Firebase Console](https://console.firebase.google.com/).

```json
{
  "apiKey": "<YOUR_API_KEY>",
  "authDomain": "<YOUR_PROJECT_ID>.firebaseapp.com",
  "projectId": "<YOUR_PROJECT_ID>",
  "storageBucket": "<YOUR_PROJECT_ID>.firebasestorage.app",
  "messagingSenderId": "<YOUR_MESSAGING_SENDER_ID>",
  "appId": "<YOUR_APP_ID>"
}
```

---

## 2. Firestore Data Structure

```
users/{uid}/
├── progress/{sanitizedProblemName}/    # User problem progress
└── config/
    ├── awareness/                       # Spaced repetition settings
    ├── filters/                         # Filter & tab state
    ├── exportPrefs/                     # Export format preferences
    └── uiPrefs/                         # Theme, columns, sort
```

### 2.1 Progress Document Schema

**Path**: `users/{uid}/progress/{docId}`
**Document ID**: `sanitizeProblemName(name)` - replaces `/\#$[]` with `_`, max 100 chars

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | String | Yes | Original problem name |
| `solved` | Boolean | Yes | Whether marked solved |
| `time_to_solve` | String | No | Minutes taken (numeric string) |
| `comments` | String | No | User notes |
| `solved_date` | String | No | ISO 8601 timestamp |
| `updatedAt` | Timestamp | Yes | Firestore server timestamp |
| `updatedFrom` | String | Yes | Source: `"web"` or `"android"` |

### 2.2 Config Documents

#### awareness
```json
{
  "commitment": { "problemsPerDay": 2.0 },
  "baseRate": 2.0,
  "baseSolvedScaling": 0.1,
  "tierSolvedBonus": { "top": 0.3, "advanced": 0.2, "intermediate": 0.1, "below": 0 },
  "tierDifficultyMultipliers": {
    "top": { "Easy": 0, "Medium": 0.25, "Hard": 0.4 },
    "advanced": { "Easy": 1.2, "Medium": 0.9, "Hard": 0.7 },
    "intermediate": { "Easy": 1.5, "Medium": 1.0, "Hard": 0.75 },
    "below": { "Easy": 1.8, "Medium": 1.3, "Hard": 1.0 }
  },
  "thresholds": { "white": 10, "green": 30, "yellow": 50, "red": 70, "darkRed": 90 },
  "refreshInterval": 86400000,
  "refreshOnFocus": true,
  "updatedAt": "<Timestamp>",
  "updatedFrom": "web"
}
```

#### filters
```json
{
  "activeTab": "neetcode150",
  "tabStates": {
    "neetcode150": {
      "difficultyFilter": "all",
      "solvedFilter": "all",
      "patternFilter": "all",
      "colorFilter": "all",
      "searchTerm": ""
    }
  },
  "updatedAt": "<Timestamp>",
  "updatedFrom": "web"
}
```

#### exportPrefs
```json
{
  "defaultFormat": "json",
  "defaultMode": "user",
  "updatedAt": "<Timestamp>",
  "updatedFrom": "web"
}
```

#### uiPrefs
```json
{
  "theme": "light",
  "columnVisibility": {
    "intermediateTime": true, "advancedTime": true, "topTime": true,
    "pattern": true, "comments": true, "solvedDate": true
  },
  "sortPreferences": { "neetcode150": { "column": "name", "direction": "asc" } },
  "updatedAt": "<Timestamp>",
  "updatedFrom": "web"
}
```

---

## 3. Problem Data Structure

### 3.1 Static Problem Fields (from TSV)
| Field | Type | Mutable |
|-------|------|---------|
| `name` | String | No |
| `difficulty` | "Easy" \| "Medium" \| "Hard" | No |
| `intermediate_time` | String (minutes) | No |
| `advanced_time` | String (minutes) | No |
| `top_time` | String (minutes) | No |
| `pattern` | String | No |

### 3.2 User Progress Fields (synced)
| Field | Type | Mutable |
|-------|------|---------|
| `solved` | Boolean | Yes |
| `time_to_solve` | String (minutes) | Yes |
| `comments` | String | Yes |
| `solved_date` | String (ISO 8601) | Yes |

### 3.3 Problem Lists (file_list)
- `neetcode150` (150 problems)
- `blind75` (75 problems)
- `neetcode250` (250 problems)
- `salesforce` (custom list)

### 3.4 Duplicate Map
Problems appearing in multiple lists. Map: `problemName → [fileKey1, fileKey2, ...]`
When syncing, update the **same Firestore document** regardless of which list triggered the change.

---

## 4. Sync Operations

### 4.1 Authentication
- **Provider**: Google Sign-In
- **Method**: `firebase.auth().signInWithPopup(GoogleAuthProvider)`
- **State Observer**: `onAuthStateChanged(user => ...)`
- **User Fields**: `uid`, `email`, `displayName`, `photoURL`

### 4.2 Initial Sync (pullFromCloud)
```
1. Fetch all docs from users/{uid}/progress
2. If empty → upload local data to cloud
3. For each local problem with matching cloud doc:
   a. detectSyncConflict(local, cloud)
   b. If cloud newer (5s tolerance) → apply cloud to local
   c. If timestamps close but data differs → record conflict
4. Show conflict dialog if any conflicts
5. Load all config docs from cloud
```

### 4.3 Push to Cloud
**Debounced sync** (2 seconds after last change):
- Only sync problems with user data (solved=true OR has time/comments)
- Use batched writes (max 400 per batch, Firestore limit 500)
- Set `updatedFrom: "android"` for Android app

### 4.4 Real-time Listeners
```javascript
userRef.collection('progress').onSnapshot(snapshot => {
  snapshot.docChanges().forEach(change => {
    if (change.type === 'modified') {
      // Apply cloud data if cloud timestamp > local timestamp
      handleCloudChange(change.doc.data());
    }
  });
});
```

---

## 5. Conflict Resolution

### 5.1 Detection Algorithm
```javascript
const TOLERANCE = 5000; // 5 seconds

if (identical(local, cloud)) return { hasConflict: false }
if (cloudTime > localTime + TOLERANCE) return { winner: 'cloud' }
if (localTime > cloudTime + TOLERANCE) return { winner: 'local' }
return { hasConflict: true } // True conflict
```

### 5.2 Resolution Options
1. **Keep Local**: Push local to cloud
2. **Keep Cloud**: Apply cloud to local (default)
3. **Merge**:
   - `solved`: `true` wins
   - `time_to_solve`: non-empty wins
   - `comments`: concatenate with `"\n---\n"`
   - `solved_date`: non-empty wins

---

## 6. Awareness Scoring Algorithm

### 6.1 Formula
```
score = days * baseRate * commitmentFactor * tierDiffMultiplier / solvedFactor

where:
- days = daysSince(solved_date)
- commitmentFactor = problemsPerDay / 2.0
- tierDiffMultiplier = matrix[tier][difficulty]
- solvedFactor = 1 + (baseSolvedScaling + tierBonus) * log2(totalSolved + 1)
```

### 6.2 Tier Determination
```
function getTier(time_to_solve, top, advanced, intermediate):
  if time <= top_time: return 'top'
  if time <= advanced_time: return 'advanced'
  if time <= intermediate_time: return 'intermediate'
  return 'below'
```

### 6.3 Color Thresholds
| Score Range | Color | CSS Class |
|-------------|-------|-----------|
| < 10 | White | `awareness-white` |
| 10-29 | Green | `awareness-green` |
| 30-49 | Yellow | `awareness-yellow` |
| 50-69 | Red | `awareness-red` |
| 70-89 | Dark Red | `awareness-dark-red` |
| >= 90 | Flashing | `awareness-flashing` |
| Not solved | Gray | `unsolved-problem` |

---

## 7. Debounce Timing

| Operation | Delay |
|-----------|-------|
| Progress sync | 2000ms |
| Filter config sync | 1000ms |
| Export prefs sync | 2000ms |
| UI prefs sync | 2000ms |
| Awareness refresh | 86400000ms (24h) |

---

## 8. Import/Export Formats

### Supported Formats
- JSON, CSV, TSV, XML, YAML

### Export Modes
- `full`: All fields
- `user`: Only progress fields (solved, time, comments, date)
- `problems`: Only static fields (name, difficulty, times, pattern)

### JSON Export Structure
```json
{
  "fileKey": "neetcode150",
  "mode": "user",
  "exportDate": "2024-01-20T10:30:00Z",
  "version": "1.0",
  "problems": [...]
}
```

---

## 9. Android Implementation Checklist

### Authentication
- [ ] Google Sign-In SDK integration
- [ ] FirebaseAuth credential conversion
- [ ] Auth state listener
- [ ] User session persistence

### Data Sync
- [ ] Initial pullFromCloud after sign-in
- [ ] Real-time listeners for progress collection
- [ ] Debounced syncToCloud on changes
- [ ] Batched Firestore writes
- [ ] Conflict detection & resolution UI

### Local Storage (SharedPreferences)
- [ ] `tracker_{fileKey}` - Problem progress arrays
- [ ] `tracker_active_tab` - Current tab
- [ ] `tracker_filters_{fileKey}` - Filter states
- [ ] `tracker_export_format/mode` - Export prefs
- [ ] `tracker_theme` - UI theme
- [ ] `tracker_column_visibility` - Column toggles
- [ ] `tracker_awareness_config` - Awareness settings

### Awareness Algorithm
- [ ] Tier determination from time_to_solve
- [ ] Score calculation with all factors
- [ ] Color mapping based on thresholds
- [ ] Configurable auto-refresh

### Error Handling
- [ ] Network error recovery
- [ ] Invalid date handling
- [ ] Auth error handling
- [ ] Offline mode support

---

## 10. TSV Problem Data Format

### 10.1 Source Files

Problem data is sourced from TSV files in `/raw/` directory:
- `blind75.tsv` - 75 classic interview problems
- `neetcode150.tsv` - 150 curated problems
- `neetcode250.tsv` - 250 extended problems
- `salesforce.tsv` - Company-specific list

### 10.2 TSV Format

**Tab-separated** with 6 columns (header + data rows):

```tsv
Problem Name	Difficulty	Intermediate Max time	Advanced Max time	Top of the crop max time	Problem Pattern (if any)
Two Sum	Easy	25	15	8	Hash Table
Best Time to Buy and Sell Stock	Easy	20	12	7	Greedy / Single Pass
Contains Duplicate	Easy	15	10	5	Hash Set
Product of Array Except Self	Medium	45	30	20	Prefix/Suffix Products
```

### 10.3 Column Mapping

| TSV Column | JSON Field | Type | Notes |
|------------|-----------|------|-------|
| Problem Name | `name` | String | Primary identifier |
| Difficulty | `difficulty` | String | "Easy", "Medium", "Hard" |
| Intermediate Max time | `intermediate_time` | String | Minutes (numeric) |
| Advanced Max time | `advanced_time` | String | Minutes (numeric) |
| Top of the crop max time | `top_time` | String | Minutes (numeric) |
| Problem Pattern | `pattern` | String | Algorithm/DS category |

### 10.4 Parsing Rules

```python
# Skip row 0 (header)
# Skip rows with < 6 columns
for row in reader:
    problem = {
        "name": row[0].strip(),
        "difficulty": row[1].strip(),
        "intermediate_time": row[2].strip(),
        "advanced_time": row[3].strip(),
        "top_time": row[4].strip(),
        "pattern": row[5].strip(),
        # User progress (initialized empty)
        "solved": False,
        "time_to_solve": "",
        "comments": "",
        "solved_date": ""
    }
```

### 10.5 Android Bundling Options

**Option A: Embed as JSON asset**
- Parse TSV at build time -> JSON
- Include `parsed_data.json` in assets folder
- Load on app startup

**Option B: Bundle TSV files**
- Include raw TSV files in assets
- Parse at first launch
- Cache parsed result in SharedPreferences

**Option C: Fetch from server**
- Host problem data on Firebase/CDN
- Fetch on first launch + periodic updates
- Allows adding new problem lists without app update

### 10.6 Duplicate Detection

Problems appearing in multiple lists share the same Firestore document.

```python
# Build duplicate map: problemName -> [fileKey1, fileKey2, ...]
duplicate_map = {
    "Two Sum": ["neetcode150", "blind75"],
    "Best Time to Buy and Sell Stock": ["neetcode150", "blind75", "neetcode250"],
    ...
}
```

**For Android**: When syncing from `blind75` list, if "Two Sum" already synced from `neetcode150`, they reference the **same** Firestore document at `users/{uid}/progress/Two Sum`.

---

## 11. Critical Implementation Notes

1. **Problem Identity**: Use `problem.name` as primary key (not auto-IDs)
2. **Document IDs**: Always sanitize: `name.replace(/[\/\\#$\[\]]/g, '_').substring(0, 100)`
3. **Timestamps**: Use ISO 8601 for `solved_date`, Firestore Timestamp for `updatedAt`
4. **Duplicate Handling**: Same problem in multiple lists = single Firestore doc
5. **Offline-First**: Local storage is primary; cloud is secondary
6. **Data Preservation**: Sign-out does NOT delete local data
7. **Set `updatedFrom: "android"`** on all writes from Android app
