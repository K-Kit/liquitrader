import React from "react";
// react component for creating dynamic tables
import ReactTable from "react-table";

// @material-ui/core components
import withStyles from "@material-ui/core/styles/withStyles";
// @material-ui/icons
import Assignment from "@material-ui/icons/Assignment";
// core components
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";
import Card from "components/Card/Card.jsx";
import CardBody from "components/Card/CardBody.jsx";
import CardIcon from "components/Card/CardIcon.jsx";
import CardHeader from "components/Card/CardHeader.jsx";

import { dataTable } from "variables/general.jsx";
// import { URL, HEADERS } from "variables/global.jsx";

import { fetchJSON } from "views/helpers/Helpers.jsx";
import { cardTitle } from "assets/jss/material-dashboard-pro-react.jsx";
import { sells_route } from "variables/global";
// const url = "https://gist.githubusercontent.com/K-Kit/9ab58d3f86ed7b59dd74a62ec395d8f1/raw/c0428e3216110a48ad2dd75f2482048908833b34/holding"
const url = sells_route;


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
    console.log('====================================');
    console.log(this.state.data.length);
    console.log('====================================');
    fetchJSON(url, this.update_rows_callback);
  }

  componentWillMount() {
    this.isCancelled = false;

    // This request takes longer, so prioritize it
    fetchJSON(url, this.update_rows_callback);


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
          <CardHeader color="info" stats icon>
                    <CardIcon color="info">
                <Assignment />
              </CardIcon>
            </CardHeader>
            <CardBody>
              <ReactTable
                data={this.state.data.reverse()}
                filterable
                columns={[
                  { Header: "Time", accessor: "timestamp", Cell: ci => {
                    let date =  new Date(ci.value);
                          return date.toLocaleString()
                      }},
                  { Header: "Symbol", accessor: "symbol" },
                  { Header: "Bought Cost", accessor: "bought_cost",
                      Cell: ci => ci.value.toFixed(8) },
                  { Header: "Sold Value", accessor: "cost",
                      Cell: ci => ci.value.toFixed(8) },
                  { Header: "Amount", accessor: "filled" ,
                      Cell: ci => ci.value.toFixed(2)},
                  { Header: "% Gain", accessor: "gain" ,
                  Cell: row => (
                          <span style={{color: row.value >= 0 ? '#85cc00' : '#ff2e00'}}>{row.value.toFixed(2)}%</span>
                      )}
                ]}
                PageSize={this.state.data.length > 0 ? this.state.data.length: 10}
                minRows={0}  // Fix for empty rows
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
