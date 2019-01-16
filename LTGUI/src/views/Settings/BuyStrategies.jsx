import React from "react";

// core components
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";
import StrategyList from "./StrategyList";

class BuyStrategies extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      strategies: []
    };
    this.handleInputChange = this.handleInputChange.bind(this);
    this.save = this.save.bind(this);
    this.strat = <StrategyList strategyType={'buy'} />
  }
  sendState(){
    {console.log(this.strat.state)}
    return this.strat.state
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
              {this.strat}
              {this.strat.state}
          </GridItem>
        </GridContainer>
    );
  }
}

export default BuyStrategies;
