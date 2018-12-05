import React from "react";

// @material-ui/core components
import withStyles from "@material-ui/core/styles/withStyles";

// core components
import CustomInput from "components/CustomInput/CustomInput.jsx";
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";
import Info from "@material-ui/icons/Info";
import customSelectStyle from "assets/jss/material-dashboard-pro-react/customSelectStyle.jsx";
import Tooltip from "@material-ui/core/Tooltip";

// #import fontawesome

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faLessThanEqual } from "@fortawesome/free-solid-svg-icons";
import FormLabel from "@material-ui/core/FormLabel";
import regularFormsStyle from "../../assets/jss/material-dashboard-pro-react/views/regularFormsStyle";
import { fetchJSON } from "./StrategyList";
import { config_route } from "../../variables/global";
import Button from "@material-ui/core/Button/Button";
import TagsInput from "react-tagsinput";

const style = theme => ({
  infoText: {
    fontWeight: "300",
    margin: "10px 0 30px",
    textAlign: "center"
  },
  inputAdornmentIcon: {
    color: "#555"
  },
  choiche: {
    textAlign: "center",
    cursor: "pointer",
    marginTop: "20px"
  },
  ...customSelectStyle
});

const less_than_icon = () => {
  return (
    <GridItem xs={1}>
      <FontAwesomeIcon icon={faLessThanEqual} />
    </GridItem>
  );
};
const marketConditions = [
  {
    title: "Pair 24h Change",
    accesor: "_change"
  },
  {
    title: "ETH 1h Change",
    accesor: "_1h_quote_change"
  },
  {
    title: "ETH 24h Change",
    accesor: "_24h_quote_change"
  },

  {
    title: "Market 24h Change",
    accesor: "_24h_quote_change"
  }
];

let fields = [
  ["max_pairs", "Maximum Pairs"],
  ["dca_timeout", "DCA Timeout"],
  ["max_spread", "Maximum Spread"],
  ["min_buy_balance", "Buy Maintain Balance"],
  ["dca_min_buy_balance", "DCA Maintain Balance"]
];

class GlobalTrade extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      bear_override: {},
      blacklist: ["TRIG/ETH", "BCN/ETH", "CHAT/ETH", "ICN/ETH"],
      bull_override: {},
      dca_min_buy_balance: "",
      dca_timeout: 60,
      max_1h_quote_change: 0,
      max_24h_market_change: 0,
      max_24h_quote_change: 0,
      min_1h_quote_change: 0,
      min_24h_market_change: 0,
      min_24h_quote_change: 0,
      max_change: 0,
      max_pairs: 10,
      max_spread: 1,
      min_available_volume: 0,
      min_buy_balance: "",
      min_change: 0,
      whitelist: [] // ["ALL"] to allow all pairs or comma seperated list of strs
    };
    this.updateTextField = this.updateTextField.bind(this);
    this.load = this.load.bind(this);
    this.save = this.save.bind(this);
  }
  sendState() {
    return this.state;
  }
  handleSimple = event => {
    this.setState({ [event.target.name]: event.target.value });
  };
  isValidated() {
    return true;
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
  save() {
    let data = {
      section: "global_trade_conditions",
      data: { ...this.state, market_conditions: { ...this.state } }
    };
    console.log(JSON.stringify(data), data);
    // postJSON(update_config, data);
  }
  componentWillMount() {
    // This request takes longer, so prioritize it
    fetchJSON(config_route, this.load);
  }
  load(config) {
    this.setState({ ...config.global_trade, market: config.general });
  }
  render() {
    const { classes } = this.props;
    return (
      <div style={{ margin: "0 auto", textAlign: "center", flexGrow: "1" }}>
        <GridContainer style={{ margin: "0 auto", textAlign: "center" }}>
          <GridContainer
            style={{ textAlign: "center" }}
            justify="center"
            spacing={0}
          >
            <GridItem xs={12}>
              <h3> Global Trade Settings </h3>
            </GridItem>
            <br />
            <br />
            {fields.map(field => {
              return (
                <GridItem>
                  <CustomInput
                    labelText={field[1]}
                    id={field[0]}
                    formControlProps={{
                      fullWidth: false
                    }}
                    inputProps={{
                      onChange: event => this.updateTextField(event, field[0]),
                      value: this.state[field[0]]
                    }}
                  />
                </GridItem>
              );
            })}
          </GridContainer>
          <GridContainer
            justify={"center"}
            style={{ margin: "0 auto", textAlign: "center" }}
          >
            {marketConditions.map(condition => {
              return (
                <GridItem xs={12} md={8}>
                  <GridContainer
                    justify={"center"}
                    style={{ margin: "0 auto", textAlign: "center" }}
                  >
                    <GridItem xs={2} lg={1}>
                      <CustomInput
                        formControlProps={{
                          fullWidth: false
                        }}
                        inputProps={{
                          onChange: event =>
                            this.updateTextField(event, condition.accesor),
                          value: this.state["min" + condition.accesor]
                        }}
                      />
                    </GridItem>

                    <GridItem xs={12} md={8} lg={3}>
                      <FormLabel className={classes.labelHorizontal}>
                        {less_than_icon()}
                        &nbsp; &nbsp;
                        {condition.title}
                        &nbsp;
                        {less_than_icon()}
                      </FormLabel>
                    </GridItem>
                    <GridItem xs={2} lg={1}>
                      <CustomInput
                        labelText=""
                        id={condition.name}
                        formControlProps={{
                          fullWidth: false
                        }}
                        inputProps={{
                          onChange: event =>
                            this.updateTextField(event, condition.accesor),
                          value: this.state["max" + condition.accesor]
                        }}
                      />
                    </GridItem>
                  </GridContainer>
                </GridItem>
              );
            })}
          </GridContainer>
          <GridContainer>
            <GridItem xs={12} md={6}>
              <FormLabel className={classes.labelHorizontal}>
                {" "}
                Whitelist
              </FormLabel>
              <TagsInput
                value={this.state.whitelist}
                onChange={this.handleTags}
                tagProps={{ className: "react-tagsinput-tag info" }}
              />
            </GridItem>
            <GridItem>
              <FormLabel className={classes.labelHorizontal}>
                {" "}
                Blacklist
              </FormLabel>
              <TagsInput
                value={this.state.blacklist}
                onChange={this.handleTags}
                tagProps={{ className: "react-tagsinput-tag warning" }}
              />
            </GridItem>
            <Button onClick={this.save} color={"primary"}>
              Save
            </Button>
          </GridContainer>
        </GridContainer>
      </div>
    );
  }
}

export default withStyles(regularFormsStyle)(GlobalTrade);
