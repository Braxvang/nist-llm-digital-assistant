var bot_response_id = 0

const form = document.querySelector("#chat-form");
const chatlog = document.querySelector("#chat-log");

greet_user()

function sleep(ms) {
  return new Promise(resolveFunc => setTimeout(resolveFunc, ms));
}


async function greet_user() {
  const greeting = ["Hello! ", "I am the ", "NIST Assistant. ", "I am ", "designed ", "to ", "assist users ", "like you ",
                    "with today's ", "complex ", "cybersecurity requirements. ", "Please ask your ", "question ", "in the ",
                    "text ", "box ", "below", "."];
  
  var greeting_chunks = "NIST Assistant: ";

  // Create div that greeting will go in
  chatlog.innerHTML += "<div id=\"greeting\" style=\"background-color: rgb(26, 26, 26);\"></div>";
 
  var greeting_box = document.querySelector("#greeting");

  // slowely populate the div so it looks like it is "talking" to the user.
  for (var i = 0; i < greeting.length; i++){
    greeting_chunks += greeting[i];
    greeting_box.innerHTML = greeting_chunks;
    await sleep(250);
  }

}


form.addEventListener("submit", async (event) => {
  event.preventDefault();

  // Get the user's message from the form
  const message = form.elements.message.value;

  // Add the users message to the interface
  var message_html = "<div style=\"background-color: rgb(94, 92, 100);\">User Question: " + message + "</div>";
  chatlog.innerHTML += message_html;

  // Add a div to the interface that the bot response will get written to
  chatlog.innerHTML += "<div id=\"assistant_response" + bot_response_id.toString() + "\" style=\"background-color: rgb(26, 26, 26);\">Getting response ...</div>";
  var assistant_response_box = document.querySelector("#assistant_response" + bot_response_id.toString());
  
  //Clear the message area
  document.getElementById("message").value = "";

  // Send a request to the Flask server with the user's message
  const response = await fetch("/nist_assistant", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ messages: [{ role: "user", content: message }] }),
  });

  // Create a new TextDecoder to decode the streamed response text
  const decoder = new TextDecoder();

  // Set up a new ReadableStream to read the response body
  const reader = response.body.getReader();
  let chunks = "NIST Assistant: ";

  // Read the response stream as chunks and append them to the chat log
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks += decoder.decode(value);
    assistant_response_box.innerHTML = chunks;
  }

  // keep track of how many times the bot has responded to the user
  bot_response_id = bot_response_id + 1;
});