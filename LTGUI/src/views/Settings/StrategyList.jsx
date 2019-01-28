import React from "react";

// core components
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";
import {
  exampleBuyStrategies,
  exampleDCAStrategies
} from "views/Settings/data/ExampleStrategies.jsx";
import Button from "components/CustomButtons/Button";
import * as PropTypes from "prop-types";
import StrategyCard from "views/Settings/StrategyCard.jsx";
import Dialog from "@material-ui/core/Dialog";
import ConditionInput from "./ConditionInput";
import withStyles from "@material-ui/core/styles/withStyles";
import extendedFormsStyle from "assets/jss/material-dashboard-pro-react/views/extendedFormsStyle";
import Slide from "@material-ui/core/Slide";
import { config_route, update_config } from "variables/global";
import { fetchJSON, postJSON } from "views/helpers/Helpers.jsx";

function Transition(props) {
  return <Slide direction="down" {...props} />;
}
function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

const STRATEGYBASE = { conditions: [], dca_strategy: { default: {} } };

class StrategyList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      strategies: [],
      open: false,
      targetStrategy: 0,
      leftValue: {},
      rightValue: {},
      op: ""
    };
    this.updateTextField = this.updateTextField.bind(this);
    this.addCondition = this.addCondition.bind(this);
    this.addStrategy = this.addStrategy.bind(this);
    this.removeCondition = this.removeCondition.bind(this);
    this.removeStrategy = this.removeStrategy.bind(this);
    this.editCondition = this.editCondition.bind(this);
    this.handleOpen = this.handleOpen.bind(this);
    this.removeDCALevel = this.removeDCALevel.bind(this);
    this.editDCALevel = this.editDCALevel.bind(this);
    this.addDCALevel = this.addDCALevel.bind(this);
    this.load = this.load.bind(this);
    this.save = this.save.bind(this);
  }

  sendState() {
    return this.state;
  }

  updateTextField(event, name, id) {
    const target = event.target;
    const value = target.value;
    const strategies = [...this.state.strategies];
    strategies[id][name] = value;
    this.setState({
      strategies: strategies
    });
    console.log(this.state);
  }
  removeStrategy(id) {
    const strategies = [...this.state.strategies];
    strategies.splice(id, 1);
    this.setState({
      strategies: strategies
    });
  }
  removeDCALevel(strategyID, dcaLvl) {
    const strategies = [...this.state.strategies];

    console.log(strategies);
    delete strategies[strategyID].dca_strategy[dcaLvl];
    console.log(strategies[strategyID][dcaLvl], dcaLvl);
    this.setState({
      strategies: strategies
    });
  }
  editDCALevel(event, strategyID, dcaLvl, field) {
    const target = event.target;
    const strategies = [...this.state.strategies];
    console.log(strategies[strategyID].dca_strategy[dcaLvl][field]);
    strategies[strategyID].dca_strategy[dcaLvl][field] = target.value;

    console.log(strategies[strategyID].dca_strategy[dcaLvl][field]);
    this.setState({
      strategies: strategies
    });
  }
  addDCALevel(strategyID, dcaLvl, trigger, percent) {
    const strategies = [...this.state.strategies];
    console.log(strategies[strategyID].dca_strategy[dcaLvl]);
    strategies[strategyID].dca_strategy[dcaLvl] = {
      trigger: trigger,
      percentage: percent
    };

    console.log(strategies[strategyID].dca_strategy[dcaLvl]);
    this.setState({
      strategies: strategies
    });
  }
  addStrategy() {
    const strategies = [...this.state.strategies, { conditions: [], dca_strategy: { default: {} } }];
    this.setState({
      strategies: strategies
    });
  }
  removeCondition(strategyID, conditionID) {
    const strategies = [...this.state.strategies];
    const strategy = strategies[strategyID];
    console.log(conditionID);
    let conditions = [...strategy.conditions];
    conditions.splice(conditionID, 1);
    strategy.conditions = conditions;
    this.setState({
      strategies: strategies
    });
  }
  editCondition(strategyID, conditionID) {
    const strategies = [...this.state.strategies];
    const strategy = strategies[strategyID];
    let conditions = [...strategy.conditions];
    let condition = conditions[conditionID];
    this.setState({
      open: true,
      leftValue: condition.left,
      rightValue: condition.right,
      op: condition.op
    });
    this.removeCondition(strategyID, conditionID)
    console.log(this.state);
    console.log(condition);
  }
  addCondition(condition) {
    const strategies = [...this.state.strategies];
    const strategy = strategies[this.state.targetStrategy];
    strategy.conditions = [...strategy.conditions, condition];
    this.setState({
      strategies: strategies
    });
    this.handleClose();
  }
  handleOpen = id => {
    this.setState({
      open: true,
      targetStrategy: id
    });
  };

  handleClose = () => {
    this.setState({ open: false });
  };
  save() {
    let strategy_type =
      this.props.strategyType === "dca" ? "dca_buy" : this.props.strategyType;
    let data = {
      section: strategy_type + "_strategies",
      data: this.state.strategies
    };
    console.log(JSON.stringify(data), data);
    postJSON(update_config, data);
  }
  componentWillMount() {
    // This request takes longer, so prioritize it
    fetchJSON(config_route, this.load);
  }
  load(config) {
    let strategy_type =
      this.props.strategyType === "dca" ? "dca_buy" : this.props.strategyType;
    console.log(strategy_type, this);
    if (!this.isCancelled && config.status_code != 401) {
      try {
        this.setState({ strategies: config[strategy_type + "_strategies"] });
      } catch (e) {
        console.log(e);
        this.setState({ strategies: [] });
      }
    }
  }

  render() {
    const { classes } = this.props;
    let id = 0;
    return (
      <div>
        <Dialog
          classes={{
            root: classes.center,
            paper: classes.modal
          }}
          transition={Transition}
          open={this.state.open}
          onClose={this.handleClose}
        >
          <ConditionInput
            addCondition={this.addCondition}
            targetStrategy={this.state.targetStrategy}
            leftValue={this.state.leftValue}
            rightValue={this.state.rightValue}
            op={this.state.op}
          />
        </Dialog>
        <GridContainer justify="center">
          <legend>
            {" "}
            {capitalizeFirstLetter(this.props.strategyType)} Strategies{" "}
          </legend>
          <GridItem xs={12}>
            {this.state.strategies.map(strategy => {
              return (
                <div>
                  <StrategyCard
                    strategy={strategy}
                    id={id++}
                    updateTextField={this.updateTextField}
                    addCondition={this.addCondition}
                    handleOpen={this.handleOpen}
                    removeCondition={this.removeCondition}
                    editCondition={this.editCondition}
                    strategyType={this.props.strategyType}
                    removeStrategy={this.removeStrategy}
                    removeDCALvl={this.removeDCALevel}
                    editDCALevel={this.editDCALevel}
                    addDCALevel={this.addDCALevel}
                  />
                </div>
              );
            })}
          </GridItem>
          <Button
            style={{
              margin: "auto",
              color: "green",
              width: "98%",
              height: "200px",
              background: "transparent",
              border: "1px dashed"
            }}
            onClick={this.addStrategy}
          >
            add strategy
          </Button>
        </GridContainer>
        <Button onClick={this.save}>Save</Button>
      </div>
    );
  }
}

export default withStyles(extendedFormsStyle)(StrategyList);
