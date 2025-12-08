package com.codingtracker.data.export

import com.codingtracker.data.export.converter.CsvFormatConverter
import com.codingtracker.data.export.converter.DataFormat
import com.codingtracker.data.export.converter.DataFormatConverter
import com.codingtracker.data.export.converter.JsonFormatConverter
import com.codingtracker.data.export.converter.TsvFormatConverter
import com.codingtracker.data.export.converter.XmlFormatConverter
import com.codingtracker.data.export.converter.YamlFormatConverter
import com.codingtracker.data.export.model.ConflictStrategy
import com.codingtracker.data.export.model.ExportBundle
import com.codingtracker.data.export.model.ExportType
import com.codingtracker.data.export.model.ImportConflict
import com.codingtracker.data.export.model.ImportResult
import com.codingtracker.data.export.model.ProblemExportData
import com.codingtracker.data.export.model.ProgressExportData
import com.codingtracker.data.local.db.dao.ProblemDao
import com.codingtracker.data.local.db.dao.ProblemListDao
import com.codingtracker.data.local.db.dao.UserProgressDao
import com.codingtracker.data.local.db.entity.ProblemEntity
import com.codingtracker.data.local.db.entity.ProblemListEntity
import com.codingtracker.data.local.db.entity.UserProgressEntity
import kotlinx.coroutines.flow.first
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Implementation of ImportExportService.
 */
@Singleton
class ImportExportServiceImpl @Inject constructor(
    private val problemDao: ProblemDao,
    private val userProgressDao: UserProgressDao,
    private val problemListDao: ProblemListDao,
    private val jsonConverter: JsonFormatConverter,
    private val tsvConverter: TsvFormatConverter,
    private val csvConverter: CsvFormatConverter,
    private val xmlConverter: XmlFormatConverter,
    private val yamlConverter: YamlFormatConverter
) : ImportExportService {

    private val converters: Map<DataFormat, DataFormatConverter> by lazy {
        mapOf(
            DataFormat.JSON to jsonConverter,
            DataFormat.TSV to tsvConverter,
            DataFormat.CSV to csvConverter,
            DataFormat.XML to xmlConverter,
            DataFormat.YAML to yamlConverter
        )
    }

    private fun getConverter(format: DataFormat): DataFormatConverter {
        return converters[format] ?: throw IllegalArgumentException("Unsupported format: $format")
    }

    override suspend fun exportProgress(
        format: DataFormat,
        listId: String?
    ): Result<ExportBundle> = runCatching {
        val problems = if (listId != null) {
            problemDao.getProblemsForList(listId).first()
        } else {
            // Get all problems from all lists
            val lists = problemListDao.getAllLists().first()
            lists.flatMap { list ->
                problemDao.getProblemsForList(list.id).first()
            }
        }

        val progressData = problems.mapNotNull { problem ->
            val progress = userProgressDao.getProgressForProblem(problem.id)
            if (progress != null && progress.solved) {
                ProgressExportData(
                    problemName = problem.name,
                    solved = progress.solved,
                    timeToSolve = progress.timeToSolve,
                    comments = progress.comments,
                    solvedDate = progress.solvedDate,
                    lastModified = progress.lastModified
                )
            } else null
        }.distinctBy { it.problemName } // Unique problem names

        ExportBundle.forProgress(progressData, listId)
    }

    override suspend fun exportProblemsWithProgress(
        format: DataFormat,
        listId: String?
    ): Result<ExportBundle> = runCatching {
        val problems = if (listId != null) {
            problemDao.getProblemsForList(listId).first()
        } else {
            val lists = problemListDao.getAllLists().first()
            lists.flatMap { list ->
                problemDao.getProblemsForList(list.id).first()
            }
        }

        val problemData = problems.map { problem ->
            val progress = userProgressDao.getProgressForProblem(problem.id)
            ProblemExportData(
                name = problem.name,
                difficulty = problem.difficulty,
                intermediateTime = problem.intermediateTime,
                advancedTime = problem.advancedTime,
                topTime = problem.topTime,
                pattern = problem.pattern,
                listId = problem.listId,
                solved = progress?.solved ?: false,
                timeToSolve = progress?.timeToSolve,
                comments = progress?.comments,
                solvedDate = progress?.solvedDate,
                lastModified = progress?.lastModified
            )
        }

        ExportBundle.forProblems(problemData, listId)
    }

    override fun serializeBundle(bundle: ExportBundle, format: DataFormat): String {
        return getConverter(format).serialize(bundle)
    }

    override fun parseImportContent(
        content: String,
        format: DataFormat?,
        filename: String?
    ): Result<ExportBundle> = runCatching {
        val detectedFormat = format ?: detectFormat(content, filename)
            ?: throw IllegalArgumentException("Could not detect file format")

        getConverter(detectedFormat).deserialize(content)
    }

    override suspend fun importProgress(
        bundle: ExportBundle,
        conflictStrategy: ConflictStrategy
    ): ImportResult {
        val progressData = when (bundle.exportType) {
            ExportType.PROGRESS_ONLY -> bundle.progressData ?: emptyList()
            ExportType.FULL_DATA -> bundle.problemData?.map { problem ->
                ProgressExportData(
                    problemName = problem.name,
                    solved = problem.solved,
                    timeToSolve = problem.timeToSolve,
                    comments = problem.comments,
                    solvedDate = problem.solvedDate,
                    lastModified = problem.lastModified ?: System.currentTimeMillis()
                )
            } ?: emptyList()
        }

        var successCount = 0
        var failedCount = 0
        var skippedCount = 0
        val errors = mutableListOf<String>()
        val conflicts = mutableListOf<ImportConflict>()

        for (data in progressData) {
            try {
                // Find all problems with this name
                val problems = problemDao.getProblemsByName(data.problemName)
                if (problems.isEmpty()) {
                    skippedCount++
                    continue
                }

                for (problem in problems) {
                    val existingProgress = userProgressDao.getProgressForProblem(problem.id)

                    val shouldUpdate = when (conflictStrategy) {
                        ConflictStrategy.REPLACE_ALL -> true
                        ConflictStrategy.SKIP_ALL -> existingProgress == null
                        ConflictStrategy.MERGE_ALL -> {
                            // Keep the more recent one
                            existingProgress == null ||
                                data.lastModified > existingProgress.lastModified
                        }
                        ConflictStrategy.ASK_EACH -> {
                            if (existingProgress != null && existingProgress.solved) {
                                conflicts.add(
                                    ImportConflict(
                                        problemName = data.problemName,
                                        existingData = ProgressExportData(
                                            problemName = data.problemName,
                                            solved = existingProgress.solved,
                                            timeToSolve = existingProgress.timeToSolve,
                                            comments = existingProgress.comments,
                                            solvedDate = existingProgress.solvedDate,
                                            lastModified = existingProgress.lastModified
                                        ),
                                        importedData = data
                                    )
                                )
                                false // Don't update yet, will be handled by UI
                            } else {
                                true
                            }
                        }
                    }

                    if (shouldUpdate) {
                        userProgressDao.upsert(
                            problemId = problem.id,
                            solved = data.solved,
                            timeToSolve = data.timeToSolve,
                            comments = data.comments,
                            solvedDate = data.solvedDate,
                            lastModified = data.lastModified
                        )
                    }
                }
                successCount++
            } catch (e: Exception) {
                failedCount++
                errors.add("Failed to import ${data.problemName}: ${e.message}")
            }
        }

        return ImportResult(
            successCount = successCount,
            failedCount = failedCount,
            skippedCount = skippedCount,
            errors = errors,
            conflicts = conflicts
        )
    }

    override suspend fun importProblems(
        bundle: ExportBundle,
        targetListId: String,
        conflictStrategy: ConflictStrategy
    ): ImportResult {
        val problemData = bundle.problemData
            ?: return ImportResult.empty().copy(errors = listOf("No problem data to import"))

        // Ensure the target list exists
        ensureListExists(targetListId)

        var successCount = 0
        var failedCount = 0
        var skippedCount = 0
        val errors = mutableListOf<String>()

        for (data in problemData) {
            try {
                val problemId = "${targetListId}_${data.name.replace(" ", "_").lowercase()}"

                // Check if problem already exists
                val existingProblem = problemDao.getProblemById(problemId)

                val shouldInsert = when (conflictStrategy) {
                    ConflictStrategy.REPLACE_ALL -> true
                    ConflictStrategy.SKIP_ALL -> existingProblem == null
                    ConflictStrategy.MERGE_ALL -> true // Always update problems in merge mode
                    ConflictStrategy.ASK_EACH -> existingProblem == null
                }

                if (shouldInsert) {
                    // Insert problem
                    problemDao.insert(
                        ProblemEntity(
                            id = problemId,
                            name = data.name,
                            difficulty = data.difficulty,
                            intermediateTime = data.intermediateTime,
                            advancedTime = data.advancedTime,
                            topTime = data.topTime,
                            pattern = data.pattern,
                            listId = targetListId
                        )
                    )

                    // Insert progress if solved
                    if (data.solved) {
                        userProgressDao.upsert(
                            problemId = problemId,
                            solved = data.solved,
                            timeToSolve = data.timeToSolve,
                            comments = data.comments,
                            solvedDate = data.solvedDate,
                            lastModified = data.lastModified ?: System.currentTimeMillis()
                        )
                    }
                    successCount++
                } else {
                    skippedCount++
                }
            } catch (e: Exception) {
                failedCount++
                errors.add("Failed to import ${data.name}: ${e.message}")
            }
        }

        // Update list problem count
        updateListProblemCount(targetListId)

        return ImportResult(
            successCount = successCount,
            failedCount = failedCount,
            skippedCount = skippedCount,
            errors = errors
        )
    }

    override fun detectFormat(content: String, filename: String?): DataFormat? {
        // Try filename first
        filename?.let { DataFormat.fromFilename(it) }?.let { return it }

        // Then try content detection
        return DataFormat.fromContent(content)
    }

    override fun getSuggestedFilename(
        format: DataFormat,
        listId: String?,
        isProgressOnly: Boolean
    ): String {
        val dateFormat = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US)
        val timestamp = dateFormat.format(Date())

        val prefix = when {
            listId != null -> listId
            isProgressOnly -> "progress"
            else -> "problems"
        }

        return "coding_tracker_${prefix}_$timestamp.${format.fileExtension}"
    }

    private suspend fun ensureListExists(listId: String) {
        val existingList = problemListDao.getListById(listId)
        if (existingList == null) {
            // Create a new custom list
            val currentLists = problemListDao.getAllLists().first()
            val maxSortOrder = currentLists.maxOfOrNull { it.sortOrder } ?: 0

            problemListDao.insert(
                ProblemListEntity(
                    id = listId,
                    displayName = formatListName(listId),
                    problemCount = 0,
                    sortOrder = maxSortOrder + 1
                )
            )
        }
    }

    private suspend fun updateListProblemCount(listId: String) {
        val problems = problemDao.getProblemsForList(listId).first()
        val existingList = problemListDao.getListById(listId) ?: return

        problemListDao.insert(
            existingList.copy(problemCount = problems.size)
        )
    }

    private fun formatListName(listId: String): String {
        return listId
            .replace("_", " ")
            .split(" ")
            .joinToString(" ") { it.replaceFirstChar { c -> c.uppercase() } }
    }
}
