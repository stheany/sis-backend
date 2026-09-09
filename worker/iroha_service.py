import binascii
import os

from iroha import Iroha, IrohaCrypto, IrohaGrpc

IROHA_HOST = os.getenv('IROHA_HOST')
VAULT_KEY = os.getenv('VAULT_KEY')
NBC_KEY = os.getenv('NBC_KEY')
FIS_KEY = os.getenv('FIS_KEY')
VAULT_ACCOUNT = os.getenv('VAULT_ACCOUNT')
FIS_ACCOUNT = os.getenv('FIS_ACCOUNT')
NBC_ACCOUNT = os.getenv('NBC_ACCOUNT')


def transfer_to_iroha(sender_id, receiver_id, currency, amount, desc):
    """
        Used to transfer settlement content to Iroha

    :param sender_id:
        An account ID of sender nbc@nbc or vault@nbc
    :param receiver_id:
        An account ID of receiver vault@nbc or nbc@nbc
    :param currency:
        Currency type "KHR" or "USD"
    :param amount:
        Amount money that need to transfer
    :param desc:
        An additional description
    :return:
        A hash code after transfer settlement to Iroha
    """
    currency = f"{currency.lower()}#nbc"
    iroha = Iroha(sender_id)
    iroha_node = IrohaGrpc(IROHA_HOST)

    if sender_id == VAULT_ACCOUNT:
        private_key = VAULT_KEY
    elif sender_id == NBC_ACCOUNT:
        private_key = NBC_KEY
    elif sender_id == FIS_ACCOUNT:
        private_key = FIS_KEY
    else:
        return "Invalid sender account id: " + sender_id

    iroha_tx = iroha.transaction(
        [iroha.command(
            'TransferAsset',
            src_account_id=sender_id,
            dest_account_id=receiver_id,
            asset_id=currency,
            description=desc,
            amount=amount
        )]
    )

    IrohaCrypto.sign_transaction(iroha_tx, private_key)
    iroha_node.send_tx(iroha_tx)
    hash = binascii.hexlify(IrohaCrypto.hash(iroha_tx))
    return hash.decode('utf8')


def get_iroha_status(hash):
    """
        Used to get status from Iroha

    :param hash:
        A hash code
    :return:
        Iroha Status
    """
    iroha_node = IrohaGrpc(IROHA_HOST)

    # get the final status from iroha
    final_status = ""

    for status in iroha_node.tx_hash_status_stream(hash):
        final_status = status[0]

    return final_status
