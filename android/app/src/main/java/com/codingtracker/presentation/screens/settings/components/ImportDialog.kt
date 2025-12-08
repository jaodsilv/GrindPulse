package com.codingtracker.presentation.screens.settings.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.codingtracker.data.export.converter.DataFormat
import com.codingtracker.data.export.model.ConflictStrategy
import com.codingtracker.data.export.model.ExportBundle
import com.codingtracker.data.export.model.ExportType
import com.codingtracker.domain.model.ProblemList

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ImportDialog(
    problemLists: List<ProblemList>,
    selectedFormat: DataFormat?,
    selectedListId: String,
    selectedConflictStrategy: ConflictStrategy,
    isImporting: Boolean,
    importBundle: ExportBundle?,
    onFormatChange: (DataFormat) -> Unit,
    onListIdChange: (String) -> Unit,
    onConflictStrategyChange: (ConflictStrategy) -> Unit,
    onSelectFile: () -> Unit,
    onNewList: () -> Unit,
    onImport: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = { if (!isImporting) onDismiss() },
        title = { Text("Import Data") },
        text = {
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                if (importBundle == null) {
                    // File selection phase
                    Text(
                        text = "Select a file to import",
                        style = MaterialTheme.typography.bodyMedium
                    )

                    Button(
                        onClick = onSelectFile,
                        enabled = !isImporting,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Choose File")
                    }

                    Text(
                        text = "Supported formats: TSV, CSV, JSON, YAML, XML",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                } else {
                    // File loaded phase
                    Text(
                        text = "File loaded successfully!",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.primary
                    )

                    // Show detected info
                    Text(
                        text = buildString {
                            append("Type: ")
                            append(
                                when (importBundle.exportType) {
                                    ExportType.PROGRESS_ONLY -> "Progress data"
                                    ExportType.FULL_DATA -> "Full problem data"
                                }
                            )
                            appendLine()
                            append("Items: ")
                            append(
                                when (importBundle.exportType) {
                                    ExportType.PROGRESS_ONLY -> importBundle.progressData?.size ?: 0
                                    ExportType.FULL_DATA -> importBundle.problemData?.size ?: 0
                                }
                            )
                        },
                        style = MaterialTheme.typography.bodySmall
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    // Target list selection (only for full data import)
                    if (importBundle.exportType == ExportType.FULL_DATA) {
                        Text(
                            text = "Import to list:",
                            style = MaterialTheme.typography.labelLarge
                        )

                        var listExpanded by remember { mutableStateOf(false) }
                        ExposedDropdownMenuBox(
                            expanded = listExpanded,
                            onExpandedChange = { listExpanded = it }
                        ) {
                            OutlinedTextField(
                                value = problemLists.find { it.id == selectedListId }?.displayName
                                    ?: selectedListId,
                                onValueChange = {},
                                readOnly = true,
                                label = { Text("Target List") },
                                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = listExpanded) },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .menuAnchor()
                            )
                            ExposedDropdownMenu(
                                expanded = listExpanded,
                                onDismissRequest = { listExpanded = false }
                            ) {
                                problemLists.forEach { list ->
                                    DropdownMenuItem(
                                        text = { Text(list.displayName) },
                                        onClick = {
                                            onListIdChange(list.id)
                                            listExpanded = false
                                        }
                                    )
                                }
                                DropdownMenuItem(
                                    text = { Text("+ Create new list...") },
                                    onClick = {
                                        listExpanded = false
                                        onNewList()
                                    }
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    // Conflict strategy
                    Text(
                        text = "When conflicts occur:",
                        style = MaterialTheme.typography.labelLarge
                    )

                    var strategyExpanded by remember { mutableStateOf(false) }
                    ExposedDropdownMenuBox(
                        expanded = strategyExpanded,
                        onExpandedChange = { strategyExpanded = it }
                    ) {
                        OutlinedTextField(
                            value = when (selectedConflictStrategy) {
                                ConflictStrategy.ASK_EACH -> "Ask me"
                                ConflictStrategy.REPLACE_ALL -> "Replace existing"
                                ConflictStrategy.SKIP_ALL -> "Keep existing"
                                ConflictStrategy.MERGE_ALL -> "Keep newest"
                            },
                            onValueChange = {},
                            readOnly = true,
                            label = { Text("Conflict Resolution") },
                            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = strategyExpanded) },
                            modifier = Modifier
                                .fillMaxWidth()
                                .menuAnchor()
                        )
                        ExposedDropdownMenu(
                            expanded = strategyExpanded,
                            onDismissRequest = { strategyExpanded = false }
                        ) {
                            ConflictStrategy.entries.forEach { strategy ->
                                DropdownMenuItem(
                                    text = {
                                        Text(
                                            when (strategy) {
                                                ConflictStrategy.ASK_EACH -> "Ask me for each conflict"
                                                ConflictStrategy.REPLACE_ALL -> "Replace all existing data"
                                                ConflictStrategy.SKIP_ALL -> "Keep all existing data"
                                                ConflictStrategy.MERGE_ALL -> "Keep the newest version"
                                            }
                                        )
                                    },
                                    onClick = {
                                        onConflictStrategyChange(strategy)
                                        strategyExpanded = false
                                    }
                                )
                            }
                        }
                    }
                }

                if (isImporting) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.Center
                    ) {
                        CircularProgressIndicator()
                    }
                }
            }
        },
        confirmButton = {
            if (importBundle != null) {
                Button(
                    onClick = onImport,
                    enabled = !isImporting
                ) {
                    Text("Import")
                }
            }
        },
        dismissButton = {
            OutlinedButton(
                onClick = onDismiss,
                enabled = !isImporting
            ) {
                Text("Cancel")
            }
        }
    )
}
