console.log("Script running!");

document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#emails-view').addEventListener('click', function(event) {
    if (event.target.closest(".email")) {
      email = event.target.closest(".email")
      id = email.dataset.id
      mailbox = document.querySelector("#emails-view").querySelector("h3").innerText;
      load_email(id, mailbox);
    }
  });

  // By default, load the inbox
  load_mailbox('inbox');

  // Listen for submit of compose message
  document.querySelector("#compose-form").onsubmit = send_email;
});

function load_email(id, mailbox) {
  // Show email view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';

  fetch( `/emails/${id}`)
  .then(response => response.json())
  .then(email => {
    console.log(email);
    div = document.getElementById("email-view");
  
    // add email info to container
    title = document.createElement("h4");
    title.innerHTML = `${email.subject}`;
    div.append(title);

    sender = document.createElement("p");
    sender.innerHTML = `Sender: ${email.sender}`;
    div.append(sender);
  
    recipients = document.createElement("p");
    recipients.innerHTML = `Recipients: ${email.recipients}`;
    div.append(recipients);
  
    time = document.createElement("p");
    time.innerHTML = `Time: ${email.timestamp}`;
    div.append(time);
    
    body = document.createElement("p");
    body.innerHTML = email.body;
    div.append(body);
    console.log(mailbox);
    // add archive or unarchive button as needed
    if (mailbox === "Sent") {

    } else if (email.archived === true) {
      button = document.createElement("button");
      button.innerText = "Unarchive";
      button.className = "Unarchive";
      div.append(button);
      button.onclick = () => unarchive(id);
    } else if (email.archived === false) {
      button = document.createElement("button");
      button.innerText = "Archive";
      div.append(button);
      button.onclick = () => archive(id);
    }

    // add reply button
    if (mailbox === "Sent") {
  
    } else {
      console.log("working");
      reply_btn = document.createElement("button");
      reply_btn.innerText = "Reply";
      reply_btn.className = "reply";
      div.append(reply_btn);
      reply_btn.onclick = () => reply(email);
    }
  })

  // mark as read
  fetch(`/emails/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      read: true
    })
  })
}

function archive(id) {
  fetch(`/emails/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      archived: true
    })
  })
  .then(response => {
    load_mailbox("inbox");
  })
}

function unarchive(id) {
  fetch(`/emails/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      archived: false
    })
  })
  .then(response => {
    load_mailbox("inbox");
  })
}

function send_email(event) {
  event.preventDefault();
  fetch("/emails", {
    method: "POST",
    body: JSON.stringify({
      recipients: document.getElementById("compose-recipients").value,
      subject: document.getElementById("compose-subject").value,
      body: document.getElementById("compose-body").value,
    })
  })
  .then(response => response.json())
  .then(result => {
    console.log(result);
    load_mailbox('sent');
  })
  return false
}

function reply(email) {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector("#email-view").innerHTML = "";

  // Fill out composition fields
  document.querySelector('#compose-recipients').value = email.sender;
  document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
  document.querySelector('#compose-body').value = `On ${email.timestamp}, ${email.sender} wrote:\n ${email.body}\n\n`;
}

function compose_email() {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector("#email-view").innerHTML = "";

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector("#email-view").innerHTML = "";

  // remove archive button listeners
  document.querySelector('button').onclick = null;

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Fetch mail in mailbox
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    console.log(emails);
    emails.forEach(email => {
      // create container div
      div = document.createElement("div");
      div.className = "email";
      document.querySelector("#emails-view").append(div);

      // check if read
      if (email.read === true) {
        div.classList.add("read"); 
      } else {
        div.classList.add("unread");
      }

      // add email id to container data attribute
      div.setAttribute("data-id", email.id);

      // add email info to container
      title = document.createElement("h5");
      title.innerHTML = `${email.subject}`;
      div.append(title);

      sender = document.createElement("p");
      sender.innerHTML = `Sender: ${email.sender}`;
      div.append(sender);

      time = document.createElement("p");
      time.innerHTML = `Time: ${email.timestamp}`;
      div.append(time);
    });
  })
}