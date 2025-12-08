package com.codingtracker.presentation.screens.settings.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.codingtracker.data.export.model.ConflictStrategy
import com.codingtracker.data.export.model.ImportConflict
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@Composable
fun ConflictDialog(
    conflicts: List<ImportConflict>,
    onResolveWithStrategy: (ConflictStrategy) -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("${conflicts.size} Conflict(s) Found") },
        text = {
            Column(
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "The following items already have progress data. How would you like to handle them?",
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(bottom = 16.dp)
                )

                LazyColumn(
                    modifier = Modifier.height(200.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(conflicts) { conflict ->
                        ConflictItem(conflict)
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                Text(
                    text = "Choose an action:",
                    style = MaterialTheme.typography.labelLarge
                )
            }
        },
        confirmButton = {
            Column(
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(
                    onClick = { onResolveWithStrategy(ConflictStrategy.REPLACE_ALL) },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Replace All")
                }
                OutlinedButton(
                    onClick = { onResolveWithStrategy(ConflictStrategy.SKIP_ALL) },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Skip All")
                }
                OutlinedButton(
                    onClick = { onResolveWithStrategy(ConflictStrategy.MERGE_ALL) },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Keep Newest")
                }
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}

@Composable
private fun ConflictItem(conflict: ImportConflict) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(12.dp)
        ) {
            Text(
                text = conflict.problemName,
                style = MaterialTheme.typography.titleSmall
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                // Existing data
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Existing",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    conflict.existingData?.let { existing ->
                        Text(
                            text = if (existing.solved) "Solved" else "Not solved",
                            style = MaterialTheme.typography.bodySmall
                        )
                        existing.timeToSolve?.let {
                            Text(
                                text = "${it}m",
                                style = MaterialTheme.typography.bodySmall
                            )
                        }
                        existing.solvedDate?.let {
                            Text(
                                text = formatDate(it),
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }

                // Imported data
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Importing",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                    Text(
                        text = if (conflict.importedData.solved) "Solved" else "Not solved",
                        style = MaterialTheme.typography.bodySmall
                    )
                    conflict.importedData.timeToSolve?.let {
                        Text(
                            text = "${it}m",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                    conflict.importedData.solvedDate?.let {
                        Text(
                            text = formatDate(it),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }
}

private fun formatDate(timestamp: Long): String {
    val formatter = SimpleDateFormat("MMM d, yyyy", Locale.getDefault())
    return formatter.format(Date(timestamp))
}
