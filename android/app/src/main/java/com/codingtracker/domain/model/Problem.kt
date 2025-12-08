package com.codingtracker.domain.model

data class Problem(
    val id: String,
    val name: String,
    val difficulty: Difficulty,
    val intermediateTime: Int?,
    val advancedTime: Int?,
    val topTime: Int?,
    val pattern: String?,
    val listId: String,
    val progress: UserProgress,
    val isDuplicate: Boolean,
    val duplicateListIds: List<String>
)
