package com.codingtracker.presentation.navigation

sealed class Screen(val route: String) {
    data object Home : Screen("home")

    data object ProblemDetail : Screen("problem/{problemId}") {
        fun createRoute(problemId: String) = "problem/$problemId"
    }

    data object Settings : Screen("settings")
}
