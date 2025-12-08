package com.codingtracker.data.local.db.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.codingtracker.data.local.db.entity.DuplicateMappingEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface DuplicateMappingDao {

    @Query("SELECT * FROM duplicate_mappings WHERE problemName = :problemName")
    suspend fun getMappingForProblem(problemName: String): DuplicateMappingEntity?

    @Query("SELECT * FROM duplicate_mappings WHERE problemName = :problemName")
    fun getMappingForProblemFlow(problemName: String): Flow<DuplicateMappingEntity?>

    @Query("SELECT * FROM duplicate_mappings")
    fun getAllMappings(): Flow<List<DuplicateMappingEntity>>

    @Query("SELECT COUNT(*) FROM duplicate_mappings")
    fun getDuplicateCount(): Flow<Int>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(mapping: DuplicateMappingEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(mappings: List<DuplicateMappingEntity>)

    @Query("DELETE FROM duplicate_mappings")
    suspend fun deleteAll()
}
