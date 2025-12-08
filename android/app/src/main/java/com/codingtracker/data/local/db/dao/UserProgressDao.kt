package com.codingtracker.data.local.db.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.codingtracker.data.local.db.entity.UserProgressEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface UserProgressDao {

    @Query("SELECT * FROM user_progress WHERE problemId = :problemId")
    suspend fun getProgressForProblem(problemId: String): UserProgressEntity?

    @Query("SELECT * FROM user_progress WHERE problemId = :problemId")
    fun getProgressForProblemFlow(problemId: String): Flow<UserProgressEntity?>

    @Query("SELECT * FROM user_progress WHERE solved = 1")
    fun getAllSolvedProgress(): Flow<List<UserProgressEntity>>

    @Query("""
        SELECT COUNT(DISTINCT p.name)
        FROM problems p
        INNER JOIN user_progress up ON p.id = up.problemId
        WHERE up.solved = 1
    """)
    fun getUniqueSolvedCount(): Flow<Int>

    @Query("""
        SELECT COUNT(*)
        FROM user_progress up
        INNER JOIN problems p ON up.problemId = p.id
        WHERE p.listId = :listId AND up.solved = 1
    """)
    fun getSolvedCountForList(listId: String): Flow<Int>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(progress: UserProgressEntity)

    @Update
    suspend fun update(progress: UserProgressEntity)

    @Query("""
        INSERT OR REPLACE INTO user_progress (problemId, solved, timeToSolve, comments, solvedDate, lastModified)
        VALUES (:problemId, :solved, :timeToSolve, :comments, :solvedDate, :lastModified)
    """)
    suspend fun upsert(
        problemId: String,
        solved: Boolean,
        timeToSolve: Int?,
        comments: String?,
        solvedDate: Long?,
        lastModified: Long = System.currentTimeMillis()
    )

    @Query("DELETE FROM user_progress WHERE problemId = :problemId")
    suspend fun delete(problemId: String)

    @Query("DELETE FROM user_progress")
    suspend fun deleteAll()
}
