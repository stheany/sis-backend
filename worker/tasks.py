import os
import re
import settings
from datetime import datetime
from xml.sax.saxutils import escape as _xml_escape

import cx_Oracle
import requests
from bs4 import BeautifulSoup as BS
from celery.utils.log import get_task_logger
 
from worker import celery_app
 
from worker.iroha_service import transfer_to_iroha, get_iroha_status
from worker.system_service import update_system_status

logger = get_task_logger(__name__)

 
SETTLE_STATUS_PENDING = (1, 'PENDING')
SETTLE_STATUS_SUCCESS = (2, 'SUCCESS')
SETTLE_STATUS_FAIL = (3, 'FAIL')
SETTLE_STATUS_ERROR = (4, 'ERROR')
SETTLE_STATUS_COMMITTED = (5, 'COMMITTED')
SETTLE_STATUS_REJECTED = (6, 'REJECTED')
SETTLE_STATUS_STATELESS_VALIDATION_FAILED = (7, 'STATELESS_VALIDATION_FAILED')
DSN = f"{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_SERVICE_NAME')}"
FLEXCUBE_VERIFY_SSL = settings.FLEXCUBE_VERIFY_SSL


@celery_app.task()
def send_to_flexcube(system_url, settle_cbs_id, flexcube, settlement_cbs_details):
    logger.info('Got Request - Send to FLEXCUBE')

    try:
        # establish connection between the python program and sis oracle database using connect()
        con = cx_Oracle.connect(user=os.environ.get('DB_USERNAME'),
                                password=os.environ.get('DB_PASSWORD'),
                                dsn=DSN,
                                encoding="UTF-8")
    except cx_Oracle.DatabaseError as er:
        logger.info("There is an error in the Oracle database:", str(er))

    # after connect to database successfully
    else:
        try:
            # create cursor to execute SQL query
            cur = con.cursor()

            # add the settlement cbs details to details
            details = ''
            i = 1
            for detail in settlement_cbs_details:
                currency_code = detail['currencyCode']
                cr_dr = ''
                if detail['cr_dr'].lower() == 'dr':
                    cr_dr = 'D'
                elif detail['cr_dr'].lower() == 'cr':
                    cr_dr = 'C'

                details += """<fcub:Detbs-Jrnl-Txn-Detail>
                                    <fcub:SERIAL_NO>""" + _xml_escape(str(i)) + """</fcub:SERIAL_NO>
                                    <fcub:DR_CR>""" + _xml_escape(str(cr_dr)) + """</fcub:DR_CR>
                                    <fcub:BRANCH_CODE>001</fcub:BRANCH_CODE>
                                    <fcub:ACCOUNT>""" + _xml_escape(str(detail['customerAccount'])) + """</fcub:ACCOUNT>
                                    <fcub:CCY>""" + _xml_escape(str(currency_code)) + """</fcub:CCY>
                                    <fcub:AMOUNT>""" + _xml_escape(str(detail['amount'])) + """</fcub:AMOUNT>
                                    <fcub:TXN_CODE>""" + _xml_escape(str(detail['transactionCode'])) + """</fcub:TXN_CODE>
                                    <fcub:ADDL_TEXT>""" + _xml_escape(str(detail['description'])) + """</fcub:ADDL_TEXT>
                                </fcub:Detbs-Jrnl-Txn-Detail>"""
                i += 1
#    <fcub:FUNCTIONID>DEGJNLON</fcub:FUNCTIONID>
            request_body = """<soapenv:Envelope
                                xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                                xmlns:fcub="http://fcubs.ofss.com/service/FCUBSDEService">
                                <soapenv:Header/>
                                <soapenv:Body>
                                    <fcub:CREATEMJRNLBOOK_FSFS_REQ>
                                        <fcub:FCUBS_HEADER>
                                            <fcub:SOURCE>""" + _xml_escape(str(flexcube['source'])) + """</fcub:SOURCE>
                                            <fcub:UBSCOMP>""" + _xml_escape(str(flexcube['ubscomp'])) + """</fcub:UBSCOMP>
                                            <fcub:USERID>""" + _xml_escape(str(flexcube['user_id'])) + """</fcub:USERID>
                                            <fcub:BRANCH>""" + _xml_escape(str(flexcube['branch'])) + """</fcub:BRANCH>
                                            <fcub:MODULEID>""" + _xml_escape(str(flexcube['module_id'])) + """</fcub:MODULEID>
                                            <fcub:SERVICE>""" + _xml_escape(str(flexcube['service'])) + """</fcub:SERVICE>
                                            <fcub:OPERATION>CreateMjrnlbook</fcub:OPERATION>
                                            <fcub:FUNCTIONID>DEDJNLON</fcub:FUNCTIONID>
                                            <fcub:ACTION>NEW</fcub:ACTION>
                                        </fcub:FCUBS_HEADER>
                                        <fcub:FCUBS_BODY>
                                            <fcub:Detbs-Jrnl-Txn-Master-Full>
                                                <fcub:BRANCH_CODE>001</fcub:BRANCH_CODE>
                                                <fcub:CCY>""" + _xml_escape(str(currency_code)) + """</fcub:CCY>
                                                """ + details + """
                                                <fcub:Devws-Batch-Master>
                                                    <fcub:BALANCING>Y</fcub:BALANCING>
                                                </fcub:Devws-Batch-Master>
                                            </fcub:Detbs-Jrnl-Txn-Master-Full>
                                        </fcub:FCUBS_BODY>
                                    </fcub:CREATEMJRNLBOOK_FSFS_REQ>
                                </soapenv:Body>
                            </soapenv:Envelope>"""

            sent_time = datetime.now()

            # create a post request to flexcube
            response = requests.post(
                os.environ.get('FLEXCUBE_URL'),
                data=request_body,
                headers={'Content-Type': 'text/xml'},
                verify=FLEXCUBE_VERIFY_SSL)

            logger.info(response.content.decode('utf-8'))

            # find the MSGSTAT tag from flexcube response
            soup = BS(re.search('<MSGSTAT>\s*(.+)\s*</MSGSTAT>',
                                response.content.decode('utf-8')).group(0),
                      features="html.parser")

            # check flexcube status success or fail
            if soup.find('msgstat').text == 'SUCCESS':
                status = SETTLE_STATUS_SUCCESS
            elif soup.find('msgstat').text == 'FAILURE':
                status = SETTLE_STATUS_FAIL

            # declare the sql statement for updating settle cbs in SIS database table
            sql_stmt = 'UPDATE SETTLE_CBS ' \
                       'SET FLEXCUBE_CONTENT = :request_body, ' \
                       'FLEXCUBE_MESSAGE = :response_body, ' \
                       'FLEXCUBE_RESPONSE_STATUS_ID = :response_status, ' \
                       'FLEXCUBE_RESPONSE_AT = :response_at, ' \
                       'SETTLEMENT_STATUS_ID = :response_status, ' \
                       'UPDATED_AT = :settlement_update_at, ' \
                       'SENT_AT = :submit_at ' \
                       'WHERE SETTLE_CBS_ID = :settle_cbs_id'

            # execute the SQL query
            cur.execute(sql_stmt, {'request_body': request_body.strip(),
                                   'response_body': response.content.decode('utf-8'),
                                   'response_status': status[0],
                                   'response_at': datetime.now(),
                                   'submit_at': sent_time,
                                   'settlement_update_at': datetime.now(),
                                   'settle_cbs_id': settle_cbs_id})

            # save the execution into database
            con.commit()

            # update the status to external system
            if update_system_status(system_url=system_url, settle_cbs_id=settle_cbs_id, status=status):
                logger.info("Connect to external system success")
            else:
                logger.info("Fail connect to external system")

        except cx_Oracle.DatabaseError as er:
            logger.info("There is an error in the Oracle database:", str(er))
        except Exception as er:
            logger.info("Error:", str(er))

    # finally if any error occurs, then we also close all database operation
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


@celery_app.task()
def send_to_iroha(settle_iroha_id, settlement_iroha_detail):
    logger.info('Got Request - Sent to IROHA')

    try:
        # establish connection between the python program and sis oracle database using connect()
        con = cx_Oracle.connect(user=os.environ.get('DB_USERNAME'),
                                password=os.environ.get('DB_PASSWORD'),
                                dsn=DSN,
                                encoding="UTF-8")
    except cx_Oracle.DatabaseError as er:
        logger.info("There is an error in the Oracle database:", str(er))

    # after connect to database successfully
    else:
        try:
            # create cursor to execute SQL query
            cur = con.cursor()

            # time that sent to iroha
            sent_at = datetime.now()

            # get hash from iroha transfer
            iroha_response_transaction_hash = \
                transfer_to_iroha(sender_id=settlement_iroha_detail['senderAccountId'],
                                  receiver_id=settlement_iroha_detail['receiverAccountId'],
                                  currency=settlement_iroha_detail['currencyCode'],
                                  amount=settlement_iroha_detail['amount'],
                                  desc=settlement_iroha_detail['description'])

            # time that iroha response
            iroha_response_at = datetime.now()

            # get status from iroha by hash
            iroha_response_status = get_iroha_status(hash=iroha_response_transaction_hash)

            # store status as id
            if iroha_response_status == SETTLE_STATUS_COMMITTED[1]:
                iroha_response_status_id = SETTLE_STATUS_COMMITTED[0]
            elif iroha_response_status == SETTLE_STATUS_REJECTED[1]:
                iroha_response_status_id = SETTLE_STATUS_REJECTED[0]
            elif iroha_response_status == SETTLE_STATUS_STATELESS_VALIDATION_FAILED[1]:
                iroha_response_status_id = SETTLE_STATUS_STATELESS_VALIDATION_FAILED[0]

            stmt = 'UPDATE SETTLE_IROHA ' \
                   'SET UPDATED_AT = :update_at, ' \
                   'SENT_AT = :sent_at, ' \
                   'IROHA_RESPONSE_STATUS_ID = :response_status, ' \
                   'SETTLEMENT_STATUS_ID = :response_status, ' \
                   'IROHA_RESPONSE_TRANSACTION_HASH = :iroha_hash, ' \
                   'IROHA_RESPONSE_AT = :response_at ' \
                   'WHERE SETTLE_IROHA_ID = :settle_iroha_id'
            cur.execute(stmt, {'update_at': datetime.now(),
                               'sent_at': sent_at,
                               'response_status': iroha_response_status_id,
                               'iroha_hash': iroha_response_transaction_hash,
                               'response_at': iroha_response_at,
                               'settle_iroha_id': settle_iroha_id})
            con.commit()
        except cx_Oracle.DatabaseError as er:
            logger.info("There is an error in the Oracle database:", str(er))
        except Exception as er:
            logger.info("Error:", str(er))

    # finally if any error occurs, then we also close all database operation
    finally:
        if cur:
            cur.close()
        if con:
            con.close()
