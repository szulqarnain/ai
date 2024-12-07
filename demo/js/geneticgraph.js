const config = {
  container_id: "graph",
  server_url: "bolt://localhost:7687",
  server_user: "neo4j",
  server_password: "Password123$", // user , user only have read access! So safe to put it here
  labels: {
    Strain: {
      caption: "name",
      size: "id",
      community: "type_id",
    },
  },
  relationships: {
    DISTANCE: {
      thickness: "value",
      caption: false,
    },


  },
  initial_cypher: `MATCH p=(s1:Strain)-[r:DISTANCE]->(s2:Strain) RETURN *`,
};

var driver = neo4j.driver(
  "bolt://localhost:7687",
  neo4j.auth.basic("neo4j", "Password123$")
);

// function draw(name, subType, relationType, value) {
//   const strainName = name === "All" ? "" : `{name:'${name}'}`;
//  /// const relation = relationType == 1 ? "SEQUENCE_SIMILARITY" : "DISTANCE";
//   ///const relation = relationType == "1" ? "SEQUENCE_SIMILARITY" :(relationType=="0" ? "DISTANCE":"HI_TITER_VALUE");
//   const relation = relationType == "1" ? "" :"GENETIC_DISTANCE";
//   //const operatorString = operator == 1 ? "<=" : ">=";
//  // const operatorString = "=";
//   const operatorQuery =
//     //value === "" ? "" : `r.value ${operatorString} ${value}`;
//       value === "" ? "" : `${value}`;
//   ///
//   const subTypeString =
//     subType === "All"
//       ? ""
//       : `s1.type = '${subType}' AND s2.type = '${subType}'`;
//   const whereCause =
//     subTypeString !== "" || operatorQuery !== ""
//       ? ` LIMIT${subTypeString} ${operatorQuery}`
//       :  ``;
//   const cipher = `MATCH p=(s1:Strain${strainName})-[r:${relation}]->(s2:Strain) RETURN p ORDER BY r.value ${whereCause} `;
// //WHERE ${subTypeString} ${operatorQuery}
//   console.log(cipher);
//   graph.renderWithCypher(cipher);
// }
function draw(name, subType, relationType, value, operator) {
  const strainName = name === "All" ? "" : `{name:'${name}'}`;
 // const relation = relationType == 1 ? "SEQUENCE_SIMILARITY" : "DISTANCE";
  //const relation = relationType == "1" ? "SEQUENCE_SIMILARITY" :(relationType=="0" ? "DISTANCE":"HI_TITER_VALUE");
  const relation = relationType == "0" && "GENETIC_DISTANCE";
  const operatorString = operator == 1 ? "<=" : ">=";
  const operatorQuery =
    value === "" ? "" : `AND r.value ${operatorString} ${value}`;
  ///
  const subTypeString =
    subType === "All"
      ? ""
      : `s1.type = '${subType}' AND s2.type = '${subType}'`;
  const whereCause =
    subTypeString !== "" || operatorQuery !== ""
      ? `WHERE ${subTypeString} ${operatorQuery}`
      : "";
  const cipher = `MATCH p=(s1:Strain${strainName})-[r:${relation}]->(s2:Strain) ${whereCause} RETURN *`;

  console.log(cipher);
  graph.renderWithCypher(cipher);
}

function filter() {
  setLoading(true);
  const subType = document.getElementById("subType").value;
  const relationType = document.getElementById("relationType").value;
  const optionValue = document.getElementById("optionValue").value;
  const operator = document.getElementById("operator").value;
  const name = document.getElementById("name").value;
  draw(name, subType, relationType, optionValue, operator);
}

// function clearFilter() {
//   setLoading(true);
//   document.getElementById("name").value="All";
//   document.getElementById("subType").value = "All";
//   document.getElementById("relationType").value = 0;
//   document.getElementById("optionValue").value = "";
//   //document.getElementById("operator").value = 0;
//   graph.renderWithCypher(config.initial_cypher);
// }
function clearFilter() {
  setLoading(true);

  // Save existing options excluding "All"
  const nameSelect = document.getElementById("name");
  const existingOptions = Array.from(nameSelect.options).filter(
    (option) => option.value !== "All"
  );

  // Reset filter input values to default
  document.getElementById("subType").value = "All";
  document.getElementById("relationType").value = "0";
  document.getElementById("optionValue").value = "";
  document.getElementById("operator").value = "0";

  // Clear and set the Name select box to display "All"
  nameSelect.innerHTML = "";
  const allOption = document.createElement("option");
  allOption.value = "All";
  allOption.text = "All";
  nameSelect.appendChild(allOption);

  // Add back the existing options excluding "All"
  existingOptions.forEach((option) => {
    const newOption = document.createElement("option");
    newOption.value = option.value;
    newOption.text = option.text;
    nameSelect.appendChild(newOption);
  });

  // Fetch the graph based on default filters (All)
  const subType = document.getElementById("subType").value;
  const relationType = document.getElementById("relationType").value;
  const optionValue = document.getElementById("optionValue").value;
  const operator = document.getElementById("operator").value;
  draw("All", subType, relationType, optionValue, operator);
}

function render_completed() {
  setTimeout(function () {
    setLoading(false);
  }, 1000);
}

function setLoading(status) {
  const loading = document.getElementById("loading");
  if (status) {
    loading.style.display = "block";
  } else {
    loading.style.display = "none";
  }
}

function loadRegions() {
  let session = driver.session();
  let readTxResultPromise = session.readTransaction((txc) => {
    return txc.run(
      "MATCH p=(s1:Strain)-[]-(s2:Strain) WHERE s1.region IS NOT NULL RETURN DISTINCT s1.region LIMIT 1500;"
    );
  });

  // returned Promise can be later consumed like this:
  readTxResultPromise
    .then((result) => {
      let data = [{ id: "All", text: "All" }];
      result.records.forEach(function (record, index) {
        data.push({ id: record._fields[0], text: record._fields[0] });
      });
      $("#region").select2({ placeholder: "Search region", data: data });
    })
    .catch((error) => {
      console.log(error);
    })
    .then(() => session.close());
}

function loadStrains() {
  let session = driver.session();
  let readTxResultPromise = session.readTransaction((txc) => {
    return txc.run(
      "MATCH p=(s1:Strain)-[]-(s2:Strain) RETURN DISTINCT s1.name LIMIT 1500;"
    );
  });

  // returned Promise can be later consumed like this:
  readTxResultPromise
    .then((result) => {
      let data = [{ id: "All", text: "All" }];
      result.records.forEach(function (record, index) {
        data.push({ id: record._fields[0], text: record._fields[0] });
      });
      $("#name").select2({ placeholder: "Search strain", data: data });
    })
    .catch((error) => {
      console.log(error);
    })
    .then(() => session.close());
}

var graph = new NeoVis.default(config);
graph.registerOnEvent("completed", render_completed);
graph.render();

$(document).ready(function () {
  loadRegions();
  loadStrains();
});

$(".toggle_button").click(function () {
  if ($(".filter_box").hasClass("hide")) {
    $(".filter_box").removeClass("hide");
    $(".toggle_button").html('<i class="far fa-times-circle"></i>');
  } else {
    $(".filter_box").addClass("hide");
    $(".toggle_button").html('<i class="fas fa-cogs"></i>');
  }
});
