package com.codingtracker.data.repository

import android.content.Context
import com.codingtracker.data.local.db.dao.DuplicateMappingDao
import com.codingtracker.data.local.db.dao.ProblemDao
import com.codingtracker.data.local.db.dao.ProblemListDao
import com.codingtracker.data.local.db.dao.UserProgressDao
import com.codingtracker.data.local.db.entity.DuplicateMappingEntity
import com.codingtracker.data.local.db.entity.ProblemEntity
import com.codingtracker.data.local.db.entity.ProblemListEntity
import com.codingtracker.data.local.db.entity.UserProgressEntity
import com.codingtracker.data.mapper.toDomain
import com.codingtracker.data.mapper.toEntity
import com.codingtracker.domain.model.Difficulty
import com.codingtracker.domain.model.DifficultyStats
import com.codingtracker.domain.model.Problem
import com.codingtracker.domain.model.ProblemList
import com.codingtracker.domain.model.ProgressStats
import com.codingtracker.domain.model.UserProgress
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.map
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ProblemRepositoryImpl @Inject constructor(
    @ApplicationContext private val context: Context,
    private val problemDao: ProblemDao,
    private val problemListDao: ProblemListDao,
    private val userProgressDao: UserProgressDao,
    private val duplicateMappingDao: DuplicateMappingDao
) : ProblemRepository {

    private val json = Json { ignoreUnknownKeys = true }

    override fun getProblemLists(): Flow<List<ProblemList>> {
        return problemListDao.getAllLists().map { entities ->
            entities.map { it.toDomain() }
        }
    }

    override fun getProblemsForList(listId: String): Flow<List<Problem>> {
        return problemDao.getProblemsForList(listId).map { entities ->
            entities.map { entity ->
                val progress = userProgressDao.getProgressForProblem(entity.id)
                val duplicateMapping = duplicateMappingDao.getMappingForProblem(entity.name)
                val duplicateListIds = duplicateMapping?.let {
                    json.decodeFromString<List<String>>(it.listIds)
                } ?: listOf(listId)
                entity.toDomain(progress, duplicateListIds)
            }
        }
    }

    override fun getFilteredProblems(
        listId: String,
        searchQuery: String?,
        difficulty: Difficulty?,
        pattern: String?,
        solvedOnly: Boolean?
    ): Flow<List<Problem>> {
        return getProblemsForList(listId).map { problems ->
            problems.filter { problem ->
                val matchesSearch = searchQuery.isNullOrBlank() ||
                    problem.name.contains(searchQuery, ignoreCase = true)
                val matchesDifficulty = difficulty == null || problem.difficulty == difficulty
                val matchesPattern = pattern == null || problem.pattern == pattern
                val matchesSolved = solvedOnly == null ||
                    (solvedOnly && problem.progress.solved) ||
                    (!solvedOnly && !problem.progress.solved)

                matchesSearch && matchesDifficulty && matchesPattern && matchesSolved
            }
        }
    }

    override suspend fun getProblemById(problemId: String): Problem? {
        val entity = problemDao.getProblemById(problemId) ?: return null
        val progress = userProgressDao.getProgressForProblem(problemId)
        val duplicateMapping = duplicateMappingDao.getMappingForProblem(entity.name)
        val duplicateListIds = duplicateMapping?.let {
            json.decodeFromString<List<String>>(it.listIds)
        } ?: listOf(entity.listId)
        return entity.toDomain(progress, duplicateListIds)
    }

    override fun getAllPatterns(): Flow<List<String>> {
        return problemDao.getAllPatterns()
    }

    override suspend fun updateProgress(problemId: String, progress: UserProgress) {
        userProgressDao.insert(progress.toEntity(problemId))
    }

    override suspend fun syncDuplicates(problemName: String, progress: UserProgress) {
        val duplicateMapping = duplicateMappingDao.getMappingForProblem(problemName) ?: return
        val listIds = json.decodeFromString<List<String>>(duplicateMapping.listIds)

        if (listIds.size <= 1) return

        // Get all problems with the same name
        val problems = problemDao.getProblemsByName(problemName)

        // Update progress for all duplicates
        problems.forEach { problem ->
            userProgressDao.insert(progress.toEntity(problem.id))
        }
    }

    override fun getProgressForList(listId: String): Flow<ProgressStats> {
        return combine(
            problemDao.getProblemsForList(listId),
            userProgressDao.getSolvedCountForList(listId)
        ) { problems, solvedCount ->
            val total = problems.size
            val byDifficulty = Difficulty.entries.associateWith { difficulty ->
                val totalForDifficulty = problems.count {
                    Difficulty.fromString(it.difficulty) == difficulty
                }
                val solvedForDifficulty = problems.count { problem ->
                    val progress = userProgressDao.getProgressForProblem(problem.id)
                    Difficulty.fromString(problem.difficulty) == difficulty &&
                        progress?.solved == true
                }
                DifficultyStats(solvedForDifficulty, totalForDifficulty)
            }
            ProgressStats(
                solved = solvedCount,
                total = total,
                byDifficulty = byDifficulty
            )
        }
    }

    override fun getOverallProgress(): Flow<ProgressStats> {
        return combine(
            problemDao.getUniqueProblemsCount(),
            userProgressDao.getUniqueSolvedCount()
        ) { total, solved ->
            ProgressStats(solved = solved, total = total)
        }
    }

    override suspend fun initializeData() {
        // Check if data already exists
        if (isDataInitialized()) return

        // Initialize problem lists
        val lists = listOf(
            ProblemListEntity("blind75", "Blind 75", 75, 0),
            ProblemListEntity("neetcode150", "NeetCode 150", 150, 1),
            ProblemListEntity("neetcode250", "NeetCode 250", 250, 2),
            ProblemListEntity("salesforce", "Salesforce", 16, 3)
        )
        problemListDao.insertAll(lists)

        // Load problems from assets
        val problemsByName = mutableMapOf<String, MutableList<String>>()

        lists.forEach { list ->
            val problems = loadProblemsFromAsset("${list.id}.tsv", list.id)
            problemDao.insertAll(problems)

            // Track duplicates
            problems.forEach { problem ->
                problemsByName.getOrPut(problem.name) { mutableListOf() }.add(list.id)
            }
        }

        // Create duplicate mappings
        val duplicateMappings = problemsByName
            .filter { it.value.size > 1 }
            .map { (name, listIds) ->
                DuplicateMappingEntity(
                    problemName = name,
                    listIds = json.encodeToString(listIds)
                )
            }
        duplicateMappingDao.insertAll(duplicateMappings)
    }

    override suspend fun isDataInitialized(): Boolean {
        return problemListDao.getAllLists().first().isNotEmpty()
    }

    private fun loadProblemsFromAsset(filename: String, listId: String): List<ProblemEntity> {
        return try {
            context.assets.open(filename).bufferedReader().useLines { lines ->
                lines.drop(1) // Skip header
                    .filter { it.isNotBlank() }
                    .map { line ->
                        val parts = line.split("\t")
                        ProblemEntity(
                            id = UUID.randomUUID().toString(),
                            name = parts.getOrNull(0)?.trim() ?: "",
                            difficulty = parts.getOrNull(1)?.trim() ?: "Medium",
                            intermediateTime = parts.getOrNull(2)?.trim()?.toIntOrNull(),
                            advancedTime = parts.getOrNull(3)?.trim()?.toIntOrNull(),
                            topTime = parts.getOrNull(4)?.trim()?.toIntOrNull(),
                            pattern = parts.getOrNull(5)?.trim()?.takeIf { it.isNotEmpty() },
                            listId = listId
                        )
                    }
                    .toList()
            }
        } catch (e: Exception) {
            emptyList()
        }
    }
}
