package com.codingtracker.presentation.screens.problemdetail

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.codingtracker.data.repository.ProblemRepository
import com.codingtracker.domain.model.Problem
import com.codingtracker.domain.model.UserProgress
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.time.Instant
import javax.inject.Inject

data class ProblemDetailUiState(
    val isLoading: Boolean = true,
    val problem: Problem? = null,
    val timeToSolve: String = "",
    val comments: String = "",
    val error: String? = null
)

@HiltViewModel
class ProblemDetailViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val repository: ProblemRepository
) : ViewModel() {

    private val problemId: String = savedStateHandle.get<String>("problemId") ?: ""

    private val _uiState = MutableStateFlow(ProblemDetailUiState())
    val uiState: StateFlow<ProblemDetailUiState> = _uiState.asStateFlow()

    init {
        loadProblem()
    }

    private fun loadProblem() {
        viewModelScope.launch {
            try {
                val problem = repository.getProblemById(problemId)
                if (problem != null) {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        problem = problem,
                        timeToSolve = problem.progress.timeToSolve?.toString() ?: "",
                        comments = problem.progress.comments ?: ""
                    )
                } else {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = "Problem not found"
                    )
                }
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }

    fun updateTimeToSolve(time: String) {
        _uiState.value = _uiState.value.copy(timeToSolve = time)
    }

    fun updateComments(comments: String) {
        _uiState.value = _uiState.value.copy(comments = comments)
    }

    fun toggleSolved() {
        viewModelScope.launch {
            val problem = _uiState.value.problem ?: return@launch
            val newSolved = !problem.progress.solved

            val newProgress = UserProgress(
                solved = newSolved,
                timeToSolve = _uiState.value.timeToSolve.toIntOrNull(),
                comments = _uiState.value.comments.takeIf { it.isNotBlank() },
                solvedDate = if (newSolved) Instant.now() else null
            )

            repository.updateProgress(problem.id, newProgress)

            if (problem.isDuplicate) {
                repository.syncDuplicates(problem.name, newProgress)
            }

            _uiState.value = _uiState.value.copy(
                problem = problem.copy(progress = newProgress)
            )
        }
    }

    fun saveProgress() {
        viewModelScope.launch {
            val problem = _uiState.value.problem ?: return@launch

            val newProgress = problem.progress.copy(
                timeToSolve = _uiState.value.timeToSolve.toIntOrNull(),
                comments = _uiState.value.comments.takeIf { it.isNotBlank() }
            )

            repository.updateProgress(problem.id, newProgress)

            if (problem.isDuplicate) {
                repository.syncDuplicates(problem.name, newProgress)
            }

            _uiState.value = _uiState.value.copy(
                problem = problem.copy(progress = newProgress)
            )
        }
    }
}
