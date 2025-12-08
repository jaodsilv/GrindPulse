package com.codingtracker.presentation.screens.settings

import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.codingtracker.data.export.converter.DataFormat
import com.codingtracker.presentation.screens.settings.components.ConflictDialog
import com.codingtracker.presentation.screens.settings.components.ExportDialog
import com.codingtracker.presentation.screens.settings.components.ImportDialog
import com.codingtracker.presentation.screens.settings.components.NewListDialog

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    onNavigateBack: () -> Unit,
    viewModel: SettingsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current
    val snackbarHostState = remember { SnackbarHostState() }

    // File picker for import
    val importFilePicker = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocument()
    ) { uri ->
        uri?.let { viewModel.loadImportFile(it) }
    }

    // File saver for export
    val exportFileSaver = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.CreateDocument(
            uiState.selectedExportFormat.mimeType
        )
    ) { uri ->
        uri?.let { viewModel.saveExportToUri(it) }
    }

    // Handle success messages
    LaunchedEffect(uiState.successMessage) {
        uiState.successMessage?.let { message ->
            snackbarHostState.showSnackbar(message)
            viewModel.clearSuccessMessage()
        }
    }

    // Handle errors
    LaunchedEffect(uiState.error) {
        uiState.error?.let { error ->
            Toast.makeText(context, error, Toast.LENGTH_LONG).show()
            viewModel.clearError()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Settings") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary,
                    navigationIconContentColor = MaterialTheme.colorScheme.onPrimary
                )
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Appearance section
            Text(
                text = "Appearance",
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(16.dp)
            )

            ListItem(
                headlineContent = { Text("Dark Mode") },
                supportingContent = { Text("Use dark theme") },
                leadingContent = {
                    Icon(
                        Icons.Default.Star,
                        contentDescription = null
                    )
                },
                trailingContent = {
                    Switch(
                        checked = uiState.darkModeEnabled,
                        onCheckedChange = { viewModel.setDarkMode(it) }
                    )
                }
            )

            HorizontalDivider()

            // Data section
            Text(
                text = "Data",
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(16.dp)
            )

            ListItem(
                headlineContent = { Text("Export Data") },
                supportingContent = { Text("Export progress to file") },
                leadingContent = {
                    Icon(
                        Icons.Default.Share,
                        contentDescription = null
                    )
                },
                trailingContent = {
                    Icon(
                        Icons.AutoMirrored.Filled.Send,
                        contentDescription = null
                    )
                },
                modifier = Modifier.clickable { viewModel.showExportDialog() }
            )

            ListItem(
                headlineContent = { Text("Import Data") },
                supportingContent = { Text("Import progress from file") },
                leadingContent = {
                    Icon(
                        Icons.Default.Add,
                        contentDescription = null
                    )
                },
                trailingContent = {
                    Icon(
                        Icons.AutoMirrored.Filled.Send,
                        contentDescription = null
                    )
                },
                modifier = Modifier.clickable { viewModel.showImportDialog() }
            )

            HorizontalDivider()

            // About section
            Text(
                text = "About",
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(16.dp)
            )

            ListItem(
                headlineContent = { Text("Coding Tracker") },
                supportingContent = { Text("Version 1.0.0") },
                leadingContent = {
                    Icon(
                        Icons.Default.Info,
                        contentDescription = null
                    )
                }
            )

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Track your coding interview preparation across Blind 75, NeetCode 150/250, and more.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }

        // Export Dialog
        if (uiState.showExportDialog) {
            ExportDialog(
                problemLists = uiState.problemLists,
                selectedFormat = uiState.selectedExportFormat,
                selectedType = uiState.selectedExportType,
                selectedListId = uiState.selectedExportListId,
                isExporting = uiState.isExporting,
                exportReady = uiState.exportContent != null,
                onFormatChange = viewModel::setExportFormat,
                onTypeChange = viewModel::setExportType,
                onListIdChange = viewModel::setExportListId,
                onPrepareExport = viewModel::prepareExport,
                onSaveExport = {
                    uiState.exportFilename?.let { filename ->
                        exportFileSaver.launch(filename)
                    }
                },
                onDismiss = viewModel::hideExportDialog
            )
        }

        // Import Dialog
        if (uiState.showImportDialog) {
            ImportDialog(
                problemLists = uiState.problemLists,
                selectedFormat = uiState.selectedImportFormat,
                selectedListId = uiState.selectedImportListId,
                selectedConflictStrategy = uiState.selectedConflictStrategy,
                isImporting = uiState.isImporting,
                importBundle = uiState.importBundle,
                onFormatChange = viewModel::setImportFormat,
                onListIdChange = viewModel::setImportListId,
                onConflictStrategyChange = viewModel::setConflictStrategy,
                onSelectFile = {
                    importFilePicker.launch(DataFormat.allMimeTypes)
                },
                onNewList = viewModel::showNewListDialog,
                onImport = viewModel::performImport,
                onDismiss = viewModel::hideImportDialog
            )
        }

        // Conflict Dialog
        if (uiState.showConflictDialog) {
            ConflictDialog(
                conflicts = uiState.conflicts,
                onResolveWithStrategy = viewModel::resolveConflictsWithStrategy,
                onDismiss = viewModel::hideConflictDialog
            )
        }

        // New List Dialog
        if (uiState.showNewListDialog) {
            NewListDialog(
                listName = uiState.newListName,
                onNameChange = viewModel::setNewListName,
                onCreate = viewModel::createAndSelectNewList,
                onDismiss = viewModel::hideNewListDialog
            )
        }
    }
}
