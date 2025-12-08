package com.codingtracker.data.export.converter

import com.codingtracker.data.export.model.ExportBundle
import com.codingtracker.data.export.model.ExportType
import com.codingtracker.data.export.model.ProblemExportData
import com.codingtracker.data.export.model.ProgressExportData
import javax.inject.Inject
import javax.inject.Singleton

/**
 * TSV (Tab-Separated Values) format converter.
 */
@Singleton
class TsvFormatConverter @Inject constructor() : DataFormatConverter {

    override val format: DataFormat = DataFormat.TSV

    override fun serialize(bundle: ExportBundle): String {
        val sb = StringBuilder()

        // Add metadata as comments
        sb.appendLine("# version=${bundle.version}")
        sb.appendLine("# exportedAt=${bundle.exportedAt}")
        sb.appendLine("# exportType=${bundle.exportType.name}")
        bundle.listId?.let { sb.appendLine("# listId=$it") }

        when (bundle.exportType) {
            ExportType.PROGRESS_ONLY -> {
                sb.appendLine(PROGRESS_HEADERS.joinToString("\t"))
                bundle.progressData?.forEach { data ->
                    sb.appendLine(serializeProgress(data))
                }
            }
            ExportType.FULL_DATA -> {
                sb.appendLine(PROBLEM_HEADERS.joinToString("\t"))
                bundle.problemData?.forEach { data ->
                    sb.appendLine(serializeProblem(data))
                }
            }
        }

        return sb.toString()
    }

    override fun deserialize(content: String): ExportBundle {
        val lines = content.lines().filter { it.isNotBlank() }
        if (lines.isEmpty()) {
            throw FormatParseException("Empty TSV file")
        }

        // Parse metadata from comments
        var version = 1
        var exportedAt = System.currentTimeMillis()
        var exportType: ExportType? = null
        var listId: String? = null

        val metadataLines = lines.filter { it.startsWith("#") }
        metadataLines.forEach { line ->
            val parts = line.removePrefix("#").trim().split("=", limit = 2)
            if (parts.size == 2) {
                when (parts[0].trim()) {
                    "version" -> version = parts[1].toIntOrNull() ?: 1
                    "exportedAt" -> exportedAt = parts[1].toLongOrNull() ?: System.currentTimeMillis()
                    "exportType" -> exportType = runCatching { ExportType.valueOf(parts[1]) }.getOrNull()
                    "listId" -> listId = parts[1].takeIf { it.isNotBlank() }
                }
            }
        }

        val dataLines = lines.filter { !it.startsWith("#") }
        if (dataLines.isEmpty()) {
            throw FormatParseException("No data found in TSV file")
        }

        val headers = dataLines.first().split("\t")
        val isProgressOnly = PROGRESS_HEADERS.all { it in headers } &&
                             PROBLEM_SPECIFIC_HEADERS.none { it in headers }

        val actualExportType = exportType ?: if (isProgressOnly) ExportType.PROGRESS_ONLY else ExportType.FULL_DATA

        return when (actualExportType) {
            ExportType.PROGRESS_ONLY -> {
                val progressData = dataLines.drop(1).mapNotNull { line ->
                    parseProgressLine(line, headers)
                }
                ExportBundle(
                    version = version,
                    exportedAt = exportedAt,
                    exportType = ExportType.PROGRESS_ONLY,
                    listId = listId,
                    progressData = progressData
                )
            }
            ExportType.FULL_DATA -> {
                val problemData = dataLines.drop(1).mapNotNull { line ->
                    parseProblemLine(line, headers)
                }
                ExportBundle(
                    version = version,
                    exportedAt = exportedAt,
                    exportType = ExportType.FULL_DATA,
                    listId = listId,
                    problemData = problemData
                )
            }
        }
    }

    private fun serializeProgress(data: ProgressExportData): String {
        return listOf(
            escape(data.problemName),
            data.solved.toString(),
            data.timeToSolve?.toString() ?: "",
            escape(data.comments ?: ""),
            data.solvedDate?.toString() ?: "",
            data.lastModified.toString()
        ).joinToString("\t")
    }

    private fun serializeProblem(data: ProblemExportData): String {
        return listOf(
            escape(data.name),
            data.difficulty,
            data.intermediateTime?.toString() ?: "",
            data.advancedTime?.toString() ?: "",
            data.topTime?.toString() ?: "",
            escape(data.pattern ?: ""),
            data.listId,
            data.solved.toString(),
            data.timeToSolve?.toString() ?: "",
            escape(data.comments ?: ""),
            data.solvedDate?.toString() ?: "",
            data.lastModified?.toString() ?: ""
        ).joinToString("\t")
    }

    private fun parseProgressLine(line: String, headers: List<String>): ProgressExportData? {
        val values = line.split("\t")
        if (values.size < headers.size) return null

        val map = headers.zip(values).toMap()
        return try {
            ProgressExportData(
                problemName = unescape(map["Problem Name"] ?: return null),
                solved = map["Solved"]?.toBooleanStrictOrNull() ?: false,
                timeToSolve = map["Time To Solve"]?.toIntOrNull(),
                comments = unescape(map["Comments"]).takeIf { it.isNotBlank() },
                solvedDate = map["Solved Date"]?.toLongOrNull(),
                lastModified = map["Last Modified"]?.toLongOrNull() ?: System.currentTimeMillis()
            )
        } catch (e: Exception) {
            null
        }
    }

    private fun parseProblemLine(line: String, headers: List<String>): ProblemExportData? {
        val values = line.split("\t")
        if (values.size < headers.size) return null

        val map = headers.zip(values).toMap()
        return try {
            ProblemExportData(
                name = unescape(map["Problem Name"] ?: return null),
                difficulty = map["Difficulty"] ?: "Medium",
                intermediateTime = map["Intermediate Time"]?.toIntOrNull(),
                advancedTime = map["Advanced Time"]?.toIntOrNull(),
                topTime = map["Top Time"]?.toIntOrNull(),
                pattern = unescape(map["Pattern"]).takeIf { it.isNotBlank() },
                listId = map["List ID"] ?: "custom",
                solved = map["Solved"]?.toBooleanStrictOrNull() ?: false,
                timeToSolve = map["Time To Solve"]?.toIntOrNull(),
                comments = unescape(map["Comments"]).takeIf { it.isNotBlank() },
                solvedDate = map["Solved Date"]?.toLongOrNull(),
                lastModified = map["Last Modified"]?.toLongOrNull()
            )
        } catch (e: Exception) {
            null
        }
    }

    private fun escape(value: String): String {
        return value
            .replace("\\", "\\\\")
            .replace("\t", "\\t")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
    }

    private fun unescape(value: String?): String {
        if (value == null) return ""
        return value
            .replace("\\r", "\r")
            .replace("\\n", "\n")
            .replace("\\t", "\t")
            .replace("\\\\", "\\")
    }

    companion object {
        private val PROGRESS_HEADERS = listOf(
            "Problem Name",
            "Solved",
            "Time To Solve",
            "Comments",
            "Solved Date",
            "Last Modified"
        )

        private val PROBLEM_HEADERS = listOf(
            "Problem Name",
            "Difficulty",
            "Intermediate Time",
            "Advanced Time",
            "Top Time",
            "Pattern",
            "List ID",
            "Solved",
            "Time To Solve",
            "Comments",
            "Solved Date",
            "Last Modified"
        )

        private val PROBLEM_SPECIFIC_HEADERS = listOf(
            "Difficulty",
            "Intermediate Time",
            "Advanced Time",
            "Top Time",
            "Pattern",
            "List ID"
        )
    }
}
