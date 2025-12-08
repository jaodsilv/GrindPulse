package com.codingtracker.data.export.model

import kotlinx.serialization.Serializable

/**
 * Data transfer object for exporting progress-only data.
 * Used when user wants to export just their solving progress without problem details.
 */
@Serializable
data class ProgressExportData(
    val problemName: String,
    val solved: Boolean,
    val timeToSolve: Int? = null,
    val comments: String? = null,
    val solvedDate: Long? = null,
    val lastModified: Long
)
