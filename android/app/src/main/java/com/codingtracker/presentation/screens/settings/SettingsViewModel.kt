package com.codingtracker.presentation.screens.settings

import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.codingtracker.data.export.FileOperations
import com.codingtracker.data.export.ImportExportService
import com.codingtracker.data.export.converter.DataFormat
import com.codingtracker.data.export.model.ConflictStrategy
import com.codingtracker.data.export.model.ExportBundle
import com.codingtracker.data.export.model.ExportType
import com.codingtracker.data.export.model.ImportConflict
import com.codingtracker.data.export.model.ImportResult
import com.codingtracker.data.repository.ProblemRepository
import com.codingtracker.domain.model.ProblemList
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SettingsUiState(
    val darkModeEnabled: Boolean = false,
    val problemLists: List<ProblemList> = emptyList(),

    // Export state
    val showExportDialog: Boolean = false,
    val selectedExportFormat: DataFormat = DataFormat.JSON,
    val selectedExportType: ExportType = ExportType.PROGRESS_ONLY,
    val selectedExportListId: String? = null,
    val isExporting: Boolean = false,
    val exportContent: String? = null,
    val exportFilename: String? = null,

    // Import state
    val showImportDialog: Boolean = false,
    val selectedImportFormat: DataFormat? = null,
    val isImporting: Boolean = false,
    val importBundle: ExportBundle? = null,
    val selectedImportListId: String = "custom",
    val showNewListDialog: Boolean = false,
    val newListName: String = "",

    // Conflict state
    val showConflictDialog: Boolean = false,
    val conflicts: List<ImportConflict> = emptyList(),
    val selectedConflictStrategy: ConflictStrategy = ConflictStrategy.ASK_EACH,

    // Results
    val importResult: ImportResult? = null,
    val error: String? = null,
    val successMessage: String? = null
)

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val importExportService: ImportExportService,
    private val fileOperations: FileOperations,
    private val problemRepository: ProblemRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(SettingsUiState())
    val uiState: StateFlow<SettingsUiState> = _uiState.asStateFlow()

    init {
        loadProblemLists()
    }

    private fun loadProblemLists() {
        viewModelScope.launch {
            problemRepository.getProblemLists().collect { lists ->
                _uiState.value = _uiState.value.copy(problemLists = lists)
            }
        }
    }

    // Dark mode
    fun setDarkMode(enabled: Boolean) {
        _uiState.value = _uiState.value.copy(darkModeEnabled = enabled)
    }

    // Export Dialog
    fun showExportDialog() {
        _uiState.value = _uiState.value.copy(
            showExportDialog = true,
            error = null,
            successMessage = null
        )
    }

    fun hideExportDialog() {
        _uiState.value = _uiState.value.copy(
            showExportDialog = false,
            exportContent = null,
            exportFilename = null
        )
    }

    fun setExportFormat(format: DataFormat) {
        _uiState.value = _uiState.value.copy(selectedExportFormat = format)
    }

    fun setExportType(type: ExportType) {
        _uiState.value = _uiState.value.copy(selectedExportType = type)
    }

    fun setExportListId(listId: String?) {
        _uiState.value = _uiState.value.copy(selectedExportListId = listId)
    }

    fun prepareExport() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isExporting = true, error = null)

            val state = _uiState.value
            val result = when (state.selectedExportType) {
                ExportType.PROGRESS_ONLY -> importExportService.exportProgress(
                    state.selectedExportFormat,
                    state.selectedExportListId
                )
                ExportType.FULL_DATA -> importExportService.exportProblemsWithProgress(
                    state.selectedExportFormat,
                    state.selectedExportListId
                )
            }

            result.fold(
                onSuccess = { bundle ->
                    val content = importExportService.serializeBundle(bundle, state.selectedExportFormat)
                    val filename = importExportService.getSuggestedFilename(
                        state.selectedExportFormat,
                        state.selectedExportListId,
                        state.selectedExportType == ExportType.PROGRESS_ONLY
                    )
                    _uiState.value = _uiState.value.copy(
                        isExporting = false,
                        exportContent = content,
                        exportFilename = filename
                    )
                },
                onFailure = { e ->
                    _uiState.value = _uiState.value.copy(
                        isExporting = false,
                        error = "Export failed: ${e.message}"
                    )
                }
            )
        }
    }

    fun saveExportToUri(uri: Uri) {
        viewModelScope.launch {
            val content = _uiState.value.exportContent ?: return@launch
            _uiState.value = _uiState.value.copy(isExporting = true)

            fileOperations.writeToUri(uri, content).fold(
                onSuccess = {
                    _uiState.value = _uiState.value.copy(
                        isExporting = false,
                        showExportDialog = false,
                        exportContent = null,
                        exportFilename = null,
                        successMessage = "Export successful!"
                    )
                },
                onFailure = { e ->
                    _uiState.value = _uiState.value.copy(
                        isExporting = false,
                        error = "Failed to save file: ${e.message}"
                    )
                }
            )
        }
    }

    // Import Dialog
    fun showImportDialog() {
        _uiState.value = _uiState.value.copy(
            showImportDialog = true,
            error = null,
            successMessage = null,
            importBundle = null,
            selectedImportFormat = null
        )
    }

    fun hideImportDialog() {
        _uiState.value = _uiState.value.copy(
            showImportDialog = false,
            importBundle = null,
            selectedImportFormat = null
        )
    }

    fun setImportFormat(format: DataFormat) {
        _uiState.value = _uiState.value.copy(selectedImportFormat = format)
    }

    fun setImportListId(listId: String) {
        _uiState.value = _uiState.value.copy(selectedImportListId = listId)
    }

    fun loadImportFile(uri: Uri) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isImporting = true, error = null)

            val filename = fileOperations.getFilenameFromUri(uri)
            val contentResult = fileOperations.readFromUri(uri)

            contentResult.fold(
                onSuccess = { content ->
                    val parseResult = importExportService.parseImportContent(
                        content,
                        _uiState.value.selectedImportFormat,
                        filename
                    )

                    parseResult.fold(
                        onSuccess = { bundle ->
                            val detectedFormat = importExportService.detectFormat(content, filename)
                            _uiState.value = _uiState.value.copy(
                                isImporting = false,
                                importBundle = bundle,
                                selectedImportFormat = detectedFormat
                            )
                        },
                        onFailure = { e ->
                            _uiState.value = _uiState.value.copy(
                                isImporting = false,
                                error = "Failed to parse file: ${e.message}"
                            )
                        }
                    )
                },
                onFailure = { e ->
                    _uiState.value = _uiState.value.copy(
                        isImporting = false,
                        error = "Failed to read file: ${e.message}"
                    )
                }
            )
        }
    }

    fun setConflictStrategy(strategy: ConflictStrategy) {
        _uiState.value = _uiState.value.copy(selectedConflictStrategy = strategy)
    }

    fun performImport() {
        viewModelScope.launch {
            val bundle = _uiState.value.importBundle ?: return@launch
            _uiState.value = _uiState.value.copy(isImporting = true, error = null)

            val result = when (bundle.exportType) {
                ExportType.PROGRESS_ONLY -> {
                    importExportService.importProgress(
                        bundle,
                        _uiState.value.selectedConflictStrategy
                    )
                }
                ExportType.FULL_DATA -> {
                    importExportService.importProblems(
                        bundle,
                        _uiState.value.selectedImportListId,
                        _uiState.value.selectedConflictStrategy
                    )
                }
            }

            if (result.hasConflicts && _uiState.value.selectedConflictStrategy == ConflictStrategy.ASK_EACH) {
                _uiState.value = _uiState.value.copy(
                    isImporting = false,
                    showConflictDialog = true,
                    conflicts = result.conflicts
                )
            } else {
                _uiState.value = _uiState.value.copy(
                    isImporting = false,
                    showImportDialog = false,
                    importResult = result,
                    importBundle = null,
                    successMessage = buildImportMessage(result)
                )
            }
        }
    }

    // Conflict Dialog
    fun hideConflictDialog() {
        _uiState.value = _uiState.value.copy(
            showConflictDialog = false,
            conflicts = emptyList()
        )
    }

    fun resolveConflictsWithStrategy(strategy: ConflictStrategy) {
        viewModelScope.launch {
            val bundle = _uiState.value.importBundle ?: return@launch

            _uiState.value = _uiState.value.copy(
                showConflictDialog = false,
                isImporting = true
            )

            val result = importExportService.importProgress(bundle, strategy)

            _uiState.value = _uiState.value.copy(
                isImporting = false,
                showImportDialog = false,
                importResult = result,
                importBundle = null,
                conflicts = emptyList(),
                successMessage = buildImportMessage(result)
            )
        }
    }

    // New List Dialog
    fun showNewListDialog() {
        _uiState.value = _uiState.value.copy(
            showNewListDialog = true,
            newListName = ""
        )
    }

    fun hideNewListDialog() {
        _uiState.value = _uiState.value.copy(showNewListDialog = false)
    }

    fun setNewListName(name: String) {
        _uiState.value = _uiState.value.copy(newListName = name)
    }

    fun createAndSelectNewList() {
        val name = _uiState.value.newListName.trim()
        if (name.isBlank()) return

        val listId = name.lowercase().replace(" ", "_")
        _uiState.value = _uiState.value.copy(
            selectedImportListId = listId,
            showNewListDialog = false,
            newListName = ""
        )
    }

    // Clear messages
    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }

    fun clearSuccessMessage() {
        _uiState.value = _uiState.value.copy(successMessage = null)
    }

    private fun buildImportMessage(result: ImportResult): String {
        return buildString {
            append("Import complete: ")
            append("${result.successCount} imported")
            if (result.skippedCount > 0) {
                append(", ${result.skippedCount} skipped")
            }
            if (result.failedCount > 0) {
                append(", ${result.failedCount} failed")
            }
        }
    }
}
