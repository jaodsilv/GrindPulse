package com.codingtracker.presentation.screens.settings.components

import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import com.codingtracker.data.export.converter.DataFormat

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FormatSelector(
    selectedFormat: DataFormat,
    onFormatSelected: (DataFormat) -> Unit,
    modifier: Modifier = Modifier,
    label: String = "Format"
) {
    var expanded by remember { mutableStateOf(false) }

    ExposedDropdownMenuBox(
        expanded = expanded,
        onExpandedChange = { expanded = it },
        modifier = modifier
    ) {
        OutlinedTextField(
            value = selectedFormat.displayName,
            onValueChange = {},
            readOnly = true,
            label = { Text(label) },
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
            modifier = Modifier
                .fillMaxWidth()
                .menuAnchor()
        )
        ExposedDropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false }
        ) {
            DataFormat.entries.forEach { format ->
                DropdownMenuItem(
                    text = {
                        Text("${format.displayName} (.${format.fileExtension})")
                    },
                    onClick = {
                        onFormatSelected(format)
                        expanded = false
                    }
                )
            }
        }
    }
}
