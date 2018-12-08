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
import { cardTitle } from "assets/jss/material-dashboard-pro-react.jsx";
import ReactTable from "react-table";
import CardBody from "../../components/Card/CardBody";

export function fetchJSON(url, callback) {
  fetch(url)
    .then(resp => {
      return resp.json();
    })
    .then(callback);
}
const styles = {
  cardIconTitle: {
    ...cardTitle,
    marginTop: "15px",
    marginBottom: "0px"
  }
};
const accessors = ["symbol", "trail_from", "trail_to", "close", "stats"];

const tabs = ["trailing", "statistics", "strategy"];

const analyzerCard = props => {
  let analyzer = props.analyzer;
  console.log(analyzer);
  let pairs = Object.values(analyzer.pairs_trailing);
  pairs = typeof pairs !== "undefined" ? pairs : [];
  console.log(pairs, "pairs");
  return (
    <div>
      <Card>
        <CardBody>
          <GridContainer justify={"center"}>
            {pairs.map(pair => {
              return accessors.map(accesor => {
                if (accesor !== "stats") {
                  return (
                    <GridItem lg={2}>
                      <small>{accesor} : </small>
                      {accesor === "symbol"
                        ? pair[accesor]
                        : pair[accesor].toFixed(8)}
                    </GridItem>
                  );
                } else {
                  return (
                    <GridItem lg={4}>
                      <GridContainer>
                        {pair.stats.map(stat => {
                          return (
                            <GridItem xs={4}>
                              {stat[0]}:{" "}
                              {stat[1] === null
                                ? "n/a"
                                : stat[1].toString().length > 5
                                  ? stat[1].toFixed(8)
                                  : stat[1].toFixed(2)}
                            </GridItem>
                          );
                        })}
                      </GridContainer>
                    </GridItem>
                  );
                }
              });
            })}
          </GridContainer>
        </CardBody>
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
    console.log(analyzers);
    let analyzerType = "buy";

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

export default withStyles(styles)(BuyAnalyzer);
