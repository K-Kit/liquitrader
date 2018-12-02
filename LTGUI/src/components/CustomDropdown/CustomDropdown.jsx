import React from "react";
// nodejs library that concatenates classes
import classNames from "classnames";
// nodejs library to set properties for components
import PropTypes from "prop-types";

// material-ui components
import withStyles from "@material-ui/core/styles/withStyles";
import MenuItem from "@material-ui/core/MenuItem";
import MenuList from "@material-ui/core/MenuList";
import ClickAwayListener from "@material-ui/core/ClickAwayListener";
import Paper from "@material-ui/core/Paper";
import Grow from "@material-ui/core/Grow";
import Divider from "@material-ui/core/Divider";
import Popper from "@material-ui/core/Popper";

// core components
import Button from "components/CustomButtons/Button.jsx";

import customDropdownStyle from "assets/jss/material-dashboard-pro-react/components/customDropdownStyle.jsx";

class CustomDropdown extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      open: false
    };
    this.handleClick = this.handleClick.bind(this);
    this.handleClose = this.handleClose.bind(this);
  }
  handleClick = () => {
    this.setState(state => ({ open: !state.open }));
  };
  handleClose = event => {
    if (this.anchorEl.contains(event.target)) {
      return;
    }

    this.setState({ open: false });
  };

  render() {
    const { open } = this.state;
    const {
      classes,
      buttonText,
      buttonIcon,
      dropdownList,
      buttonProps,
      dropup,
      dropdownHeader,
      caret,
      hoverColor,
      left,
      rtlActive
    } = this.props;
    const caretClasses = classNames({
      [classes.caret]: true,
      [classes.caretDropup]: dropup && !open,
      [classes.caretActive]: open && !dropup,
      [classes.caretRTL]: rtlActive
    });
    const dropdownItem = classNames({
      [classes.dropdownItem]: true,
      [classes[hoverColor + "Hover"]]: true,
      [classes.dropdownItemRTL]: rtlActive
    });
    return (
      <div>
        <Button
          aria-label="Notifications"
          aria-owns={open ? "menu-list" : null}
          aria-haspopup="true"
          onClick={this.handleClick}
          buttonRef={node => {
            this.anchorEl = node;
          }}
          {...buttonProps}
        >
          {buttonIcon !== undefined ? (
            <this.props.buttonIcon className={classes.buttonIcon} />
          ) : null}
          {buttonText !== undefined ? buttonText : null}
          {caret ? <b className={caretClasses} /> : null}
        </Button>
        <Popper
          open={open}
          anchorEl={this.anchorEl}
          transition
          disablePortal
          placement={
            dropup
              ? left
                ? "top-start"
                : "top"
              : left
                ? "bottom-start"
                : "bottom"
          }
          className={classNames({
            [classes.popperClose]: !open,
            [classes.pooperResponsive]: true
          })}
        >
          {({ TransitionProps, placement }) => (
            <Grow
              {...TransitionProps}
              id="menu-list"
              style={
                dropup
                  ? { transformOrigin: "0 100% 0" }
                  : { transformOrigin: "0 0 0" }
              }
            >
              <Paper className={classes.dropdown}>
                <ClickAwayListener onClickAway={this.handleClose}>
                  <MenuList role="menu" className={classes.menuList}>
                    {dropdownHeader !== undefined ? (
                      <MenuItem
                        onClick={this.handleClose}
                        className={classes.dropdownHeader}
                      >
                        {dropdownHeader}
                      </MenuItem>
                    ) : null}
                    {dropdownList.map((prop, key) => {
                      if (prop.divider) {
                        return (
                          <Divider
                            key={key}
                            onClick={this.handleClose}
                            className={classes.dropdownDividerItem}
                          />
                        );
                      }
                      return (
                        <MenuItem
                          key={key}
                          onClick={this.handleClose}
                          className={dropdownItem}
                        >
                          {prop}
                        </MenuItem>
                      );
                    })}
                  </MenuList>
                </ClickAwayListener>
              </Paper>
            </Grow>
          )}
        </Popper>
      </div>
    );
  }
}

CustomDropdown.defaultProps = {
  caret: true,
  hoverColor: "primary"
};

CustomDropdown.propTypes = {
  classes: PropTypes.object.isRequired,
  hoverColor: PropTypes.oneOf(["primary", "black"]),
  buttonText: PropTypes.node,
  buttonIcon: PropTypes.func,
  dropdownList: PropTypes.array,
  buttonProps: PropTypes.object,
  dropup: PropTypes.bool,
  dropdownHeader: PropTypes.node,
  rtlActive: PropTypes.bool,
  caret: PropTypes.bool,
  left: PropTypes.bool
};

export default withStyles(customDropdownStyle)(CustomDropdown);
