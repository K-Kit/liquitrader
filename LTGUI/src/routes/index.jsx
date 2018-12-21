import Dashboard from "layouts/Dashboard.jsx";
import Pages from "layouts/Pages.jsx";
import Fingerprint from "../../node_modules/@material-ui/icons/Fingerprint";
var indexRoutes = [
  { path: "/", name: "Home", component: Dashboard },
  { path: "/pages", name: "Pages", component: Pages },
];

export default indexRoutes;
