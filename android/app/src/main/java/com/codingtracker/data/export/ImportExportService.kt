package com.codingtracker.data.export

import com.codingtracker.data.export.converter.DataFormat
import com.codingtracker.data.export.model.ConflictStrategy
import com.codingtracker.data.export.model.ExportBundle
import com.codingtracker.data.export.model.ImportResult

/**
 * Service interface for import/export operations.
 */
interface ImportExportService {

    /**
     * Export progress data for problems.
     * @param format The output format
     * @param listId Optional list ID to filter. Null exports all lists.
     * @return Result containing the export bundle
     */
    suspend fun exportProgress(
        format: DataFormat,
        listId: String? = null
    ): Result<ExportBundle>

    /**
     * Export full problem data with progress.
     * @param format The output format
     * @param listId Optional list ID to filter. Null exports all lists.
     * @return Result containing the export bundle
     */
    suspend fun exportProblemsWithProgress(
        format: DataFormat,
        listId: String? = null
    ): Result<ExportBundle>

    /**
     * Serialize an export bundle to string.
     * @param bundle The bundle to serialize
     * @param format The output format
     * @return Serialized string
     */
    fun serializeBundle(bundle: ExportBundle, format: DataFormat): String

    /**
     * Parse and validate imported content.
     * @param content The raw file content
     * @param format The format to parse as. If null, auto-detect.
     * @param filename Optional filename for format detection
     * @return Parsed export bundle
     */
    fun parseImportContent(
        content: String,
        format: DataFormat? = null,
        filename: String? = null
    ): Result<ExportBundle>

    /**
     * Import progress data.
     * @param bundle The parsed export bundle
     * @param conflictStrategy How to handle conflicts
     * @return Import result with success/failure counts
     */
    suspend fun importProgress(
        bundle: ExportBundle,
        conflictStrategy: ConflictStrategy
    ): ImportResult

    /**
     * Import problems into an existing or new list.
     * @param bundle The parsed export bundle
     * @param targetListId The list to import into. Creates new list if doesn't exist.
     * @param conflictStrategy How to handle conflicts
     * @return Import result with success/failure counts
     */
    suspend fun importProblems(
        bundle: ExportBundle,
        targetListId: String,
        conflictStrategy: ConflictStrategy
    ): ImportResult

    /**
     * Detect format from content or filename.
     * @param content File content
     * @param filename Optional filename
     * @return Detected format or null
     */
    fun detectFormat(content: String, filename: String? = null): DataFormat?

    /**
     * Get suggested filename for export.
     * @param format The format
     * @param listId Optional list ID for naming
     * @param isProgressOnly Whether this is progress-only export
     * @return Suggested filename
     */
    fun getSuggestedFilename(
        format: DataFormat,
        listId: String? = null,
        isProgressOnly: Boolean = true
    ): String
}
