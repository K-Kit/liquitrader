import React from "react";

// core components
import Wizard from "components/Wizard/Wizard.jsx";
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";
import StepZilla from "react-stepzilla";

import Step1 from "./WizardSteps/Step1.jsx";
import StrategyList from "views/Settings/StrategyList.jsx";
import General from "views/Settings/GeneralSettings.jsx";
import GlobalTrade from "views/Settings/GlobalTrade.jsx";

import { fetchJSON, postJSON } from "../helpers/Helpers";

const wizsteps =
[
  {stepName: 'Account', stepComponent: Step1, stepId: "account"},
  {stepName: 'General Settings', stepComponent: General, stepId: "general"},
  {stepName: 'Global Trading Settings', stepComponent: GlobalTrade, stepId: "globalTrade"},
  {stepName: 'Buy Strategies', stepComponent: StrategyList, stepId: "buy", strategyType:'buy'},
  {stepName: 'Sell Strategies', stepComponent: StrategyList, stepId: "sell", strategyType:'sell'},
  {stepName: 'Dollar Cost Average (DCA) Strategies', stepComponent: StrategyList, stepId: "dca", strategyType:'dca'}
]

    // { stepName: "About", stepComponent: Step1, stepId: "about" },

    function printState(params) {
      console.log('printing state')
      console.log(this.state.allState)
      console.log(this)
    }
class WizardView extends React.Component {
  render() {
    return (
      <GridContainer justify="center">
        <GridItem xs={12} sm={12}>
        <Wizard 
          validate
          steps={wizsteps}
          // hardcoded finishbutton click method into the wiz componant 
          finishButtonClick={
             () => {console.log(this)}
            }
            title="LiquiTrader Setup Wizard"
            subtitle="Welcome to LiquiTrader! Let's get you set up and start making money!"
        />
        </GridItem>
      </GridContainer>
    );
  }
}

export default WizardView;
