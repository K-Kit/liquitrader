import Dashboard from "layouts/Dashboard.jsx";
import WizardPage from "views/Pages/WizardPage";
import BuyStrategy from "views/Settings/BuyStrategy.jsx";
import ConditionInput from "views/Settings/ConditionInput.jsx";
import operand from "views/Settings/operand.jsx";

var indexRoutes = [
  { path: "/wiz", name: "Wz", component: WizardPage },

  { path: "/buystrategy", name: "BuyStrategy", component: BuyStrategy },
  { path: "/condinput", name: "ConditionInput", component: ConditionInput },
  { path: "/op", name: "operand", component: operand },
  { path: "/strategylist", name: "sl", component: operand },
  { path: "/", name: "Home", component: Dashboard }
];

export default indexRoutes;
