console.log("Script running!");

document.addEventListener('DOMContentLoaded', function() {
    // identify page changing buttons
    let page_back = document.querySelector("#page-back")
    let page_forward = document.querySelector("#page-forward")
    
    // initialise page as 1 for paginator
    let page = 1;

    // csrf token
    const csrf = document.querySelector("[name=csrfmiddlewaretoken]").getAttribute("content");

    // fetch page 1 of posts
    fetch(`/following/${page}`)
    .then(response => response.json())
    .then(posts => {
        posts.forEach(post => create_posts(post));
    })

    // set listeners and actions
    page_back.addEventListener('click', () => {
        // if page 1, do nothing
        if (page === 1) {
            
        } else {
            // reduce page variable by 1
            page = page - 1;
            document.querySelector("#page-current").innerHTML = `Page ${page} of ${num_pages}`;

            // find and remove all currently shown posts
            shown_posts = document.querySelectorAll(".post");
            for (post of shown_posts) {
                post.remove();
            }

            // fetch page of posts
            fetch(`/following/${page}`)
            .then(response => response.json())
            .then(posts => {
                posts.forEach(post => create_posts(post));
            })
        }
    })
    
    // set listeners and actions
    page_forward.addEventListener('click', () => {
        // if final page, do nothing
        if (page === num_pages) {

        } else {
            // increment page variable by 1
            page = page + 1;
            document.querySelector("#page-current").innerHTML = `Page ${page} of ${num_pages}`;

            // find and remove all currently shown posts
            shown_posts = document.querySelectorAll(".post");
            for (post of shown_posts) {
                post.remove();
            }

            // fetch page of posts
            fetch(`/following/${page}`)
            .then(response => response.json())
            .then(posts => {
                posts.forEach(post => create_posts(post));
            })
        }
    })

    function create_posts(post) {
        // create container
        let div = document.createElement("div");
        div.className = "post";
        div.setAttribute("id", `post_${post.id}`)
        document.querySelector("#posts").append(div);
        
        // add post info
        user = document.createElement("a");
        user.setAttribute("href", `/profile/${post.user}`)
        user.innerHTML = `<strong>${post.user}</strong>`;
        div.append(user);

        text = document.createElement("p");
        text.innerHTML = `${post.text}`;
        div.append(text);
        
        timestamp = document.createElement("p");
        timestamp.innerHTML = `${post.timestamp}`;
        timestamp.setAttribute("id", "timestamp");
        div.append(timestamp);
        
        likes = document.createElement("p");
        likes.innerHTML = `${post.likes} Likes`;
        likes.setAttribute("id", "likes-count");
        div.append(likes);

        // like button
        like_button = document.createElement("button");
        like_button.setAttribute("id", "like-button");
        like_button.innerHTML = "Like";
        div.append(like_button);
        
        // unlike button
        unlike_button = document.createElement("button");
        unlike_button.setAttribute("id", "unlike-button");
        unlike_button.innerHTML = "Unlike";
        div.append(unlike_button);

        // check if post was liked and set display states
        if (post.liked == true) {
            like_button.setAttribute("style", "display: none");
            unlike_button.setAttribute("style", "display: block");
        } else {
            like_button.setAttribute("style", "display: block");
            unlike_button.setAttribute("style", "display: none");
        }

        // like buttons onclick
        like_button.addEventListener("click", () => like(post.id))
        unlike_button.addEventListener("click", () => unlike(post.id))
    }

    function like(post_id) {
        fetch(`/like`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrf
            },
            body: JSON.stringify({
                liker: viewer,
                post: post_id
            })
        }).then(response => response.json())
        .then(response => {
            document.querySelector(`#post_${post_id} #likes-count`).innerHTML = `${response.likes} Likes`;

            // hide follow button and show unfollow button
            like_button = document.querySelector(`#post_${post_id} #like-button`)
            unlike_button = document.querySelector(`#post_${post_id} #unlike-button`)
            like_button.setAttribute("style", "display: none;")
            unlike_button.setAttribute("style", "display: block;")
        })
    }
    
    function unlike(post_id) {
        fetch(`/unlike`, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrf
            },
            body: JSON.stringify({
                liker: viewer,
                post: post_id
            })
        }).then(response => response.json())
        .then(response => {
            document.querySelector(`#post_${post_id} #likes-count`).innerHTML = `${response.likes} Likes`;

            // hide follow button and show unfollow button
            like_button = document.querySelector(`#post_${post_id} #like-button`)
            unlike_button = document.querySelector(`#post_${post_id} #unlike-button`)
            like_button.setAttribute("style", "display: block;")
            unlike_button.setAttribute("style", "display: none;")
        })
    }
})
