package com.codingtracker.data.export.converter

import android.util.Xml
import com.codingtracker.data.export.model.ExportBundle
import com.codingtracker.data.export.model.ExportType
import com.codingtracker.data.export.model.ProblemExportData
import com.codingtracker.data.export.model.ProgressExportData
import org.xmlpull.v1.XmlPullParser
import org.xmlpull.v1.XmlSerializer
import java.io.StringReader
import java.io.StringWriter
import javax.inject.Inject
import javax.inject.Singleton

/**
 * XML format converter using Android's XmlPullParser and XmlSerializer.
 */
@Singleton
class XmlFormatConverter @Inject constructor() : DataFormatConverter {

    override val format: DataFormat = DataFormat.XML

    override fun serialize(bundle: ExportBundle): String {
        val writer = StringWriter()
        val serializer = Xml.newSerializer()

        try {
            serializer.setOutput(writer)
            serializer.startDocument("UTF-8", true)
            serializer.setFeature("http://xmlpull.org/v1/doc/features.html#indent-output", true)

            // Root element with attributes
            serializer.startTag(null, "exportBundle")
            serializer.attribute(null, "version", bundle.version.toString())
            serializer.attribute(null, "exportedAt", bundle.exportedAt.toString())
            serializer.attribute(null, "exportType", bundle.exportType.name)
            bundle.listId?.let { serializer.attribute(null, "listId", it) }

            // Data element
            serializer.startTag(null, "data")

            when (bundle.exportType) {
                ExportType.PROGRESS_ONLY -> {
                    bundle.progressData?.forEach { data ->
                        serializeProgress(serializer, data)
                    }
                }
                ExportType.FULL_DATA -> {
                    bundle.problemData?.forEach { data ->
                        serializeProblem(serializer, data)
                    }
                }
            }

            serializer.endTag(null, "data")
            serializer.endTag(null, "exportBundle")
            serializer.endDocument()

            return writer.toString()
        } catch (e: Exception) {
            throw FormatParseException("Failed to serialize to XML: ${e.message}", e)
        }
    }

    override fun deserialize(content: String): ExportBundle {
        val parser = Xml.newPullParser()
        try {
            parser.setInput(StringReader(content))

            var version = 1
            var exportedAt = System.currentTimeMillis()
            var exportType: ExportType = ExportType.PROGRESS_ONLY
            var listId: String? = null
            val progressData = mutableListOf<ProgressExportData>()
            val problemData = mutableListOf<ProblemExportData>()

            var eventType = parser.eventType
            while (eventType != XmlPullParser.END_DOCUMENT) {
                when (eventType) {
                    XmlPullParser.START_TAG -> {
                        when (parser.name) {
                            "exportBundle" -> {
                                version = parser.getAttributeValue(null, "version")?.toIntOrNull() ?: 1
                                exportedAt = parser.getAttributeValue(null, "exportedAt")?.toLongOrNull()
                                    ?: System.currentTimeMillis()
                                exportType = parser.getAttributeValue(null, "exportType")?.let {
                                    runCatching { ExportType.valueOf(it) }.getOrNull()
                                } ?: ExportType.PROGRESS_ONLY
                                listId = parser.getAttributeValue(null, "listId")
                            }
                            "progress" -> {
                                parseProgress(parser)?.let { progressData.add(it) }
                            }
                            "problem" -> {
                                parseProblem(parser)?.let { problemData.add(it) }
                            }
                        }
                    }
                }
                eventType = parser.next()
            }

            return ExportBundle(
                version = version,
                exportedAt = exportedAt,
                exportType = exportType,
                listId = listId,
                progressData = if (exportType == ExportType.PROGRESS_ONLY) progressData else null,
                problemData = if (exportType == ExportType.FULL_DATA) problemData else null
            )
        } catch (e: Exception) {
            throw FormatParseException("Failed to parse XML: ${e.message}", e)
        }
    }

    private fun serializeProgress(serializer: XmlSerializer, data: ProgressExportData) {
        serializer.startTag(null, "progress")
        serializer.attribute(null, "problemName", data.problemName)
        serializer.attribute(null, "solved", data.solved.toString())
        data.timeToSolve?.let { serializer.attribute(null, "timeToSolve", it.toString()) }
        data.solvedDate?.let { serializer.attribute(null, "solvedDate", it.toString()) }
        serializer.attribute(null, "lastModified", data.lastModified.toString())

        if (!data.comments.isNullOrBlank()) {
            serializer.startTag(null, "comments")
            serializer.text(data.comments)
            serializer.endTag(null, "comments")
        }

        serializer.endTag(null, "progress")
    }

    private fun serializeProblem(serializer: XmlSerializer, data: ProblemExportData) {
        serializer.startTag(null, "problem")
        serializer.attribute(null, "name", data.name)
        serializer.attribute(null, "difficulty", data.difficulty)
        serializer.attribute(null, "listId", data.listId)
        data.intermediateTime?.let { serializer.attribute(null, "intermediateTime", it.toString()) }
        data.advancedTime?.let { serializer.attribute(null, "advancedTime", it.toString()) }
        data.topTime?.let { serializer.attribute(null, "topTime", it.toString()) }
        data.pattern?.let { serializer.attribute(null, "pattern", it) }
        serializer.attribute(null, "solved", data.solved.toString())
        data.timeToSolve?.let { serializer.attribute(null, "timeToSolve", it.toString()) }
        data.solvedDate?.let { serializer.attribute(null, "solvedDate", it.toString()) }
        data.lastModified?.let { serializer.attribute(null, "lastModified", it.toString()) }

        if (!data.comments.isNullOrBlank()) {
            serializer.startTag(null, "comments")
            serializer.text(data.comments)
            serializer.endTag(null, "comments")
        }

        serializer.endTag(null, "problem")
    }

    private fun parseProgress(parser: XmlPullParser): ProgressExportData? {
        return try {
            val problemName = parser.getAttributeValue(null, "problemName") ?: return null
            val solved = parser.getAttributeValue(null, "solved")?.toBooleanStrictOrNull() ?: false
            val timeToSolve = parser.getAttributeValue(null, "timeToSolve")?.toIntOrNull()
            val solvedDate = parser.getAttributeValue(null, "solvedDate")?.toLongOrNull()
            val lastModified = parser.getAttributeValue(null, "lastModified")?.toLongOrNull()
                ?: System.currentTimeMillis()

            // Parse nested comments element
            var comments: String? = null
            var depth = 1
            while (depth > 0) {
                val eventType = parser.next()
                when (eventType) {
                    XmlPullParser.START_TAG -> {
                        if (parser.name == "comments") {
                            comments = parser.nextText()
                        }
                        depth++
                    }
                    XmlPullParser.END_TAG -> depth--
                    XmlPullParser.END_DOCUMENT -> break
                }
            }

            ProgressExportData(
                problemName = problemName,
                solved = solved,
                timeToSolve = timeToSolve,
                comments = comments?.takeIf { it.isNotBlank() },
                solvedDate = solvedDate,
                lastModified = lastModified
            )
        } catch (e: Exception) {
            null
        }
    }

    private fun parseProblem(parser: XmlPullParser): ProblemExportData? {
        return try {
            val name = parser.getAttributeValue(null, "name") ?: return null
            val difficulty = parser.getAttributeValue(null, "difficulty") ?: "Medium"
            val listId = parser.getAttributeValue(null, "listId") ?: "custom"
            val intermediateTime = parser.getAttributeValue(null, "intermediateTime")?.toIntOrNull()
            val advancedTime = parser.getAttributeValue(null, "advancedTime")?.toIntOrNull()
            val topTime = parser.getAttributeValue(null, "topTime")?.toIntOrNull()
            val pattern = parser.getAttributeValue(null, "pattern")
            val solved = parser.getAttributeValue(null, "solved")?.toBooleanStrictOrNull() ?: false
            val timeToSolve = parser.getAttributeValue(null, "timeToSolve")?.toIntOrNull()
            val solvedDate = parser.getAttributeValue(null, "solvedDate")?.toLongOrNull()
            val lastModified = parser.getAttributeValue(null, "lastModified")?.toLongOrNull()

            // Parse nested comments element
            var comments: String? = null
            var depth = 1
            while (depth > 0) {
                val eventType = parser.next()
                when (eventType) {
                    XmlPullParser.START_TAG -> {
                        if (parser.name == "comments") {
                            comments = parser.nextText()
                        }
                        depth++
                    }
                    XmlPullParser.END_TAG -> depth--
                    XmlPullParser.END_DOCUMENT -> break
                }
            }

            ProblemExportData(
                name = name,
                difficulty = difficulty,
                intermediateTime = intermediateTime,
                advancedTime = advancedTime,
                topTime = topTime,
                pattern = pattern?.takeIf { it.isNotBlank() },
                listId = listId,
                solved = solved,
                timeToSolve = timeToSolve,
                comments = comments?.takeIf { it.isNotBlank() },
                solvedDate = solvedDate,
                lastModified = lastModified
            )
        } catch (e: Exception) {
            null
        }
    }
}
