package com.codingtracker.domain.model

import java.time.Instant

data class UserProgress(
    val solved: Boolean = false,
    val timeToSolve: Int? = null,
    val comments: String? = null,
    val solvedDate: Instant? = null
)
