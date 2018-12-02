import React from "react";

// core components
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";
import Card from "components/Card/Card.jsx";
import CardHeader from "components/Card/CardHeader.jsx";
import CardBody from "components/Card/CardBody.jsx";

import Button from "../../../node_modules/@material-ui/core/Button/Button";
import * as PropTypes from "prop-types";
import StrategyList from "./StrategyList";


class SellStrategies extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      strategies: []
    };
    this.handleInputChange = this.handleInputChange.bind(this);
    this.save = this.save.bind(this);
  }
  handleInputChange(event) {
    const target = event.target;
    const value = target.type === "checkbox" ? target.checked : target.value;
    const name = target.name;

    this.setState({
      [name]: value
    });
  }
  save() {
    console.log(this.state);
  }
  render() {
    const { classes } = this.props;
    return (
        <GridContainer justify="center">
          <GridItem xs={12}>
            <StrategyList strategyType={"sell"}/>
          </GridItem>
        </GridContainer>
    );
  }
}

export default SellStrategies;
