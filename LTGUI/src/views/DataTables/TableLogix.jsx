const buyLogVars = {
  columns: [
    {
      Header: "Time",
      accessor: "timestamp",
      Cell: ci => {
        let date = new Date(ci.value);
        return date.toLocaleString();
      }
    },
    { Header: "Symbol", accessor: "symbol" },
    { Header: "Price", accessor: "price" },
    { Header: "Remaining", accessor: "remaining" },
    { Header: "Filled", accessor: "filled" }
  ],
  label: "Buy Log",
  
};
