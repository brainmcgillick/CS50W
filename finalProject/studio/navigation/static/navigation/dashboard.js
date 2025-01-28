document.addEventListener("DOMContentLoaded", () => {
    // fetch to API for upcoming classes
    fetch("upcoming_classes")
    .then(response => response.json())
    .then(classes => {
        classes.forEach(classObject => {
            let upcomingTable = document.querySelector("#upcoming");
            // create table row and append to table body
            row = document.createElement("tr");
            upcomingTable.append(row);

            // create table data elements for each column
            tableClass = document.createElement("td");
            tableClass.innerHTML = classObject.fields["style"];
            row.append(tableClass);
            
            if (userType == "student") {
                tableInstructor = document.createElement("td");
                var instructorName = classObject.fields["instructor_name"];
                tableInstructor.innerHTML = instructorName;
                row.append(tableInstructor);
            }
            
            let rawDate = classObject.fields["date"];
            let date = new Date(rawDate);
            let formattedDate = date.toLocaleDateString("en-IE", {year: 'numeric', month: 'long', day: 'numeric'});
            tableDate = document.createElement("td");
            tableDate.innerHTML = formattedDate;
            row.append(tableDate);
            
            let rawTime = classObject.fields["time"];
            let [hours, minutes, seconds] = rawTime.split(":");
            var formattedTime = `${hours}:${minutes}`;
            tableTime = document.createElement("td");
            tableTime.innerHTML = formattedTime;
            row.append(tableTime);
            tableData = document.createElement("td");
            row.append(tableData);
            tableButton = document.createElement("button");
            tableButton.className = "btn btn-danger";
            tableButton.innerHTML = "Cancel";
            tableData.append(tableButton);

            // create event listener for booking buttons
            tableButton.addEventListener("click", function() {
                // fetch to cancel classes API, if prevents repeat if button pressed again after cancelling
                if (this.innerHTML == "Cancel") {
                    fetch(`cancel_class/${rawTime}/${rawDate}/${instructorName}`)
                    this.className = "btn btn-secondary";
                    this.innerHTML = "Cancelled";
                }
            });
        })
    })
    
    // initialise page for class history pagination
    let page = 1;

    // fetch to API for class history
    fetch(`class_history/${page}`)
    .then(response => response.json())
    .then(classes => {
        classes.forEach(classObject => {
            let historyTable = document.querySelector("#history");
            // create table row and append to table body
            row = document.createElement("tr");
            historyTable.append(row);

            // create table data elements for each column
            tableClass = document.createElement("td");
            tableClass.innerHTML = classObject.fields["style"];
            row.append(tableClass);
            
            if (userType == "student") {
                tableInstructor = document.createElement("td");
                instructorName = classObject.fields["instructor_name"];
                tableInstructor.innerHTML = instructorName;
                row.append(tableInstructor);
            }
            
            let rawDate = classObject.fields["date"];
            let date = new Date(rawDate);
            let formattedDate = date.toLocaleDateString("en-IE", {year: 'numeric', month: 'long', day: 'numeric'});
            tableDate = document.createElement("td");
            tableDate.innerHTML = formattedDate;
            row.append(tableDate);
            
            let rawTime = classObject.fields["time"];
            let [hours, minutes, seconds] = rawTime.split(":");
            var formattedTime = `${hours}:${minutes}`;
            tableTime = document.createElement("td");
            tableTime.innerHTML = formattedTime;
            row.append(tableTime);
        })
    })

    // fetch stats for user
    fetch("stats")
    .then(response => response.json())
    .then(stats => {
        if (userType == "student") {
            // variables for stats
            attendedClasses = stats["count"];
            favStyle = stats["fav_style"];
            favInstructor = stats["fav_teacher"];
    
            document.querySelector("#attended").innerHTML = `No. of Classes Attended: ${attendedClasses}`;
            document.querySelector("#fav_class").innerHTML = `Favourite Class Type: ${favStyle}`;
            document.querySelector("#fav_instructor").innerHTML = `Favourite Instructor: ${favInstructor}`;
        } else {
            // variables for stats
            taughtClasses = stats["count"];
            favStyle = stats["fav_style"];
    
            document.querySelector("#taught").innerHTML = `No. of Classes Taught: ${taughtClasses}`;
            document.querySelector("#fav_class").innerHTML = `Favourite Class Type: ${favStyle}`;
        }
    })

    // pagination buttons
    let previous = document.querySelector("#previous");
    let next = document.querySelector("#next");

    previous.addEventListener("click", () => {
        if (page == 1) {
        } else {
            page = page - 1;
            fetch(`class_history/${page}`)
            .then(response => response.json())
            .then(classes => {
                // remove every existing row in table from previous page
                let historyTable = document.querySelector("#history");
                let rows = historyTable.querySelectorAll("tr");
                rows.forEach(each => {
                    each.remove();
                })

                classes.forEach(classObject => {
                    // create table row and append to table body
                    row = document.createElement("tr");
                    historyTable.append(row);
        
                    // create table data elements for each column
                    tableClass = document.createElement("td");
                    tableClass.innerHTML = classObject.fields["style"];
                    row.append(tableClass);
                    
                    if (userType == "student") {
                        tableInstructor = document.createElement("td");
                        instructorName = classObject.fields["instructor_name"];
                        tableInstructor.innerHTML = instructorName;
                        row.append(tableInstructor);
                    }
                    
                    let rawDate = classObject.fields["date"];
                    let date = new Date(rawDate);
                    let formattedDate = date.toLocaleDateString("en-IE", {year: 'numeric', month: 'long', day: 'numeric'});
                    tableDate = document.createElement("td");
                    tableDate.innerHTML = formattedDate;
                    row.append(tableDate);
                    
                    let rawTime = classObject.fields["time"];
                    let [hours, minutes, seconds] = rawTime.split(":");
                    var formattedTime = `${hours}:${minutes}`;
                    tableTime = document.createElement("td");
                    tableTime.innerHTML = formattedTime;
                    row.append(tableTime);
                })
            });
        }
    })

    next.addEventListener("click", () => {
        if (page == numPages) {
        } else {
            page = page + 1;
            fetch(`class_history/${page}`)
            .then(response => response.json())
            .then(classes => {
                // remove every existing row in table from previous page
                let historyTable = document.querySelector("#history");
                let rows = historyTable.querySelectorAll("tr");
                rows.forEach(each => {
                    each.remove();
                })

                classes.forEach(classObject => {
                    // create table row and append to table body
                    row = document.createElement("tr");
                    historyTable.append(row);
        
                    // create table data elements for each column
                    tableClass = document.createElement("td");
                    tableClass.innerHTML = classObject.fields["style"];
                    row.append(tableClass);
                    
                    if (userType == "student") {
                        tableInstructor = document.createElement("td");
                        instructorName = classObject.fields["instructor_name"];
                        tableInstructor.innerHTML = instructorName;
                        row.append(tableInstructor);
                    }
                    
                    let rawDate = classObject.fields["date"];
                    let date = new Date(rawDate);
                    let formattedDate = date.toLocaleDateString("en-IE", {year: 'numeric', month: 'long', day: 'numeric'});
                    tableDate = document.createElement("td");
                    tableDate.innerHTML = formattedDate;
                    row.append(tableDate);
                    
                    let rawTime = classObject.fields["time"];
                    let [hours, minutes, seconds] = rawTime.split(":");
                    var formattedTime = `${hours}:${minutes}`;
                    tableTime = document.createElement("td");
                    tableTime.innerHTML = formattedTime;
                    row.append(tableTime);
                })
            });
        }
    })
})