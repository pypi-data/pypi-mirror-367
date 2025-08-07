#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import os
import time
from unittest.mock import Mock

import pytest
from airflow.utils.context import Context
from snowflake.operators.snowpark_submit.snowpark_submit_operator import (
    SnowparkSubmitOperator,
)
from snowflake.operators.snowpark_submit.snowpark_submit_status_operator import (
    SnowparkSubmitStatusOperator,
)
from snowflake.snowpark_submit.cluster_mode.job_runner import logger

from snowflake.connector.config_manager import CONFIG_MANAGER

from .conftest import DEFAULT_TEST_CONNECTION_NAME


class TestSnowparkOperatorsIntegration:
    @classmethod
    def setup_class(cls):
        cls.tests_path = os.path.dirname(os.path.abspath(__file__))
        cls.project_root = os.path.dirname(cls.tests_path)

        snowpark_config = CONFIG_MANAGER["connections"][DEFAULT_TEST_CONNECTION_NAME]
        cls.connection_config = {
            "account": snowpark_config.get("account"),
            "host": snowpark_config.get("host"),
            "user": snowpark_config.get("user"),
            "password": snowpark_config.get("password"),
            "role": snowpark_config.get("role"),
            "warehouse": snowpark_config.get("warehouse"),
            "database": snowpark_config.get("database"),
            "schema": snowpark_config.get("schema"),
            "compute_pool": snowpark_config.get("compute_pool"),
        }

        cls.mock_ti = Mock()
        cls.mock_ti.xcom_push = Mock()
        cls.mock_context = Context()
        cls.mock_context["ti"] = cls.mock_ti

    def test_submit_and_check_status(self):
        # Submit a job and check its status
        submit_operator = SnowparkSubmitOperator(
            task_id="test_submit_job",
            file=os.path.join(self.tests_path, "resources/pyspark-test.py"),
            connections_config=self.connection_config,
            wait_for_completion=False,
        )

        result = submit_operator.execute(self.mock_context)

        assert result is not None
        assert result["return_code"] == 0
        assert result["service_name"] is not None
        assert result["service_name"].startswith("SNOWPARK_SUBMIT_AIRFLOW_OPERATOR_")

        stdout_content = result["stdout"]
        service_name = result["service_name"]

        job_msg = "has been submitted and running asynchorously in SPCS"
        assert (
            job_msg in stdout_content
        ), f"Job submission to SPCS not confirmed for service {service_name}"

        status_operator = SnowparkSubmitStatusOperator(
            task_id="test_check_status",
            snowflake_workload_name=service_name,
            connections_config=self.connection_config,
            display_logs=False,
        )

        status_result = status_operator.execute(self.mock_context)

        assert status_result is not None
        assert (status_result.workload_name or service_name) == service_name
        assert status_result.service_status in ["PENDING", "RUNNING", "DONE"]
        assert status_result.workload_status in ["PENDING", "RUNNING", "DONE"]
        assert isinstance(status_result.created_on, str) and status_result.created_on

    @pytest.mark.skip(
        reason="Requires SPCS testing infra. Temporarily skipped for to avoid long merge gate time."
    )
    def test_submit_wait_and_check_status(self):
        # Submit a job with wait_for_completion=True and check status with display_logs=True
        submit_operator = SnowparkSubmitOperator(
            task_id="test_submit_wait",
            file=os.path.join(self.tests_path, "resources/pyspark-test.py"),
            connections_config=self.connection_config,
            wait_for_completion=True,
        )

        submit_result = submit_operator.execute(self.mock_context)

        assert submit_result is not None
        assert submit_result["return_code"] == 0
        assert "Service Status: DONE" in submit_result["stdout"]

        service_name = submit_result["service_name"]
        status_operator = SnowparkSubmitStatusOperator(
            task_id="test_check_logs",
            snowflake_workload_name=service_name,
            connections_config=self.connection_config,
            display_logs=True,
            log_fetch_delay=5,
        )

        status_result = status_operator.execute(self.mock_context)

        assert status_result is not None
        assert (status_result.workload_name or service_name) == service_name
        assert status_result.service_status == "DONE"
        assert status_result.workload_status == "DONE"
        assert isinstance(status_result.created_on, str) and status_result.created_on
        assert (
            isinstance(status_result.terminated_at, str) and status_result.terminated_at
        )

    @pytest.mark.skip(
        reason="Requires SPCS testing infra. Temporarily skipped for to avoid long merge gate time. Can be enabled in the future with more testing resources."
    )
    def test_submit_failing_job_and_check_status(self):
        # Submit a failing job and verify FAILED status
        submit_operator = SnowparkSubmitOperator(
            task_id="test_submit_failing",
            file=os.path.join(self.tests_path, "resources/pyspark-test-failing.py"),
            connections_config=self.connection_config,
            wait_for_completion=True,
        )

        submit_result = submit_operator.execute(self.mock_context)

        assert submit_result is not None
        assert submit_result["return_code"] == 0
        assert "Service Status: FAILED" in submit_result["stdout"]

        service_name = submit_result["service_name"]
        logger.debug(f"Failing job completed with service name: {service_name}")

        status_operator = SnowparkSubmitStatusOperator(
            task_id="test_check_failed_status",
            snowflake_workload_name=service_name,
            connections_config=self.connection_config,
            display_logs=True,
            log_fetch_delay=5,
        )

        status_result = status_operator.execute(self.mock_context)

        assert status_result is not None
        assert (status_result.workload_name or service_name) == service_name
        assert status_result.service_status == "FAILED"
        assert status_result.workload_status == "FAILED"
        assert isinstance(status_result.created_on, str) and status_result.created_on
        assert (
            isinstance(status_result.terminated_at, str) and status_result.terminated_at
        )

        assert (
            status_result.job_exit_code != 0
        ), f"Expected non-zero exit code but got: {status_result.job_exit_code}"

    @pytest.mark.skip(
        reason="Log retrieval can be flaky. This test should only be run locally."
    )
    def test_submit_wait_and_check_logs(self):
        # Submit a job with wait_for_completion=True, check status, and check logs
        submit_operator = SnowparkSubmitOperator(
            task_id="test_submit_wait",
            file=os.path.join(self.tests_path, "resources/pyspark-test.py"),
            connections_config=self.connection_config,
            wait_for_completion=True,
        )

        submit_result = submit_operator.execute(self.mock_context)

        assert submit_result is not None
        assert submit_result["return_code"] == 0
        assert "Service Status: DONE" in submit_result["stdout"]

        service_name = submit_result["service_name"]
        status_operator = SnowparkSubmitStatusOperator(
            task_id="test_check_logs",
            snowflake_workload_name=service_name,
            connections_config=self.connection_config,
            display_logs=True,
            log_fetch_delay=15,
        )

        status_result = status_operator.execute(self.mock_context)

        assert status_result is not None
        assert (status_result.workload_name or service_name) == service_name
        assert status_result.service_status == "DONE"
        assert status_result.workload_status == "DONE"
        assert isinstance(status_result.created_on, str) and status_result.created_on
        assert (
            isinstance(status_result.terminated_at, str) and status_result.terminated_at
        )

        max_retries = 8
        base_delay = 2
        # wait for logs to be available
        for attempt in range(max_retries):
            if attempt > 0:  # dont need to re-fetch immediately on first attempt
                status_result = status_operator.execute(self.mock_context)

            logger.debug(
                f"Attempt {attempt + 1}: logs count = {len(status_result.logs)}"
            )

            if any(
                "-------PYSPARK TEST JOB SUCCEEDED--------" in log
                for log in status_result.logs
            ):
                break

            if attempt < max_retries - 1:
                # Exponential backoff: 2, 4, 8, 16, 32, ... seconds (capped at 30s)
                delay = min(base_delay * (2**attempt), 30)
                logger.debug(
                    f"Success message not found, waiting {delay} seconds before retry..."
                )
                time.sleep(delay)
            else:
                logger.debug("Last few log entries:")
                for i, log in enumerate(status_result.logs[-3:]):
                    logger.debug(f"  {i}: {log}")
                raise AssertionError(
                    f"Expected log entry not found in logs after {max_retries} attempts"
                )

    @pytest.mark.skip(
        reason="Log retrieval can be flaky. This test should only be run locally."
    )
    def test_submit_failing_job_and_check_logs(self):
        # Submit a failing job, verify FAILED status, check logs for relevant error
        submit_operator = SnowparkSubmitOperator(
            task_id="test_submit_failing",
            file=os.path.join(self.tests_path, "resources/pyspark-test-failing.py"),
            connections_config=self.connection_config,
            wait_for_completion=True,
        )

        submit_result = submit_operator.execute(self.mock_context)

        assert submit_result is not None
        assert submit_result["return_code"] == 0
        assert "Service Status: FAILED" in submit_result["stdout"]

        service_name = submit_result["service_name"]
        logger.debug(f"Failing job completed with service name: {service_name}")

        status_operator = SnowparkSubmitStatusOperator(
            task_id="test_check_failed_status",
            snowflake_workload_name=service_name,
            connections_config=self.connection_config,
            display_logs=True,
            log_fetch_delay=15,
        )

        status_result = status_operator.execute(self.mock_context)

        assert status_result is not None
        assert (status_result.workload_name or service_name) == service_name
        assert status_result.service_status == "FAILED"
        assert status_result.workload_status == "FAILED"
        assert isinstance(status_result.created_on, str) and status_result.created_on
        assert (
            isinstance(status_result.terminated_at, str) and status_result.terminated_at
        )

        assert (
            status_result.job_exit_code != 0
        ), f"Expected non-zero exit code but got: {status_result.job_exit_code}"

        max_retries = 8
        base_delay = 2
        # wait for logs to be available
        for attempt in range(max_retries):
            if attempt > 0:
                status_result = status_operator.execute(self.mock_context)

            logger.debug(
                f"Attempt {attempt + 1}: logs count = {len(status_result.logs)}"
            )

            if any("thisShouldFail" in log for log in status_result.logs):
                logger.debug("Error indicators found in logs (as expected)")
                break

            if attempt < max_retries - 1:
                # Exponential backoff: 2, 4, 8, 16, 32, ... seconds (capped at 30s)
                delay = min(base_delay * (2**attempt), 30)
                logger.debug(
                    f"Error indicators not found, waiting {delay} seconds before retry..."
                )
                time.sleep(delay)
            else:
                logger.debug("Last few log entries:")
                for i, log in enumerate(status_result.logs[-3:]):
                    logger.debug(f"  {i}: {log}")
                raise AssertionError(
                    f"Expected error indicators not found in logs after {max_retries} attempts"
                )

    @pytest.mark.skip(
        reason="Requires SPCS testing infra. Temporarily skipped for to avoid long merge gate time. Can be enabled in the future with more testing resources."
    )
    def test_submit_async_then_wait_for_completion(self):
        # submit async, then use status operator with wait_for_completion=True
        submit_operator = SnowparkSubmitOperator(
            task_id="test_submit_async",
            file=os.path.join(self.tests_path, "resources/pyspark-test.py"),
            connections_config=self.connection_config,
            wait_for_completion=False,
        )

        submit_result = submit_operator.execute(self.mock_context)

        assert submit_result is not None
        assert submit_result["return_code"] == 0
        assert submit_result["service_name"] is not None
        assert submit_result["service_name"].startswith(
            "SNOWPARK_SUBMIT_AIRFLOW_OPERATOR_"
        )

        service_name = submit_result["service_name"]
        logger.debug(f"Submitted async job with service name: {service_name}")

        status_operator = SnowparkSubmitStatusOperator(
            task_id="test_wait_for_existing",
            snowflake_workload_name=service_name,
            connections_config=self.connection_config,
            wait_for_completion=True,
            display_logs=False,
        )

        status_result = status_operator.execute(self.mock_context)

        assert status_result is not None
        assert (status_result.workload_name or service_name) == service_name
        assert status_result.service_status == "DONE"
        assert status_result.workload_status == "DONE"
        assert isinstance(status_result.created_on, str) and status_result.created_on
        assert (
            isinstance(status_result.terminated_at, str) and status_result.terminated_at
        ), "Expected terminated_at to be set for completed workload"
