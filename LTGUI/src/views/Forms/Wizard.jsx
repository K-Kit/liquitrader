import React from "react";

// core components
import Wizard from "components/Wizard/Wizard.jsx";
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";

import Step1 from "./WizardSteps/Step1.jsx";
import Step2 from "./WizardSteps/Step2.jsx";
import Step3 from "./WizardSteps/Step3.jsx";
import Step4 from "./WizardSteps/Step4.jsx";
import Step5 from "./WizardSteps/Step5.jsx";
import Step6 from "./WizardSteps/Step6.jsx";

class WizardView extends React.Component {
  render() {
    return (
      <GridContainer justify="center">
        <GridItem xs={12} sm={12}>
          <Wizard
            validate
            steps={[
              { stepName: "Account", stepComponent: Step1, stepId: "a" },
              { stepName: "General Settings", stepComponent: Step2, stepId: "b" },
              { stepName: "Trade Settings", stepComponent: Step4, stepId:"c"},
              { stepName: "Buy Strategies", stepComponent: Step3, stepId: "d" },
              { stepName: "Sell Strategies", stepComponent: Step6, stepId: "e" },
              { stepName: "DCA Strategies", stepComponent: Step5, stepId: "f" },
            ]}
            title="Welcome to LiquiTrader"
            subtitle="Lets go through a few setup steps and start making some money!"
            
          />
         
        </GridItem>
      </GridContainer>
    );
  }
}

export default WizardView;
