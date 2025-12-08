package com.codingtracker.data.local.db.entity

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index

@Entity(
    tableName = "user_progress",
    primaryKeys = ["problemId"],
    foreignKeys = [
        ForeignKey(
            entity = ProblemEntity::class,
            parentColumns = ["id"],
            childColumns = ["problemId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [
        Index(value = ["problemId"]),
        Index(value = ["solved"])
    ]
)
data class UserProgressEntity(
    val problemId: String,
    val solved: Boolean = false,
    val timeToSolve: Int? = null,
    val comments: String? = null,
    val solvedDate: Long? = null,
    val lastModified: Long = System.currentTimeMillis()
)
