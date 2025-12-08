package com.codingtracker.data.repository

import com.codingtracker.domain.model.Difficulty
import com.codingtracker.domain.model.Problem
import com.codingtracker.domain.model.ProblemList
import com.codingtracker.domain.model.ProgressStats
import com.codingtracker.domain.model.UserProgress
import kotlinx.coroutines.flow.Flow

interface ProblemRepository {
    // Problem Lists
    fun getProblemLists(): Flow<List<ProblemList>>

    // Problems
    fun getProblemsForList(listId: String): Flow<List<Problem>>
    fun getFilteredProblems(
        listId: String,
        searchQuery: String?,
        difficulty: Difficulty?,
        pattern: String?,
        solvedOnly: Boolean?
    ): Flow<List<Problem>>
    suspend fun getProblemById(problemId: String): Problem?
    fun getAllPatterns(): Flow<List<String>>

    // Progress
    suspend fun updateProgress(problemId: String, progress: UserProgress)
    suspend fun syncDuplicates(problemName: String, progress: UserProgress)

    // Statistics
    fun getProgressForList(listId: String): Flow<ProgressStats>
    fun getOverallProgress(): Flow<ProgressStats>

    // Data initialization
    suspend fun initializeData()
    suspend fun isDataInitialized(): Boolean
}
