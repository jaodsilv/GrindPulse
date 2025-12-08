package com.codingtracker.presentation.screens.settings.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.selection.selectable
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
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import com.codingtracker.data.export.converter.DataFormat
import com.codingtracker.data.export.model.ExportType
import com.codingtracker.domain.model.ProblemList

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExportDialog(
    problemLists: List<ProblemList>,
    selectedFormat: DataFormat,
    selectedType: ExportType,
    selectedListId: String?,
    isExporting: Boolean,
    exportReady: Boolean,
    onFormatChange: (DataFormat) -> Unit,
    onTypeChange: (ExportType) -> Unit,
    onListIdChange: (String?) -> Unit,
    onPrepareExport: () -> Unit,
    onSaveExport: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = { if (!isExporting) onDismiss() },
        title = { Text("Export Data") },
        text = {
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Export type selection
                Text(
                    text = "What to export:",
                    style = MaterialTheme.typography.labelLarge
                )

                ExportType.entries.forEach { type ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .selectable(
                                selected = selectedType == type,
                                onClick = { onTypeChange(type) },
                                role = Role.RadioButton
                            )
                            .padding(vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        RadioButton(
                            selected = selectedType == type,
                            onClick = null
                        )
                        Text(
                            text = when (type) {
                                ExportType.PROGRESS_ONLY -> "Progress only"
                                ExportType.FULL_DATA -> "Full data (problems + progress)"
                            },
                            modifier = Modifier.padding(start = 8.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))

                // List selection
                Text(
                    text = "Select list:",
                    style = MaterialTheme.typography.labelLarge
                )

                var listExpanded by remember { mutableStateOf(false) }
                ExposedDropdownMenuBox(
                    expanded = listExpanded,
                    onExpandedChange = { listExpanded = it }
                ) {
                    OutlinedTextField(
                        value = selectedListId?.let { id ->
                            problemLists.find { it.id == id }?.displayName
                        } ?: "All lists",
                        onValueChange = {},
                        readOnly = true,
                        label = { Text("List") },
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = listExpanded) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .menuAnchor()
                    )
                    ExposedDropdownMenu(
                        expanded = listExpanded,
                        onDismissRequest = { listExpanded = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("All lists") },
                            onClick = {
                                onListIdChange(null)
                                listExpanded = false
                            }
                        )
                        problemLists.forEach { list ->
                            DropdownMenuItem(
                                text = { Text(list.displayName) },
                                onClick = {
                                    onListIdChange(list.id)
                                    listExpanded = false
                                }
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))

                // Format selection
                FormatSelector(
                    selectedFormat = selectedFormat,
                    onFormatSelected = onFormatChange
                )

                if (isExporting) {
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
            if (exportReady) {
                Button(
                    onClick = onSaveExport,
                    enabled = !isExporting
                ) {
                    Text("Save File")
                }
            } else {
                Button(
                    onClick = onPrepareExport,
                    enabled = !isExporting
                ) {
                    Text("Export")
                }
            }
        },
        dismissButton = {
            OutlinedButton(
                onClick = onDismiss,
                enabled = !isExporting
            ) {
                Text("Cancel")
            }
        }
    )
}
