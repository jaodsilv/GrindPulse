package com.codingtracker.di

import android.content.Context
import androidx.room.Room
import com.codingtracker.data.local.db.CodingTrackerDatabase
import com.codingtracker.data.local.db.dao.DuplicateMappingDao
import com.codingtracker.data.local.db.dao.ProblemDao
import com.codingtracker.data.local.db.dao.ProblemListDao
import com.codingtracker.data.local.db.dao.UserProgressDao
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(
        @ApplicationContext context: Context
    ): CodingTrackerDatabase {
        return Room.databaseBuilder(
            context,
            CodingTrackerDatabase::class.java,
            CodingTrackerDatabase.DATABASE_NAME
        )
            .fallbackToDestructiveMigration()
            .build()
    }

    @Provides
    fun provideProblemDao(database: CodingTrackerDatabase): ProblemDao {
        return database.problemDao()
    }

    @Provides
    fun provideProblemListDao(database: CodingTrackerDatabase): ProblemListDao {
        return database.problemListDao()
    }

    @Provides
    fun provideUserProgressDao(database: CodingTrackerDatabase): UserProgressDao {
        return database.userProgressDao()
    }

    @Provides
    fun provideDuplicateMappingDao(database: CodingTrackerDatabase): DuplicateMappingDao {
        return database.duplicateMappingDao()
    }
}
