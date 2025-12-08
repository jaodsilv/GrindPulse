package com.codingtracker.data.export.converter

import com.charleskorn.kaml.Yaml
import com.charleskorn.kaml.YamlConfiguration
import com.codingtracker.data.export.model.ExportBundle
import javax.inject.Inject
import javax.inject.Singleton

/**
 * YAML format converter using kaml library with kotlinx.serialization.
 */
@Singleton
class YamlFormatConverter @Inject constructor() : DataFormatConverter {

    private val yaml = Yaml(
        configuration = YamlConfiguration(
            encodeDefaults = true,
            strictMode = false
        )
    )

    override val format: DataFormat = DataFormat.YAML

    override fun serialize(bundle: ExportBundle): String {
        return try {
            yaml.encodeToString(ExportBundle.serializer(), bundle)
        } catch (e: Exception) {
            throw FormatParseException("Failed to serialize to YAML: ${e.message}", e)
        }
    }

    override fun deserialize(content: String): ExportBundle {
        return try {
            yaml.decodeFromString(ExportBundle.serializer(), content)
        } catch (e: Exception) {
            throw FormatParseException("Failed to parse YAML: ${e.message}", e)
        }
    }
}
