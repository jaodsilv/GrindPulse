package com.codingtracker.domain.model

data class ProblemList(
    val id: String,
    val displayName: String,
    val problemCount: Int,
    val sortOrder: Int
) {
    companion object {
        val DEFAULT_LISTS = listOf(
            ProblemList("blind75", "Blind 75", 75, 0),
            ProblemList("neetcode150", "NeetCode 150", 150, 1),
            ProblemList("neetcode250", "NeetCode 250", 250, 2),
            ProblemList("salesforce", "Salesforce", 16, 3)
        )
    }
}
