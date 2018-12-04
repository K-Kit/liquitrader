import React from "react";
// react component for creating dynamic tables
import ReactTable from "react-table";

// @material-ui/core components
import withStyles from "@material-ui/core/styles/withStyles";
// @material-ui/icons
import Assignment from "@material-ui/icons/Assignment";
import Dvr from "@material-ui/icons/Dvr";
import Favorite from "@material-ui/icons/Favorite";
import Close from "@material-ui/icons/Close";
// core components
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";
import Button from "components/CustomButtons/Button.jsx";
import Card from "components/Card/Card.jsx";
import CardBody from "components/Card/CardBody.jsx";
import CardIcon from "components/Card/CardIcon.jsx";
import CardHeader from "components/Card/CardHeader.jsx";

import { dataTable } from "variables/general.jsx";
// import { URL, HEADERS } from "variables/global.jsx";

import { cardTitle } from "assets/jss/material-dashboard-pro-react.jsx";
import { holding_route } from "variables/global";
// const url = "https://gist.githubusercontent.com/K-Kit/9ab58d3f86ed7b59dd74a62ec395d8f1/raw/c0428e3216110a48ad2dd75f2482048908833b34/holding"
const url = holding_route;

export function fetchJSON(url, callback) {
  fetch(url)
    .then(resp => {
      return resp.json();
    })
    .then(callback)
    .catch(function(error) {
      console.log(error);
    });
}

const styles = {
  cardIconTitle: {
    ...cardTitle,
    marginTop: "15px",
    marginBottom: "0px"
  }
};

class ReactTables extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      data: [],
      columnDefs: "",
      loading: false
    };

    this.auto_update_frequency = 10 * 1000; // x * 1000 = x seconds

    this.isCancelled = true;

    this.update = this.update.bind(this);
    this.update_cols_callback = this.update_cols_callback.bind(this);
    this.update_rows_callback = this.update_rows_callback.bind(this);
    // this.timeFriendlySort = this.timeFriendlySort.bind(this);
  }

  update_rows_callback(rowData) {
    rowData = JSON.parse(rowData);

    if (!this.isCancelled) {
      this.setState({ data: rowData });
    }
  }

  update_cols_callback(columnDefs) {
    columnDefs = JSON.parse(columnDefs);

    if (!this.isCancelled) {
      this.setState({ columnDefs });
    }
  }

  update() {
    fetchJSON(holding_route, this.update_rows_callback);
  }

  componentWillMount() {
    this.isCancelled = false;

    // This request takes longer, so prioritize it
    fetchJSON(holding_route, this.update_rows_callback);

    // Only update columns once
    // fetchJSON(this.props.url + "_cols", this.update_cols_callback);

    this.auto_update = setInterval(this.update, this.auto_update_frequency);
  }

  componentWillUnmount() {
    this.isCancelled = true;
    clearInterval(this.auto_update);
  }
  render() {
    const { classes } = this.props;
    return (
      <GridContainer>
        <GridItem xs={12}>
          <Card>
            <CardHeader color="primary" icon>
              <CardIcon color="primary">
                <Assignment />
              </CardIcon>
              <h4 className={classes.cardIconTitle}>Holding</h4>
            </CardHeader>
            <CardBody>
              <ReactTable
                data={this.state.data}
                filterable
                columns={[
                  {
                    Header: "Last Purchase Time",
                    accessor: "Last Purchase Time"
                  },
                  { Header: "Symbol", accessor: "Symbol" },
                  { Header: "Price", accessor: "Price" },
                  { Header: "Bought Price", accessor: "Bought Price" },
                  { Header: "% Change",
                      accessor: "% Change",
                      Cell: row => (
                          <span style={{color: row.value >= 0 ? '#85cc00' : '#ff2e00'}}>{row.value.toFixed(2)}%</span>
                      )
                  },
                  { Header: "Volume", accessor: "Volume" },
                  { Header: "Bought Value", accessor: "Bought Value" },
                  { Header: "Current Value", accessor: "Current Value" },
                  { Header: "DCA Level", accessor: "DCA Level" },
                  { Header: "Amount", accessor: "Amount" },
                  { Header: "24h Change",
                      accessor: "24h Change",
                      Cell: row => (
                          <span style={{color: row.value >= 0 ? '#85cc00' : '#ff2e00'}}>{row.value}%</span>
                      )}
                ]}
                defaultPageSize={10}
                showPaginationTop
                showPaginationBottom={false}
                className="-striped -highlight"
              />
            </CardBody>
          </Card>
        </GridItem>
      </GridContainer>
    );
  }
}

export default withStyles(styles)(ReactTables);
