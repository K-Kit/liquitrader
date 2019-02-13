import React from "react";

// core components
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";
import Table from "components/Table/Table.jsx";
import FormLabel from "@material-ui/core/FormLabel";
import withStyles from "../../../node_modules/@material-ui/core/styles/withStyles";
import regularFormsStyle from "../../assets/jss/material-dashboard-pro-react/views/regularFormsStyle";

import CustomInput from "components/CustomInput/CustomInput.jsx";

import extendedFormsStyle from "assets/jss/material-dashboard-pro-react/views/extendedFormsStyle.jsx";
import { fetchJSON, postJSON } from "../helpers/Helpers";
import Button from "../../../node_modules/@material-ui/core/Button/Button";

class GlobalTrade extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      username: "",
      password: "",
      role: "admin",
      userlist: []
    };
    this.load = this.load.bind(this);
    this.save = this.save.bind(this);
    this.change = this.change.bind(this);
  }
  handleSimple = event => {
    this.setState({ [event.target.name]: event.target.value });
  };
  save() {
    console.log(this.state, "hello");
    let data = {
      username: this.state.username,
      password: this.state.password,
      role: this.state.role
    };
    console.log(data);
    postJSON("/api/add_user", data);
  }
  componentWillMount() {
    // This request takes longer, so prioritize it
    fetchJSON("/api/all_users", this.load);
  }
  load(users) {
    console.log(users);
    this.setState({
      userlist: users
    });
  }
  change(event, stateName) {
    this.setState({ [stateName]: event.target.value });
  }
  render() {
    const { classes } = this.props;

    return (
      <div style={{ margin: "0 auto", textAlign: "center", flexGrow: "1" }}>
        <GridContainer justify="space-between" alignItems="stretch">
          <GridItem xs={12} sm={12} md={12}>
            <Table
              tableHead={["User Name", "Role"]}
              tableData={this.state.userlist}
            />
          </GridItem>
          <GridItem xs={12}>
            <CustomInput
              labelText={"username"}
              formControlProps={{
                fullWidth: false
              }}
              inputProps={{
                onChange: event => {
                  "change";
                  return this.change(event, "username");
                },
                value: this.state.username
              }}
            />
            <CustomInput
              labelText={"password"}
              formControlProps={{
                fullWidth: false
              }}
              inputProps={{
                onChange: event => {
                  "change";
                  return this.change(event, "password");
                },
                value: this.state.password
              }}
            />
            <CustomInput
              labelText={"role"}
              formControlProps={{
                fullWidth: false
              }}
              inputProps={{
                onChange: event => {
                  "change";
                  return this.change(event, "role");
                },
                value: this.state.role
              }}
            />
            <Button onClick={this.save} color={'primary'}> add user </Button>
          </GridItem>
        </GridContainer>
      </div>
    );
  }
}

export default withStyles(regularFormsStyle)(GlobalTrade);
