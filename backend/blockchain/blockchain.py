import hashlib
import json
from datetime import datetime


class Block:
    def __init__(self, index, data, previous_hash):
        self.index = index
        self.timestamp = str(datetime.now())
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = (
            str(self.index)
            + self.timestamp
            + json.dumps(self.data, sort_keys=True)
            + self.previous_hash
        )

        return hashlib.sha256(
            block_data.encode()
        ).hexdigest()


class Blockchain:

    def __init__(self):
        self.chain = []

        # Create the first block
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(
            0,
            {"message": "Tourist Safety Blockchain"},
            "0"
        )

        self.chain.append(genesis_block)

    def add_block(self, data):

        previous_block = self.chain[-1]

        new_block = Block(
            len(self.chain),
            data,
            previous_block.hash
        )

        self.chain.append(new_block)

        return new_block
    def is_chain_valid(self):

        for i in range(1, len(self.chain)):

            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Check whether the current block was modified
            if current_block.hash != current_block.calculate_hash():
                return False

            # Check whether the chain connection was modified
            if current_block.previous_hash != previous_block.hash:
                return False

        return True
def create_identity_hash(tourist_id, digital_id, name, email):
         identity_data = {
       	 "tourist_id": tourist_id,
         "digital_id": digital_id,
         "name": name,
         "email": email
         }

         identity_string = json.dumps(
         identity_data,
         sort_keys=True
         )

         return hashlib.sha256(
            identity_string.encode()
         ).hexdigest()		
