import React from "react";
import GridContainer from "../../components/Grid/GridContainer";
import GridItem from "../../components/Grid/GridItem";
import CustomInput from "../../components/CustomInput/CustomInput";
import IndicatorInput from "./IndicatorInput";

export const indicatorInput = (id, label, callback, value) => {
  return (
    <div>
      <CustomInput
        labelText={label}
        id={id}
        formControlProps={{
          fullWidth: true
        }}
        inputProps={{
          onChange: event => callback(event),
          name: id,
          value: value
        }}
      />
    </div>
  );
};

const getIndicatorInput = (id, label, action, val) => {
  return <IndicatorInput id={id} label={label} val={val} callback={action} />;
};

export default class Operand extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ...this.props.initialState
    };
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleChange = this.handleChange.bind(this);
  }

  handleInputChange(event) {
   
      const target = event.target;
      const value = target.type === "checkbox" ? target.checked : target.value;
      const name = target.name;
    console.log(name,value)

    this.setState({
      [name]: value
    });
    this.state[name] = value;
    this.props.callback(this.state);
  }

  handleChange(event) {
    this.setState({
      "value": event.value
    });
    this.state["value"] = event.value;
    this.props.callback(this.state);
  };
  render() {
    return (
      <div>
        <GridContainer>
          <GridItem md={3}>
            {indicatorInput(
              "timeframe",
              "timeframe",
              this.handleInputChange,
              this.state.timeframe
            )}
          </GridItem>
          <GridItem md={6}>
            {getIndicatorInput(
              "value",
              "Indicator",
              this.handleChange,
              this.state.value
            )}
          </GridItem>
          <GridItem md={3}>
            {indicatorInput(
              "candle_period",
              "period",
              this.handleInputChange,
              this.state.candle_period
            )}
          </GridItem>

          <GridItem md={6}>
            {indicatorInput(
              "change_over",
              "Change (optional)",
              this.handleInputChange,
              this.state.change_over
            )}
          </GridItem>
        </GridContainer>
      </div>
    );
  }
}
