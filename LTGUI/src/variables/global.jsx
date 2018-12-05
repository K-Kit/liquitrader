export const url = !process.env.NODE_ENV || process.env.NODE_ENV === 'development' ? "http://45.77.216.107:8080/": window.location.origin + "/";

export const dashboard_route = url + 'dashboard_data';

export const market_route = url + "market";
export const holding_route = url + "holding";
export const buys_route = url + "buy_log";
export const sells_route = url + "sell_log";
export const config_route = url + "config";
export const update_config = url + "update_config";
export const HEADERS = { mode: "no-cors" };
