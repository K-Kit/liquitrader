import Dashboard from "views/Dashboard/Dashboard.jsx";

// @material-ui/icons
import DashboardIcon from "@material-ui/icons/Dashboard";
import Image from "@material-ui/icons/Image";
import Apps from "@material-ui/icons/Apps";
// import ContentPaste from "@material-ui/icons/ContentPaste";
import Place from "@material-ui/icons/Place";
import WidgetsIcon from "@material-ui/icons/Widgets";
import Timeline from "@material-ui/icons/Timeline";
import DateRange from "@material-ui/icons/DateRange";

import GeneralSettings from "views/Settings/GeneralSettings.jsx";
import GlobalTrade from "views/Settings/GlobalTrade.jsx";
import BuyStrategies from "views/Settings/BuyStrategies.jsx";
import DCAStrategies from "views/Settings/DCAStrategies.jsx";
import SellStrategies from "views/Settings/SellStrategies.jsx";

import Holding from "views/DataTables/Holding";
import BuyLog from "views/DataTables/BuyLog";
import SellLog from "views/DataTables/SellLog";
import Market from "views/DataTables/Market";
import {
  BuyAnalyzer,
  SellAnalyzer,
  DCAAnalyzer
} from "views/Analyzers/Analyzers";

var dashRoutes = [
  {
    path: "/dashboard",
    name: "Dashboard",
    icon: DashboardIcon,
    component: Dashboard
  },
  { path: "/market", name: "Market", icon: WidgetsIcon, component: Market },
  { path: "/holding", name: "Holding", icon: Timeline, component: Holding },

  {
    path: "/buys",
    name: "Buy Log",
    icon: DateRange,
    component: BuyLog
  },

  {
    path: "/sales",
    name: "Sales Log",
    icon: DateRange,
    component: SellLog
  },
  {
    path: "/buyAnalyzer",
    name: "Buy Analyzer",
    icon: DateRange,
    component: BuyAnalyzer
  },
  {
    path: "/sellAnalyzer",
    name: "Sell Analyzer",
    icon: DateRange,
    component: SellAnalyzer
  },
  {
    path: "/dcaAnalyzer",
    name: "DCA Analyzer",
    icon: DateRange,
    component: DCAAnalyzer
  },
  // { path: "/calendar", name: "Analyzer", icon: DateRange, component: Holding },
  {
    collapse: true,
    path: "/settings",
    name: "Settings",
    state: "openSettings",
    icon: Place,
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
      }
    ]
  },
  { redirect: true, path: "/", pathTo: "/dashboard", name: "Dashboard" }
];
export default dashRoutes;
