// ##############################
// // // ExtendedForms view styles
// #############################

import { cardTitle } from "assets/jss/material-dashboard-pro-react.jsx";
import customSelectStyle from "assets/jss/material-dashboard-pro-react/customSelectStyle.jsx";
import customCheckboxRadioSwitch from "assets/jss/material-dashboard-pro-react/customCheckboxRadioSwitch.jsx";
import modalStyle from "assets/jss/material-dashboard-pro-react/modalStyle.jsx";

const extendedFormsStyle = {
    ...modalStyle,
    modalStyle,
  ...customCheckboxRadioSwitch,
  ...customSelectStyle,
  cardTitle,
  cardIconTitle: {
    ...cardTitle,
    marginTop: "15px",
    marginBottom: "0px"
  },
  label: {
    cursor: "pointer",
    paddingLeft: "0",
    color: "#d7e3eb !important",
    fontSize: "14px",
    lineHeight: "1.428571429",
    fontWeight: "400",
    display: "inline-flex"
  },
selectLabel: {
    color:"#d7e3eb !important",
},
selectMenuItemSelected: {
    color:"#d7e3eb !important",
},
    selectLabel: {
    color:"#d7e3eb !important",
},
select: {
    color:"#d7e3eb !important",
},
    selectMenu: {
    color:"#d7e3eb !important",
}
};

export default extendedFormsStyle;
