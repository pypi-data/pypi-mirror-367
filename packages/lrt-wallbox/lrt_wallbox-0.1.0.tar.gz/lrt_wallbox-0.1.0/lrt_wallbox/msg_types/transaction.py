from dataclasses import dataclass, field
from typing import List

from cbor2 import CBORTag


@dataclass
class TransactionEntry:
    ocppCpState: str
    connectionState: str
    currentChargeRate: int
    authorizationState: str
    secondsSinceChargeStart: int
    currentTransactionEnergy: int


@dataclass
class TransactionStopResponse:
    energy: int
    endTime: str
    startTime: str
    startedBy: list[int]
    sessionNumber: int


@dataclass
class TransactionStartRequest:
    transaction_id: int = 0
    connector_id: int = 1
    tag_id_length: int = 4
    tag_id: List[int] = field(default_factory=list)

    def to_array(self):
        tag_length = len([x for x in self.tag_id if x != 0])
        tag_inverted = self.tag_id[::-1]
        return [CBORTag(64, self.transaction_id), CBORTag(64, self.connector_id), CBORTag(64, tag_length), *tag_inverted[0:7]]
