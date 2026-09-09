import requests
from celery.utils.log import get_task_logger
from requests.adapters import HTTPAdapter, Retry

logger = get_task_logger(__name__)


def update_system_status(system_url: str, settle_cbs_id: int, status: tuple) -> bool:
    """
    This function is used to update the status to external system that login to SIS
    :return: Boolean true or false
    """
    try:
        logger.info("Start Request to External System")

        request_session = requests.Session()
        request_session.mount(
            'http://', HTTPAdapter(max_retries=Retry(connect=3, backoff_factor=0.5)))
        request_session.mount(
            'https://', HTTPAdapter(max_retries=Retry(connect=3, backoff_factor=0.5)))

        # parsed = request_session.post(system_url + '/sys/auth',
        #                               json={'username': 'admin',
        #                                     'password': 'admin'
        #                                     }
        #                               ).json()

        response = request_session.post(system_url + '/sys/update-status',
                                        json={'status': status[1],
                                              'id': settle_cbs_id,
                                              'reference': 'FLEXCUBE PROCESSED'
                                              }
                                        #       ,
                                        # headers={"Authorization": "Bearer " + parsed['data']['access_token']}
                                        )

        logger.info(system_url + '/sys/update-status')
        logger.info('Work Finished - FLEXCUBE REPSONSE')
        logger.info(response.content)

        return True
    except Exception as error:
        logger.info("Error:", str(error))
        return False
