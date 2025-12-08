package com.codingtracker.data.export.converter

import com.codingtracker.data.export.model.ExportBundle
import com.codingtracker.data.export.model.ExportType
import com.codingtracker.data.export.model.ProblemExportData
import com.codingtracker.data.export.model.ProgressExportData
import javax.inject.Inject
import javax.inject.Singleton

/**
 * CSV (Comma-Separated Values) format converter.
 * Follows RFC 4180 specification.
 */
@Singleton
class CsvFormatConverter @Inject constructor() : DataFormatConverter {

    override val format: DataFormat = DataFormat.CSV

    override fun serialize(bundle: ExportBundle): String {
        val sb = StringBuilder()

        // Add metadata as comments (non-standard but useful)
        sb.appendLine("# version=${bundle.version}")
        sb.appendLine("# exportedAt=${bundle.exportedAt}")
        sb.appendLine("# exportType=${bundle.exportType.name}")
        bundle.listId?.let { sb.appendLine("# listId=$it") }

        when (bundle.exportType) {
            ExportType.PROGRESS_ONLY -> {
                sb.appendLine(PROGRESS_HEADERS.joinToString(",") { quote(it) })
                bundle.progressData?.forEach { data ->
                    sb.appendLine(serializeProgress(data))
                }
            }
            ExportType.FULL_DATA -> {
                sb.appendLine(PROBLEM_HEADERS.joinToString(",") { quote(it) })
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
            throw FormatParseException("Empty CSV file")
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
            throw FormatParseException("No data found in CSV file")
        }

        val headers = parseCsvLine(dataLines.first())
        val isProgressOnly = PROGRESS_HEADERS.all { it in headers } &&
                             PROBLEM_SPECIFIC_HEADERS.none { it in headers }

        val actualExportType = exportType ?: if (isProgressOnly) ExportType.PROGRESS_ONLY else ExportType.FULL_DATA

        return when (actualExportType) {
            ExportType.PROGRESS_ONLY -> {
                val progressData = dataLines.drop(1).mapNotNull { line ->
                    parseProgressLine(parseCsvLine(line), headers)
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
                    parseProblemLine(parseCsvLine(line), headers)
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
            quote(data.problemName),
            data.solved.toString(),
            data.timeToSolve?.toString() ?: "",
            quote(data.comments ?: ""),
            data.solvedDate?.toString() ?: "",
            data.lastModified.toString()
        ).joinToString(",")
    }

    private fun serializeProblem(data: ProblemExportData): String {
        return listOf(
            quote(data.name),
            quote(data.difficulty),
            data.intermediateTime?.toString() ?: "",
            data.advancedTime?.toString() ?: "",
            data.topTime?.toString() ?: "",
            quote(data.pattern ?: ""),
            quote(data.listId),
            data.solved.toString(),
            data.timeToSolve?.toString() ?: "",
            quote(data.comments ?: ""),
            data.solvedDate?.toString() ?: "",
            data.lastModified?.toString() ?: ""
        ).joinToString(",")
    }

    private fun parseProgressLine(values: List<String>, headers: List<String>): ProgressExportData? {
        if (values.size < headers.size) return null

        val map = headers.zip(values).toMap()
        return try {
            ProgressExportData(
                problemName = map["Problem Name"] ?: return null,
                solved = map["Solved"]?.toBooleanStrictOrNull() ?: false,
                timeToSolve = map["Time To Solve"]?.toIntOrNull(),
                comments = map["Comments"]?.takeIf { it.isNotBlank() },
                solvedDate = map["Solved Date"]?.toLongOrNull(),
                lastModified = map["Last Modified"]?.toLongOrNull() ?: System.currentTimeMillis()
            )
        } catch (e: Exception) {
            null
        }
    }

    private fun parseProblemLine(values: List<String>, headers: List<String>): ProblemExportData? {
        if (values.size < headers.size) return null

        val map = headers.zip(values).toMap()
        return try {
            ProblemExportData(
                name = map["Problem Name"] ?: return null,
                difficulty = map["Difficulty"] ?: "Medium",
                intermediateTime = map["Intermediate Time"]?.toIntOrNull(),
                advancedTime = map["Advanced Time"]?.toIntOrNull(),
                topTime = map["Top Time"]?.toIntOrNull(),
                pattern = map["Pattern"]?.takeIf { it.isNotBlank() },
                listId = map["List ID"] ?: "custom",
                solved = map["Solved"]?.toBooleanStrictOrNull() ?: false,
                timeToSolve = map["Time To Solve"]?.toIntOrNull(),
                comments = map["Comments"]?.takeIf { it.isNotBlank() },
                solvedDate = map["Solved Date"]?.toLongOrNull(),
                lastModified = map["Last Modified"]?.toLongOrNull()
            )
        } catch (e: Exception) {
            null
        }
    }

    /**
     * Quote a value according to RFC 4180.
     * Always quote strings, escape internal quotes by doubling.
     */
    private fun quote(value: String): String {
        val escaped = value.replace("\"", "\"\"")
        return "\"$escaped\""
    }

    /**
     * Parse a CSV line according to RFC 4180.
     * Handles quoted fields and escaped quotes.
     */
    private fun parseCsvLine(line: String): List<String> {
        val result = mutableListOf<String>()
        var current = StringBuilder()
        var inQuotes = false
        var i = 0

        while (i < line.length) {
            val c = line[i]
            when {
                c == '"' && !inQuotes -> {
                    inQuotes = true
                }
                c == '"' && inQuotes -> {
                    // Check for escaped quote
                    if (i + 1 < line.length && line[i + 1] == '"') {
                        current.append('"')
                        i++
                    } else {
                        inQuotes = false
                    }
                }
                c == ',' && !inQuotes -> {
                    result.add(current.toString())
                    current = StringBuilder()
                }
                else -> {
                    current.append(c)
                }
            }
            i++
        }
        result.add(current.toString())

        return result
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
