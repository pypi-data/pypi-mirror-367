import json
import random
import time
from datetime import timedelta
from logging import Logger
from pathlib import Path
from typing import Annotated, Union
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    StreamingResponse,
)
from fastapi.templating import Jinja2Templates
from redis import Redis
from sqlmodel import Session

from backend.auth import (
    OAuth2PasswordCaptchaRequestForm,
    authenticate_member,
    create_access_token,
    create_captcha,
    generate_ssh_keys,
    get_current_active_member,
    password_hash,
    valid_captcha,
)
from backend.config import Settings
from backend.database import get_db_session, get_redis_client
from backend.database_utils import (
    active_testphase_for_member,
    all_testphase_of_member,
    current_time_in_ns,
    first_available_osa,
    member_by_name,
    osa_by_testphase,
    product_by_id,
    testphase_of_member,
)
from backend.dependencies import get_logger, get_settings
from backend.feedback_questions import feedback_questions
from backend.models import (
    Feedback,
    Member,
    OnlineStorageAccount,
    TestPhase,
)
from backend.utils import readable_date, run_sub_process

router = APIRouter()
base_dir = Path(__file__).resolve().parent
templates_dir = base_dir / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def access_flow(
    settings: Settings,
    request: Request,
    redis_client: Redis,
    template: str,
    popup_msg: str = "",
) -> templates.TemplateResponse:
    token, base64_captcha = create_captcha(settings, redis_client)
    return templates.TemplateResponse(
        request=request,
        name=template,
        context={
            "captcha_token": token,
            "base64_captcha": base64_captcha,
            "popup_msg": popup_msg,
        },
    )


@router.get(path="/signup", response_model=None)
async def signup_form(
    settings: Annotated[Settings, Depends(get_settings)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
    request: Request,
) -> templates.TemplateResponse:
    return access_flow(
        settings=settings,
        request=request,
        redis_client=redis_client,
        template="_signup.html",
    )


@router.post(path="/signup")
async def signup(
    settings: Annotated[Settings, Depends(get_settings)],
    logger: Annotated[Logger, Depends(get_logger)],
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    form_data: Annotated[OAuth2PasswordCaptchaRequestForm, Depends()],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
):
    if not valid_captcha(logger, redis_client, form_data):
        return access_flow(
            settings,
            request,
            redis_client,
            template="_login.html",
            popup_msg="Captcha nicht korrekt!",
        )

    db_member = member_by_name(session, form_data.username)
    if db_member:
        return access_flow(
            settings=settings,
            request=request,
            redis_client=redis_client,
            template="_signup.html",
            popup_msg="Member mit dieser Email-Adresse existiert bereits!",  # risky
        )

    now = current_time_in_ns()
    member = Member(
        username=form_data.username,
        password=password_hash(form_data.password),
        join_timestamp=now,
        news_signup_at_timestamp=now if form_data.wants_news else None,
    )
    session.add(member)
    session.commit()
    return access_flow(
        settings=settings,
        request=request,
        redis_client=redis_client,
        template="_signup.html",
        popup_msg="Membership erfolgreich erstellt! Sie können sich nun anmelden.",
    )


@router.get(path="/login", response_model=None)
async def login_form(
    settings: Annotated[Settings, Depends(get_settings)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
    request: Request,
) -> templates.TemplateResponse:
    return access_flow(
        settings=settings,
        request=request,
        redis_client=redis_client,
        template="_login.html",
    )


@router.post(
    path="/login",
    response_model=None,
    response_class=Union[RedirectResponse, templates.TemplateResponse],
)
async def login(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    form_data: Annotated[OAuth2PasswordCaptchaRequestForm, Depends()],
    logger: Annotated[Logger, Depends(get_logger)],
    session: Annotated[Session, Depends(get_db_session)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
) -> Union[RedirectResponse, templates.TemplateResponse]:
    if not valid_captcha(logger, redis_client, form_data):
        return access_flow(
            settings=settings,
            request=request,
            redis_client=redis_client,
            template="_login.html",
            popup_msg="Captcha nicht korrekt!",
        )

    member = authenticate_member(session, form_data.username, form_data.password)
    if not member:
        return access_flow(
            settings=settings,
            request=request,
            redis_client=redis_client,
            template="_login.html",
            popup_msg="E-Mail Adresse oder Passwort falsch!",
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": member.username},
        settings=settings,
        expires_delta=access_token_expires,
    )
    response = RedirectResponse(
        url="/membership", status_code=status.HTTP_303_SEE_OTHER
    )
    token = jsonable_encoder(access_token)
    response.set_cookie(
        key="Authorization",
        value=f"Bearer {token}",
        domain=f"{settings.web_domain_tld}",
        httponly=True,  # not available to JavaScript
        max_age=1800,  # 30min
        expires=1800,  # 30min
    )
    return response


@router.get(path="/membership", response_class=HTMLResponse)
async def membership(
    request: Request,
    current_member: Annotated[Member, Depends(get_current_active_member)],
    session: Annotated[Session, Depends(get_db_session)],
    popup_msg: str = None,
):
    salutation = "Hallo, "
    if random.random() < 0.03:
        salutation = "Grüezi, "

    now = current_time_in_ns()
    active_product = None
    expired_products = []
    member_testphases = all_testphase_of_member(session, current_member.id)
    for testphase in member_testphases:
        # expired ones
        if testphase.ends_at_timestamp < now:
            expired_products.append(
                {
                    "testphase_id": testphase.id,
                    "public_product_name": testphase.public_product_name,
                    "ends_at_timestamp": readable_date(testphase.ends_at_timestamp),
                }
            )

        # active one
        if testphase.ends_at_timestamp > now:
            account = osa_by_testphase(session, testphase.id)
            active_product = {
                "testphase_id": testphase.id,
                "public_product_name": testphase.public_product_name,
                "created_at_timestamp": readable_date(testphase.created_at_timestamp),
                "ends_at_timestamp": readable_date(testphase.ends_at_timestamp),
                "account_name": account.account_name,
            }
            if testphase.used_storage_gigabytes:
                active_product["used_storage_gigabytes"] = (
                    testphase.used_storage_gigabytes
                )

    return templates.TemplateResponse(
        request=request,
        name="_membership.html",
        context={
            "member": current_member,
            "salutation": salutation,
            "active_product": active_product,
            "expired_products": expired_products,
            "popup_msg": popup_msg,
        },
    )


@router.get(
    path="/testphase/{product_id}",
    response_model=None,
    response_class=Union[RedirectResponse, templates.TemplateResponse],
)
async def start_testphase(
    product_id: int,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    current_member: Annotated[Member, Depends(get_current_active_member)],
) -> Union[RedirectResponse, templates.TemplateResponse]:
    # check that the product exists
    db_storage = product_by_id(session, product_id)
    if not db_storage:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
        )

    # check if the member already has a running testphase
    member_testphase = active_testphase_for_member(session, current_member.id)
    if member_testphase:
        redirect_url = request.url_for("membership")
        params = {
            "popup_msg": "Sie haben bereits eine aktive Testphase für dieses Produkt!",
        }
        full_url = f"{redirect_url}?{urlencode(params)}"
        response = RedirectResponse(url=full_url, status_code=status.HTTP_303_SEE_OTHER)
        return response

    # check that an online storage account is available
    account = first_available_osa(session)
    if not account:
        redirect_url = request.url_for("membership")
        params = {
            "popup_msg": "Leider sind momentan keine Resourcen verfügbar, versuchen Sie es später erneut!",
        }
        full_url = f"{redirect_url}?{urlencode(params)}"
        response = RedirectResponse(url=full_url, status_code=status.HTTP_303_SEE_OTHER)
        return response

    # Mark the account as in use
    account.available = False
    session.add(account)
    session.commit()
    session.refresh(account)

    current_time = time.time_ns()
    testphase = TestPhase(
        public_product_name=f"Testphase für '{db_storage.name}'",
        storage_id=product_id,
        created_at_timestamp=current_time,
        ends_at_timestamp=current_time + (10 * 60 * 1_000_000_000),  # in 10 min
        osa_id=account.id,
    )
    testphase.members.append(current_member)

    session.add(testphase)
    session.commit()

    redirect_url = request.url_for("membership")
    params = {
        "popup_msg": "Die Testphase wurde erfolgreich gestartet! "
        "Laden Sie Ihre persönlichen SSH Schlüssel (Private Key) herunter!",
    }
    full_url = f"{redirect_url}?{urlencode(params)}"
    response = RedirectResponse(url=full_url, status_code=status.HTTP_303_SEE_OTHER)
    return response


@router.get(path="/feedback", response_model=None)
async def get_feedback(
    request: Request,
    testphase_id,
) -> templates.TemplateResponse:
    return templates.TemplateResponse(
        request=request,
        name="_feedback.html",
        context={"questions": feedback_questions, "testphase_id": testphase_id},
    )


@router.post(path="/feedback")
async def give_feedback(
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    current_member: Annotated[Member, Depends(get_current_active_member)],
    feedback_text: Annotated[str, Form()] = "",
    testphase_id: Annotated[int, Form()] = "",
) -> RedirectResponse:
    form_data = await request.form()

    # check that the user is giving feedback to a testphase of theirs
    member_testphase = testphase_of_member(session, current_member.id, testphase_id)
    if not member_testphase:
        redirect_url = request.url_for("membership")
        params = {
            "popup_msg": "Bürstli!",
        }
        full_url = f"{redirect_url}?{urlencode(params)}"
        response = RedirectResponse(url=full_url, status_code=status.HTTP_303_SEE_OTHER)
        return response

    questions = {}
    known_fields = {"feedback_text", "testphase_id"}

    # todo this is asking so hard rn to be refactored and you're just ignoring it smh
    for key, value in form_data.items():
        if key not in known_fields:
            questions[key] = value

    questions_and_answers = {}
    for key, value in questions.items():
        questions_and_answers[key] = {
            "question": feedback_questions[int(key)]["question"],
            "answer": feedback_questions[int(key)]["answer_options"][value[-1:]],
        }

    current_time = time.time_ns()

    feedback = Feedback(
        member_id=current_member.id,
        textfield=feedback_text,
        created_at_timestamp=current_time,
        questions_and_answers_json=json.dumps(questions_and_answers),
    )
    feedback.test_phases.append(member_testphase)

    session.add(feedback)
    session.commit()

    redirect_url = request.url_for("membership")
    params = {
        "popup_msg": "Danke für Ihr Feedback!",
    }
    full_url = f"{redirect_url}?{urlencode(params)}"
    response = RedirectResponse(url=full_url, status_code=status.HTTP_303_SEE_OTHER)
    return response


def gen_and_upload_ssh_keys(
    logger: Logger, settings: Settings, account: OnlineStorageAccount
) -> bytes:
    private, public = generate_ssh_keys()

    # todo
    # check that the remote server is accepting requests with this key,
    # you never know if the key has been deleted
    append_ssh_public_key = (
        f"echo '{public.decode('utf-8')}' | "
        f"ssh -i {settings.osa_admin_key_location} {account.account_name}@{account.server} '"
        f"dd of=.ssh/authorized_keys oflag=append conv=notrunc'"
    )
    expected_output = "0+1 records in\n0+1 records out"
    success, output = run_sub_process(
        logger=logger,
        command=append_ssh_public_key,
        partial_expected_output=expected_output,
    )
    if not success:
        logger.error(output)
        raise RuntimeError
    return private


@router.get(path="/getkey", response_class=StreamingResponse)
async def download_ssh_key(
    logger: Annotated[Logger, Depends(get_logger)],
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[Session, Depends(get_db_session)],
    request: Request,
    current_member: Annotated[Member, Depends(get_current_active_member)],
):
    account = first_available_osa(session)
    if not account:
        redirect_url = request.url_for("membership")
        params = {
            "popup_msg": "Leider sind momentan keine Resourcen verfügbar, versuchen Sie es später erneut!",
        }
        full_url = f"{redirect_url}?{urlencode(params)}"
        response = RedirectResponse(url=full_url, status_code=status.HTTP_303_SEE_OTHER)
        return response

    private_key: bytes = gen_and_upload_ssh_keys(logger=logger, settings=settings, account=account)

    async def send_private_key():
        yield private_key

    headers = {
        "Content-Disposition": f"attachment; filename=backupbackup_{account.account_name}_private_key"
    }
    return StreamingResponse(
        send_private_key(), headers=headers, media_type="text/plain"
    )
