package com.codingtracker.data.mapper

import com.codingtracker.data.local.db.entity.ProblemEntity
import com.codingtracker.data.local.db.entity.ProblemListEntity
import com.codingtracker.data.local.db.entity.UserProgressEntity
import com.codingtracker.domain.model.Difficulty
import com.codingtracker.domain.model.Problem
import com.codingtracker.domain.model.ProblemList
import com.codingtracker.domain.model.UserProgress
import java.time.Instant

fun ProblemEntity.toDomain(
    progress: UserProgressEntity?,
    duplicateListIds: List<String>
): Problem {
    return Problem(
        id = id,
        name = name,
        difficulty = Difficulty.fromString(difficulty),
        intermediateTime = intermediateTime,
        advancedTime = advancedTime,
        topTime = topTime,
        pattern = pattern,
        listId = listId,
        progress = progress?.toDomain() ?: UserProgress(),
        isDuplicate = duplicateListIds.size > 1,
        duplicateListIds = duplicateListIds
    )
}

fun UserProgressEntity.toDomain(): UserProgress {
    return UserProgress(
        solved = solved,
        timeToSolve = timeToSolve,
        comments = comments,
        solvedDate = solvedDate?.let { Instant.ofEpochMilli(it) }
    )
}

fun UserProgress.toEntity(problemId: String): UserProgressEntity {
    return UserProgressEntity(
        problemId = problemId,
        solved = solved,
        timeToSolve = timeToSolve,
        comments = comments,
        solvedDate = solvedDate?.toEpochMilli(),
        lastModified = System.currentTimeMillis()
    )
}

fun ProblemListEntity.toDomain(): ProblemList {
    return ProblemList(
        id = id,
        displayName = displayName,
        problemCount = problemCount,
        sortOrder = sortOrder
    )
}

fun ProblemList.toEntity(): ProblemListEntity {
    return ProblemListEntity(
        id = id,
        displayName = displayName,
        problemCount = problemCount,
        sortOrder = sortOrder
    )
}
