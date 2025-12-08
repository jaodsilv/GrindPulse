package com.codingtracker.domain.model

data class ProgressStats(
    val solved: Int,
    val total: Int,
    val percentage: Float = if (total > 0) (solved.toFloat() / total * 100) else 0f,
    val byDifficulty: Map<Difficulty, DifficultyStats> = emptyMap()
)

data class DifficultyStats(
    val solved: Int,
    val total: Int,
    val percentage: Float = if (total > 0) (solved.toFloat() / total * 100) else 0f
)
