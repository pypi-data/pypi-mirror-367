"""
Pipeline analysis MCP tools for GitLab Pipeline Analyzer

Copyright (c) 2025 Siarhei Skuratovich
Licensed under the MIT License - see LICENSE file for details
"""

from datetime import datetime
from typing import Any

import httpx
from fastmcp import FastMCP

from gitlab_analyzer.parsers.log_parser import LogParser

from .utils import get_gitlab_analyzer


def register_analysis_tools(mcp: FastMCP) -> None:
    """Register pipeline analysis tools"""

    @mcp.tool
    async def analyze_failed_pipeline(
        project_id: str | int, pipeline_id: int
    ) -> dict[str, Any]:
        """
        Analyze a failed GitLab CI/CD pipeline and extract errors/warnings from all
        failed jobs. Uses optimized API calls to fetch only failed jobs.

        Args:
            project_id: The GitLab project ID or path
            pipeline_id: The ID of the GitLab pipeline to analyze

        Returns:
            Complete analysis including pipeline info, failed jobs, and extracted
            errors/warnings
        """
        try:
            analyzer = get_gitlab_analyzer()

            # Get pipeline status first
            pipeline_status = await analyzer.get_pipeline(project_id, pipeline_id)

            # Get only failed jobs (optimized)
            failed_jobs = await analyzer.get_failed_pipeline_jobs(
                project_id, pipeline_id
            )

            # Analyze each failed job
            job_analyses = []
            for job in failed_jobs:
                job_id = job.id
                job_name = job.name

                try:
                    # Get job trace
                    trace = await analyzer.get_job_trace(project_id, job_id)

                    # Extract errors/warnings from trace
                    entries = LogParser.extract_log_entries(trace)

                    errors = [
                        {
                            "level": entry.level,
                            "message": entry.message,
                            "line_number": entry.line_number,
                            "timestamp": entry.timestamp,
                            "context": entry.context,
                        }
                        for entry in entries
                        if entry.level == "error"
                    ]

                    warnings = [
                        {
                            "level": entry.level,
                            "message": entry.message,
                            "line_number": entry.line_number,
                            "timestamp": entry.timestamp,
                            "context": entry.context,
                        }
                        for entry in entries
                        if entry.level == "warning"
                    ]

                    job_analysis = {
                        "job_id": job_id,
                        "job_name": job_name,
                        "job_status": job.status,
                        "errors": errors,
                        "warnings": warnings,
                        "error_count": len(errors),
                        "warning_count": len(warnings),
                        "total_entries": len(entries),
                    }

                except Exception as job_error:
                    job_analysis = {
                        "job_id": job_id,
                        "job_name": job_name,
                        "job_status": job.status,
                        "error": f"Failed to analyze job: {str(job_error)}",
                        "errors": [],
                        "warnings": [],
                        "error_count": 0,
                        "warning_count": 0,
                        "total_entries": 0,
                    }

                job_analyses.append(job_analysis)

            # Aggregate results
            total_errors = sum(
                job["error_count"]
                for job in job_analyses
                if isinstance(job["error_count"], int)
            )
            total_warnings = sum(
                job["warning_count"]
                for job in job_analyses
                if isinstance(job["warning_count"], int)
            )

            return {
                "project_id": str(project_id),
                "pipeline_id": pipeline_id,
                "pipeline_status": pipeline_status,
                "failed_jobs_count": len(failed_jobs),
                "job_analyses": job_analyses,
                "summary": {
                    "total_errors": total_errors,
                    "total_warnings": total_warnings,
                    "jobs_with_errors": len(
                        [
                            job
                            for job in job_analyses
                            if isinstance(job.get("error_count"), int)
                            and isinstance(job["error_count"], int)
                            and job["error_count"] > 0
                        ]
                    ),
                    "jobs_with_warnings": len(
                        [
                            job
                            for job in job_analyses
                            if isinstance(job.get("warning_count"), int)
                            and isinstance(job["warning_count"], int)
                            and job["warning_count"] > 0
                        ]
                    ),
                },
                "analysis_timestamp": datetime.now().isoformat(),
            }

        except (httpx.HTTPError, httpx.RequestError, ValueError, KeyError) as e:
            return {
                "error": f"Failed to analyze pipeline: {str(e)}",
                "project_id": str(project_id),
                "pipeline_id": pipeline_id,
            }

    @mcp.tool
    async def analyze_single_job(project_id: str | int, job_id: int) -> dict[str, Any]:
        """
        Analyze a single GitLab CI/CD job and extract errors/warnings from its
        trace.

        Args:
            project_id: The GitLab project ID or path
            job_id: The ID of the specific job to analyze

        Returns:
            Analysis of the single job including extracted errors/warnings
        """
        try:
            analyzer = get_gitlab_analyzer()

            # Get job trace
            trace = await analyzer.get_job_trace(project_id, job_id)

            # Extract errors/warnings from trace
            entries = LogParser.extract_log_entries(trace)

            errors = [
                {
                    "level": entry.level,
                    "message": entry.message,
                    "line_number": entry.line_number,
                    "timestamp": entry.timestamp,
                    "context": entry.context,
                    "categorization": LogParser.categorize_error(
                        entry.message, entry.context or ""
                    ),
                }
                for entry in entries
                if entry.level == "error"
            ]

            warnings = [
                {
                    "level": entry.level,
                    "message": entry.message,
                    "line_number": entry.line_number,
                    "timestamp": entry.timestamp,
                    "context": entry.context,
                }
                for entry in entries
                if entry.level == "warning"
            ]

            return {
                "project_id": str(project_id),
                "job_id": job_id,
                "errors": errors,
                "warnings": warnings,
                "error_count": len(errors),
                "warning_count": len(warnings),
                "total_entries": len(entries),
                "trace_length": len(trace),
                "analysis_timestamp": datetime.now().isoformat(),
            }

        except (httpx.HTTPError, httpx.RequestError, ValueError, KeyError) as e:
            return {
                "error": f"Failed to analyze job: {str(e)}",
                "project_id": str(project_id),
                "job_id": job_id,
            }


async def analyze_failed_pipeline_optimized(
    project_id: str | int, pipeline_id: int
) -> dict[str, Any]:
    """
    Optimized version of pipeline analysis that processes multiple jobs concurrently
    and provides enhanced error categorization.
    """
    try:
        analyzer = get_gitlab_analyzer()

        # Get pipeline status and failed jobs concurrently
        import asyncio

        pipeline_status, failed_jobs = await asyncio.gather(
            analyzer.get_pipeline(project_id, pipeline_id),
            analyzer.get_failed_pipeline_jobs(project_id, pipeline_id),
        )

        # Process multiple jobs concurrently
        async def analyze_job_concurrent(job: Any) -> dict[str, Any]:  # JobInfo type
            job_id = job.id
            job_name = job.name

            try:
                trace = await analyzer.get_job_trace(project_id, job_id)
                entries = LogParser.extract_log_entries(trace)

                errors = [
                    {
                        "level": entry.level,
                        "message": entry.message,
                        "line_number": entry.line_number,
                        "timestamp": entry.timestamp,
                        "context": entry.context,
                        "categorization": LogParser.categorize_error(
                            entry.message, entry.context or ""
                        ),
                    }
                    for entry in entries
                    if entry.level == "error"
                ]

                warnings = [
                    {
                        "level": entry.level,
                        "message": entry.message,
                        "line_number": entry.line_number,
                        "timestamp": entry.timestamp,
                        "context": entry.context,
                    }
                    for entry in entries
                    if entry.level == "warning"
                ]

                return {
                    "job_id": job_id,
                    "job_name": job_name,
                    "job_status": job.status,
                    "errors": errors,
                    "warnings": warnings,
                    "error_count": len(errors),
                    "warning_count": len(warnings),
                    "total_entries": len(entries),
                    "trace_length": len(trace),
                }

            except Exception as job_error:
                return {
                    "job_id": job_id,
                    "job_name": job_name,
                    "job_status": job.status,
                    "error": f"Failed to analyze job: {str(job_error)}",
                    "errors": [],
                    "warnings": [],
                    "error_count": 0,
                    "warning_count": 0,
                    "total_entries": 0,
                    "trace_length": 0,
                }

        # Analyze jobs concurrently (limit concurrency to avoid overwhelming the API)
        semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent requests

        async def analyze_with_semaphore(job: Any) -> dict[str, Any]:  # JobInfo type
            async with semaphore:
                return await analyze_job_concurrent(job)

        job_analyses = await asyncio.gather(
            *[analyze_with_semaphore(job) for job in failed_jobs]
        )

        # Aggregate and categorize results
        total_errors = sum(job["error_count"] for job in job_analyses)
        total_warnings = sum(job["warning_count"] for job in job_analyses)

        # Categorize errors by type
        error_categories: dict[str, list[dict[str, Any]]] = {}
        for job in job_analyses:
            for error in job.get("errors", []):
                if "categorization" in error:
                    category = error["categorization"].get("category", "Unknown")
                    if category not in error_categories:
                        error_categories[category] = []
                    error_categories[category].append(
                        {
                            "job_id": job["job_id"],
                            "job_name": job["job_name"],
                            "message": error["message"],
                            "severity": error["categorization"].get(
                                "severity", "medium"
                            ),
                        }
                    )

        return {
            "project_id": str(project_id),
            "pipeline_id": pipeline_id,
            "pipeline_status": pipeline_status,
            "failed_jobs_count": len(failed_jobs),
            "job_analyses": job_analyses,
            "summary": {
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "jobs_with_errors": len(
                    [job for job in job_analyses if job["error_count"] > 0]
                ),
                "jobs_with_warnings": len(
                    [job for job in job_analyses if job["warning_count"] > 0]
                ),
                "error_categories": error_categories,
                "category_count": len(error_categories),
            },
            "analysis_timestamp": datetime.now().isoformat(),
            "processing_mode": "optimized_concurrent",
        }

    except (httpx.HTTPError, httpx.RequestError, ValueError, KeyError) as e:
        return {
            "error": f"Failed to analyze pipeline (optimized): {str(e)}",
            "project_id": str(project_id),
            "pipeline_id": pipeline_id,
        }
