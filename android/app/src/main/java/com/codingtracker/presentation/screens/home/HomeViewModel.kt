package com.codingtracker.presentation.screens.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.codingtracker.data.repository.ProblemRepository
import com.codingtracker.domain.model.Difficulty
import com.codingtracker.domain.model.Problem
import com.codingtracker.domain.model.ProblemList
import com.codingtracker.domain.model.ProgressStats
import com.codingtracker.domain.model.UserProgress
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import java.time.Instant
import javax.inject.Inject

data class HomeUiState(
    val isLoading: Boolean = true,
    val problemLists: List<ProblemList> = emptyList(),
    val selectedListId: String = "blind75",
    val problems: List<Problem> = emptyList(),
    val patterns: List<String> = emptyList(),
    val listProgress: ProgressStats = ProgressStats(0, 0),
    val overallProgress: ProgressStats = ProgressStats(0, 0),
    val searchQuery: String = "",
    val selectedDifficulty: Difficulty? = null,
    val selectedPattern: String? = null,
    val showSolvedOnly: Boolean? = null,
    val error: String? = null
)

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val repository: ProblemRepository
) : ViewModel() {

    private val _selectedListId = MutableStateFlow("blind75")
    private val _searchQuery = MutableStateFlow("")
    private val _selectedDifficulty = MutableStateFlow<Difficulty?>(null)
    private val _selectedPattern = MutableStateFlow<String?>(null)
    private val _showSolvedOnly = MutableStateFlow<Boolean?>(null)
    private val _isLoading = MutableStateFlow(true)

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        initializeData()
        observeData()
    }

    private fun initializeData() {
        viewModelScope.launch {
            try {
                repository.initializeData()
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    error = "Failed to initialize data: ${e.message}"
                )
            } finally {
                _isLoading.value = false
            }
        }
    }

    private fun observeData() {
        viewModelScope.launch {
            // Observe problem lists
            repository.getProblemLists().collect { lists ->
                _uiState.value = _uiState.value.copy(problemLists = lists)
            }
        }

        viewModelScope.launch {
            // Observe patterns
            repository.getAllPatterns().collect { patterns ->
                _uiState.value = _uiState.value.copy(patterns = patterns)
            }
        }

        viewModelScope.launch {
            // Observe overall progress
            repository.getOverallProgress().collect { progress ->
                _uiState.value = _uiState.value.copy(overallProgress = progress)
            }
        }

        viewModelScope.launch {
            // Observe filtered problems for selected list
            combine(
                _selectedListId,
                _searchQuery,
                _selectedDifficulty,
                _selectedPattern,
                _showSolvedOnly
            ) { listId, query, difficulty, pattern, solvedOnly ->
                FilterParams(listId, query, difficulty, pattern, solvedOnly)
            }.flatMapLatest { params ->
                repository.getFilteredProblems(
                    listId = params.listId,
                    searchQuery = params.searchQuery.takeIf { it.isNotBlank() },
                    difficulty = params.difficulty,
                    pattern = params.pattern,
                    solvedOnly = params.solvedOnly
                )
            }.collect { problems ->
                _uiState.value = _uiState.value.copy(
                    problems = problems,
                    isLoading = false
                )
            }
        }

        viewModelScope.launch {
            // Observe list progress
            _selectedListId.flatMapLatest { listId ->
                repository.getProgressForList(listId)
            }.collect { progress ->
                _uiState.value = _uiState.value.copy(listProgress = progress)
            }
        }

        // Observe filter state changes
        viewModelScope.launch {
            _selectedListId.collect { listId ->
                _uiState.value = _uiState.value.copy(selectedListId = listId)
            }
        }

        viewModelScope.launch {
            _searchQuery.collect { query ->
                _uiState.value = _uiState.value.copy(searchQuery = query)
            }
        }

        viewModelScope.launch {
            _selectedDifficulty.collect { difficulty ->
                _uiState.value = _uiState.value.copy(selectedDifficulty = difficulty)
            }
        }

        viewModelScope.launch {
            _selectedPattern.collect { pattern ->
                _uiState.value = _uiState.value.copy(selectedPattern = pattern)
            }
        }

        viewModelScope.launch {
            _showSolvedOnly.collect { solvedOnly ->
                _uiState.value = _uiState.value.copy(showSolvedOnly = solvedOnly)
            }
        }

        viewModelScope.launch {
            _isLoading.collect { loading ->
                _uiState.value = _uiState.value.copy(isLoading = loading)
            }
        }
    }

    fun selectList(listId: String) {
        _selectedListId.value = listId
    }

    fun updateSearchQuery(query: String) {
        _searchQuery.value = query
    }

    fun selectDifficulty(difficulty: Difficulty?) {
        _selectedDifficulty.value = difficulty
    }

    fun selectPattern(pattern: String?) {
        _selectedPattern.value = pattern
    }

    fun setSolvedFilter(solvedOnly: Boolean?) {
        _showSolvedOnly.value = solvedOnly
    }

    fun toggleProblemSolved(problem: Problem) {
        viewModelScope.launch {
            val newProgress = problem.progress.copy(
                solved = !problem.progress.solved,
                solvedDate = if (!problem.progress.solved) Instant.now() else null
            )
            repository.updateProgress(problem.id, newProgress)

            if (problem.isDuplicate) {
                repository.syncDuplicates(problem.name, newProgress)
            }
        }
    }

    fun clearFilters() {
        _searchQuery.value = ""
        _selectedDifficulty.value = null
        _selectedPattern.value = null
        _showSolvedOnly.value = null
    }

    private data class FilterParams(
        val listId: String,
        val searchQuery: String,
        val difficulty: Difficulty?,
        val pattern: String?,
        val solvedOnly: Boolean?
    )
}
