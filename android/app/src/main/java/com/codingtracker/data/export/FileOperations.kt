package com.codingtracker.data.export

import android.content.Context
import android.net.Uri
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Utility class for file operations using Android's Storage Access Framework.
 */
@Singleton
class FileOperations @Inject constructor(
    @ApplicationContext private val context: Context
) {

    /**
     * Write content to a URI obtained from Storage Access Framework.
     */
    suspend fun writeToUri(uri: Uri, content: String): Result<Unit> = withContext(Dispatchers.IO) {
        runCatching {
            context.contentResolver.openOutputStream(uri)?.use { outputStream ->
                OutputStreamWriter(outputStream, Charsets.UTF_8).use { writer ->
                    writer.write(content)
                }
            } ?: throw IllegalStateException("Could not open output stream for URI: $uri")
        }
    }

    /**
     * Read content from a URI obtained from Storage Access Framework.
     */
    suspend fun readFromUri(uri: Uri): Result<String> = withContext(Dispatchers.IO) {
        runCatching {
            context.contentResolver.openInputStream(uri)?.use { inputStream ->
                BufferedReader(InputStreamReader(inputStream, Charsets.UTF_8)).use { reader ->
                    reader.readText()
                }
            } ?: throw IllegalStateException("Could not open input stream for URI: $uri")
        }
    }

    /**
     * Get the filename from a URI.
     */
    fun getFilenameFromUri(uri: Uri): String? {
        return context.contentResolver.query(uri, null, null, null, null)?.use { cursor ->
            val nameIndex = cursor.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME)
            if (nameIndex != -1 && cursor.moveToFirst()) {
                cursor.getString(nameIndex)
            } else null
        }
    }

    /**
     * Get the file size from a URI.
     */
    fun getFileSizeFromUri(uri: Uri): Long? {
        return context.contentResolver.query(uri, null, null, null, null)?.use { cursor ->
            val sizeIndex = cursor.getColumnIndex(android.provider.OpenableColumns.SIZE)
            if (sizeIndex != -1 && cursor.moveToFirst()) {
                cursor.getLong(sizeIndex)
            } else null
        }
    }

    /**
     * Get the MIME type from a URI.
     */
    fun getMimeTypeFromUri(uri: Uri): String? {
        return context.contentResolver.getType(uri)
    }
}
