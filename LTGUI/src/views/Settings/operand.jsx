import React from "react";
import GridContainer from "../../components/Grid/GridContainer";
import GridItem from "../../components/Grid/GridItem";
import CustomInput from "../../components/CustomInput/CustomInput";

let indicatorInput = (id, label, callback) => {
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
          name: id
        }}
      />
    </div>
  );
};

export default class Operand extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      value: "",
      candle_period: "",
      candle_count: "",
      change_over: ""
    };
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
            {indicatorInput("timeframe", "period", this.handleInputChange)}
          </GridItem>
          <GridItem md={6}>
            {indicatorInput("value", "Indicator", this.handleInputChange)}
          </GridItem>
          <GridItem md={3}>
            {indicatorInput("candle_period", "count", this.handleInputChange)}
          </GridItem>

          <GridItem md={6}>
            {indicatorInput(
              "change_over",
              "Change (optional)",
              this.handleInputChange
            )}
          </GridItem>
        </GridContainer>
      </div>
    );
  }
}
