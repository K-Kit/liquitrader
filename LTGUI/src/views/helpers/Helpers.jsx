export function loginUserSuccess(token) {
  localStorage.setItem("token", token);
}

export function fetchErrorHandler(response, error = false) {
  if (error) {
    console.log("error: ", error);
  }

  if (response.status === 401 && window.location.pathname != "/setup") {
    window.location.pathname = "/login";
  }

  return response;
}

export function fetchJSON(uri, callback, log_error = true) {
  fetch(uri, {
    credentials: "include",
    headers: {
        "Authorization": localStorage.getItem("token")
    }
  })
    .then(response => {
      if (log_error) {
        fetchErrorHandler(response);
      }
      return response;
    })
    .then(response => {
      return response.json();
    })
    .then(callback)
    .catch(error => fetchErrorHandler(error));
}

export function fetchDataBlocking(uri) {
  let request = new XMLHttpRequest();

  request.open("GET", uri, false);
  request.send(null);

  return [request.status, request.response];
}

export function fetchData(uri, callback) {
  return fetch(uri, { credentials: "include" })
    .then(fetchErrorHandler)
    .then(response => {
      return response.text();
    })
    .then(response_body => {
      try {
        return response_body;
      } catch (err) {
        console.log("No data received from /" + uri);
      }
    })
    .then(callback)
    .catch(error => fetchErrorHandler(false, error));
}

export function postJSON(uri, data, callback) {
  return fetch(uri, {
    // credentials: "include",
    method: "post",
    headers: {
      "Accept": "application/json, text/plain, */*",
      "Content-Type": "application/json",
      "Authorization": localStorage.getItem("token")
    },
    body: JSON.stringify(data)
  })
    .then(fetchErrorHandler)
    .then(response => {
      console.log(response);
      return response.text();
    })
    .then(response_body => {
      try {
        return response_body;
      } catch (err) {
        console.log("No data received from /" + uri);
      }
    })
    .then(callback)
    .catch(error => fetchErrorHandler(false, error));
}

export function getCurrentTab() {
  return window !== undefined ? window.location.hash.substring(1) : false;
}

function generate_table() {
  if (!String.format) {
    String.format = function(format) {
      let args = Array.prototype.slice.call(arguments, 1);
      return format.replace(/{(\d+)}/g, function(match, number) {
        return typeof args[number] !== "undefined" ? args[number] : match;
      });
    };
  }

  // Unify newline format and split into an array by newline character
  let lines = this.state.data.replace(/\r/g, "").split("\n");
  let settings = {};
  let current_header = "";

  // Parse lines into object
  lines.forEach(line => {
    // Section heading,
    if (line.indexOf(";") !== -1) {
      let cleaned_line = line.replace(/ *; */g, "");
      let header_parts = cleaned_line.split(" ");
      current_header = header_parts.join(" ");

      settings[current_header] = {};

      // Setting/value pairs
    } else if (line.indexOf("=") !== -1) {
      let cleaned_line = line.replace(/ *= */g, "=");
      let header_and_values = cleaned_line.split("=");

      settings[current_header][
        header_and_values[0]
      ] = header_and_values[1].split(",");
    }
  });

  // Eliminate sections with no inputs (caused by comments that aren't section headers)
  Object.keys(settings).forEach(header => {
    if (Object.keys(settings[header]).length === 0) {
      delete settings[header];
    }
  });

  let section_start_format =
    '<div class="config-section"><span class="config-header">{0}</span>';
  let setting_line_format =
    '<div class="config-line"><div class="setting-label-container"><span class="setting-label">{0}</span></div><div class="setting-input-group">';
  let setting_input_format =
    '<input class="setting-input" id="{0}_{1}" value="{2}" />';

  let table =
    "<style>" +
    ".config-section:not(:first-of-type) { margin-top: 40px; }" +
    ".config-section { border: solid 1px grey; padding: 20px; }" +
    ".config-header { font-weight: 1000; font-size: 14pt; }" +
    ".config-line { display: flex; border-top: solid .5px grey; padding: 10px 0; }" +
    ".config-line:first-of-type { margin-top: 20px; }" +
    ".config-line:last-of-type { border-bottom: solid .5px grey; }" +
    ".config-line { display: flex; } " +
    ".setting-label-container { display: flex; flex-direction: column; justify-content: center; }" +
    ".setting-label { width: 250px; }" +
    ".setting-input-group { display: flex; flex-wrap: wrap; width: calc(100% - 250px); }" +
    ".setting-input { margin: 5px; border: solid 1px; width: 250px; padding: 7px; }" +
    "</style>";

  table += '<div id="config_table">';

  // Loop headers (BUY SETTINGS, etc.)
  Object.keys(settings).forEach(header => {
    let current_header = settings[header];

    table += String.format(section_start_format, header); // Create section and section label

    // Loop settings (max_spread, etc.)
    Object.keys(current_header).forEach(setting => {
      table += String.format(setting_line_format, setting); // Config line container, label, and input container

      // Loop values (setting line split by commas) and create inputs for each
      let sub_id = 0;
      current_header[setting].forEach(val => {
        table += String.format(setting_input_format, setting, sub_id, val);
        sub_id += 1;
      });

      table += "</div></div>"; // Close input group and config-line
    });

    table += "</div>"; // Close config-section
  });

  table += "</div>"; // Close table

  return table;
}

export function strCount(string, subString) {
  if (string.length === 0 || subString.length === 0) {
    return 0;
  }

  return Math.max(0, string.split(subString).length - 1);
}
