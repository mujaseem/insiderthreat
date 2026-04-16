import hashlib
import json
from datetime import datetime

from app.models.blockchain_block import BlockchainBlock
from app import db


def calculate_hash(index, timestamp, data, previous_hash):
    block_content = {
        "index": index,
        "timestamp": str(timestamp),
        "data": data,
        "previous_hash": previous_hash
    }

    block_string = json.dumps(block_content, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()


class BlockchainLogger:

    def create_genesis_block(self):
        first = BlockchainBlock.query.first()

        if first:
            return

        timestamp = datetime.utcnow()
        data = "SOC System Initialized"

        hash_value = calculate_hash(
            0,
            timestamp,
            data,
            "0"
        )

        block = BlockchainBlock(
            block_index=0,
            timestamp=timestamp,
            data=data,
            previous_hash="0",
            hash=hash_value
        )

        db.session.add(block)
        db.session.commit()

    def add_block(self, data):
        last_block = BlockchainBlock.query.order_by(
            BlockchainBlock.block_index.desc()
        ).first()

        if not last_block:
            self.create_genesis_block()
            last_block = BlockchainBlock.query.first()

        index = last_block.block_index + 1
        previous_hash = last_block.hash
        timestamp = datetime.now()

        # Convert event data to JSON string
        data_json = json.dumps(data, sort_keys=True)

        hash_value = calculate_hash(
            index,
            timestamp,
            data_json,
            previous_hash
        )

        block = BlockchainBlock(
            block_index=index,
            timestamp=timestamp,
            data=data_json,
            previous_hash=previous_hash,
            hash=hash_value
        )

        db.session.add(block)
        db.session.commit()


# Initialize blockchain logger
blockchain_logger = BlockchainLogger()