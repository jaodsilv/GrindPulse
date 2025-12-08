package com.codingtracker.data.export.model

/**
 * How to resolve conflicts when importing data that already exists.
 */
enum class ConflictResolution {
    /**
     * Replace existing data with imported data.
     */
    REPLACE,

    /**
     * Keep existing data, skip importing.
     */
    SKIP,

    /**
     * Merge data, keeping the most recent modifications.
     */
    MERGE
}

/**
 * User's choice for handling all conflicts.
 */
enum class ConflictStrategy {
    /**
     * Ask user for each conflict individually.
     */
    ASK_EACH,

    /**
     * Replace all existing data with imported data.
     */
    REPLACE_ALL,

    /**
     * Skip all conflicts, only import new data.
     */
    SKIP_ALL,

    /**
     * Merge all, keeping most recent modifications.
     */
    MERGE_ALL
}
