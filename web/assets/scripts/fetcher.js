async function getWords(date) {
  const url = `http://0.0.0.0:5000/api/v1/${date}/words`;
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const json = await response.json();
    // console.log(json);
  } catch (error) {
    console.error(error.message);
  }
}

async function getWord(idx) {
  const url = `http://0.0.0.0:5000/api/v1/word/${idx}/`;
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const json = await response.json();
    renderWord(json);
  } catch (error) {
    console.error(error.message);
  }
}

function clear_content() {
  document.querySelector("#word-pronunciation").innerHTML = "";
  document.querySelector("section.definitions").innerHTML = "";
}

function renderWord(word) {
  clear_content();
  title = document.querySelector("h1#word-title");
  title.textContent = word.title;
  pronunciation = document.querySelector("#word-pronunciation");
  if (word.pronunciation) {
    ipa = document.createElement("i");
    ipa.setAttribute("id", "word-ipa");
    ipa.textContent = word.pronunciation["ipa"];
    pronunciation.appendChild(ipa);

    if (word.pronunciation.audio_link) {
      speak = document.createElement("audio");
      speak.setAttribute("controls", "");
      speak.setAttribute("id", "word-audio");
      speak.src = word.pronunciation.audio_link;
      pronunciation.appendChild(speak);
    }
  }

  definitions = document.querySelector("section.definitions");
  for (const def of word.definitions) {
    divDesc = document.createElement("div");
    divDesc.setAttribute("class", "word-description");

    // part of speech
    wordPOS = document.createElement("span");
    wordPOS.setAttribute("class", "word-pos");
    wordPOS.textContent = `${def.part_of_speech.toLowerCase()}:`;
    divDesc.appendChild(wordPOS);

    // definition
    divDef = document.createElement("div");
    divDef.setAttribute("class", "word-definition");
    txt = document.createElement("p");
    txt.textContent = def.definition;
    divDef.appendChild(txt);

    //examples
    if (def.examples.length) {
      examples = document.createElement("ul");
      examples.setAttribute("class", "examples");
      lbl = document.createElement("h3");
      lbl.setAttribute("class", "header-examples");
      lbl.textContent = "examples";
      examples.appendChild(lbl);
      for (const ex of def.examples) {
        li = document.createElement("li");
        li.textContent = ex;
        examples.appendChild(li);
      }
      divDef.appendChild(examples);
    }
    divDesc.appendChild(divDef);
    definitions.appendChild(divDesc);
  }
}

function selectRandomWord(arr) {
  const idx = Math.floor(Math.random() * arr.length);
  w = arr[idx];
  arr.splice(idx, 1);

  return w;
}

unseen = [...Array(20).keys()];
getWord(selectRandomWord(unseen));

document
  .querySelector("#next-word")
  .addEventListener("click", function handleClick(event) {
    w = selectord(unseen);
    getWord(w);
  });
