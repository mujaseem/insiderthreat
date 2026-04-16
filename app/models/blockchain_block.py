from app import db
from datetime import datetime


class BlockchainBlock(db.Model):

    __tablename__ = "blockchain_blocks"

    id = db.Column(db.Integer, primary_key=True)

    block_index = db.Column(db.Integer)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    data = db.Column(db.Text)

    previous_hash = db.Column(db.String(256))

    hash = db.Column(db.String(256))