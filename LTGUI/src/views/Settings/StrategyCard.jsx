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
    ["min_price", "Minimum Price"]
  ]
};

class StrategyCard extends React.Component {
  state = { expanded: false };

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
                      {condition(item, () => removeCondition(id, item.id))}
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
          {props.strategyType === "dca" ? (
            <div>
              <GridContainer justify="center" style={{ textAlign: "center" }}>
                <GridItem xs={12}>
                  DCA
                  <IconButton
                    className={classnames(classes.expand, {
                      [classes.expandOpen]: this.state.expanded
                    })}
                    onClick={this.handleExpandClick}
                    aria-expanded={this.state.expanded}
                    aria-label="Show more"
                  >
                    <ExpandMoreIcon />
                  </IconButton>
                </GridItem>
              </GridContainer>
              <Collapse in={this.state.expanded} timeout="auto" unmountOnExit>
                <GridContainer justify="center">
                  <GridItem xs={3}>Level</GridItem>
                  <GridItem xs={3}>Trigger</GridItem>
                  <GridItem xs={3}>Percent</GridItem>
                </GridContainer>

                <GridContainer justify="center">
                  <GridItem xs={3}>
                    <p style={{ padding: "20px" }}> Default </p>
                  </GridItem>
                  <GridItem xs={3}>
                    <CustomInput
                      labelText=""
                      id=""
                      formControlProps={{
                        fullWidth: false
                      }}
                    />
                  </GridItem>
                  <GridItem xs={3}>
                    <CustomInput
                      labelText="%"
                      id=""
                      formControlProps={{
                        fullWidth: false
                      }}
                    />
                  </GridItem>
                </GridContainer>

                <GridContainer justify="center">
                  <GridItem xs={3}>
                    <CustomInput
                      labelText=""
                      id=""
                      formControlProps={{
                        fullWidth: false
                      }}
                    />
                  </GridItem>
                  <GridItem xs={3}>
                    <CustomInput
                      labelText=""
                      id=""
                      formControlProps={{
                        fullWidth: false
                      }}
                    />
                  </GridItem>
                  <GridItem xs={3}>
                    <CustomInput
                      labelText="%"
                      id=""
                      formControlProps={{
                        fullWidth: false
                      }}
                    />
                  </GridItem>
                </GridContainer>

                <GridContainer justify="center">
                  <GridItem xs={3}>
                    <CustomInput
                      labelText=""
                      id=""
                      formControlProps={{
                        fullWidth: false
                      }}
                    />
                  </GridItem>
                  <GridItem xs={3}>
                    <CustomInput
                      labelText=""
                      id=""
                      formControlProps={{
                        fullWidth: false
                      }}
                    />
                  </GridItem>
                  <GridItem xs={3}>
                    <CustomInput
                      labelText="%"
                      id=""
                      formControlProps={{
                        fullWidth: false
                      }}
                    />
                  </GridItem>
                </GridContainer>

                <GridContainer justify="center">
                  <GridItem xs={3}>
                    <CustomInput
                      labelText=""
                      id=""
                      formControlProps={{
                        fullWidth: false
                      }}
                    />
                  </GridItem>
                  <GridItem xs={3}>
                    <CustomInput
                      labelText=""
                      id=""
                      formControlProps={{
                        fullWidth: false
                      }}
                    />
                  </GridItem>
                  <GridItem xs={3}>
                    <CustomInput
                      labelText="%"
                      id=""
                      formControlProps={{
                        fullWidth: false
                      }}
                    />
                  </GridItem>
                </GridContainer>
              </Collapse>{" "}
            </div>
          ) : null}
        </GridContainer>
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
const condition = (props, remove) => {
  return (
    <div>
      <Button style={cardstyle}>
        {props.left.timeframe} {props.left.value} {props.left.candle_period}{" "}
        &nbsp; {props.op} &nbsp;
        {props.right.timeframe} {props.right.value} {props.right.candle_period}{" "}
        {props.inverse ? "inverse" : null}
        <Tooltip id="tooltip-top" title="Edit" placement="top">
          <IconButton aria-label="Edit">
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
