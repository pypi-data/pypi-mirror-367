import datetime
import subprocess
import time
from logging import Logger
from subprocess import CompletedProcess
from typing import Tuple

from sqlalchemy import Engine
from sqlmodel import Session

from backend.config import Settings
from backend.database_utils import (
    all_active_testphase,
    all_inactive_testphases,
    osa_by_id,
)


def readable_date(ts_ns) -> str:
    tz_string = datetime.datetime.now().astimezone().tzinfo
    myb = datetime.datetime.fromtimestamp(ts_ns / 1e9)
    return myb.strftime(f"%Y-%m-%d %H:%M {tz_string}")


def run_sub_process(
    logger: Logger, command: str, partial_expected_output: str = ""
) -> Tuple[bool, str]:
    try:
        result: CompletedProcess = subprocess.run(
            command, capture_output=True, text=True, shell=True, check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error("Subprocess did not finish with a non-zero exit code")
        logger.error(e)
        raise
    except Exception as e:
        logger.error("Subprocess run did not execute as expected")
        logger.error(e)
        raise

    if result.returncode != 0:
        logger.error(f"Subprocess failed: {result.stderr}")
        return False, result.stderr

    if partial_expected_output not in result.stdout:
        if partial_expected_output not in result.stderr:
            logger.debug("expected output:")
            logger.debug(partial_expected_output)
            logger.critical("Subprocess returned unexpected value:")
            logger.debug(result.stdout)
            return False, result.stderr

    return True, result.stdout


def get_account_usage(engine: Engine, logger: Logger, settings: Settings) -> None:
    logger.info("getting account usage")
    with Session(engine) as session:
        results = all_active_testphase(session)
        for testphase in results:
            account = osa_by_id(session, testphase.osa_id)
            # todo
            # check that the remote server is accepting requests with this key,
            # you never know if the key has been deleted
            current_account_size = (
                f"ssh -i {settings.osa_admin_key_location} {account.account_name}@{account.server} du -schg | "
                "tail -n1 | "
                "awk '{print $1}'"
            )
            success, output = run_sub_process(logger, current_account_size)
            if not success:
                raise RuntimeError
            testphase.used_storage_gigabytes = output
            session.add(testphase)
            session.add(account)
            session.commit()


def account_cleanup(engine: Engine, logger: Logger, settings: Settings) -> None:
    """
    Mark online storage accounts as available if the testphase time has expired.
    """
    logger.debug("online storage account clean up")
    with Session(engine) as session:
        results = all_inactive_testphases(session)
        for result in results:
            account = osa_by_id(session, result.osa_id)
            # todo
            # what if a user removes the current admin key on the server from ".ssh/authorized_keys"?
            # fall back to password if needed
            # also clean up the file ".ssh/authorized_keys", restoring to default
            rm_all = (
                f"ssh -i {settings.osa_admin_key_location} {account.account_name}@{account.server} "
                "find . -mindepth 1 -path './.ssh' -prune -o -exec rm -rf {} +"
            )
            success, output = run_sub_process(logger, rm_all)
            if not success:
                raise RuntimeError
            account.available = True
            session.add(account)
            session.commit()
