from sqlalchemy import Engine
from sqlmodel import Session, or_, select

from backend.database_utils import member_by_name
from backend.models import Member, OnlineStorageAccount, Storage


# only used during development
def create_default_member(engine: Engine) -> None:
    member = Member(
        username="admin@backupbackup.ch",
        password="$2b$12$6EyrL1WzZm/ORZelspiCaO5psU6ORr3vxzGEg5Gt1EMhr/JUF9SGG",  # 'password'
    )
    with Session(engine) as session:
        db_member = member_by_name(session, member.username)
        # only add if not already added
        if not db_member:
            session.add(member)
            session.commit()
            session.refresh(member)


def create_default_osa(engine: Engine, settings) -> None:
    accounts = settings.osas
    with Session(engine) as session:
        get_account_by_name = select(OnlineStorageAccount).where(
            or_(
                OnlineStorageAccount.account_name == accounts[0],
                OnlineStorageAccount.account_name == accounts[1],
            )
        )
        db_accounts = session.exec(get_account_by_name).all()
        if len(db_accounts) == len(accounts):
            return

        for account_name in accounts:
            new_account = OnlineStorageAccount(
                account_name=account_name,
                server=f"{account_name}.{settings.osa_provider}",
                base_path=f"{settings.osa_base_path}{account_name}",
                available=True,
            )
            session.add(new_account)
            session.commit()
            session.refresh(new_account)


def create_default_product(engine: Engine) -> None:
    product = Storage(
        name="1TB Online Speicher (Schweiz)",
        one_time_payment=True,
        billing_interval_months=0,
        price=0,
        disabled=False,
        storage_capacity_gigabytes=1_000,  # 1TB
    )
    with Session(engine) as session:
        statement = select(Storage).where(Storage.name == product.name)
        db_product = session.exec(statement).first()
        # only add if not already added
        if not db_product:
            session.add(product)
            session.commit()
            session.refresh(product)
