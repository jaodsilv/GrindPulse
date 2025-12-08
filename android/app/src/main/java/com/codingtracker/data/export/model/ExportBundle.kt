package com.codingtracker.data.export.model

import kotlinx.serialization.Serializable

/**
 * Type of export operation.
 */
@Serializable
enum class ExportType {
    PROGRESS_ONLY,
    FULL_DATA
}

/**
 * Wrapper for exported data with metadata.
 * Contains version info for future compatibility and export context.
 */
@Serializable
data class ExportBundle(
    val version: Int = 1,
    val exportedAt: Long = System.currentTimeMillis(),
    val exportType: ExportType,
    val listId: String? = null,
    val progressData: List<ProgressExportData>? = null,
    val problemData: List<ProblemExportData>? = null
) {
    companion object {
        const val CURRENT_VERSION = 1

        fun forProgress(
            data: List<ProgressExportData>,
            listId: String? = null
        ): ExportBundle = ExportBundle(
            exportType = ExportType.PROGRESS_ONLY,
            listId = listId,
            progressData = data
        )

        fun forProblems(
            data: List<ProblemExportData>,
            listId: String? = null
        ): ExportBundle = ExportBundle(
            exportType = ExportType.FULL_DATA,
            listId = listId,
            problemData = data
        )
    }
}
