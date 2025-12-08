package com.codingtracker.domain.model

import androidx.compose.ui.graphics.Color
import com.codingtracker.presentation.theme.DifficultyEasy
import com.codingtracker.presentation.theme.DifficultyHard
import com.codingtracker.presentation.theme.DifficultyMedium

enum class Difficulty(val displayName: String, val color: Color) {
    EASY("Easy", DifficultyEasy),
    MEDIUM("Medium", DifficultyMedium),
    HARD("Hard", DifficultyHard);

    companion object {
        fun fromString(value: String): Difficulty {
            return when (value.lowercase()) {
                "easy" -> EASY
                "medium" -> MEDIUM
                "hard" -> HARD
                else -> MEDIUM
            }
        }
    }
}
