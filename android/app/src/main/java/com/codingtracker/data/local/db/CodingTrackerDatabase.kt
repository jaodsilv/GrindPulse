package com.codingtracker.data.local.db

import androidx.room.Database
import androidx.room.RoomDatabase
import com.codingtracker.data.local.db.dao.DuplicateMappingDao
import com.codingtracker.data.local.db.dao.ProblemDao
import com.codingtracker.data.local.db.dao.ProblemListDao
import com.codingtracker.data.local.db.dao.UserProgressDao
import com.codingtracker.data.local.db.entity.DuplicateMappingEntity
import com.codingtracker.data.local.db.entity.ProblemEntity
import com.codingtracker.data.local.db.entity.ProblemListEntity
import com.codingtracker.data.local.db.entity.UserProgressEntity

@Database(
    entities = [
        ProblemEntity::class,
        ProblemListEntity::class,
        UserProgressEntity::class,
        DuplicateMappingEntity::class
    ],
    version = 1,
    exportSchema = true
)
abstract class CodingTrackerDatabase : RoomDatabase() {
    abstract fun problemDao(): ProblemDao
    abstract fun problemListDao(): ProblemListDao
    abstract fun userProgressDao(): UserProgressDao
    abstract fun duplicateMappingDao(): DuplicateMappingDao

    companion object {
        const val DATABASE_NAME = "coding_tracker.db"
    }
}
