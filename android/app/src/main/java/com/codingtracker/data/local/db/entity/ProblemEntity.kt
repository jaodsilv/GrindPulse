package com.codingtracker.data.local.db.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "problems",
    indices = [
        Index(value = ["listId"]),
        Index(value = ["name"]),
        Index(value = ["difficulty"]),
        Index(value = ["pattern"])
    ]
)
data class ProblemEntity(
    @PrimaryKey
    val id: String,
    val name: String,
    val difficulty: String,
    val intermediateTime: Int?,
    val advancedTime: Int?,
    val topTime: Int?,
    val pattern: String?,
    val listId: String
)
