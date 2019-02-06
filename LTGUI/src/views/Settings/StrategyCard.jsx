import IconButton from "@material-ui/core/IconButton";
import withStyles from "@material-ui/core/styles/withStyles";
import Tooltip from "@material-ui/core/Tooltip";
import Close from "@material-ui/icons/Close";
import Delete from "@material-ui/icons/Delete";
import Save from "@material-ui/icons/Save";
import Edit from "@material-ui/icons/Edit";
import Card from "components/Card/Card";
import Button from "components/CustomButtons/Button";
import CustomInput from "components/CustomInput/CustomInput";
import GridContainer from "components/Grid/GridContainer";
import GridItem from "components/Grid/GridItem";
import React from "react";
import * as lt_colors from "variables/lt_colors";

const deleteButtonStyle = {
  position: "absolute",
  top: ".05em",
  right: ".15em",
  fontSize: "1.5em"
};

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
        {/* todo add are you sure modal for delete */}
        <IconButton
          style={deleteButtonStyle}
          aria-label="Delete"
          onClick={() => removeStrategy(id)}
        >
          <Close
            style={{
              fill: lt_colors.warning
            }}
          />
          <small
            style={{
              fontSize: ".5em",
              color: lt_colors.fontcolor
            }}
          >
            (delete)
          </small>
        </IconButton>
        <GridContainer
          justify="center"
          styles={{
            padding: "1em .2em"
          }}
        >
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
              <Button
                style={{
                  background: lt_colors.yetanotherblue
                }}
                onClick={() => handleOpen(id)}
              >
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

              {strategy.dca_strategy !== undefined
                ? Object.entries(strategy.dca_strategy).reverse().map(item => {
                    return (
                      <GridContainer
                        justify={"center"}
                        style={{ textAlign: "center" }}
                      >
                        <GridItem xs={2}>
                          {" "}

                          <CustomInput
                            labelText={"Level"}
                            id={"level"}
                            disabled
                            formControlProps={{
                              fullWidth: false
                            }}
                            inputProps={{
                              value: item[0],
                              disabled: true
                            }}
                          />
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
                        {item[0] != 'default' ? (
                          <Button
                            color={"warning"}
                            onClick={() => removeDCALvl(id, item[0])}
                          >
                            {" "}
                            -{" "}
                          </Button>):null}
                        </GridItem>
                      </GridContainer>
                    );
                  })
                : null}
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

        {/* <IconButton
          style={deleteButtonStyle}
          aria-label="Save"
          onClick={() => removeStrategy(id)}
        >
          <Save
            style={{
              fill: lt_colors.green
            }}
          />
        </IconButton> */}
      </Card>
    );
  }
}

const cardstyle = {
  background: lt_colors.purp,
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
