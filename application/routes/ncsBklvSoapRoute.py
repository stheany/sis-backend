from flask import Blueprint, Response, request
from application.services.ncsBklvSoapService import handle_ncs_bklv_soap_request

ncs_bklv_soap_route = Blueprint("ncs_bklv_soap", __name__, url_prefix="/ws")


def _handle(expected_operation: str) -> Response:
    raw_xml = request.get_data(as_text=True)
    response_xml = handle_ncs_bklv_soap_request(raw_xml, expected_operation=expected_operation)
    return Response(response_xml, mimetype="application/soap+xml")


@ncs_bklv_soap_route.route('/getFCDate', methods=["POST"])
def ncs_bklv_get_fc_date() -> Response:
    """[POST] /ws/getFCDate"""
    return _handle('getFCDate')

@ncs_bklv_soap_route.route('/getCBSAccountBalanceNCS', methods=["POST"])
def ncs_bklv_get_cbs_account_balance() -> Response:
    """[POST] /ws/getCBSAccountBalanceNCS"""
    return _handle('getCBSAccountBalanceNCS')

@ncs_bklv_soap_route.route('/upload_File_GI_FLATFILE', methods=["POST"])
def ncs_bklv_upload_file_gi_flatfile() -> Response:
    """[POST] /ws/upload_File_GI_FLATFILE"""
    return _handle('upload_File_GI_FLATFILE')

@ncs_bklv_soap_route.route('/getFile_Status_Detail', methods=["POST"])
def ncs_bklv_get_file_status_detail() -> Response:
    """[POST] /ws/getFile_Status_Detail"""
    return _handle('getFile_Status_Detail')
