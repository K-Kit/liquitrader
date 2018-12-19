import React from "react";
import PropTypes from "prop-types";
// react plugin for creating charts
import ChartistGraph from "react-chartist";
// react plugin for creating vector maps

// @material-ui/core components
import withStyles from "@material-ui/core/styles/withStyles";
// import Tooltip from "@material-ui/core/Tooltip";

import Language from "@material-ui/icons/Language";

// core components
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";
import Table from "components/Table/Table.jsx";
import Card from "components/Card/Card.jsx";
import CardHeader from "components/Card/CardHeader.jsx";
import CardIcon from "components/Card/CardIcon.jsx";
import CardBody from "components/Card/CardBody.jsx";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEthereum } from "@fortawesome/free-brands-svg-icons";

import { faChartLine, faPercentage } from "@fortawesome/free-solid-svg-icons";

import { dashboard_route } from "variables/global";
import dashboardStyle from "assets/jss/material-dashboard-pro-react/views/dashboardStyle";
import Typography from "@material-ui/core/Typography/Typography";

const lightgreyfont = {
  color: "gray"
};

let temp_cum = [
  { timestamp: 1540010515572, gain: 1 },
  { timestamp: 1551510005572, gain: 1 },
  { timestamp: 1561515000572, gain: 1 },
  { timestamp: 1571510005572, gain: 1 },
  { timestamp: 1581500015572, gain: 1 }
];

let getData = data => {
  let coordinates = [];
  let cumGain = 0;
  data.map(row => {
    cumGain += row.gain;
    let date = new Date(row.timestamp);
    coordinates.push({
      gain: row.gain,
      cumGain: cumGain,
      timestamp: date.getMonth().toString() + "/" + date.getDate().toString()
    });
    // coordinates.x.push(date.getMonth().toString() + "/" + date.getDate().toString())
  });
  return coordinates;
};

export function fetchJSON(url, callback) {
  fetch(url)
    .then(resp => {
      return resp.json();
    })
    .then(data => callback(data))
    .catch(function(error) {
      console.log(error);
    });
}

class Dashboard extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      quote_balance: "",
      total_pending_value: "",
      total_current_value: "",
      market: "",
      usd_balance_info: "/",
      usd_total_profit: "",
      usd_average_daily_gain: "",
      market_change_24h: "",
      average_daily_gain: "",
      total_profit: "",
      total_profit_percent: "",
      daily_profit_data: [],
      quote_candles: [],

      holding_chart_data: [],
      cum_profit: [],
      market_conditions: [],
      pair_profit_data: [],
      recent_sales: []
    };

    this.auto_update_frequency = 10 * 1000; // x * 1000 = x seconds

    this.isCancelled = false;
    this.update = this.update.bind(this);
    this.update_state = this.update_state.bind(this);
  }

  update() {
    fetchJSON(dashboard_route, this.update_state);
  }

  update_state(data) {
    // data = JSON.parse(data);

    this.setState(data);
    return data;
  }

  componentDidMount() {
    this.update();
  }

  componentWillMount() {
    // This request takes longer, so prioritize it
    console.log("will mount");
    this.update();
    console.log("fetched");
    this.isCancelled = false;

    this.auto_update = setInterval(this.update, this.auto_update_frequency);
  }

  componentWillUnmount() {
    this.isCancelled = true;
    clearInterval(this.auto_update);
  }

  render() {
    const { classes } = this.props;
    let cum_profit_chart = data => {
      return (
        <GridItem xs={12} sm={12} md={6}>
          <Card chart>
            <CardHeader color="info">
              <ChartistGraph
                className="ct-chart-white-colors"
                data={{
                  labels: this.state.cum_profit.map(item => {
                    return item.date;
                  }),
                  series: [
                    this.state.cum_profit.map(item => {
                      return item.gain;
                    })
                  ]
                }}
                type="Line"
                // options={dailySalesChart.options}
              />
            </CardHeader>
            <CardBody>
              <h4 className={classes.cardTitle}>Cumulative Profit</h4>
            </CardBody>
          </Card>
        </GridItem>
      );
    };
    return (
      <div>
        <GridContainer alignItems={"stretch"}>
          {cum_profit_chart(getData(temp_cum))}
          <GridItem md={6}>
            <GridContainer alignItems={"stretch"}>
              <GridItem xs={12} md={6}>
                <Card>
                  <CardHeader color="warning" stats icon>
                    <CardIcon color="warning">
                      <FontAwesomeIcon icon={faEthereum} />
                    </CardIcon>
                    <p className={classes.cardCategory}>Available Balance</p>
                    <h4 className={classes.cardTitle}>
                      {this.state.quote_balance} {this.state.market}
                    </h4>
                    <small style={lightgreyfont}>
                      {this.state.usd_balance_info.split("/")[0]}
                    </small>
                  </CardHeader>
                </Card>
              </GridItem>
              <GridItem xs={12} md={6}>
                <Card>
                  <CardHeader color="warning" stats icon>
                    <CardIcon color="warning">
                      <FontAwesomeIcon icon={faEthereum} />
                    </CardIcon>
                    <p className={classes.cardCategory}>Total Balance</p>
                    <h4 className={classes.cardTitle}>
                      {this.state.total_pending_value} {this.state.market}
                    </h4>
                    <small style={lightgreyfont}>
                      {this.state.usd_balance_info.split("/")[1]}
                    </small>
                  </CardHeader>
                </Card>
              </GridItem>
              <GridItem xs={12} md={6}>
                <Card>
                  <CardHeader color="warning" stats icon>
                    <CardIcon color="warning">
                      <FontAwesomeIcon icon={faEthereum} />
                    </CardIcon>
                    <p className={classes.cardCategory}>Current Value</p>
                    <h4 className={classes.cardTitle}>
                      {this.state.total_current_value} {this.state.market}
                    </h4>
                    <small style={lightgreyfont}>
                      {this.state.usd_current_value}
                    </small>
                  </CardHeader>
                </Card>
              </GridItem>
              <GridItem xs={12} md={6}>
                <Card>
                  <CardHeader color="success" stats icon>
                    <CardIcon color="success">
                      <FontAwesomeIcon icon={faChartLine} />
                    </CardIcon>
                    <p className={classes.cardCategory}>Total Profit</p>
                    <h4 className={classes.cardTitle}>
                      {this.state.total_profit} {this.state.market}
                    </h4>
                    <small style={lightgreyfont}>
                      {this.state.usd_total_profit}
                    </small>
                  </CardHeader>
                </Card>
              </GridItem>
            </GridContainer>
          </GridItem>
        </GridContainer>
        <GridContainer>
          <GridItem xs={12} sm={12} md={3}>
            <Card>
              <CardHeader color="danger" stats icon>
                <CardIcon color="danger">
                  <FontAwesomeIcon icon={faPercentage} />
                </CardIcon>
                <p className={classes.cardCategory}>
                  Global Trading Conditions
                </p>
              </CardHeader>
              <CardBody>
                <GridContainer spacing={0} justify="center" alignItems="center">
                  <Typography noWrap>
                    {this.state.market_conditions.map(condition => {
                      return (
                        <div>
                          <GridItem xs={6} className={classes.cardCategory}>
                            <p style={lightgreyfont}>{condition[0]}</p>
                          </GridItem>
                          <GridItem
                            xs={1}
                            style={{
                              color: condition[1].includes("True")
                                ? "#85cc00"
                                : "#ff2e00"
                            }}
                          >
                            {condition[1]}
                          </GridItem>
                        </div>
                      );
                    })}
                  </Typography>
                </GridContainer>
              </CardBody>
            </Card>
          </GridItem>

          <GridItem xs={12} sm={12} md={3}>
            <Card>
              <CardHeader color="danger" stats icon>
                <CardIcon color="danger">
                  <FontAwesomeIcon icon={faPercentage} />
                </CardIcon>
                <p className={classes.cardCategory}>Recent Sales</p>
              </CardHeader>
              <CardBody>
                <p>
                  {console.log(this.state.recent_trades, this.state)}
                  <Table
                    tableHead={["Symbol", "Gain"]}
                    tableData={this.state.recent_sales.map(value => {
                      return [
                        value["symbol"],
                        <span
                          style={{
                            color: value["gain"] > 0 ? "#85cc00" : "#ff2e00"
                          }}
                        >
                          {" "}
                          {value["gain"].toFixed(2)}<small>%</small>
                        </span>
                      ];
                    })}
                  />
                </p>
              </CardBody>
            </Card>
          </GridItem>
          <GridItem xs={12} md={6}>
            <GridContainer>
              <GridItem xs={12} sm={12} md={6}>
                <Card>
                  <CardHeader color="danger" stats icon>
                    <CardIcon color="danger">
                      <FontAwesomeIcon icon={faPercentage} />
                    </CardIcon>
                    <p className={classes.cardCategory}>Average Daily Gain</p>
                    <h3 className={classes.cardTitle}>
                      {this.state.average_daily_gain}%
                    </h3>
                    <small style={lightgreyfont}>
                      {this.state.usd_average_daily_gain}
                    </small>
                  </CardHeader>
                </Card>
              </GridItem>
              <GridItem xs={12} sm={12} md={6}>
                <Card>
                  <CardHeader color="info" stats icon>
                    <CardIcon color="info">
                      <FontAwesomeIcon icon={faChartLine} />
                    </CardIcon>
                    <p className={classes.cardCategory}>24h Market Change</p>
                    <h3 className={classes.cardTitle}>
                      {this.state.market_change_24h}
                    </h3>
                  </CardHeader>
                </Card>
              </GridItem>
              <GridItem xs={12} sm={12} md={12}>
                <Card chart>
                  <CardHeader color="danger">
                    {console.log(this.state.quote_candles.map(item => {
                      let date = new Date(item.timestamp);
                      return date;
                    }), 'qc')}
                    <ChartistGraph
                      className="ct-chart-white-colors"
                      data={{
                        labels: this.state.quote_candles.map(item => {
                          let date = new Date(item.timestamp).toLocaleTimeString();
                          let split = date.split(" ");
                          let time = split[0].slice(0,-3);
                          return  time;
                        }),
                        series: [
                          this.state.quote_candles.map(item => {
                            return item.close;
                          })
                        ]
                      }}
                      type="Line"
                      // options={dailySalesChart.options}
                    />
                  </CardHeader>
                  <CardBody>
                    <h4 className={classes.cardTitle}>
                      24h {this.state.market} Change
                    </h4>

                    <small> ${this.state.quote_price} </small>
                  </CardBody>
                </Card>
              </GridItem>
            </GridContainer>
          </GridItem>
        </GridContainer>
        <GridContainer>
          <GridItem xs={12}>
            <Card>
              <CardHeader color="success" icon>
                <CardIcon color="success">
                  <Language />
                </CardIcon>
                <h4 className={classes.cardIconTitle}>
                  Daily profit distribution
                </h4>
              </CardHeader>
              <CardBody>
                <GridContainer justify="space-between">
                  <GridItem xs={12} sm={12} md={8}>
                    <Table
                      tableHead={["Date", "Bought Value", "Sold Value", "Gain"]}
                      tableData={this.state.daily_profit_data.map(value => {
                        return [
                          value["date"],
                          value["total_cost"].toFixed(8),
                          value["cost"].toFixed(8),
                          value["gain"].toFixed(8)
                        ];
                      })}
                    />
                  </GridItem>
                  <GridItem xs={12} sm={12} md={4}>
                    <Card chart>
                      <CardHeader color="danger">
                        <ChartistGraph
                          className="ct-chart-white-colors"
                          data={{
                            labels: this.state.daily_profit_data.map(item => {
                              return item.date;
                            }),
                            series: [
                              this.state.daily_profit_data.map(item => {
                                return item.gain;
                              })
                            ]
                          }}
                          type="Bar"
                          // options={dailySalesChart.options}
                        />
                      </CardHeader>
                      <CardBody>
                        <h4 className={classes.cardTitle}>Daily Profit</h4>
                      </CardBody>
                    </Card>
                  </GridItem>
                </GridContainer>
              </CardBody>
            </Card>
          </GridItem>
        </GridContainer>
      </div>
    );
  }
}

Dashboard.propTypes = {
  classes: PropTypes.object.isRequired
};

export default withStyles(dashboardStyle)(Dashboard);
