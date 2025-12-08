package com.codingtracker.data.local.db.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "duplicate_mappings",
    indices = [Index(value = ["problemName"])]
)
data class DuplicateMappingEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val problemName: String,
    val listIds: String  // JSON array of list IDs: ["blind75", "neetcode150"]
)
