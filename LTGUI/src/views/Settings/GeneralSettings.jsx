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
import Tooltip from '@material-ui/core/Tooltip';
import Info from "@material-ui/icons/Info";


// core components
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";

import CustomInput from "components/CustomInput/CustomInput.jsx";

import extendedFormsStyle from "assets/jss/material-dashboard-pro-react/views/extendedFormsStyle.jsx";
let exchanges = ["binance", "bittrex"];
let markets = ["BTC", "ETH", "BNB", "USDT"];
class GeneralSettings extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      checkedA: true,
      checkedB: false,
      marketSelect: "",
      exchangeSelect: "",
      multipleSelect: [],
      blacklist: [],
      whitelist: []
    };
    this.handleBlacklist = this.handleBlacklist.bind(this);
    this.handleWhitelist = this.handleWhitelist.bind(this);
  }
  handleSimple = event => {
    this.setState({ [event.target.name]: event.target.value });
  };
  handleExchange = event => {
    this.setState({ [event.target.name]: event.target.value });
  };
  handleMultiple = event => {
    this.setState({ multipleSelect: event.target.value });
  };
  handleChange = name => event => {
    this.setState({ [name]: event.target.checked });
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
                    htmlFor="exchange-select"
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
                    value={this.state.exchangeSelect}
                    onChange={this.handleExchange}
                    inputProps={{
                      name: "exchangeSelect",
                      id: "exchange-select"
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
                          {exchange}
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
              <br/>
              <Tooltip
              onClose={this.handleTooltipClose}
              onOpen={this.handleTooltipOpen}
              open={this.state.open}
              title="this is the asset you trade against ex. ADA/BTC, market = BTC"
              >
              <Info/>
              </Tooltip>
              <GridItem xs={12} sm={10} md={12} lg={12} >
                <FormControl
                  fullWidth
                  className={classes.selectFormControl}
                >
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
                    value={this.state.marketSelect}
                    onChange={this.handleSimple}
                    inputProps={{
                      name: "marketSelect",
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

          <GridItem xs={12} md={6}>
            <CustomInput
              labelText="Minimum Buy Balance"
              id="min_buy_balance"
              formControlProps={{
                fullWidth: true
              }}
              inputProps={{
                type: "min_buy_balance",
                onChange: event => this.change(event, "min_buy_balance")
              }}
            />
          </GridItem>

          <GridItem xs={12} md={6}>
            <CustomInput
              labelText="Max Pairs"
              id="max_pairs"
              formControlProps={{
                fullWidth: true
              }}
              inputProps={{
                onChange: event => this.change(event, "maxPairs"),
                type: "maxPairs"
              }}
            />
          </GridItem>

          <GridItem xs={12} sm={10} md={6}>
            <br />
            <GridContainer justify={"center"}>
              <br />
              <Tooltip
                onClose={this.handleTooltipClose}
                onOpen={this.handleTooltipOpen}
                open={this.state.open}
                title="No purchases or sales will be made on your exchange account"
              >
                <legend>
                  Enable Paper Trading <small>(simulated trading)</small>
                </legend>
              </Tooltip>
              <br />
              <FormControlLabel
                control={
                  <Switch
                    checked={this.state.checkedA}
                    onChange={this.handleChange("checkedA")}
                    value="checkedA"
                    classes={{
                      switchBase: classes.switchBase,
                      checked: classes.switchChecked,
                      icon: classes.switchIcon,
                      iconChecked: classes.switchIconChecked,
                      bar: classes.switchBar
                    }}
                  />
                }
                classes={{
                  label: classes.label
                }}
                label="Paper Trading (left = live trading, right(checked) = paper"
              />
            </GridContainer>
          </GridItem>
          <br />
        </GridContainer>
        <GridContainer />
      </div>
    );
  }
}

export default withStyles(extendedFormsStyle)(GeneralSettings);
