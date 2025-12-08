package com.codingtracker.data.local.db.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.codingtracker.data.local.db.entity.ProblemEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ProblemDao {

    @Query("SELECT * FROM problems WHERE listId = :listId ORDER BY name")
    fun getProblemsForList(listId: String): Flow<List<ProblemEntity>>

    @Query("SELECT * FROM problems WHERE id = :problemId")
    suspend fun getProblemById(problemId: String): ProblemEntity?

    @Query("SELECT * FROM problems WHERE name = :name")
    suspend fun getProblemsByName(name: String): List<ProblemEntity>

    @Query("SELECT * FROM problems WHERE name LIKE '%' || :query || '%'")
    fun searchProblems(query: String): Flow<List<ProblemEntity>>

    @Query("""
        SELECT * FROM problems
        WHERE listId = :listId
        AND (:difficulty IS NULL OR difficulty = :difficulty)
        AND (:pattern IS NULL OR pattern = :pattern)
        ORDER BY name
    """)
    fun getFilteredProblems(
        listId: String,
        difficulty: String?,
        pattern: String?
    ): Flow<List<ProblemEntity>>

    @Query("SELECT DISTINCT pattern FROM problems WHERE pattern IS NOT NULL ORDER BY pattern")
    fun getAllPatterns(): Flow<List<String>>

    @Query("SELECT COUNT(*) FROM problems WHERE listId = :listId")
    fun getCountForList(listId: String): Flow<Int>

    @Query("SELECT COUNT(DISTINCT name) FROM problems")
    fun getUniqueProblemsCount(): Flow<Int>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(problems: List<ProblemEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(problem: ProblemEntity)

    @Query("DELETE FROM problems")
    suspend fun deleteAll()
}
