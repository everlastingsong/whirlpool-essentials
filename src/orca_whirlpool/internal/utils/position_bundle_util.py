from typing import List, Optional
from ..accounts.types import PositionBundle
from ..constants import POSITION_BUNDLE_SIZE
from ..invariant import invariant


class PositionBundleUtil:
    @staticmethod
    def is_bundle_index_in_bounds(bundle_index: int) -> bool:
        return 0 <= bundle_index < POSITION_BUNDLE_SIZE

    @staticmethod
    def convert_bitmap_to_array(position_bundle: PositionBundle) -> List[bool]:
        result = []
        for bitmap in position_bundle.position_bitmap:
            result.append(bitmap & 0x01 > 0)
            result.append(bitmap & 0x02 > 0)
            result.append(bitmap & 0x04 > 0)
            result.append(bitmap & 0x08 > 0)
            result.append(bitmap & 0x10 > 0)
            result.append(bitmap & 0x20 > 0)
            result.append(bitmap & 0x40 > 0)
            result.append(bitmap & 0x80 > 0)
        return result

    @staticmethod
    def get_occupied_bundle_indexes(position_bundle: PositionBundle) -> List[int]:
        result = []
        for i, occupied in enumerate(PositionBundleUtil.convert_bitmap_to_array(position_bundle)):
            if occupied:
                result.append(i)
        return result

    @staticmethod
    def get_unoccupied_bundle_indexes(position_bundle: PositionBundle) -> List[int]:
        result = []
        for i, occupied in enumerate(PositionBundleUtil.convert_bitmap_to_array(position_bundle)):
            if not occupied:
                result.append(i)
        return result

    @staticmethod
    def is_full(position_bundle: PositionBundle) -> bool:
        unoccupied = PositionBundleUtil.get_unoccupied_bundle_indexes(position_bundle)
        return len(unoccupied) == 0

    @staticmethod
    def is_empty(position_bundle: PositionBundle) -> bool:
        occupied = PositionBundleUtil.get_occupied_bundle_indexes(position_bundle)
        return len(occupied) == 0

    @staticmethod
    def is_occupied(position_bundle: PositionBundle, bundle_index: int) -> bool:
        invariant(
            PositionBundleUtil.is_bundle_index_in_bounds(bundle_index),
            "invalid bundle_index"
        )
        array = PositionBundleUtil.convert_bitmap_to_array(position_bundle)
        return array[bundle_index]

    @staticmethod
    def is_unoccupied(position_bundle: PositionBundle, bundle_index: int) -> bool:
        return not PositionBundleUtil.is_occupied(position_bundle, bundle_index)

    @staticmethod
    def find_unoccupied_bundle_index(position_bundle: PositionBundle) -> Optional[int]:
        unoccupied = PositionBundleUtil.get_unoccupied_bundle_indexes(position_bundle)
        if len(unoccupied) == 0:
            return None
        else:
            return unoccupied[0]
