import React from "react";
// @material-ui/core components
import withStyles from "@material-ui/core/styles/withStyles";
import FormLabel from "@material-ui/core/FormLabel";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import InputAdornment from "@material-ui/core/InputAdornment";
import Radio from "@material-ui/core/Radio";
import Checkbox from "@material-ui/core/Checkbox";

// @material-ui/icons
import MailOutline from "@material-ui/icons/MailOutline";
import Check from "@material-ui/icons/Check";
import Clear from "@material-ui/icons/Clear";
import Contacts from "@material-ui/icons/Contacts";
import FiberManualRecord from "@material-ui/icons/FiberManualRecord";

import Button from "components/CustomButtons/Button.jsx";
import Card from "components/Card/Card.jsx";
import CardHeader from "components/Card/CardHeader.jsx";
import CardText from "components/Card/CardText.jsx";
import CardIcon from "components/Card/CardIcon.jsx";
import CardBody from "components/Card/CardBody.jsx";

import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";
import CustomInput from "components/CustomInput/CustomInput.jsx";
import extendedFormsStyle from "assets/jss/material-dashboard-pro-react/views/extendedFormsStyle.jsx";
// react component plugin for creating beatiful tags on an input
import Slide from "@material-ui/core/Slide";

import Operand from "views/Settings/operand.jsx";
import Tabs from "components/CustomTabs/CustomTabs.jsx";
import Tasks from "components/Tasks/Tasks.jsx";
import MenuItem from "@material-ui/core/MenuItem/MenuItem";
import Select from "@material-ui/core/Select/Select";
import {PATTERNS} from "views/Settings/data/Indicators.jsx";
import FormControl from "@material-ui/core/FormControl/FormControl";
import InputLabel from "@material-ui/core/InputLabel/InputLabel";

function Transition(props) {
  return <Slide direction="down" {...props} />;
}

let mfi = { value: "MFI", timeframe: "5m", candle_period: 30 };
let staticval = { value: 30 };
let mfo = { left: mfi, op: ">", right: staticval };

let cup = { left: mfi, op: "cross_up", right: staticval };
let conditions = [cup, mfo];
let opList = [">", "<", "cross_up", "cross_down", "GAIN"];
let indicatorInput = (side, label, callback) => {
  return (
    <div>
      <CustomInput
        labelText={label}
        id={side}
        formControlProps={{
          fullWidth: true
        }}
        inputProps={{
          onChange: event => callback(event),
          name: side
        }}
      />
    </div>
  );
};



class ConditionInput extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      left: {},
      right: {},
        op: ""
    };
    this.handleInputChange = this.handleInputChange.bind(this);

    this.handleLeft = this.handleLeft.bind(this);
    this.handleRight = this.handleRight.bind(this);
  }

  handleInputChange(event) {
    const target = event.target;
    const value = target.type === "checkbox" ? target.checked : target.value;
    const name = target.name;
    name !== "left" && name !== "right" ?
        this.setState({
          [name]: value
        }):
        this.setState({
            [name]: {"value": value}
        });

    console.log(this.state);
  }
  handleLeft(data) {
    this.setState({
      left: data
    });
    console.log(this.state);
  }
  handleRight(data) {
      if (typeof(data) === "string") {
          this.setState({
              right: {"value": data}
          });
      }
      else {
          this.setState({
              right: data
          });
      };
  }
  render() {
    const { classes } = this.props;
    const opselect = <div>
        <FormControl
            fullWidth
            className={classes.selectFormControl}>
            <InputLabel
                htmlFor="simple-select"
                className={classes.selectLabel}>
                Operation
            </InputLabel>
        <Select
            MenuProps={{
                className: classes.selectMenu
            }}
            classes={{
                select: classes.select
            }}
            autoWidth
            value={this.state.op != "" ? this.state.op: "Operation"}
            onChange={event => this.handleInputChange(event)}
            inputProps={{
                name: "op",
                id: "op"
            }}>
            <MenuItem
                disabled
                value={""}
                classes={{
                    root: classes.selectMenuItem
                }}>
                Operation
            </MenuItem>
            {opList.map(op => {
                    return (
                        <MenuItem
                            classes={{
                                root: classes.selectMenuItem,
                                selected: classes.selectMenuItemSelected
                            }}
                            value={op}>
                            {op}
                        </MenuItem>
                    )
                })}
        </Select>
        </FormControl>
    </div>;
    return (
      <div >
          {console.log(this.state)}
          <Tabs
              title="Tasks:"
              headerColor="primary"
              tabs={[
                  {
                      tabName: "Indicator vs Indicator",
                      tabContent: (
                          <GridContainer spacing={16} justify={"center"}>
                              <GridItem xs={5}>
                                  <Operand callback={this.handleLeft} />
                              </GridItem>
                              <GridItem xs={2}>
                                  {opselect}
                              </GridItem>
                              <GridItem xs={5}>
                                  <Operand callback={this.handleRight} />
                              </GridItem>
                              <Button
                                  onClick={() => {
                                      this.props.addCondition(this.state);
                                  }}
                              >
                                  save strategy
                              </Button>
                          </GridContainer>
                      )
                  },
                  {
                      tabName: "Indicator vs Number",
                      tabContent: (
                          <GridContainer spacing={16} justify={"center"}>
                              <GridItem xs={5}>
                                  <Operand callback={this.handleLeft} />
                              </GridItem>
                              <GridItem xs={2}>
                                  {opselect}
                              </GridItem>
                              <GridItem xs={5}>
                                  {indicatorInput("right", "Number", this.handleInputChange)}
                              </GridItem>
                              <Button
                                  onClick={() => {
                                      this.props.addCondition(this.state);
                                  }}
                              >
                                  save strategy
                              </Button>
                          </GridContainer>
                      )
                  },
                  {
                      tabName: "Indicator vs Price",
                      tabContent: (
                          <GridContainer spacing={16} justify={"center"} style={{ textAlign: "center" }}>
                              <GridItem xs={5}>
                                  <Operand callback={this.handleLeft} />
                              </GridItem>
                              <GridItem xs={2}>
                                  {opselect}
                              </GridItem>
                              <GridItem xs={5}>
                                  <CustomInput
                                      labelText="Price"
                                      id="price"
                                      formControlProps={{
                                          fullWidth: true
                                      }}
                                      inputProps={{
                                          disabled: true
                                      }}
                                  />
                              </GridItem>
                              <Button
                                  onClick={() => {
                                      this.props.addCondition(this.state);
                                      this.handleRight("price");
                                  }}
                              >
                                  save strategy
                              </Button>
                          </GridContainer>
                      )
                  },
                  {
                      tabName: "Candlestick Patterns",
                      tabContent: (
                          <GridContainer spacing={16} justify={"center"} style={{ textAlign: "center" }}>
                              <GridItem xs={4}>
                                  <FormControl
                                      fullWidth
                                      className={classes.selectFormControl}>
                                      <InputLabel
                                          htmlFor="left"
                                          className={classes.selectLabel}>
                                          Candlestick Pattern:
                                      </InputLabel>
                                  <Select
                                      MenuProps={{
                                          className: classes.selectMenu
                                      }}
                                      classes={{
                                          select: classes.select
                                      }}
                                      autoWidth
                                      value={
                                          PATTERNS.includes(this.state.left.value) ? this.state.left.value: ""
                                      }
                                      onChange={event => this.handleInputChange(event)}
                                      inputProps={{
                                          name: "left",
                                          id: "left"
                                      }}>
                                      <MenuItem
                                          disabled
                                          value={""}
                                          classes={{
                                              root: classes.selectMenuItem
                                          }}>
                                          Candle Patterns
                                      </MenuItem>
                                      {
                                        PATTERNS.map(pattern => {
                                            return (
                                                <MenuItem
                                                    classes={{
                                                        root: classes.selectMenuItem,
                                                        selected: classes.selectMenuItemSelected
                                                    }}
                                                    value={pattern}>
                                                    {pattern}
                                                </MenuItem>
                                            )
                                        })
                                      }
                                  </Select>
                                  </FormControl>
                              </GridItem>
                              <GridItem xs={2}>
                                  <InputLabel
                                      htmlFor="Inverse"
                                      className={classes.selectLabel}>
                                      Inverse:
                                  </InputLabel>
                                  <Checkbox
                                      checked={this.state.inverse}
                                      onChange={event => this.handleInputChange(event)}
                                      value="inverse"
                                      name={"inverse"}
                                  />
                              </GridItem>
                              <br/>
                              <Button
                                  onClick={() => {
                                      this.props.addCondition(this.state);
                                  }}
                              >
                                  save strategy
                              </Button>
                          </GridContainer>
                      )
                  },
              ]}
          />

      </div>
    );
  }
}

export default withStyles(extendedFormsStyle)(ConditionInput);
