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
import { fetchJSON } from "views/Settings/helpers/Helpers.jsx";
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
import Badge from "components/Badge/Badge.jsx";
import CardHeader from "../../components/Card/CardHeader";

const styles = {
  cardIconTitle: {
    ...cardTitle,
    marginTop: "15px",
    marginBottom: "0px"
  }
};
const accessors = ["symbol", "trail_from", "trail_to", "close", "stats"];
const headers = ["Symbol", "Trail From", "Trail To", "Price", "Statistics"];

const tabs = ["trailing", "statistics", "strategy"];
const cardstyle = {
  background: "#904bff",
  textAlign: "center",
  justify: "center",
  padding: "10px 10px"
};

const analyzerCard = props => {
  let analyzer = props.analyzer;
  let pairs = Object.values(analyzer.pairs_trailing);
  pairs = typeof pairs !== "undefined" ? pairs : [];
  console.log(analyzer);
  return (
    <div>
      <Card>
        <CardHeader>{analyzer.conditions_list.map(condition => {

        })}</CardHeader>
        <CardBody>
          <Table
            tableHead={headers}
            tableData={pairs.map(pair => {
              return accessors.map(accesor => {
                if (accesor === "stats") {
                  return (
                    <GridContainer justify={"center"}>
                      {pair.stats.map(stat => {
                        return (
                          <GridItem>
                            <Button style={cardstyle}>
                              {stat[0]}: &nbsp; &nbsp;
                              {stat[1] === null
                                ? "n/a"
                                : stat[1].toString().length > 5
                                  ? stat[1].toFixed(8)
                                  : stat[1].toFixed(2)}
                            </Button>
                          </GridItem>
                        );
                      })}
                    </GridContainer>
                  );
                } else {
                  return (
                    <label>
                      {accesor === "symbol"
                        ? pair[accesor]
                        : pair[accesor].toFixed(8)}
                    </label>
                  );
                }
              });
            })}
          />
        </CardBody>
      </Card>
    </div>
  );
};

class GenericAnalyzer extends React.Component {
  constructor(props) {
    super(props);
    this.state = { analyzers: [] };
    this.load = this.load.bind(this);
    this.auto_update_frequency = 10 * 1000; // x * 1000 = x seconds
  }
  componentWillMount() {
    // This request takes longer, so prioritize it
    fetchJSON(analyzer_route, this.load);
    this.auto_update = setInterval(()=> fetchJSON(analyzer_route, this.load), this.auto_update_frequency);
  }
  load(analyzers) {
    console.log(analyzers);
    let analyzerType = this.props.analyzerType;
    this.setState({ analyzers: analyzers[analyzerType] });
  }
  render() {
    let i = 0;
    return (
      <div>
        {this.state.analyzers.map(analyzer => {
          i++;

          return (
            <div>
              <legend>Strategy: {i}</legend>

              {analyzerCard({ analyzer: analyzer })}
            </div>
          );
        })}
      </div>
    );
  }
}

export default withStyles(styles)(GenericAnalyzer);
