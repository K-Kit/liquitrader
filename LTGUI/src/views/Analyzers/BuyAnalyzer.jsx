import React from "react";

// core components
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";
import {
  exampleBuyStrategies,
  exampleDCAStrategies
} from "views/Settings/data/ExampleStrategies.jsx";
import Button from "components/CustomButtons/Button";
import * as PropTypes from "prop-types";
import StrategyCard from "views/Settings/StrategyCard.jsx";
import Dialog from "@material-ui/core/Dialog";
import withStyles from "@material-ui/core/styles/withStyles";
import extendedFormsStyle from "assets/jss/material-dashboard-pro-react/views/extendedFormsStyle";
import Slide from "@material-ui/core/Slide";
import { analyzer_route } from "variables/global";
import { postJSON } from "views/Settings/helpers/Helpers.jsx";
import Card from "../../components/Card/Card";
import Tooltip from "@material-ui/core/Tooltip";
import IconButton from "@material-ui/core/IconButton";
import Edit from "../../../node_modules/@material-ui/icons/Edit";
import Close from "../../../node_modules/@material-ui/icons/Close";
import ChartistGraph from "react-chartist";
import Table from "components/Table/Table.jsx";

import ReactTable from "react-table";


const analyzerDict = {
  buy: [
    {
      buy_value: "4.2%",
      conditions_list: [
        {
          id: 0,
          left: { timeframe: "30m", value: "MFI" },
          op: "<",
          right: { value: 40 }
        },
        {
          id: 1,
          left: {
            candle_period: 30,
            change_over: 2,
            timeframe: "5m",
            value: "MFI"
          },
          op: ">",
          right: { value: 1 }
        },
        {
          id: 2,
          left: { timeframe: "1h", value: "MFI" },
          op: "<",
          right: { value: 50 }
        }
      ],
      pairs_trailing: {
        "ADA/ETH": { trail_from: 0.00032424, trail_to: 0.0003250506 },
        "DOCK/ETH": { trail_from: 9.954e-5, trail_to: 9.978884999999999e-5 },
        "EVX/ETH": { trail_from: 0.002203, trail_to: 0.0022085075 },
        "HC/ETH": { trail_from: 0.006777, trail_to: 0.0067939425 },
        "IOTX/ETH": { trail_from: 7.787e-5, trail_to: 7.806467499999999e-5 },
        "KEY/ETH": { trail_from: 2.641e-5, trail_to: 2.6476024999999997e-5 },
        "KNC/ETH": { trail_from: 0.0014025, trail_to: 0.00140600625 },
        "LRC/ETH": { trail_from: 0.00038288, trail_to: 0.00038383719999999995 },
        "LTC/ETH": { trail_from: 0.27074, trail_to: 0.27141685 },
        "ONT/ETH": { trail_from: 0.006147, trail_to: 0.006162367499999999 },
        "POE/ETH": { trail_from: 5.341e-5, trail_to: 5.3543524999999995e-5 },
        "POWR/ETH": { trail_from: 0.00073634, trail_to: 0.00073818085 },
        "PPT/ETH": { trail_from: 0.013912, trail_to: 0.01394678 },
        "QTUM/ETH": { trail_from: 0.017077, trail_to: 0.0171196925 },
        "SALT/ETH": { trail_from: 0.00222, trail_to: 0.00222555 },
        "SKY/ETH": { trail_from: 0.00961, trail_to: 0.009634025 },
        "TNB/ETH": { trail_from: 3.265e-5, trail_to: 3.2731625e-5 },
        "WAVES/ETH": { trail_from: 0.015797, trail_to: 0.015836492499999997 },
        "XMR/ETH": { trail_from: 0.50213, trail_to: 0.5033853249999999 }
      },
      trailing_value: 0.25
    },
    {
      buy_value: "1.5%",
      conditions_list: [
        {
          id: 0,
          left: { timeframe: "30m", value: "RSI" },
          op: "<",
          right: { value: 10 }
        },
        {
          id: 1,
          left: {
            candle_period: 30,
            change_over: 2,
            timeframe: "5m",
            value: "MFI"
          },
          op: ">",
          right: { value: 1 }
        },
        {
          id: 2,
          left: { timeframe: "1h", value: "MFI" },
          op: "<",
          right: { value: 50 }
        },
        {
          id: 3,
          left: { timeframe: "1h", value: "CDLDOJISTAR" },
          op: "",
          right: {}
        }
      ],
      pairs_trailing: {},
      trailing_value: 0.3
    },
    {
      buy_value: "1%",
      conditions_list: [
        {
          id: 0,
          left: { timeframe: "4h", value: "CDLHARAMI" },
          op: "",
          right: {}
        }
      ],
      pairs_trailing: {},
      trailing_value: "0.3"
    }
  ],
  dca: [
    {
      conditions_list: [
        {
          left: { timeframe: "30m", value: "MFI" },
          op: "<",
          right: { value: 40 }
        },
        {
          left: {
            candle_period: 30,
            change_over: 2,
            timeframe: "5m",
            value: "MFI"
          },
          op: ">",
          right: { value: 1 }
        },
        {
          left: { timeframe: "1h", value: "MFI" },
          op: "<",
          right: { value: 50 }
        }
      ],
      dca_strategy: {
        "0": { percentage: 100, trigger: -3 },
        "3": { percentage: 200, trigger: -7.5 },
        default: { percentage: 50, trigger: -2.5 }
      },
      max_dca_level: 4,
      pairs_trailing: {
        "ONT/ETH": { trail_from: 0.006151, trail_to: 0.006169452999999999 }
      },
      trailing_value: 0.3
    }
  ],
  sell: [
    {
      conditions_list: [
        {
          id: 0,
          left: { timeframe: "30m", value: "MFI" },
          op: ">",
          right: { value: 20 }
        }
      ],
      pairs_trailing: {},
      sell_value: 0.8,
      trailing_value: 0.22
    },
    {
      conditions_list: [
        {
          id: 0,
          left: { timeframe: "30m", value: "MFI" },
          op: "<",
          right: { value: 4 }
        },
        {
          id: 1,
          left: { timeframe: "30m", value: "EMA" },
          op: ">",
          right: { value: 0 }
        }
      ],
      pairs_trailing: {},
      sell_value: 1.5,
      trailing_value: 0.22
    }
  ]
};

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

const analyzerCard = props => {
  let analyzer = props.analyzer;
  return (
    <div>
      <Card>
          {console.log(analyzer)}
        <ReactTable
                data={analyzer.pairs_trailing}
                filterable
                columns={[
                  { Header: "Time", accessor: "timestamp", Cell: ci => {
                    let date =  new Date(ci.value)
                          return date.toLocaleString()
                      }},
                  { Header: "Symbol", accessor: "symbol" },
                  { Header: "Price", accessor: "price" },
                  { Header: "Remaining", accessor: "remaining" },
                  { Header: "Filled", accessor: "filled" }
                ]}
                defaultPageSize={10}
                showPaginationBottom={false}
                className="-striped -highlight"
              />

        {Object.entries(analyzer.pairs_trailing).map(pair => {
          return (
            <p>
              {" "}
              {pair[0]} trail_from: {pair[1].trail_from} trail_to:{" "}
              {pair[1].trail_to}{" "}
            </p>
          );
        })}
      </Card>
    </div>
  );
};
class BuyAnalyzer extends React.Component {
  constructor(props) {
    super(props);
    this.state = { analyzers: [] };
    this.load = this.load.bind(this);

  }
  componentWillMount() {
    // This request takes longer, so prioritize it
    fetchJSON(analyzer_route, this.load);
  }
  load(analyzers) {
    let analyzerType = 'buy';

    this.setState({ analyzers: analyzers[analyzerType] });

    console.log(analyzers[analyzerType]);
  }
  render() {
    return (
      <div>
        {this.state.analyzers.map(analyzer => {
          return analyzerCard({ analyzer: analyzer });
        })}
      </div>
    );
  }
}

export default withStyles(extendedFormsStyle)(BuyAnalyzer);
