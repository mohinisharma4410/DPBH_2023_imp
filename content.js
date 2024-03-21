const endpoint = "http://127.0.0.1:5000/fetch_prices";
const epoint = "http://127.0.0.1:5000/";
const epointtwo = "http://127.0.0.1:5000/authenticity"
const descriptions = {
  "Sneaking": "Coerces users to act in ways that they would not normally act by obscuring information.",
  "Urgency": "Places deadlines on things to make them appear more desirable",
  "Misdirection": "Aims to deceptively incline a user towards one choice over the other.",
  "Social Proof": "Gives the perception that a given action or product has been approved by other people.",
  "Scarcity": "Tries to increase the value of something by making it appear to be limited in availability.",
  "Obstruction": "Tries to make an action more difficult so that a user is less likely to do that action.",
  "Forced Action": "Forces a user to complete extra, unrelated tasks to do something that should be simple.",
};
const dp = "Misdirection"

function scrape() {
  // website has already been analyzed
  if (document.getElementById("insite_count")) {
    return;
  }

  // aggregate all DOM elements on the page
  let elements = segments(document.body);
  let filtered_elements = [];

  for (let i = 0; i < elements.length; i++) {
    let text = elements[i].innerText.trim().replace(/\t/g, " ");
    if (text.length == 0) {
      continue;
    }
    filtered_elements.push(text);
  }

  console.log(filtered_elements);
    fetch(epoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tokens: filtered_elements }),
    })
      .then((resp) => resp.json())
      .then((data) => {
        console.log(data);
        data = data.replace(/'/g, '"');
        json = JSON.parse(data);
        let dp_count = 0;
        let element_index = 0;

      for (let i = 0; i < elements.length; i++) {
        let text = elements[i].innerText.trim().replace(/\t/g, " ");
        if (text.length == 0) {
          continue;
        }

        if (json.result[i] !== "Not Dark") {
          highlight(elements[element_index], json.result[i]);
          dp_count++;
        }
        element_index++;
      }

      // store number of dark patterns
      let g = document.createElement("div");
      g.id = "insite_count";
      g.value = dp_count;
      g.style.opacity = 0;
      g.style.position = "fixed";
      document.body.appendChild(g);
      // sendDarkPatterns(g.value);
    })
    .catch((error) => {
      alert(error);
      alert(error.stack);
    });
}


function highlight(element, type) {
  console.log("called highlight");
  console.log(element);
  if(descriptions.hasOwnProperty(type)){
  element.classList.add("insite-highlight");
  let body = document.createElement("span");
  body.classList.add("insite-highlight-body");
  element.appendChild(body);
  }
}
function authenticity(){
  let xyz=[];
fetch(epointtwo, {
  
  method: "OPTIONS",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ tokens: xyz }),
})
  .then((resp) => resp.json())
  .then((data) => {
    console.log(typeof data);
    // let tum=JSON.parse(data);
    // console.log(typeof tum);
    // console.log(tum['auth']);
    let dp_count = 0;
    let element_index = 0;
    createBox(data);
    let g = document.createElement("div");
    g.id = "insite_count";
    g.value = dp_count;
    g.style.opacity = 255;
    g.style.position = "fixed";
    document.body.appendChild(g);
    // sendDarkPatterns(g.value);
  })
  .catch((error) => {
    alert(error);
    alert(error.stack);
  });
}

function createBox(cont) {
  var box = document.createElement("div");
  box.textContent = cont;
  box.style.fontSize="25px";
  box.style.backgroundColor = "red";
  box.style.color = "white";
  box.style.padding = "10px";
  box.style.borderRadius = "5px";
  box.style.position = "fixed";
  box.style.top = "30%";
  box.style.left = "30%";
  box.style.transform = "translate(-50%, -50%)";

  // Append the box to the document body
  document.body.appendChild(box);
}
function creategreenBox(data) {
  var box = document.createElement("div");
  var content = "";

  for (let item of data) {
    content += `<p><strong>${item.name}</strong>: ${item.price}</p>`;
  }

  box.innerHTML = content;
  box.style.backgroundColor = "green";
  box.style.color = "white";
  box.style.padding = "10px";
  box.style.borderRadius = "5px";
  box.style.position = "fixed";
  box.style.top = "50%";
  box.style.left = "40%";
  box.style.transform = "translate(-50%, -50%)";

  // Append the box to the document body
  document.body.appendChild(box);
}
function fetchProductPrices() {
  asdw=[]
  fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tokens: asdw }),
  })
    .then((resp) => resp.json())
    .then((data) => {
      console.log(data);
      // console.log(json);
      let dp_count = 0;
      let element_index = 0;
      creategreenBox(data);

      let g = document.createElement("div");
      g.id = "insite_count";
      g.value = dp_count;
      g.style.opacity = 0;
      g.style.position = "fixed";
      document.body.appendChild(g);
      // sendDarkPatterns(g.value);
    })
    .catch((error) => {
      alert(error);
      alert(error.stack);
    });
}

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
  if (message.action === "function1") {
    scrape()
    console.log("Function 1 executed!");
  } else if (message.action === "function2") {
    console.log("Function 2 executed!");
    authenticity()
  }
  else if (message.action === "function3") {
    console.log("Function 3 executed!");
    fetchProductPrices()
  }
  else if (message.action === "function4") {
    console.log("Function 4 executed!");
    // secondbutton()
  }
});