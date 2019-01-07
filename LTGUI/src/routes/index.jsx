import Dashboard from "layouts/Dashboard.jsx";
import Pages from "layouts/Pages.jsx";
import Fingerprint from "../../node_modules/@material-ui/icons/Fingerprint";
import LoginPage from "views/Pages/LoginPage.jsx";
var indexRoutes = [
  // { path: "/dashboard", name: "Home", component: Dashboard },
  { path: "/pages", name: "Pages", component: Pages },

    {path: "/login", name: "Login", component: LoginPage},
  { path: "/", name: "Home", component: Dashboard },
];
console.log(indexRoutes);
export default indexRoutes;
