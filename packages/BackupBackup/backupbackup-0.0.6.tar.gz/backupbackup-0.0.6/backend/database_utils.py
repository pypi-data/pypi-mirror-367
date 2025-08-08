import time
from typing import Union

from pydantic import EmailStr
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from backend.models import (
    Member,
    OnlineStorageAccount,
    Storage,
    TestPhase,
    TestPhaseMemberLink,
)


def current_time_in_ns():
    return time.time_ns()


def member_by_name(session: Session, username: Union[EmailStr, str]) -> Member | None:
    statement = select(Member).where(Member.username == username)
    try:
        return session.exec(statement).one()
    except NoResultFound:
        return None


def all_active_testphase(session: Session) -> TestPhase | None:
    now = current_time_in_ns()
    statement = select(TestPhase).where(TestPhase.ends_at_timestamp > now)
    try:
        return session.exec(statement)
    except NoResultFound:
        return None


def all_inactive_testphases(session: Session) -> TestPhase | None:
    now = current_time_in_ns()
    statement = select(TestPhase).where(TestPhase.ends_at_timestamp < now)
    try:
        return session.exec(statement)
    except NoResultFound:
        return None


def active_testphase_for_member(session: Session, member_id: int) -> TestPhase | None:
    now = current_time_in_ns()
    statement = (
        select(TestPhase)
        .join(TestPhaseMemberLink, TestPhase.id == TestPhaseMemberLink.testphase_id)
        .where(TestPhaseMemberLink.member_id == member_id)
        .where(TestPhase.ends_at_timestamp > now)
    )
    try:
        return session.exec(statement).first()
    except NoResultFound:
        return None


def testphase_of_member(
    session: Session, member_id: int, testphase_id: int
) -> TestPhase | None:
    get_member_testphase = (
        select(TestPhase)
        .join(TestPhaseMemberLink, TestPhase.id == TestPhaseMemberLink.testphase_id)
        .where(
            TestPhaseMemberLink.member_id == member_id,
            TestPhase.id == testphase_id,
        )
    )
    try:
        return session.exec(get_member_testphase).one()
    except NoResultFound:
        return None


def osa_by_testphase(
    session: Session, testphase_id: int
) -> OnlineStorageAccount | None:
    statement = (
        select(OnlineStorageAccount)
        .join(TestPhase, OnlineStorageAccount.id == TestPhase.osa_id)
        .where(TestPhase.id == testphase_id)
    )
    try:
        return session.exec(statement).one()
    except NoResultFound:
        return None


def all_testphase_of_member(session: Session, member_id: int):
    get_member_testphase = (
        select(TestPhase)
        .join(TestPhaseMemberLink, TestPhase.id == TestPhaseMemberLink.testphase_id)
        .where(
            TestPhaseMemberLink.member_id == member_id,
        )
    )
    try:
        return session.exec(get_member_testphase).all()
    except NoResultFound:
        return None


def osa_by_id(session: Session, current_id: int) -> OnlineStorageAccount | None:
    statement = select(OnlineStorageAccount).where(
        OnlineStorageAccount.id == current_id
    )
    try:
        return session.exec(statement).one()
    except NoResultFound:
        return None


def first_available_osa(session: Session):
    statement = select(OnlineStorageAccount).where(OnlineStorageAccount.available == 1)
    try:
        return session.exec(statement).first()
    except NoResultFound:
        return None


def product_by_id(session: Session, product_id: int) -> Storage | None:
    statement = select(Storage).where(Storage.id == product_id)
    try:
        return session.exec(statement).one()
    except NoResultFound:
        return None
