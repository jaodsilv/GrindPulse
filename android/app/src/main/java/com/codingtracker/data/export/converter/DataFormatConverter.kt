package com.codingtracker.data.export.converter

import com.codingtracker.data.export.model.ExportBundle

/**
 * Supported data formats for import/export.
 */
enum class DataFormat(
    val displayName: String,
    val fileExtension: String,
    val mimeType: String
) {
    TSV(
        displayName = "TSV (Tab-Separated)",
        fileExtension = "tsv",
        mimeType = "text/tab-separated-values"
    ),
    CSV(
        displayName = "CSV (Comma-Separated)",
        fileExtension = "csv",
        mimeType = "text/csv"
    ),
    JSON(
        displayName = "JSON",
        fileExtension = "json",
        mimeType = "application/json"
    ),
    YAML(
        displayName = "YAML",
        fileExtension = "yaml",
        mimeType = "application/x-yaml"
    ),
    XML(
        displayName = "XML",
        fileExtension = "xml",
        mimeType = "application/xml"
    );

    companion object {
        /**
         * Detect format from filename or content.
         */
        fun fromFilename(filename: String): DataFormat? {
            val extension = filename.substringAfterLast('.', "").lowercase()
            return entries.find { it.fileExtension == extension }
        }

        /**
         * Detect format from file content.
         */
        fun fromContent(content: String): DataFormat? {
            val trimmed = content.trim()
            return when {
                trimmed.startsWith("{") || trimmed.startsWith("[") -> JSON
                trimmed.startsWith("<?xml") || trimmed.startsWith("<") -> XML
                trimmed.contains("\t") && !trimmed.contains(",") -> TSV
                trimmed.contains(",") -> CSV
                trimmed.contains(":") && trimmed.contains("\n") -> YAML
                else -> null
            }
        }

        val allMimeTypes: Array<String>
            get() = entries.map { it.mimeType }.toTypedArray()
    }
}

/**
 * Interface for format converters.
 * Each format (TSV, CSV, JSON, etc.) implements this interface.
 */
interface DataFormatConverter {
    /**
     * The format this converter handles.
     */
    val format: DataFormat

    /**
     * Serialize an export bundle to string.
     */
    fun serialize(bundle: ExportBundle): String

    /**
     * Deserialize string content to an export bundle.
     * @throws FormatParseException if content cannot be parsed
     */
    fun deserialize(content: String): ExportBundle
}

/**
 * Exception thrown when format parsing fails.
 */
class FormatParseException(
    message: String,
    cause: Throwable? = null
) : Exception(message, cause)
