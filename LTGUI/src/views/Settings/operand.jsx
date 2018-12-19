import React from "react";
import GridContainer from "../../components/Grid/GridContainer";
import GridItem from "../../components/Grid/GridItem";
import CustomInput from "../../components/CustomInput/CustomInput";

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

export default class Operand extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
        ...this.props.initialState
    };
    console.log('operand', this.state)
    this.handleInputChange = this.handleInputChange.bind(this);
  }

  handleInputChange(event) {
    const target = event.target;
    const value = target.type === "checkbox" ? target.checked : target.value;
    const name = target.name;

    this.setState({
      [name]: value
    });
    this.state[name] = value;
    this.props.callback(this.state);
  }
  render() {
    return (
      <div>
        <GridContainer>
          <GridItem md={3}>
            {indicatorInput("timeframe", "timeframe", this.handleInputChange, this.state.timeframe)}
          </GridItem>
          <GridItem md={6}>
            {indicatorInput("value", "Indicator", this.handleInputChange, this.state.value)}
          </GridItem>
          <GridItem md={3}>
            {indicatorInput("candle_period", "period", this.handleInputChange, this.state.candle_period)}
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
