package com.codingtracker.data.export.converter

import com.codingtracker.data.export.model.ExportBundle
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import javax.inject.Inject
import javax.inject.Singleton

/**
 * JSON format converter using kotlinx.serialization.
 */
@Singleton
class JsonFormatConverter @Inject constructor() : DataFormatConverter {

    private val json = Json {
        prettyPrint = true
        ignoreUnknownKeys = true
        encodeDefaults = true
    }

    override val format: DataFormat = DataFormat.JSON

    override fun serialize(bundle: ExportBundle): String {
        return try {
            json.encodeToString(bundle)
        } catch (e: Exception) {
            throw FormatParseException("Failed to serialize to JSON: ${e.message}", e)
        }
    }

    override fun deserialize(content: String): ExportBundle {
        return try {
            json.decodeFromString<ExportBundle>(content)
        } catch (e: Exception) {
            throw FormatParseException("Failed to parse JSON: ${e.message}", e)
        }
    }
}
