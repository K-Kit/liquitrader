import React from "react";

// core components
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";
import StrategyList from "./StrategyList";

class DCAStrategies extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            strategies: []
        };
    }
    sendState() {
      return this.state;
    }
    render() {
        const { classes } = this.props;
        return (
            <GridContainer justify="center">
                <GridItem xs={12}>
                    <StrategyList strategyType={'dca'} />
                </GridItem>
            </GridContainer>
        );
    }
}

export default DCAStrategies;
