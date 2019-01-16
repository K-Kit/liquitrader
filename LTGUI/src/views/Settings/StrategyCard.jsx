import FormControlLabel from "@material-ui/core/FormControlLabel";
import Switch from "@material-ui/core/Switch";
import React from "react";
import GridItem from "components/Grid/GridItem";
import CustomInput from "components/CustomInput/CustomInput";
import GridContainer from "components/Grid/GridContainer";
import Button from "components/CustomButtons/Button";
import Card from "components/Card/Card";
import IconButton from "@material-ui/core/IconButton";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import classnames from "classnames";
import Collapse from "@material-ui/core/Collapse";
import withStyles from "@material-ui/core/styles/withStyles";
import Close from "@material-ui/icons/Close";
import Tooltip from "@material-ui/core/Tooltip";
import Edit from "@material-ui/icons/Edit";

import { PATTERNS } from "views/Settings/data/Indicators.jsx";

const styles = theme => ({
  card: {
    maxWidth: 400
  },
  media: {
    height: 0,
    paddingTop: "56.25%" // 16:9
  },
  actions: {
    display: "flex"
  },
  expand: {
    transform: "rotate(0deg)",
    transition: theme.transitions.create("transform", {
      duration: theme.transitions.duration.shortest
    }),
    marginLeft: "auto",
    [theme.breakpoints.up("sm")]: {
      marginRight: -8
    }
  },
  expandOpen: {
    transform: "rotate(180deg)"
  },
  avatar: {
    backgroundColor: "red[500]"
  }
});

const FIELDS = {
  buy: [
    ["buy_value", "Buy Value"],
    ["min_volume", "Minimum Volume"],
    ["trailing %", "Trailing Value (%)"],
    ["min_price", "Minimum Price"]
  ],
  sell: [
    ["sell_value", "Sell Value"],
    ["min_volume", "Minimum Volume"],
    ["trailing %", "Trailing Value (%)"]
  ],
  dca: [
    ["min_volume", "Minimum Volume"],
    ["trailing %", "Trailing Value (%)"],
    ["min_price", "Minimum Price"],
    ["max_dca_level", "Max DCA level"]
  ]
};

class StrategyCard extends React.Component {
  constructor(props) {
    super(props);
    this.state = { expanded: false };
    this.handleInputChange = this.handleInputChange.bind(this);
  }

  handleInputChange(event) {
    const target = event.target;
    const value = target.type === "checkbox" ? target.checked : target.value;
    const name = target.name;
    console.log(this.state);
    this.setState({
      [name]: value
    });
  }
  handleExpandClick = () => {
    this.setState(state => ({ expanded: !state.expanded }));
  };

  render() {
    const { classes } = this.props;
    let props = this.props;
    let strategy = props.strategy;
    let updateTextField = props.updateTextField;
    let removeCondition = props.removeCondition;
    let handleOpen = props.handleOpen;
    let removeStrategy = props.removeStrategy;
    let removeDCALvl = props.removeDCALvl;
    let editCondition = props.editCondition;
    let editDCALevel = props.editDCALevel;
    let addDCALevel = props.addDCALevel;
    let id = props.id;
    let conditionID = 0;
    let fields = FIELDS[props.strategyType];
    return (
      <Card>
        <GridContainer justify="center">
          <GridItem xs={12}>
            <GridContainer justify={"center"}>
              {strategy.conditions.map(item => {
                {
                  item.id = conditionID++;
                }
                return (
                  <div>
                    <GridItem xs={12}>
                      {condition(
                        item,
                        () => removeCondition(id, item.id),
                        () => editCondition(id, item.id)
                      )}
                    </GridItem>
                  </div>
                );
              })}
              <Button color="info" onClick={() => handleOpen(id)}>
                add condition
              </Button>
            </GridContainer>
          </GridItem>

          <GridContainer justify="Center" style={{ textAlign: "center" }}>
            {fields.map(field => {
              return (
                <GridItem xs={6}>
                  <CustomInput
                    labelText={field[1]}
                    id={field[0]}
                    formControlProps={{
                      fullWidth: false
                    }}
                    inputProps={{
                      onChange: event => updateTextField(event, field[0], id),
                      value: strategy[field[0]]
                    }}
                  />
                </GridItem>
              );
            })}
          </GridContainer>
          <br />
          <br />
          {props.strategyType === "dca" ? (
            <GridContainer justify="center" style={{ textAlign: "center" }}>
              <GridContainer justify="center">
                <GridItem xs={2}>Level</GridItem>
                <GridItem xs={2}>Trigger</GridItem>
                <GridItem xs={2}>Percent</GridItem>
                <GridItem xs={2}>Add/Remove</GridItem>
              </GridContainer>

              {strategy.dca_strategy !== undefined ? Object.entries(strategy.dca_strategy).map(item => {
                return (
                  <GridContainer
                    justify={"center"}
                    style={{ textAlign: "center" }}
                  >
                    <GridItem xs={2}>
                      {" "}
                      <CustomInput
                        labelText={"trigger"}
                        id={"trigger"}
                        disabled
                        formControlProps={{
                          fullWidth: false
                        }}
                        inputProps={{
                          value: item[0],
                          disabled: true
                        }}
                      />{" "}
                    </GridItem>
                    <GridItem xs={2}>
                      {" "}
                      <CustomInput
                        labelText={"trigger"}
                        id={"trigger"}
                        formControlProps={{
                          fullWidth: false
                        }}
                        inputProps={{
                          onChange: event =>
                            editDCALevel(event, id, item[0], "trigger"),
                          value: item[1].trigger
                        }}
                      />{" "}
                    </GridItem>

                    <GridItem xs={2}>
                      <CustomInput
                        labelText={"percentage"}
                        id={"percentage"}
                        formControlProps={{
                          fullWidth: false
                        }}
                        inputProps={{
                          onChange: event =>
                            editDCALevel(event, id, item[0], "percentage"),
                          value: item[1].percentage
                        }}
                      />{" "}
                    </GridItem>
                    <GridItem xs={2}>
                      {" "}
                      <Button
                        color={"warning"}
                        onClick={() => removeDCALvl(id, item[0])}
                      >
                        {" "}
                        -{" "}
                      </Button>{" "}
                    </GridItem>
                  </GridContainer>
                );
              }): null}
              {/* add dca level */}
              <GridContainer justify={"center"} style={{ textAlign: "center" }}>
                <GridItem xs={2}>
                  {" "}
                  <CustomInput
                    labelText={"Level"}
                    id={"lvl"}
                    formControlProps={{
                      fullWidth: false
                    }}
                    inputProps={{
                      onChange: this.handleInputChange,
                      value: this.state.level,
                      name: "level"
                    }}
                  />{" "}
                </GridItem>
                <GridItem xs={2}>
                  {" "}
                  <CustomInput
                    labelText={"trigger"}
                    id={"trigger"}
                    formControlProps={{
                      fullWidth: false
                    }}
                    inputProps={{
                      onChange: this.handleInputChange,
                      value: this.state.trigger,
                      name: "trigger"
                    }}
                  />{" "}
                </GridItem>

                <GridItem xs={2}>
                  <CustomInput
                    labelText={"percentage"}
                    id={"percentage"}
                    formControlProps={{
                      fullWidth: false
                    }}
                    inputProps={{
                      onChange: this.handleInputChange,
                      value: this.state.percentage,
                      name: "percentage"
                    }}
                  />{" "}
                </GridItem>
                <GridItem xs={2}>
                  {" "}
                  <Button
                    color={"success"}
                    onClick={() => {
                      addDCALevel(
                        id,
                        this.state.level,
                        this.state.trigger,
                        this.state.percent
                      );
                      this.setState({
                        trigger: "",
                        percentage: "",
                        level: ""
                      });
                    }}
                  >
                    {" "}
                    +{" "}
                  </Button>{" "}
                </GridItem>
              </GridContainer>
            </GridContainer>
          ) : null}
        </GridContainer>
        <Button color={"warning"} onClick={() => removeStrategy(id)}>
          {" "}
          DELETE STRATEGY{" "}
        </Button>
      </Card>
    );
  }
}

const cardstyle = {
  background: "#904bff",
  textAlign: "center",
  justify: "center",
  padding: "10px 10px"
};
const condition = (props, remove, edit) => {
  return (
    <div>
      <Button style={cardstyle}>
        {props.left.timeframe} {props.left.value} {props.left.candle_period}{" "}
        &nbsp; {props.op} &nbsp;
        {props.right.timeframe} {props.right.value} {props.right.candle_period}{" "}
        {props.inverse ? "inverse" : null}
        <Tooltip id="tooltip-top" title="Edit" placement="top">
          <IconButton aria-label="Edit" onClick={edit}>
            <Edit />
          </IconButton>
        </Tooltip>
        <Tooltip id="tooltip-top-start" title="Remove" placement="top">
          <IconButton aria-label="Close" onClick={remove}>
            <Close />
          </IconButton>
        </Tooltip>
      </Button>
    </div>
  );
};
export default withStyles(styles)(StrategyCard);
