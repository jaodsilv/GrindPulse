package com.codingtracker.data.local.db.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "problem_lists")
data class ProblemListEntity(
    @PrimaryKey
    val id: String,
    val displayName: String,
    val problemCount: Int,
    val sortOrder: Int
)
