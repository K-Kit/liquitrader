import React from "react";

// @material-ui/core components
import withStyles from "@material-ui/core/styles/withStyles";
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import InputLabel from "@material-ui/core/InputLabel";
import FormControl from "@material-ui/core/FormControl";

// core components
import CustomInput from "components/CustomInput/CustomInput.jsx";
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";
import NestedGrid from "components/Grid/NestedGrid.jsx";
import ArrowBack from "@material-ui/icons/ArrowBack";
import Info from "@material-ui/icons/Info";
import customSelectStyle from "assets/jss/material-dashboard-pro-react/customSelectStyle.jsx";
import Tooltip from "@material-ui/core/Tooltip";

// #import fontawesome

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faLessThanEqual } from "@fortawesome/free-solid-svg-icons";
import { faEthereum } from "@fortawesome/free-brands-svg-icons";

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

const less_than_label = (name, form_to_right) => {
  return (
    <div>
      <GridItem xs={12}>
        <GridContainer>
          <GridItem xs={2}>
            <CustomInput
              labelText=""
              id=""
              formControlProps={{
                fullWidth: false
              }}
            />
          </GridItem>

          {less_than_icon()}

          <GridItem xs={4}>{name}</GridItem>

          {less_than_icon()}

          <GridItem xs={2}>
            <CustomInput
              labelText=""
              id=""
              formControlProps={{
                fullWidth: false
              }}
            />
          </GridItem>
        </GridContainer>
      </GridItem>
    </div>
  );
};

class GlobalTrade extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      simpleSelect: "",
      desgin: false,
      code: false,
      develop: false
    };
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
  render() {
    return (
      <div style={{ margin: "0 auto", textAlign: "center", flexGrow: "1" }}>
        <GridContainer
          justify="center"
          style={{ margin: "0 auto", textAlign: "center" }}
        >
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

            {less_than_label("Pair 24h Change")}

            <GridItem xs={6} sm={3}>
              <CustomInput
                labelText="Minimum Buy Balance"
                id=""
                formControlProps={{
                  fullWidth: false
                }}
              />
            </GridItem>
            <Tooltip
              onClose={this.handleTooltipClose}
              onOpen={this.handleTooltipOpen}
              open={this.state.open}
              title="Lowest balance the bot will look to open new positions (does not apply to DCA)"
            >
              <Info />
            </Tooltip>
          </GridContainer>
          <GridContainer
            style={{ textAlign: "center" }}
            justify="center"
            spacing={12}
          >
            {less_than_label("ETH 1h Change")}

            <GridItem xs={3}>
              <CustomInput
                labelText="Max Pairs"
                id=""
                formControlProps={{
                  fullWidth: false
                }}
              />
            </GridItem>
            <Tooltip
              onClose={this.handleTooltipClose}
              onOpen={this.handleTooltipOpen}
              open={this.state.open}
              title="Maximum number of trading pairs at any one time."
            >
              <Info />
            </Tooltip>
          </GridContainer>
          <GridContainer
            style={{ textAlign: "center" }}
            justify="center"
            spacing={12}
          >
            {less_than_label("ETH 24h Change")}

            <GridItem xs={3}>
              <CustomInput
                labelText="DCA Timeout"
                id=""
                formControlProps={{
                  fullWidth: false
                }}
              />
            </GridItem>
            <Tooltip
              onClose={this.handleTooltipClose}
              onOpen={this.handleTooltipOpen}
              open={this.state.open}
              title="Time until bot will repurchase a pair."
            >
              <Info />
            </Tooltip>
          </GridContainer>
          <GridContainer
            style={{ textAlign: "center" }}
            justify="center"
            spacing={12}
          >
            {less_than_label("Market 24h Change")}

            <GridItem xs={3}>
              <CustomInput
                labelText="Max Spread"
                id=""
                formControlProps={{
                  fullWidth: false
                }}
              />
            </GridItem>
            <Tooltip
              onClose={this.handleTooltipClose}
              onOpen={this.handleTooltipOpen}
              open={this.state.open}
              title="Max gap between bid and ask."
            >
              <Info />
            </Tooltip>
          </GridContainer>
        </GridContainer>
      </div>
    );
  }
}

export default withStyles(style)(GlobalTrade);
