"""
SystemToSis routes is used represent the API related to external system request to SIS
"""
from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required

from application.services.flexcubeService import flexcube_date_get, flexcube_account_balance_get
from application.services.settlementCbsService import settle_cbs_post
from application.services.settlementPmBookService import settle_pm_book_post
from application.services.settlementIrohaService import settle_iroha_post
from application.services.settlementStatusService import settlements_status_get
from application.services.bklvTransferService import bklv_transfer_post
from application.services.systemAuthService import login, logout

system_to_sis_route = Blueprint("system_to_sis", __name__, url_prefix="/api/v1/sis")


@system_to_sis_route.route('/auth', methods=["POST"])
def system_auth() -> Response:
    """
    Endpoint for external system login to SIS
    :return: JSON representation of system authentication and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/auth"""
        return login()


@system_to_sis_route.route('/logout', methods=["POST"])
@jwt_required()
def system_logout():
    """
    Endpoint for external system logout from SIS
    :return: JSON representation of system authentication and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/logout"""
        return logout()


@system_to_sis_route.route('/get-status', methods=["GET"])
@jwt_required()
def status_settlement() -> Response:
    """
    Endpoints for retrieving a list of settlement status based on list of settlement id.
    :return: JSON representation of status settlement and relevant metadata.
    """
    if request.method == "GET":
        """[POST] /api/v1/sis/get-status"""
        return settlements_status_get()


@system_to_sis_route.route('/create-settlement-iroha', methods=["POST"])
@jwt_required()
def iroha_settlement() -> Response:
    """
    Endpoints for creating new iroha settlement.
    :return: JSON representation of iroha settlement and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/create-settlement-iroha"""
        return settle_iroha_post()

@system_to_sis_route.route('/create-settlement-pm-book', methods=["POST"])
@jwt_required()
def pm_book_settlement() -> Response:
    """
    Endpoint for creating new PM Book settlement (single leg).
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/create-settlement-pm-book"""
        return settle_pm_book_post()
    
# disable this endpoint, this is multiple leg request
@system_to_sis_route.route('/create-settlement-cbs', methods=["POST"])
@jwt_required()
def cbs_settlement_disabled() -> Response: 
    """
    Endpoints for creating new cbs settlement.
    :return: JSON representation of cbs settlement and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/create-settlement-cbs"""
        return settle_cbs_post()

@system_to_sis_route.route('/get-date', methods=['GET'])
@jwt_required()
def flexcube_date() -> Response:
    """
    Endpoints for retrieving flexcube date.
    :return: JSON representation of a flexcube date and relevant metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/get-date"""
        return flexcube_date_get()


@system_to_sis_route.route('/get-account-balance', methods=['GET'])
@jwt_required()
def flexcube_account_balance() -> Response:
    """
    Endpoints for retrieving flexcube account balance.
    :return: JSON representation of a flexcube account balance and relevance metadata.
    """
    if request.method == "GET":
        """[GET] /api/v1/sis/get-account-balance"""
        return flexcube_account_balance_get()

@system_to_sis_route.route('/bklv/transfer', methods=["POST"])
@jwt_required()
def bklv_transfer() -> Response:
    """
    Endpoint for BKLV fund transfer (Bakong Large Value).
    :return: JSON representation of BKLV transfer result and relevant metadata.
    """
    if request.method == "POST":
        """[POST] /api/v1/sis/bklv/transfer"""
        return bklv_transfer_post()