import React from "react";
// @material-ui/core components
import withStyles from "@material-ui/core/styles/withStyles";
import FormLabel from "@material-ui/core/FormLabel";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import InputAdornment from "@material-ui/core/InputAdornment";
import Radio from "@material-ui/core/Radio";
import Checkbox from "@material-ui/core/Checkbox";

// @material-ui/icons
import MailOutline from "@material-ui/icons/MailOutline";
import Check from "@material-ui/icons/Check";
import Clear from "@material-ui/icons/Clear";
import Contacts from "@material-ui/icons/Contacts";
import FiberManualRecord from "@material-ui/icons/FiberManualRecord";
import AddIcon from "@material-ui/icons/Add";
import DeleteIcon from "@material-ui/icons/Delete";
import Switch from "@material-ui/core/Switch";

import Button from "components/CustomButtons/Button.jsx";
import Card from "components/Card/Card.jsx";
import CardHeader from "components/Card/CardHeader.jsx";
import CardText from "components/Card/CardText.jsx";
import CardIcon from "components/Card/CardIcon.jsx";
import CardBody from "components/Card/CardBody.jsx";

import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";
import CustomInput from "components/CustomInput/CustomInput.jsx";
import extendedFormsStyle from "assets/jss/material-dashboard-pro-react/views/extendedFormsStyle.jsx";
// react component plugin for creating beatiful tags on an input
import TagsInput from "react-tagsinput";
import SweetAlert from "react-bootstrap-sweetalert";

import sweetAlertStyle from "assets/jss/material-dashboard-pro-react/views/sweetAlertStyle.jsx";

import modalStyle from "assets/jss/material-dashboard-pro-react/modalStyle.jsx";
import Slide from "@material-ui/core/Slide";
import Dialog from "@material-ui/core/Dialog";
import DialogTitle from "@material-ui/core/DialogTitle";
import DialogContent from "@material-ui/core/DialogContent";
import DialogActions from "@material-ui/core/DialogActions";
import Close from "@material-ui/icons/Close";
import ConditionInput from "views/Settings/ConditionInput.jsx";
import Indicators from "./data/Indicators.jsx";

let conditions = [];
// const text = "text";

let condition = props => {
  return (
    <div>
      <Button color="primary">
        <GridContainer spacing={8} justify="space-evenly">
          <GridItem>
            {props.left.timeframe} {props.left.value} {props.left.candle_period}
          </GridItem>
          <GridItem>{props.op}</GridItem>
          <GridItem>
            {props.right.timeframe} {props.right.value}{" "}
            {props.right.candle_period}
          </GridItem>
        </GridContainer>
      </Button>
    </div>
  );
};

class MultipleStrategies extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      strategies: []
    };

    this.handleConditionChange = this.handleConditionChange.bind(this);
    this.Transition = this.Transition.bind(this);
    this.addCondition = this.addCondition.bind(this);
    this.change = this.change.bind(this);
    this.handleClickOpen = this.handleClickOpen.bind(this);
  }

  change(event, stateName) {
    this.setState({ [stateName]: event.target.value });
    console.log(this.state);
  }

  handleClickOpen(modal) {
    var x = [];
    x[modal] = true;
    this.setState(x);
  }

  change(event, stateName) {
    this.setState({ [stateName]: event.target.value });
    console.log(this.state);
  }

  addCondition = data => {
    console.log(data);
    // l = createIndicator(data)
    conditions.push(data);
    this.handleClose("modal");
  };

  Transition(props) {
    return <Slide direction="down" {...props} />;
  }

  mod = props => {
    let classes = props;
    return (
      <div>
        <GridContainer>
          <GridItem xs={12}>
            <Dialog
              classes={{
                root: classes.center,
                paper: classes.modal
              }}
              open={this.state.modal}
              transition={this.Transition}
              keepMounted
              onClose={() => this.handleClose("modal")}
              aria-labelledby="modal-slide-title"
              aria-describedby="modal-slide-description"
            >
              <DialogTitle
                id="classic-modal-slide-title"
                disableTypography
                className={classes.modalHeader}
              >
                <Button
                  justIcon
                  className={classes.modalCloseButton}
                  key="close"
                  aria-label="Close"
                  color="transparent"
                  onClick={() => this.handleClose("modal")}
                >
                  <Close className={classes.modalClose} />
                </Button>
                <h4 className={classes.modalTitle}>Add Conditional Strategy</h4>
              </DialogTitle>
              <DialogContent
                id="modal-slide-description"
                className={classes.modalBody}
              >
                <ConditionInput addCondition={this.addCondition} />
              </DialogContent>
              <DialogActions
                className={
                  classes.modalFooter + " " + classes.modalFooterCenter
                }
              />
            </Dialog>
          </GridItem>
        </GridContainer>
      </div>
    );
  };

  handleConditionChange(conds) {
    this.setState({ conditions: conds });
  }

  handleClose(modal) {
    var x = [];
    x[modal] = false;
    this.setState(x);
  }

  render() {
const { deleteStrategy }  = this.props;

    return (
      <GridContainer justify="center">
        {this.state.alert}
        {this.mod(this.props, this.state.modal)}
        <Clear style={{float:'right',color:'red',cursor:'pointer'}}  className="deleteItem" onClick={deleteStrategy}> </Clear>

        <GridItem xs={3}>
          {conditions.map(item => {
            return (
              <div>
                <GridItem xs={12}>{condition(item)}</GridItem>
              </div>
            );
          })}
          <Button color="rose" onClick={() => this.handleClickOpen("modal")}>
            add condition
          </Button>
        </GridItem>
        <GridItem xs={3}>
          <FormControlLabel
            control={<Switch value="checkStrategy" />}
            label="Enable Strategy"
          />
        </GridItem>
        <GridContainer justify="center">
          <GridItem xs={3}>
            <CustomInput
              labelText="Buy Value"
              id="buy_value"
              formControlProps={{
                fullWidth: false
              }}
              inputProps={{
                onChange: event => this.change(event, "buyValue"),
                type: "buyValue"
              }}
            />
          </GridItem>

          <GridItem xs={3}>
            <CustomInput
              labelText="Minimum Volume"
              id="min_volume"
              formControlProps={{
                fullWidth: false
              }}
              inputProps={{
                onChange: event => this.change(event, "minVolume"),
                type: "minVolume"
              }}
            />
          </GridItem>
        </GridContainer>
        <GridContainer justify="center">
          <GridItem xs={3}>
            <CustomInput
              labelText="Trailing Value (%)"
              id="trailing_value"
              formControlProps={{
                fullWidth: false
              }}
              inputProps={{
                onChange: event => this.change(event, "trailingValue"),
                type: "trailingValue"
              }}
            />
          </GridItem>
          <GridItem xs={3}>
            <CustomInput
              labelText="Minimum Price"
              id="min_price"
              formControlProps={{
                fullWidth: false
              }}
              inputProps={{
                onChange: event => this.change(event, "minPrice"),
                type: "minPrice"
              }}
            />
          </GridItem>
        </GridContainer>
      </GridContainer>
    );
  }
}

export default withStyles(extendedFormsStyle)(MultipleStrategies);
