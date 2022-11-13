from ..types.enums import TickArrayReduction
from .increase_liquidity import IncreaseLiquidityQuote, IncreaseLiquidityQuoteParams, increase_liquidity_quote_by_input_token_with_params
from .decrease_liquidity import DecreaseLiquidityQuote, DecreaseLiquidityQuoteParams, decrease_liquidity_quote_by_liquidity_with_params
from .collect_fees_and_rewards import CollectFeesQuote, CollectFeesQuoteParams, collect_fees_quote
from .collect_fees_and_rewards import CollectRewardsQuote, CollectRewardsQuoteParams, collect_rewards_quote
from .swap import SwapQuote, SwapQuoteParams, swap_quote_with_params


class QuoteBuilder:
    @staticmethod
    def swap(params: SwapQuoteParams, tick_array_reduction: TickArrayReduction = TickArrayReduction.No) -> SwapQuote:
        return swap_quote_with_params(params, tick_array_reduction)

    @staticmethod
    def increase_liquidity_by_input_token(params: IncreaseLiquidityQuoteParams) -> IncreaseLiquidityQuote:
        return increase_liquidity_quote_by_input_token_with_params(params)

    @staticmethod
    def decrease_liquidity_by_liquidity(params: DecreaseLiquidityQuoteParams) -> DecreaseLiquidityQuote:
        return decrease_liquidity_quote_by_liquidity_with_params(params)

    @staticmethod
    def collect_fees(params: CollectFeesQuoteParams) -> CollectFeesQuote:
        return collect_fees_quote(params)

    @staticmethod
    def collect_rewards(params: CollectRewardsQuoteParams) -> CollectRewardsQuote:
        return collect_rewards_quote(params)
