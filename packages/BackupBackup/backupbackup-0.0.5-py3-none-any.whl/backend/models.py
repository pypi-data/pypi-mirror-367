from typing import List, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


class TestPhaseMemberLink(SQLModel, table=True):
    member_id: int = Field(foreign_key="member.id", primary_key=True)
    testphase_id: int = Field(foreign_key="testphase.id", primary_key=True)


class TestPhaseFeedbackLink(SQLModel, table=True):
    feedback_id: int = Field(foreign_key="feedback.id", primary_key=True)
    testphase_id: int = Field(foreign_key="testphase.id", primary_key=True)


class MemberBase(SQLModel):
    # this needs to be `username` for it to follow the OAuth convention
    username: EmailStr = Field(index=True, unique=True)
    password: str


class Member(MemberBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    join_timestamp: Optional[int] = Field(
        default=None
    )  # todo create this here and not in the api
    last_online_timestamp: Optional[int] = Field(default=None)
    disabled_at_timestamp: Optional[int] = Field(default=None)
    news_signup_at_timestamp: Optional[int] = Field(default=None)
    test_phases: List["TestPhase"] = Relationship(
        back_populates="members", link_model=TestPhaseMemberLink
    )
    feedbacks: List["Feedback"] = Relationship(
        back_populates="member",
    )


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    # this needs to be `username` for it to follow the OAuth convention
    username: Optional[str] = None


class ProductBase(SQLModel):
    name: str = Field(unique=True, index=True)
    one_time_payment: bool
    billing_interval_months: Optional[int] = Field(default=None, ge=1, le=12)
    price: int = Field(ge=0)
    disabled: bool


class Storage(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    storage_capacity_gigabytes: Optional[int] = Field(default=None)


class TestPhaseBase(SQLModel):
    public_product_name: str
    created_at_timestamp: int
    ends_at_timestamp: int = Field(index=True)


class TestPhase(TestPhaseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    used_storage_gigabytes: Optional[int]
    osa_id: Optional[int] = Field(
        default=None, foreign_key="onlinestorageaccount.id", index=True
    )
    members: List["Member"] = Relationship(
        back_populates="test_phases", link_model=TestPhaseMemberLink
    )
    feedbacks: List["Feedback"] = Relationship(
        back_populates="test_phases", link_model=TestPhaseFeedbackLink
    )


class FeedbackBase(SQLModel):
    created_at_timestamp: int
    questions_and_answers_json: str  # i know this is not the way
    textfield: str


class Feedback(FeedbackBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    member_id: Optional[int] = Field(default=None, foreign_key="member.id", index=True)
    member: Optional["Member"] = Relationship(back_populates="feedbacks")
    test_phases: List["TestPhase"] = Relationship(
        back_populates="feedbacks", link_model=TestPhaseFeedbackLink
    )


class OnlineStorageAccount(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_name: str
    server: str
    base_path: str
    available: bool
