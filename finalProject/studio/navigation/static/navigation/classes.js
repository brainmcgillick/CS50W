document.addEventListener("DOMContentLoaded", function() {
    if (userType == "teacher") {
        // prevent selection of previous dates in class creator
        let today = new Date().toISOString().split('T')[0];
        document.querySelector('#date').setAttribute('min', today);
    }

    // event listener for search button
    let search = document.querySelector("#search_button");
    search.addEventListener("click", () => {
        // save date to variable
        var search_date = document.querySelector("#search_date").value;
        
        // if no search date input then do nothing
        if (search_date === "") {
        } else {
            // fetch to get_classes API
            fetch(`get_classes/${search_date}`)
            .then(response => response.json())
            .then(classes => {
                // set table header to date
                let date = new Date(search_date);
                let formattedDate = date.toLocaleDateString("en-IE", {year: 'numeric', month: 'long', day: 'numeric'});
                document.querySelector("#table_heading").innerHTML = `Class Schedule: ${formattedDate}`;
    
                // remove every existing row in table from potential previous searches
                let tableBody = document.querySelector("#classlist");
                let rows = tableBody.querySelectorAll("tr");
                rows.forEach(each => {
                    each.remove();
                })
    
                // populate rows for each class
                classes.forEach(classObject => {    
                    // create table row and append to table body
                    row = document.createElement("tr");
                    tableBody.append(row);
    
                    // create table data elements for each column
                    tableClass = document.createElement("td");
                    tableClass.innerHTML = classObject["style"];
                    row.append(tableClass);
                    
                    tableInstructor = document.createElement("td");
                    var instructorName = classObject["instructor_name"];
                    tableInstructor.innerHTML = instructorName;
                    row.append(tableInstructor);
                    
                    let rawTime = classObject["time"];
                    let [hours, minutes, seconds] = rawTime.split(":");
                    var formattedTime = `${hours}:${minutes}`;
                    tableTime = document.createElement("td");
                    tableTime.innerHTML = formattedTime;
                    row.append(tableTime);

                    tableCapacity = document.createElement("td");
                    let capacity = classObject["count"];
                    tableCapacity.innerHTML = `${capacity}/12`;
                    tableCapacity.setAttribute("id", "capacity");
                    row.append(tableCapacity);

                    // vars for check
                    var complete = classObject["complete"];
                    var booked = classObject["booked"];
                    
                    if (userType == "student") {
                        if (complete == false && booked == false && capacity < 12){
                            tableData = document.createElement("td");
                            row.append(tableData);
                            tableButton = document.createElement("button");
                            tableButton.className = "btn btn-primary";
                            tableButton.innerHTML = "Book";
                            tableData.append(tableButton);
                        } else if(complete == true) {
                            tableData = document.createElement("td");
                            row.append(tableData);
                            tableButton = document.createElement("button");
                            tableButton.className = "btn btn-secondary";
                            tableButton.innerHTML = "Completed";
                            tableData.append(tableButton);
                        } else if(booked == true) {
                            tableData = document.createElement("td");
                            row.append(tableData);
                            tableButton = document.createElement("button");
                            tableButton.className = "btn btn-danger";
                            tableButton.innerHTML = "Cancel";
                            tableData.append(tableButton);
                        } else if(capacity == 12) {
                            tableData = document.createElement("td");
                            row.append(tableData);
                            tableButton = document.createElement("button");
                            tableButton.className = "btn btn-secondary";
                            tableButton.innerHTML = "Full";
                            tableData.append(tableButton);
                        }
                    } else {
                        tableData = document.createElement("td");
                        row.append(tableData);
                        tableButton = document.createElement("button");
                        tableButton.className = "btn btn-danger";
                        tableButton.innerHTML = "Cancel";
                        tableData.append(tableButton);
                    }

                    // create event listener for booking buttons
                    tableButton.addEventListener("click", function() {
                        if (this.innerHTML == "Book"){
                            // fetch to book classes API
                            fetch(`book_class/${rawTime}/${search_date}/${instructorName}`)
                            this.className = "btn btn-danger";
                            this.innerHTML = "Cancel";

                            // get current class capacity
                            let element = this.parentElement.parentElement.querySelector("#capacity");
                            let text = element.innerText;
                            let currentCapacity = parseInt(text.split("/")[0]);
                            let newCapacity = currentCapacity + 1;

                            // update capacity
                            element.innerHTML = `${newCapacity}/12`;
                        } else if (this.innerHTML == "Cancel") {
                            // fetch to cancel classes API
                            fetch(`cancel_class/${rawTime}/${search_date}/${instructorName}`)
                            if (userType == "student") {
                                this.className = "btn btn-primary";
                                this.innerHTML = "Book";
                                // get current class capacity
                                let element = this.parentElement.parentElement.querySelector("#capacity");
                                let text = element.innerText;
                                let currentCapacity = parseInt(text.split("/")[0]);
                                let newCapacity = currentCapacity - 1;

                                // update capacity
                                element.innerHTML = `${newCapacity}/12`;
                            } else {
                                this.className = "btn btn-secondary";
                                this.innerHTML = "Cancelled";
                            }
                        }   
                    });
                });
            })
        }
    })
})