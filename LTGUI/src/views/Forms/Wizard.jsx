import React from "react";

// core components
import Wizard from "components/Wizard/Wizard.jsx";
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";

import Step1 from "./WizardSteps/Step1.jsx";
import StrategyList from "views/Settings/StrategyList.jsx";
import General from "views/Settings/GeneralSettings.jsx";
import GlobalTrade from "views/Settings/GlobalTrade.jsx";

import { fetchJSON, postJSON } from "../helpers/Helpers";
import OverlayLoader from "react-overlay-loading/lib/OverlayLoader";

const wizsteps = [
  { stepName: "Account", stepComponent: Step1, stepId: "account" },
  { stepName: "General Settings", stepComponent: General, stepId: "general" },
  {
    stepName: "Global Trading Settings",
    stepComponent: GlobalTrade,
    stepId: "global_trade_conditions"
  },
  {
    stepName: "Buy Strategies",
    stepComponent: StrategyList,
    stepId: "buy_strategies",
    strategyType: "buy"
  },
  {
    stepName: "Sell Strategies",
    stepComponent: StrategyList,
    stepId: "sell_strategies",
    strategyType: "sell"
  },
  {
    stepName: "Dollar Cost Average (DCA) Strategies",
    stepComponent: StrategyList,
    stepId: "dca_buy_strategies",
    strategyType: "dca"
  }
];

class WizardView extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: true
    };
  }
  render() {
    return (
      <GridContainer justify="center">
      {/* can't get overlay to show for some reason... */}
        {/* <OverlayLoader
      style={{
        position: "inherit !important",
        top: "50px"
      }}
      color={"red"} // default is white
      loader="ScaleLoader" // check below for more loaders
      text="Configuring LiquiTrader... Please wait!"
      active={this.state.loading}
      backgroundColor={"black"} // default is black
      opacity="0.5" // default is .9
    > */}
        <GridItem xs={12} sm={12}>
          <Wizard
            validate
            steps={wizsteps}
            // hardcoded finishbutton click method into the wiz componant
            finishButtonClick={() => {
              console.log(this);
              window.location.pathname = '/login'
            }}
            title="LiquiTrader Setup Wizard"
            subtitle="Welcome to LiquiTrader! Let's get you set up and start making money!"
          />
        </GridItem>
      </GridContainer>
      // </OverlayLoader>
    );
  }
}

export default WizardView;
