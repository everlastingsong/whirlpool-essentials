from solders.pubkey import Pubkey
from ..constants import METAPLEX_METADATA_PROGRAM_ID
from ..types.types import PDA


PDA_WHIRLPOOL_SEED = b"whirlpool"
PDA_POSITION_SEED = b"position"
PDA_METADATA_SEED = b"metadata"
PDA_TICK_ARRAY_SEED = b"tick_array"
PDA_FEE_TIER_SEED = b"fee_tier"
PDA_ORACLE_SEED = b"oracle"
PDA_POSITION_BUNDLE_SEED = b"position_bundle"
PDA_BUNDLED_POSITION_SEED = b"bundled_position"
PDA_WHIRLPOOLS_CONFIG_EXTENSION_SEED = b"config_extension"
PDA_TOKEN_BADGE_SEED = b"token_badge"


class PDAUtil:
    @staticmethod
    def get_whirlpool(
        program_id: Pubkey,
        whirlpools_config_pubkey: Pubkey,
        mint_a: Pubkey,
        mint_b: Pubkey,
        tick_spacing: int
    ) -> PDA:
        seeds = [
            PDA_WHIRLPOOL_SEED,
            bytes(whirlpools_config_pubkey),
            bytes(mint_a),
            bytes(mint_b),
            tick_spacing.to_bytes(2, "little")
        ]
        (pubkey, nonce) = Pubkey.find_program_address(seeds, program_id)
        return PDA(pubkey, nonce)

    @staticmethod
    def get_position(program_id: Pubkey, position_mint: Pubkey) -> PDA:
        seeds = [
            PDA_POSITION_SEED,
            bytes(position_mint)
        ]
        (pubkey, nonce) = Pubkey.find_program_address(seeds, program_id)
        return PDA(pubkey, nonce)

    @staticmethod
    def get_position_metadata(position_mint: Pubkey) -> PDA:
        seeds = [
            PDA_METADATA_SEED,
            bytes(METAPLEX_METADATA_PROGRAM_ID),
            bytes(position_mint)
        ]
        (pubkey, nonce) = Pubkey.find_program_address(seeds, METAPLEX_METADATA_PROGRAM_ID)
        return PDA(pubkey, nonce)

    @staticmethod
    def get_tick_array(program_id: Pubkey, whirlpool_pubkey: Pubkey, start_tick_index: int) -> PDA:
        seeds = [
            PDA_TICK_ARRAY_SEED,
            bytes(whirlpool_pubkey),
            str(start_tick_index).encode("utf-8")
        ]
        (pubkey, nonce) = Pubkey.find_program_address(seeds, program_id)
        return PDA(pubkey, nonce)

    @staticmethod
    def get_oracle(program_id: Pubkey, whirlpool_pubkey: Pubkey) -> PDA:
        seeds = [
            PDA_ORACLE_SEED,
            bytes(whirlpool_pubkey),
        ]
        (pubkey, nonce) = Pubkey.find_program_address(seeds, program_id)
        return PDA(pubkey, nonce)

    @staticmethod
    def get_fee_tier(program_id: Pubkey, whirlpools_config_pubkey: Pubkey, tick_spacing: int) -> PDA:
        seeds = [
            PDA_FEE_TIER_SEED,
            bytes(whirlpools_config_pubkey),
            tick_spacing.to_bytes(2, "little")
        ]
        (pubkey, nonce) = Pubkey.find_program_address(seeds, program_id)
        return PDA(pubkey, nonce)

    @staticmethod
    def get_bundled_position(program_id: Pubkey, position_bundle_mint: Pubkey, bundle_index: int) -> PDA:
        seeds = [
            PDA_BUNDLED_POSITION_SEED,
            bytes(position_bundle_mint),
            str(bundle_index).encode("utf-8")
        ]
        (pubkey, nonce) = Pubkey.find_program_address(seeds, program_id)
        return PDA(pubkey, nonce)

    @staticmethod
    def get_position_bundle(program_id: Pubkey, position_bundle_mint: Pubkey) -> PDA:
        seeds = [
            PDA_POSITION_BUNDLE_SEED,
            bytes(position_bundle_mint)
        ]
        (pubkey, nonce) = Pubkey.find_program_address(seeds, program_id)
        return PDA(pubkey, nonce)

    @staticmethod
    def get_position_bundle_metadata(position_bundle_mint: Pubkey) -> PDA:
        seeds = [
            PDA_METADATA_SEED,
            bytes(METAPLEX_METADATA_PROGRAM_ID),
            bytes(position_bundle_mint)
        ]
        (pubkey, nonce) = Pubkey.find_program_address(seeds, METAPLEX_METADATA_PROGRAM_ID)
        return PDA(pubkey, nonce)

    @staticmethod
    def get_whirlpools_config_extension(program_id: Pubkey, whirlpools_config_pubkey: Pubkey) -> PDA:
        seeds = [
            PDA_WHIRLPOOLS_CONFIG_EXTENSION_SEED,
            bytes(whirlpools_config_pubkey)
        ]
        (pubkey, nonce) = Pubkey.find_program_address(seeds, program_id)
        return PDA(pubkey, nonce)

    @staticmethod
    def get_token_badge(program_id: Pubkey, whirlpools_config_pubkey: Pubkey, token_mint: Pubkey) -> PDA:
        seeds = [
            PDA_TOKEN_BADGE_SEED,
            bytes(whirlpools_config_pubkey),
            bytes(token_mint)
        ]
        (pubkey, nonce) = Pubkey.find_program_address(seeds, program_id)
        return PDA(pubkey, nonce)
