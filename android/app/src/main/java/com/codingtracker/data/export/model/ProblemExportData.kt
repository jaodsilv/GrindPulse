package com.codingtracker.data.export.model

import kotlinx.serialization.Serializable

/**
 * Data transfer object for exporting full problem data with progress.
 * Used when user wants to export a custom problem set.
 */
@Serializable
data class ProblemExportData(
    val name: String,
    val difficulty: String,
    val intermediateTime: Int? = null,
    val advancedTime: Int? = null,
    val topTime: Int? = null,
    val pattern: String? = null,
    val listId: String,
    val solved: Boolean = false,
    val timeToSolve: Int? = null,
    val comments: String? = null,
    val solvedDate: Long? = null,
    val lastModified: Long? = null
)
