import React from "react";

// @material-ui/icons
import Face from "@material-ui/icons/Face";
import RecordVoiceOver from "@material-ui/icons/RecordVoiceOver";
import Email from "@material-ui/icons/Email";
import Button from "components/CustomButtons/Button.jsx";

// @material-ui/core components
import withStyles from "@material-ui/core/styles/withStyles";
import InputAdornment from "@material-ui/core/InputAdornment";

// core components
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";
import PictureUpload from "components/CustomUpload/PictureUpload.jsx";
import CustomInput from "components/CustomInput/CustomInput.jsx";

const style = {
  infoText: {
    fontWeight: "300",
    margin: "10px 0 30px",
    textAlign: "center"
  },
  inputAdornmentIcon: {
    color: "#555"
  },
  inputAdornment: {
    position: "relative"
  }
};

class Step1 extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      firstname: "",
      firstnameState: "",
      password: "",
      passwordState: "",
      public: "",
      private: "",
      license: ""
      // email: "",
      // emailState: ""
    };
  }
  sendState() {
    return this.state;
  }
  // function that returns true if value is email, false otherwise
  // verifyEmail(value) {
  // var emailRex = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  // if (emailRex.test(value)) {
  //   return true;
  // }
  // return false;
  // }
  // function that verifies if a string has a given length or not
  verifyLength(value, length) {
    if (value.length >= length) {
      return true;
    }
    return false;
  }
  change(event, stateName, type, stateNameEqualTo) {
    switch (type) {
      // case "email":
      //   if (this.verifyEmail(event.target.value)) {
      //     this.setState({ [stateName + "State"]: "success" });
      //   } else {
      //     this.setState({ [stateName + "State"]: "error" });
      //   }
      //   break;
      case "length":
        if (this.verifyLength(event.target.value, stateNameEqualTo)) {
          this.setState({ [stateName + "State"]: "success" });
        } else {
          this.setState({ [stateName + "State"]: "error" });
        }
        break;
      default:
        break;
    }
    this.setState({ [stateName]: event.target.value });
  }
  isValidated() {
    if (
      this.state.firstnameState === "success" &&
      this.state.passwordState === "success"
      // this.state.emailState === "success"
    ) {
      return true;
    } else {
      if (this.state.firstnameState !== "success") {
        this.setState({ firstnameState: "error" });
      }
      if (this.state.passwordState !== "success") {
        this.setState({ passwordState: "error" });
      }
      // if (this.state.emailState !== "success") {
      //   this.setState({ emailState: "error" });
      // }
    }
    return false;
  }
  render() {
    const { classes } = this.props;
    return (
      <GridContainer justify="center">
        <GridItem xs={12} sm={12}>
          <legend className={classes.infoText}>Sign In</legend>
        </GridItem>
        <GridItem xs={12} sm={6}>
          <CustomInput
            success={this.state.firstnameState === "success"}
            error={this.state.firstnameState === "error"}
            labelText={
              <span>
                User Name <small>(required)</small>
              </span>
            }
            id="firstname"
            formControlProps={{
              fullWidth: true
            }}
            inputProps={{
              onChange: event => this.change(event, "firstname", "length", 3),
              endAdornment: (
                <InputAdornment
                  position="end"
                  className={classes.inputAdornment}
                >
                  <Face className={classes.inputAdornmentIcon} />
                </InputAdornment>
              )
            }}
          />
          <CustomInput
            success={this.state.passwordState === "success"}
            error={this.state.passwordState === "error"}
            labelText={
              <span>
                Password <small>(required)</small>
              </span>
            }
            id="password"
            formControlProps={{
              fullWidth: true
            }}
            inputProps={{
              onChange: event => this.change(event, "password", "length", 3),
              type: "password",
              endAdornment: (
                <InputAdornment
                  position="end"
                  className={classes.inputAdornment}
                >
                  <RecordVoiceOver className={classes.inputAdornmentIcon} />
                </InputAdornment>
              )
            }}
          />

          <CustomInput
            success={this.state.passwordState === "success"}
            error={this.state.passwordState === "error"}
            labelText={
              <span>
                Confirm Password <small>(required)</small>
              </span>
            }
            id="password"
            formControlProps={{
              fullWidth: true
            }}
            inputProps={{
              onChange: event => this.change(event, "password", "length", 3),
              type: "password",
              endAdornment: (
                <InputAdornment
                  position="end"
                  className={classes.inputAdornment}
                >
                  <RecordVoiceOver className={classes.inputAdornmentIcon} />
                </InputAdornment>
              )
            }}
          />

          <CustomInput
            labelText={<span>Enter Public API key</span>}
            id="public"
            formControlProps={{
              fullWidth: true
            }}
            inputProps={{
              onChange: event => this.change(event, "public"),
              type: "public"
            }}
          />

          <CustomInput
            labelText={<span>Enter Private API Key</span>}
            id="private"
            formControlProps={{
              fullWidth: true
            }}
            inputProps={{
              onChange: event => this.change(event, "public"),
              type: "private"
            }}
          />

          <CustomInput
            labelText={<span>Enter Liquitrader License</span>}
            id="license"
            formControlProps={{
              fullWidth: true
            }}
            inputProps={{
              onChange: event => this.change(event, "license"),
              type: "license"
            }}
          />

          <Button style={{ background: "#6495ed" }}>2FA</Button>
        </GridItem>
      </GridContainer>
    );
  }
}

export default withStyles(style)(Step1);
