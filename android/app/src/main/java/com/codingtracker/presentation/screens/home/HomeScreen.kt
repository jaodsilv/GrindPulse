package com.codingtracker.presentation.screens.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.ScrollableTabRow
import androidx.compose.material3.Tab
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.codingtracker.domain.model.Difficulty
import com.codingtracker.presentation.components.ProblemCard
import com.codingtracker.presentation.components.ProgressIndicator

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onNavigateToProblem: (String) -> Unit,
    onNavigateToSettings: () -> Unit,
    viewModel: HomeViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Coding Tracker") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary
                ),
                actions = {
                    IconButton(onClick = onNavigateToSettings) {
                        Icon(
                            Icons.Default.Settings,
                            contentDescription = "Settings",
                            tint = MaterialTheme.colorScheme.onPrimary
                        )
                    }
                }
            )
        }
    ) { paddingValues ->
        if (uiState.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
            ) {
                // Overall progress
                ProgressIndicator(
                    stats = uiState.overallProgress,
                    label = "Overall Progress (unique)",
                    modifier = Modifier.padding(16.dp)
                )

                // Tab row for problem lists
                if (uiState.problemLists.isNotEmpty()) {
                    val selectedIndex = uiState.problemLists
                        .indexOfFirst { it.id == uiState.selectedListId }
                        .coerceAtLeast(0)

                    ScrollableTabRow(
                        selectedTabIndex = selectedIndex,
                        modifier = Modifier.fillMaxWidth(),
                        edgePadding = 16.dp
                    ) {
                        uiState.problemLists.forEach { list ->
                            Tab(
                                selected = list.id == uiState.selectedListId,
                                onClick = { viewModel.selectList(list.id) },
                                text = { Text(list.displayName) }
                            )
                        }
                    }
                }

                // List progress
                ProgressIndicator(
                    stats = uiState.listProgress,
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
                )

                // Search and filters
                FilterSection(
                    searchQuery = uiState.searchQuery,
                    onSearchQueryChange = viewModel::updateSearchQuery,
                    selectedDifficulty = uiState.selectedDifficulty,
                    onDifficultyChange = viewModel::selectDifficulty,
                    selectedPattern = uiState.selectedPattern,
                    onPatternChange = viewModel::selectPattern,
                    patterns = uiState.patterns,
                    showSolvedOnly = uiState.showSolvedOnly,
                    onSolvedFilterChange = viewModel::setSolvedFilter,
                    onClearFilters = viewModel::clearFilters
                )

                // Problem list
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(
                        items = uiState.problems,
                        key = { it.id }
                    ) { problem ->
                        ProblemCard(
                            problem = problem,
                            onToggleSolved = { viewModel.toggleProblemSolved(problem) },
                            onClick = { onNavigateToProblem(problem.id) }
                        )
                    }

                    if (uiState.problems.isEmpty()) {
                        item {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(32.dp),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = "No problems found",
                                    style = MaterialTheme.typography.bodyLarge,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun FilterSection(
    searchQuery: String,
    onSearchQueryChange: (String) -> Unit,
    selectedDifficulty: Difficulty?,
    onDifficultyChange: (Difficulty?) -> Unit,
    selectedPattern: String?,
    onPatternChange: (String?) -> Unit,
    patterns: List<String>,
    showSolvedOnly: Boolean?,
    onSolvedFilterChange: (Boolean?) -> Unit,
    onClearFilters: () -> Unit
) {
    var showFilters by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp)
    ) {
        // Search bar
        OutlinedTextField(
            value = searchQuery,
            onValueChange = onSearchQueryChange,
            modifier = Modifier.fillMaxWidth(),
            placeholder = { Text("Search problems...") },
            leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
            trailingIcon = {
                Row {
                    if (searchQuery.isNotEmpty()) {
                        IconButton(onClick = { onSearchQueryChange("") }) {
                            Icon(Icons.Default.Clear, contentDescription = "Clear search")
                        }
                    }
                    IconButton(onClick = { showFilters = !showFilters }) {
                        Icon(Icons.Default.Menu, contentDescription = "Toggle filters")
                    }
                }
            },
            singleLine = true
        )

        // Filters
        if (showFilters) {
            Spacer(modifier = Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // Difficulty dropdown
                var difficultyExpanded by remember { mutableStateOf(false) }
                ExposedDropdownMenuBox(
                    expanded = difficultyExpanded,
                    onExpandedChange = { difficultyExpanded = it },
                    modifier = Modifier.weight(1f)
                ) {
                    OutlinedTextField(
                        value = selectedDifficulty?.displayName ?: "All",
                        onValueChange = {},
                        readOnly = true,
                        label = { Text("Difficulty") },
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = difficultyExpanded) },
                        modifier = Modifier.menuAnchor()
                    )
                    ExposedDropdownMenu(
                        expanded = difficultyExpanded,
                        onDismissRequest = { difficultyExpanded = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("All") },
                            onClick = {
                                onDifficultyChange(null)
                                difficultyExpanded = false
                            }
                        )
                        Difficulty.entries.forEach { difficulty ->
                            DropdownMenuItem(
                                text = { Text(difficulty.displayName) },
                                onClick = {
                                    onDifficultyChange(difficulty)
                                    difficultyExpanded = false
                                }
                            )
                        }
                    }
                }

                // Status dropdown
                var statusExpanded by remember { mutableStateOf(false) }
                ExposedDropdownMenuBox(
                    expanded = statusExpanded,
                    onExpandedChange = { statusExpanded = it },
                    modifier = Modifier.weight(1f)
                ) {
                    OutlinedTextField(
                        value = when (showSolvedOnly) {
                            true -> "Solved"
                            false -> "Unsolved"
                            null -> "All"
                        },
                        onValueChange = {},
                        readOnly = true,
                        label = { Text("Status") },
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = statusExpanded) },
                        modifier = Modifier.menuAnchor()
                    )
                    ExposedDropdownMenu(
                        expanded = statusExpanded,
                        onDismissRequest = { statusExpanded = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("All") },
                            onClick = {
                                onSolvedFilterChange(null)
                                statusExpanded = false
                            }
                        )
                        DropdownMenuItem(
                            text = { Text("Solved") },
                            onClick = {
                                onSolvedFilterChange(true)
                                statusExpanded = false
                            }
                        )
                        DropdownMenuItem(
                            text = { Text("Unsolved") },
                            onClick = {
                                onSolvedFilterChange(false)
                                statusExpanded = false
                            }
                        )
                    }
                }
            }

            // Pattern dropdown (full width)
            if (patterns.isNotEmpty()) {
                Spacer(modifier = Modifier.height(8.dp))
                var patternExpanded by remember { mutableStateOf(false) }
                ExposedDropdownMenuBox(
                    expanded = patternExpanded,
                    onExpandedChange = { patternExpanded = it },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    OutlinedTextField(
                        value = selectedPattern ?: "All Patterns",
                        onValueChange = {},
                        readOnly = true,
                        label = { Text("Pattern") },
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = patternExpanded) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .menuAnchor()
                    )
                    ExposedDropdownMenu(
                        expanded = patternExpanded,
                        onDismissRequest = { patternExpanded = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("All Patterns") },
                            onClick = {
                                onPatternChange(null)
                                patternExpanded = false
                            }
                        )
                        patterns.forEach { pattern ->
                            DropdownMenuItem(
                                text = { Text(pattern) },
                                onClick = {
                                    onPatternChange(pattern)
                                    patternExpanded = false
                                }
                            )
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(8.dp))
    }
}
