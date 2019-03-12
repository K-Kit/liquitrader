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
import Card from "../../components/Card/Card";
let exchanges = ["binance", "bittrex"];
let markets = ["BTC", "ETH", "BNB", "USDT"];

const fields = [["buy", "method"], ["buy", "value"], ["sell", "value"]];
const editorfields = [["pair", "pair"], ...fields];

class PairSettings extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      editor: {
        pair: "",
        buy: {
          method: "modify",
          value: 1
        },
        sell: {
          value: 1
        }
      }
    };
    this.editPairSetting = this.editPairSetting.bind(this);
    this.removePair = this.removePair.bind(this);
    this.load = this.load.bind(this);
    this.save = this.save.bind(this);
    this.sendState = this.sendState.bind(this);
  }
  sendState() {
    return this.state;
  }
  removePair(pair) {
    console.log(this.state);
    const state = { ...this.state };
    delete state[pair];
    delete this.state[pair];
    console.log(state);
    this.setState(state);
  }
  editPairSetting(event, pair, side, field) {
    const target = event.target;
    const state = { ...this.state };
    state[pair][side][field] = target.value;
    this.setState(state);
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
          <Card>
            {Object.entries(this.state).map(pair => {
              if (pair[0] === "editor") {
                return null;
              }
              return (
                <div>
                  <GridContainer justify={"center"}>
                    <GridItem xs={2}>
                      <CustomInput
                        inputProps={{
                          disabled: true,
                          value: pair[0]
                        }}
                      />
                    </GridItem>
                    {fields.map(field => {
                      return (
                        <GridItem xs={2}>
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

                      <GridItem xs={2}>
                        <Button onClick={() => this.removePair(pair[0])}> Delete </Button>
                      </GridItem>
                  </GridContainer>
                </div>
              );
            })}
            <GridContainer justify={"center"}>
              {/*new pair editor*/}
              {editorfields.map(field => {
                return (
                  <GridItem xs={2}>
                    <CustomInput
                      labelText={
                        field[0] !== "pair" ? field[0] + " " + field[1] : "pair"
                      }
                      id={"value"}
                      formControlProps={{
                        fullWidth: false
                      }}
                      inputProps={{
                        onChange: event =>
                          this.handleEditor(event, field[0], field[1]),
                        value: this.state.editor[field[0]][field[1]]
                      }}
                    />
                  </GridItem>
                );
              })}
              <Button
                color={"success"}
                onClick={() => {
                  let editor = this.state.editor;
                  this.setState({
                    [editor.pair]: { buy: editor.buy, sell: editor.sell }
                  });
                }}
              >
                add pair setting
              </Button>
            </GridContainer>
            <Button onClick={this.save} color={"success"}>
              Save
            </Button>
          </Card>
        </GridContainer>

        <GridContainer />
      </div>
    );
  }
}

export default withStyles(extendedFormsStyle)(PairSettings);
