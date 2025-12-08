package com.codingtracker.di

import com.codingtracker.data.repository.ProblemRepository
import com.codingtracker.data.repository.ProblemRepositoryImpl
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindProblemRepository(
        impl: ProblemRepositoryImpl
    ): ProblemRepository
}
