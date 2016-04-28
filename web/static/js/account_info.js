$(document).ready(function() {
    console.log( "account info ready!" );
    requestAccountInfo();
});

function requestAccountInfo() {
    $.ajax({
        url: '/account_info',
        success: function(account_info){
            //console.log(account_info);
            $("#cash-balance-container").html(account_info['cash_balance']);
            $("#available-funds-container").html(account_info['available_funds']);
            $("#buying-power-container").html(account_info['buying_power']);
            $("#excess-liquidity-container").html(account_info['excess_liquidity']);
            $("#futures-pnl-container").html(account_info['futures_pnl']);
            $("#unrealized-pnl-container").html(account_info['unrealized_pnl']);
            $("#realized-pnl-container").html(account_info['realized_pnl']);
            setTimeout(requestAccountInfo, 100);
        },
        cache: false
    });
}
