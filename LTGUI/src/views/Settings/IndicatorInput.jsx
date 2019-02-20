/* eslint-disable react/prop-types, react/jsx-handler-names */

import React from "react";
import PropTypes from "prop-types";
import classNames from "classnames";
import Select from "react-select";
import { withStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import NoSsr from "@material-ui/core/NoSsr";
import TextField from "@material-ui/core/TextField";
import Paper from "@material-ui/core/Paper";
import Chip from "@material-ui/core/Chip";
import MenuItem from "@material-ui/core/MenuItem";
import CancelIcon from "@material-ui/icons/Cancel";
import { emphasize } from "@material-ui/core/styles/colorManipulator";
import { INDICATORS } from "./data/Indicators";
import extendedFormsStyle from "assets/jss/material-dashboard-pro-react/views/extendedFormsStyle.jsx";

import * as colors from "variables/lt_colors";

const suggestions = INDICATORS.map(suggestion => ({
  value: suggestion.label,
  label: suggestion.label
}));

const styles = theme => ({
  root: {
    flexGrow: 1,
    height: 250,
    display: "block"
  },
  input: {
    display: "inline-flex",
    padding: 0,
    color: "white"
  },
  valueContainer: {
    marginTop: "27px",
    display: "inline-flex",
    flexWrap: "wrap",
    flex: 1,
    alignItems: "center",
    overflow: "hidden",
    color: colors.mainFontColor
  },
  chip: {
    margin: `${theme.spacing.unit / 2}px ${theme.spacing.unit / 4}px`
  },
  chipFocused: {
    backgroundColor: emphasize(theme.palette.grey[300], 0.08)
  },
  noOptionsMessage: {
    padding: `${theme.spacing.unit}px ${theme.spacing.unit * 2}px`
  },
  singleValue: {
    fontSize: 14,

    color: colors.mainFontColor
  },
  placeholder: {
    position: "absolute",
    left: 2,
    color: colors.mainFontColor,

    fontSize: 14
  },
  paper: {
    position: "absolute",
    zIndex: 1,
    // marginTop: theme.spacing.unit,
    left: 0,
    right: 0
  },
  divider: {
    height: theme.spacing.unit * 2
  }
});

function NoOptionsMessage(props) {
  return (
    <Typography
      color="textSecondary"
      className={props.selectProps.classes.noOptionsMessage}
      {...props.innerProps}
    >
      {props.children}
    </Typography>
  );
}

function inputComponent({ inputRef, ...props }) {
  return <div ref={inputRef} {...props} />;
}

function Control(props) {
  return (
    <TextField
      fullWidth
      InputProps={{
        inputComponent,
        inputProps: {
          className: props.selectProps.classes.input,
          inputRef: props.innerRef,
          children: props.children,
          ...props.innerProps
        }
      }}
      {...props.selectProps.textFieldProps}
    />
  );
}

function Option(props) {
  return (
    <MenuItem
      buttonRef={props.innerRef}
      selected={props.isFocused}
      component="div"
      style={{
        fontWeight: props.isSelected ? 500 : 400
      }}
      {...props.innerProps}
    >
      {props.children}
    </MenuItem>
  );
}

function Placeholder(props) {
  return (
    <Typography
      color="textSecondary"
      className={props.selectProps.classes.placeholder}
      {...props.innerProps}
    >
      {props.children}
    </Typography>
  );
}

function SingleValue(props) {
  return (
    <Typography
      className={props.selectProps.classes.singleValue}
      {...props.innerProps}
    >
      {props.children}
    </Typography>
  );
}

function ValueContainer(props) {
  return (
    <div className={props.selectProps.classes.valueContainer}>
      {props.children}
    </div>
  );
}

function MultiValue(props) {
  return (
    <Chip
      tabIndex={-1}
      label={props.children}
      className={classNames(props.selectProps.classes.chip, {
        [props.selectProps.classes.chipFocused]: props.isFocused
      })}
      onDelete={props.removeProps.onClick}
      deleteIcon={<CancelIcon {...props.removeProps} />}
    />
  );
}

function Menu(props) {
  return (
    <Paper
      square
      className={props.selectProps.classes.paper}
      {...props.innerProps}
    >
      {props.children}
    </Paper>
  );
}

const components = {
  Control,
  Menu,
  MultiValue,
  NoOptionsMessage,
  Option,
  Placeholder,
  SingleValue,
  ValueContainer
};

class IntegrationReactSelect extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      single: this.props.val,
      multi: null
    };
  }
  handleChange = name => {
    this.setState({
      single: name.value
    });
  };

  render() {
    const { classes, theme, callback, val, id, label } = this.props;

    const selectStyles = {
      input: base => ({
        ...base,
        borderBottom: "2px " + colors.mainFontColor + " !important",
        color: "white",
        "& input": {
          font: "inherit"
        }
      })
    };
    return (
      // <div className={classes.root}>
      // <NoSsr>
      <Select
        classes={classes}
        styles={selectStyles}
        options={suggestions}
        components={components}
        // value={this.state.single}
        name={id}
        id={id}
        onChange={(name, value) => {
          this.props.callback(name, value);
          this.handleChange(name, value);
        }}
        placeholder="Select an indicator"
        isClearable
      />
      // </NoSsr>
      // </div>
    );
  }
}

// IntegrationReactSelect.propTypes = {
//   classes: PropTypes.object.isRequired,
//   theme: PropTypes.object.isRequired
// };

export default withStyles(styles, { withTheme: true })(IntegrationReactSelect);
