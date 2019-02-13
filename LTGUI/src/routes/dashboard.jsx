import Dashboard from "views/Dashboard/Dashboard.jsx";

// @material-ui/icons
import DashboardIcon from "@material-ui/icons/Dashboard";
import BuyIcon from "@material-ui/icons/AddShoppingCart";
import SellIcon from "@material-ui/icons/AttachMoney";
import MarketIcon from "@material-ui/icons/ShoppingBasket";
import WidgetsIcon from "@material-ui/icons/Widgets";
import Timeline from "@material-ui/icons/Timeline";
import DateRange from "@material-ui/icons/DateRange";
import Setting from "@material-ui/icons/Settings";
import LocationSearch from "@material-ui/icons/LocationSearching"

import GeneralSettings from "views/Settings/GeneralSettings.jsx";
import GlobalTrade from "views/Settings/GlobalTrade.jsx";
import BuyStrategies from "views/Settings/BuyStrategies.jsx";
import DCAStrategies from "views/Settings/DCAStrategies.jsx";
import SellStrategies from "views/Settings/SellStrategies.jsx";
import Users from "views/Settings/Users.jsx";

import Holding from "views/DataTables/Holding";
import BuyLog from "views/DataTables/BuyLog";
import SellLog from "views/DataTables/SellLog";
import Market from "views/DataTables/Market";
import {
  BuyAnalyzer,
  SellAnalyzer,
  DCAAnalyzer
} from "views/Analyzers/Analyzers";
import PairSettings from "../views/Settings/PairSettings";
import { faEthereum } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
// import pagesRoutes from "./pages.jsx";
// var pages = pagesRoutes

let adminroutes = {
    collapse: true,
    path: "/settings",
    name: "Settings",
    state: "openSettings",
    icon: Setting,
    views: [
      {
        path: "/Settings/General",
        name: "General",
        mini: "G",
        component: GeneralSettings
      },
      {
        path: "/Settings/GlobalTrade",
        name: "Global Trade",
        mini: "GT",
        component: GlobalTrade
      },
      {
        path: "/Settings/BuyStrategies",
        name: "Buy Strategies",
        mini: "BS",
        component: BuyStrategies
      },
      {
        path: "/Settings/DCAStrategies",
        name: "DCA Strategies",
        mini: "DCA",
        component: DCAStrategies
      },
      {
        path: "/Settings/SellStrategies",
        name: "Sell Strategies",
        mini: "SS",
        component: SellStrategies
      },

  {
    path: "/pairSettings",
    name: "Pair Specific Settings",
    mini: "PS",
    icon: DateRange,
    component: PairSettings
  },
  {
    path: "/users",
    name: "User Management",
    mini: "USR",
    icon: DateRange,
    component: Users
  },
    ]
  };
var dashRoutes = [
  {
    path: "/dashboard",
    name: "Dashboard",
    icon: DashboardIcon,
    component: Dashboard
  },
  //   {
  //   collapse: true,
  //   path: "-page",
  //   name: "Pages",
  //   state: "openPages",
  //   icon: Image,
  //   views: pages
  // },
  { path: "/market", name: "Market", icon: MarketIcon, component: Market },
  { path: "/holding", name: "Holding", icon: Timeline, component: Holding },

  {
    path: "/buys",
    name: "Buy Log",
    icon: BuyIcon,
    component: BuyLog
  },

  {
    path: "/sales",
    name: "Sales Log",
    icon: SellIcon,
    component: SellLog
  },
  {
    path: "/buyAnalyzer",
    name: "Buy Analyzer",
    icon: LocationSearch,
    component: BuyAnalyzer
  },
  {
    path: "/sellAnalyzer",
    name: "Sell Analyzer",
    icon: LocationSearch,
    component: SellAnalyzer
  },
  {
    path: "/dcaAnalyzer",
    name: "DCA Analyzer",
    icon: LocationSearch,
    component: DCAAnalyzer
  },
  // { path: "/calendar", name: "Analyzer", icon: DateRange, component: Holding },
  adminroutes,
  { redirect: true, path: "/", pathTo: "/dashboard", name: "Dashboard" }
];
export default dashRoutes;
