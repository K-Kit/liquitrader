export const url =
  !process.env.NODE_ENV || process.env.NODE_ENV === "development"
    ? "http://45.77.216.107:8080/api/"
    : window.location.origin + "/api/";

export const dashboard_route = url + "dashboard_data";

export const market_route = url + "market";
export const holding_route = url + "holding";
export const buys_route = url + "buy_log";
export const sells_route = url + "sell_log";
export const config_route = url + "config";
export const update_config = url + "update_config";
export const auth_route = url + "auth";
export const analyzer_route = url + "analyzers";
export const HEADERS = { mode: "no-cors" };
