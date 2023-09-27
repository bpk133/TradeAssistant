# response for trying to sell to close options I don't have
# {'errors':
#      {'error': 'Sell order cannot be placed unless you are closing a long position, please check open orders. '}}


"""
needs:
    manage time centrally and synchronously across all processes
    manage market state
        what is current market state
        when does it need updated
        when is the next change in market state
        when is the next change in tradeable state
    manage positions
        what are current positions
        has position state changed
    manage account balances
        what are current account balances
        what will account balances be if order executed
    manage orders
        are there outstanding orders
        should an order be issued, modified, rescinded

# start building out all of the potential flows...
# be less dependent on api data structure..
# separate api data response (or response objects) from functional objects core to app operation
# design as if api did not exist then figure out how api fits in


current_time
calendar
current_state

if current_state is open:
    if positions are open:
        gather decision data
        make should sell decision
            could also be should buy
    if positions not open:
        gather decision data
        make should buy decision

will conditions exist where I want to issue, modify, or rescind an order pre-market, post-market, or while closed
    not sure if this is even possible
    app can make near instant decisions so this is likely not necessary

revisiting the above...

1. Is it a decision window (i.e. a time when I should be analyzing and executing orders)
2. Am I in a position to make decisions (e.g. are positions open, are funds available, etc.)
3. What types of decisions am I evaluating
4. What are the values for the inputs for making those decisions
5. Make those decisions


again avoid "too much" built in functionality with objects as they may be needed for additional use cases

try to make accessing properties, filtering, sorting, and other operations direct, simple, and relatively generic...
for example, the calendar, should it be able to answer these questions

what is the current market state
what is the next tradeable market state
how much time until my option expires
how many open hours are there until expiration
is the market open 5 days from now
are there any holidays or early closures in the next 2 weeks

pretty much no for all of these. it shouldn't answer any of these questions directly,
    but another function can use the calendar data to look up the information needed to answer these questions



"""



