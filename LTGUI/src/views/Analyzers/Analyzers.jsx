import GenericAnalyzer from "./GenericAnalyzer";
import React from "react";

export const BuyAnalyzer = props => {
  return <GenericAnalyzer analyzerType={"buy"} />;
};

export const SellAnalyzer = props => {
  return <GenericAnalyzer analyzerType={"sell"} />;
};

export const DCAAnalyzer = props => {
  return <GenericAnalyzer analyzerType={"dca"} />;
};
