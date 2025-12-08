package com.codingtracker.di

import com.codingtracker.data.export.ImportExportService
import com.codingtracker.data.export.ImportExportServiceImpl
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class ImportExportModule {

    @Binds
    @Singleton
    abstract fun bindImportExportService(
        impl: ImportExportServiceImpl
    ): ImportExportService
}
