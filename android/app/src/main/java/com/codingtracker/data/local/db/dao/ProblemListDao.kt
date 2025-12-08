package com.codingtracker.data.local.db.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.codingtracker.data.local.db.entity.ProblemListEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ProblemListDao {

    @Query("SELECT * FROM problem_lists ORDER BY sortOrder")
    fun getAllLists(): Flow<List<ProblemListEntity>>

    @Query("SELECT * FROM problem_lists WHERE id = :listId")
    suspend fun getListById(listId: String): ProblemListEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(list: ProblemListEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(lists: List<ProblemListEntity>)

    @Query("DELETE FROM problem_lists")
    suspend fun deleteAll()
}
