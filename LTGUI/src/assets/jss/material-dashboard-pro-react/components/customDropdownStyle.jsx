import {
  defaultFont,
  primaryColor,
  primaryBoxShadow
} from "assets/jss/material-dashboard-pro-react.jsx";

const customDropdownStyle = theme => ({
  popperClose: {
    pointerEvents: "none",
    display: "none !important"
  },
  dropdown: {
    borderRadius: "3px",
    border: "0",
    boxShadow: "0 2px 5px 0 rgba(0, 0, 0, 0.26)",
    top: "100%",
    zIndex: "1000",
    minWidth: "160px",
    padding: "5px 0",
    margin: "2px 0 0",
    fontSize: "14px",
    textAlign: "left",
    listStyle: "none",
    backgroundColor: "#fff",
    backgroundClip: "padding-box"
  },
  menuList: {
    padding: "0"
  },
  pooperResponsive: {
    zIndex: "2",
    [theme.breakpoints.down("sm")]: {
      zIndex: "1640",
      position: "static",
      float: "none",
      width: "auto",
      marginTop: "0",
      backgroundColor: "transparent",
      border: "0",
      boxShadow: "none",
      color: "black"
    }
  },
  pooperNav: {
    [theme.breakpoints.down("sm")]: {
      color: "inherit",
      position: "static !important",
      left: "unset !important",
      top: "unset !important",
      transform: "none !important",
      willChange: "unset !important",
      boxShadow: "none !important",
      "& > div": {
        boxShadow: "none !important",
        marginLeft: "0",
        marginRight: "0",
        transition: "none !important",
        marginTop: "0px !important",
        marginBottom: "5px !important",
        padding: "0px !important",
        backgroundColor: "transparent !important",
        "& > ul li": {
          color: "inherit"
        }
      }
    }
  },
  dropdownItem: {
    ...defaultFont,
    fontSize: "13px",
    padding: "10px 20px",
    margin: "0 5px",
    borderRadius: "2px",
    position: "relative",
    transition: "all 150ms linear",
    display: "block",
    clear: "both",
    fontWeight: "400",
    height: "fit-content",
    color: "#c3ced3",
    whiteSpace: "nowrap"
  },
  dropdownItemRTL: {
    textAlign: "right !important"
  },
  blackHover: {
    "&:hover": {
      boxShadow:
        "0 4px 20px 0px rgba(0, 0, 0, 0.14), 0 7px 10px -5px rgba(33, 33, 33, 0.4)",
      backgroundColor: "#212121",
      color: "#fff"
    }
  },
  primaryHover: {
    "&:hover": {
      backgroundColor: primaryColor,
      color: "#FFFFFF",
      ...primaryBoxShadow
    }
  },
  dropdownDividerItem: {
    margin: "5px 0",
    backgroundColor: "rgba(0, 0, 0, 0.12)",
    height: "1px",
    overflow: "hidden"
  },
  buttonIcon: {
    width: "20px",
    height: "20px"
  },
  caret: {
    transition: "all 150ms ease-in",
    display: "inline-block",
    width: "0",
    height: "0",
    marginLeft: "4px",
    verticalAlign: "middle",
    borderTop: "4px solid",
    borderRight: "4px solid transparent",
    borderLeft: "4px solid transparent"
  },
  caretActive: {
    transform: "rotate(180deg)"
  },
  caretDropup: {
    transform: "rotate(180deg)"
  },
  caretRTL: {
    marginRight: "4px"
  },
  dropdownHeader: {
    display: "block",
    padding: "0.1875rem 1.25rem",
    fontSize: "0.75rem",
    lineHeight: "1.428571",
    color: "#777",
    whiteSpace: "nowrap",
    fontWeight: "inherit",
    marginTop: "10px",
    "&:hover,&:focus": {
      backgroundColor: "transparent",
      cursor: "auto"
    }
  }
});

export default customDropdownStyle;
