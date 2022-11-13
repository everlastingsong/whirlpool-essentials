from ..types.enums import TickArrayReduction
from .swap_simulator.types import SwapQuote, SwapQuoteParams
from .swap_simulator.swap_simulator import simulate_swap


def swap_quote_with_params(
    params: SwapQuoteParams,
    tick_array_reduction: TickArrayReduction,
) -> SwapQuote:
    quote = simulate_swap(params, tick_array_reduction)

    if params.specified_amount.is_swap_input:
        other_amount_threshold = params.slippage_tolerance.adjust_sub(quote.estimated_amount_out)
    else:
        other_amount_threshold = params.slippage_tolerance.adjust_add(quote.estimated_amount_in)

    return SwapQuote(
        estimated_amount_in=quote.estimated_amount_in,
        estimated_amount_out=quote.estimated_amount_out,
        estimated_end_tick_index=quote.estimated_end_tick_index,
        estimated_end_sqrt_price=quote.estimated_end_sqrt_price,
        estimated_fee_amount=quote.estimated_fee_amount,
        amount=quote.amount,
        # only other_amount_threshold is modified
        other_amount_threshold=other_amount_threshold,
        sqrt_price_limit=quote.sqrt_price_limit,
        specified_amount=quote.specified_amount,
        direction=quote.direction,
        tick_array_0=quote.tick_array_0,
        tick_array_1=quote.tick_array_1,
        tick_array_2=quote.tick_array_2,
    )
