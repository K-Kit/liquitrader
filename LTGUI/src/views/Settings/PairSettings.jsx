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
import { fetchJSON } from "./StrategyList";
import { config_route, update_config } from "../../variables/global";
import { postJSON } from "./helpers/Helpers";
import Button from "../../../node_modules/@material-ui/core/Button/Button";
import Card from "../../components/Card/Card";
let exchanges = ["binance", "bittrex"];
let markets = ["BTC", "ETH", "BNB", "USDT"];

const fields = [["buy", "method"], ["buy", "value"], ["sell", "value"]];

class PairSettings extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.editPairSetting = this.editPairSetting.bind(this);
    this.handleWhitelist = this.handleWhitelist.bind(this);
    this.load = this.load.bind(this);
    this.save = this.save.bind(this);
  }
  removePair(pair, dcaLvl) {
    const state = { ...this.state };
    delete state[pair];
    this.setState(state);
  }
  editPairSetting(event, pair, side, field) {
    const target = event.target;
    const state = { ...this.state };
    state[pair][side][field] = target.value;
    this.setState(state);
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
  save() {
    let data = {
      section: "pair_specific",
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
    console.log(...config.pair_specific);
    this.setState({ ...config.pair_specific });
  }
  render() {
    const { classes } = this.props;
    return (
      <div>
        <GridContainer justify="center">
          {JSON.stringify(this.state)}
          {Object.entries(this.state).map(pair => {
            return (
              <Card>
                <GridContainer xs={12} justify={"center"}>
                  <GridItem xs={3}>
                    <CustomInput
                      inputProps={{
                        disabled: true,
                        value: pair[0]
                      }}
                    />
                  </GridItem>
                  {fields.map(field => {
                    return (
                      <GridItem xs={3}>
                        <CustomInput
                          labelText={field[0] + " " + field[1]}
                          id={"value"}
                          formControlProps={{
                            fullWidth: false
                          }}
                          inputProps={{
                            onChange: event =>
                              this.editPairSetting(
                                event,
                                pair[0],
                                field[0],
                                field[1]
                              ),
                            value: pair[1][field[0]][field[1]]
                          }}
                        />
                      </GridItem>
                    );
                  })}
                </GridContainer>
              </Card>
            );
          })}
        </GridContainer>
        <Button onClick={this.save} color={"primary"}>
          Save
        </Button>
        <GridContainer />
      </div>
    );
  }
}

export default withStyles(extendedFormsStyle)(PairSettings);
