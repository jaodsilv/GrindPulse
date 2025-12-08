package com.codingtracker.data.export.model

/**
 * Result of an import operation.
 */
data class ImportResult(
    val successCount: Int,
    val failedCount: Int,
    val skippedCount: Int,
    val errors: List<String> = emptyList(),
    val conflicts: List<ImportConflict> = emptyList()
) {
    val totalProcessed: Int get() = successCount + failedCount + skippedCount
    val hasErrors: Boolean get() = failedCount > 0 || errors.isNotEmpty()
    val hasConflicts: Boolean get() = conflicts.isNotEmpty()

    companion object {
        fun success(count: Int) = ImportResult(
            successCount = count,
            failedCount = 0,
            skippedCount = 0
        )

        fun empty() = ImportResult(
            successCount = 0,
            failedCount = 0,
            skippedCount = 0
        )
    }
}

/**
 * Represents a conflict found during import.
 */
data class ImportConflict(
    val problemName: String,
    val existingData: ProgressExportData?,
    val importedData: ProgressExportData
)
