import React from "react";
// react component plugin for creating beatiful tags on an input
import TagsInput from "react-tagsinput";
// react plugin that creates slider

// @material-ui/core components
import withStyles from "@material-ui/core/styles/withStyles";
import FormControl from "@material-ui/core/FormControl";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import InputLabel from "@material-ui/core/InputLabel";
import Switch from "@material-ui/core/Switch";
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import Tooltip from "@material-ui/core/Tooltip";
import Info from "@material-ui/icons/Info";

// core components
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";

import CustomInput from "components/CustomInput/CustomInput.jsx";

import extendedFormsStyle from "assets/jss/material-dashboard-pro-react/views/extendedFormsStyle.jsx";
import { config_route, update_config } from "../../variables/global";
import { fetchJSON, postJSON } from "../helpers/Helpers";
import Button from "../../../node_modules/@material-ui/core/Button/Button";
let exchanges = ["binance", "bittrex"];
let markets = ["BTC", "ETH", "BNB", "USDT"];

const fields = [
  ["host", "Host"],
  ["port", "Port"],
  ["sell_only_mode", "Sell Only Mode"],
  ["trading_enabled", "Trading Enabled"],
  ["timezone", "Timezone"],
  ["starting_balance", "Starting Balance"],
  ["start_delay", "Start Delay"]
];

class GeneralSettings extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      exchange: "binance",
      paper_trading: true,
      starting_balance: 3,
      market: "ETH",
      timezone: "US/Pacific",
      start_delay: 0,
      host: window.location.hostname,
      port: window.location.port,
      use_ssl: false,
      sell_only_mode: false,
      trading_enabled: true
    };
    this.handleBlacklist = this.handleBlacklist.bind(this);
    this.handleWhitelist = this.handleWhitelist.bind(this);
    this.load = this.load.bind(this);
    this.save = this.save.bind(this);
    this.sendState = this.sendState.bind(this);
  }
  sendState() {
    return this.state;
  }
  handleSimple = event => {
    this.setState({ [event.target.name]: event.target.value });
    console.log(this.state.exchange);
  };
  handleExchange = event => {
    this.setState({ [event.target.name]: event.target.value });
  };
  handleMultiple = event => {
    this.setState({ multipleSelect: event.target.value });
  };
  handleChange = name => event => {
    this.setState({ [name]: event.target.value });
    console.log(this.state);
  };
  handleBlacklist(regularTags) {
    this.setState({ blacklist: regularTags });
  }
  handleWhitelist(regularTags) {
    this.setState({ whitelist: regularTags });
  }
  change(event, stateName) {
    this.setState({ [stateName]: event.target.value });
  }
  save() {
    let data = {
      section: "general",
      data: { ...this.state }
    };
    console.log(JSON.stringify(data), data);
    postJSON(update_config, data);
  }
  componentWillMount() {
    // This request takes longer, so prioritize it
    fetchJSON(config_route, this.load);
  }
  load(config) {
    this.setState({ ...config.global_trade });
  }
  render() {
    const { classes } = this.props;
    return (
      <div>
        <GridContainer justify="center">
          <GridItem xs={12} sm={8} md={6}>
            <GridContainer justify="center">
              <legend>Choose your Exchange</legend>
              <GridItem xs={12} sm={10} md={12} lg={12}>
                <FormControl fullWidth className={classes.selectFormControl}>
                  <InputLabel
                    htmlFor="exchange"
                    className={classes.selectLabel}
                  >
                    Choose Exchange
                  </InputLabel>
                  <Select
                    MenuProps={{
                      className: classes.selectMenu
                    }}
                    classes={{
                      select: classes.select
                    }}
                    value={this.state.exchange}
                    onChange={this.handleSimple}
                    inputProps={{
                      name: "exchange",
                      id: "exchange"
                    }}
                  >
                    <MenuItem
                      disabled
                      classes={{
                        root: classes.selectMenuItem
                      }}
                    >
                      Choose your market
                    </MenuItem>
                    {exchanges.map(exchange => {
                      return (
                        <MenuItem
                          classes={{
                            root: classes.selectMenuItem,
                            selected: classes.selectMenuItemSelected
                          }}
                          value={exchange}
                        >
                          {exchange.toUpperCase()}
                        </MenuItem>
                      );
                    })}
                  </Select>
                </FormControl>
              </GridItem>
            </GridContainer>
            <br />
            <br />
          </GridItem>

          <GridItem xs={12} sm={8} md={6}>
            <GridContainer justify="center">
              <legend>Choose your Market</legend>
              <br />
              <Tooltip
                onClose={this.handleTooltipClose}
                onOpen={this.handleTooltipOpen}
                open={this.state.open}
                title="this is the asset you trade against ex. ADA/BTC, market = BTC"
              >
                <Info />
              </Tooltip>
              <GridItem xs={12} sm={10} md={12} lg={12}>
                <FormControl fullWidth className={classes.selectFormControl}>
                  <InputLabel
                    htmlFor="market-select"
                    className={classes.selectLabel}
                  >
                    Choose Market
                  </InputLabel>
                  <Select
                    MenuProps={{
                      className: classes.selectMenu
                    }}
                    classes={{
                      select: classes.select
                    }}
                    value={this.state.market}
                    onChange={this.handleSimple}
                    inputProps={{
                      name: "market",
                      id: "market-select"
                    }}
                  >
                    <MenuItem
                      disabled
                      classes={{
                        root: classes.selectMenuItem
                      }}
                    >
                      Choose your market
                    </MenuItem>

                    {markets.map(market => {
                      return (
                        <MenuItem
                          classes={{
                            root: classes.selectMenuItem,
                            selected: classes.selectMenuItemSelected
                          }}
                          value={market}
                        >
                          {market}
                        </MenuItem>
                      );
                    })}
                  </Select>
                </FormControl>
              </GridItem>
            </GridContainer>
            <br />
            <br />
          </GridItem>

          <GridItem xs={12} sm={10} md={6}>
            <br />
            <GridContainer justify={"center"}>
              <br />
              {/*<Tooltip*/}
              {/*onClose={this.handleTooltipClose}*/}
              {/*onOpen={this.handleTooltipOpen}*/}
              {/*open={this.state.open}*/}
              {/*title="No purchases or sales will be made on your exchange account"*/}
              {/*>*/}
              {/*<legend>*/}
              {/*Enable Paper Trading <small>(simulated trading)</small>*/}
              {/*</legend>*/}
              {/*</Tooltip>*/}
              {fields.map(field => {
                return (
                  <GridItem xs={4} md={2}>
                    <CustomInput
                      labelText={field[1]}
                      id={field[0]}
                      formControlProps={{
                        fullWidth: false
                      }}
                      inputProps={{
                        onChange: this.handleSimple,
                        value: this.state[field[0]],
                        name: field[0]
                      }}
                    />
                  </GridItem>
                );
              })}
              <br />
              <br />
              <InputLabel
                    htmlFor="market-select"
                    className={classes.selectLabel}
                  >
                    Mode: &thinsp;&thinsp;
                  </InputLabel>
              <Select
                MenuProps={{
                  className: classes.selectMenu
                }}
                classes={{
                  select: classes.select
                }}
                autoWidth
                value={this.state.paper_trading}
                onChange={this.handleChange("paper_trading")}
                inputProps={{
                  name: "Mode",
                  id: "Mode"
                }}
              >
                <MenuItem
                  classes={{
                    root: classes.selectMenuItem,
                    selected: classes.selectMenuItemSelected
                  }}
                  value={false}
                >
                  Live
                </MenuItem>
                <MenuItem
                  classes={{
                    root: classes.selectMenuItem,
                    selected: classes.selectMenuItemSelected
                  }}
                  value={true}
                >
                  Simulated
                </MenuItem>
              </Select>
              {/*<FormControlLabel*/}
              {/*control={*/}
              {/*<Switch*/}
              {/*checked={!this.state.paper_trading}*/}
              {/*onChange={this.handleChange("paper_trading")}*/}
              {/*value={this.state.paper_trading}*/}
              {/*classes={{*/}
              {/*switchBase: classes.switchBase,*/}
              {/*checked: classes.switchChecked,*/}
              {/*icon: classes.switchIcon,*/}
              {/*iconChecked: classes.switchIconChecked,*/}
              {/*bar: classes.switchBar*/}
              {/*}}*/}
              {/*/>*/}
              {/*}*/}
              {/*classes={{*/}
              {/*label: classes.label*/}
              {/*}}*/}
              {/*label="Paper / Live Trading (left = paper trading, right(checked) = live"*/}
              {/*/>*/}
            </GridContainer>
          </GridItem>

          <br />
        </GridContainer>
        <Button onClick={this.save} color={"primary"}>
          Save
        </Button>
        <GridContainer />
      </div>
    );
  }
}

export default withStyles(extendedFormsStyle)(GeneralSettings);
